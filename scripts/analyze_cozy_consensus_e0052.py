"""E0052: offline reference-consensus edge diagnostic on E0021 Cozy EXRs.

Masks are chosen from references only. No new renderer calls or denoiser.
Two 1024spp references are finite; a screen is NOT a perceptual quality result.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from acd_lab.core import rgb, compare_images
from acd_lab.io import read_arrays, write_report

SOURCE = "5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395"
SEEDS = (539, 911, 1337)
METHODS = ("Raw", "STANDARD", "NATIVE_COMP_OIDN")
ROIS = {"detail_1": (192, 288, 96, 96), "detail_2": (320, 192, 96, 96),
        "detail_3": (288, 96, 96, 96), "whole_image": (0, 0, 512, 482)}


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1048576), b""):
            h.update(part)
    return h.hexdigest()


def gradients(image):
    """asinh of linear luminance, then strictly within-region horizontal/vertical gradients."""
    values = rgb(image)
    luma = np.arcsinh(values @ np.array([.2126, .7152, .0722]))
    return np.concatenate([np.diff(luma, axis=1).ravel(), np.diff(luma, axis=0).ravel()])


def inspect_region(ref1, ref2, candidate_seeds, rect):
    a, b = rgb(ref1), rgb(ref2)
    if a.shape != b.shape:
        raise ValueError("reference shape mismatch")
    x, y, w, h = rect
    if x < 0 or y < 0 or w < 2 or h < 2 or x + w > a.shape[1] or y + h > a.shape[0]:
        raise ValueError("ROI outside reference image")
    def patch(image):
        v = rgb(image)
        if v.shape != a.shape:
            raise ValueError("candidate shape mismatch")
        return v[y:y+h, x:x+w]
    g1, g2 = gradients(patch(a)), gradients(patch(b))
    strength = np.minimum(np.abs(g1), np.abs(g2))
    agree = ((g1 * g2) > 0) & (strength > 1e-12)
    threshold = float(np.quantile(strength[agree], .80)) if np.any(agree) else None
    mask = (agree & (strength >= threshold) &
            (strength > 2 * np.abs(g1-g2))) if threshold is not None else np.zeros_like(agree)
    count = int(mask.sum())
    gref = (g1 + g2) / 2
    if count:
        rms = float(np.sqrt(np.mean(gref[mask]**2)))
        spread = float(np.sqrt(np.mean((g1[mask]-g2[mask])**2)))
        relative = spread / max(rms, 1e-12)
    else:
        rms = spread = relative = None
    scores = {}
    for seed, methods in sorted(candidate_seeds.items()):
        scores[str(seed)] = {}
        for name in METHODS:
            image = patch(methods[name])
            gc = gradients(image)
            gain = (float(np.dot(gc[mask], gref[mask]) /
                          max(float(np.dot(gref[mask], gref[mask])), 1e-24))
                    if count else None)
            edge_error = (float(np.sqrt(np.mean((gc[mask]-gref[mask])**2)))
                          if count else None)
            scores[str(seed)][name] = {
                "projected_edge_gain": gain,
                "edge_gradient_rmse": edge_error,
                "rmse_ref1": compare_images(patch(a), image)["rmse_linear"],
                "rmse_ref2": compare_images(patch(b), image)["rmse_linear"]
            }
    gains = [scores[str(s)]["NATIVE_COMP_OIDN"]["projected_edge_gain"]
             for s in SEEDS if str(s) in scores]
    screen = bool(count >= 32 and relative is not None and relative < .35
                  and len(gains) == 3 and all(g is not None and 0 <= g < .85 for g in gains))
    return {
        "rect_xywh": list(rect), "agreeing_gradient_pairs": int(agree.sum()),
        "selected_reference_consensus_pairs": count, "reference_threshold": threshold,
        "reference_gradient_rms": rms, "reference_gradient_disagreement_rms": spread,
        "relative_reference_disagreement": relative, "scores": scores,
        "persistent_attenuation_screen": screen
    }


def analyze(root):
    meta = json.loads((root / "metadata.json").read_text())
    expected = {
        "source_blend_sha256": SOURCE, "resolution": [512,482],
        "samples": 24, "reference_samples": 1024, "seed": 539,
        "extra_input_seeds": [911,1337], "reference_seed": 8819,
        "second_reference": True
    }
    for k, value in expected.items():
        if meta.get(k) != value:
            raise ValueError(f"E0021 metadata {k} violated: {meta.get(k)!r}")
    if not str(meta.get("blender", "")).startswith("5.0.1"):
        raise ValueError("E0021 expected Blender 5.0.1")
    references = [rgb(read_arrays(root / path)["image"])
                  for path in ("reference.exr", "reference_check.exr")]
    if any(r.shape != (482,512,3) for r in references):
        raise ValueError("Wrong reference size")
    seeds, inputs = {}, {"references": {}}
    for path in ("reference.exr", "reference_check.exr"):
        inputs["references"][path] = digest(root / path)
    for seed in SEEDS:
        folder = root if seed == 539 else root / f"seed_{seed}"
        imgs = {name: rgb(read_arrays(folder / f"acd_compare_{name}.exr")["image"])
                for name in METHODS}
        if any(v.shape != (482,512,3) for v in imgs.values()):
            raise ValueError("Unexpected candidate dimensions")
        if float(np.max(np.abs(imgs["STANDARD"]-imgs["NATIVE_COMP_OIDN"]))) > 1e-5:
            raise ValueError("Standard does not match native OIDN on same seed")
        raw = read_arrays(folder / "raw_multilayer.exr", layer=meta["view_layer"])
        if "image" not in raw or float(np.max(np.abs(imgs["Raw"]-rgb(raw["image"])))) > 1e-5:
            raise ValueError("Same-seed Raw vs EXR multilayer AOV mismatch")
        seeds[seed] = imgs
        inputs[str(seed)] = {name: digest(folder / f"acd_compare_{name}.exr")
                             for name in METHODS}
        inputs[str(seed)]["raw_multilayer.exr"] = digest(folder / "raw_multilayer.exr")
    for seed in (911, 1337):
        if compare_images(seeds[539]["Raw"], seeds[seed]["Raw"])["rmse_linear"] < 1e-6:
            raise ValueError("No actual diversity between input seeds")
    results = {name: inspect_region(references[0], references[1], seeds, rect)
               for name, rect in ROIS.items()}
    return {
        "experiment": "E0052", "source_run": 43289852695,
        "source_sha256": SOURCE, "source_author": "Nicole Morena",
        "license": "CC BY-SA", "blender": meta["blender"],
        "same_seed_raw_and_baseline_verified": True, "new_render": False,
        "new_algorithm": False, "samples": 24,
        "input_seeds": list(SEEDS), "reference_samples": 1024,
        "reference_seeds": [8819, 8922], "reference_convergence_proven": False,
        "roi_selection": "Frozen E0021 reference-only ROIs plus full frame",
        "edge_selection": "same-sign reference gradients, top 20% agreeing strength, common gradient >2x reference gradient disagreement",
        "screens_positive": [name for name, data in results.items() if data["persistent_attenuation_screen"]],
        "regions": results, "input_sha256": inputs,
        "warning": "Two finite references can share bias/noise; a positive screen is an exploratory flag, not an OIDN failure proof or algorithm improvement."
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--directory", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    report = analyze(args.directory)
    args.output.mkdir(parents=True, exist_ok=True)
    write_report(args.output / "E0052_RESULTS.json", report)
    lines = [
        "# E0052 — Cozy Kitchen: consistent architectural edges across finite references",
        "", "Offline E0021 EXRs, original Blender 5.0.1, 24spp ×3 seeds, 1024spp ×2 references.",
        "Nicole Morena, CC BY-SA. Original outputs reused; no new rendering, denoiser or addon change.",
        "", "| ROI | Shared edge pairs | Reference discrepancy | Native OIDN gain across seeds | Screen |",
        "|---|---:|---:|---|---|",
    ]
    for name, data in report["regions"].items():
        gains = [data["scores"][str(seed)]["NATIVE_COMP_OIDN"]["projected_edge_gain"]
                 for seed in SEEDS]
        ratio = data["relative_reference_disagreement"]
        lines.append(f"| {name} | {data['selected_reference_consensus_pairs']} | "
                     f"{ratio:.3f} | {min(gains):.3f}–{max(gains):.3f} | "
                     f"{'candidate' if data['persistent_attenuation_screen'] else 'inconclusive'} |"
                     if ratio is not None else
                     f"| {name} | 0 | n/a | n/a | inconclusive |")
    lines += [
        "", "Pre-registered reference-only mask, fixed E0021 ROIs and whole frame.",
        "Positive screen: >=32 pairs, reference disagreement RMS <0.35 of signal RMS, "
        "and OIDN gain [0,0.85) in all 3 seeds. This is NOT a calibrated confidence interval.",
        "Neither two finite references nor edge contrast establishes perceptual fidelity. "
        "A negative screen also does not prove absence of lost details. More reliable "
        "references and independent scene/author at real output scale are required.",
        "", "[Raw data and SHA256 provenance](E0052_RESULTS.json).",
    ]
    (args.output / "E0052.md").write_text("\n".join(lines)+"\n")
    print("E0052_SUMMARY", json.dumps({
        "screens_positive": report["screens_positive"],
        "regions": {k: {"pairs": r["selected_reference_consensus_pairs"],
                        "reference_disagreement": r["relative_reference_disagreement"],
                        "screen": r["persistent_attenuation_screen"]}
                    for k,r in report["regions"].items()}
    }, sort_keys=True))


if __name__ == "__main__":
    main()
