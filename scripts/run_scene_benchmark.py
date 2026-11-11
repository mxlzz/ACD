"""Run reproducible ACD comparison on an existing Blender .blend file.

Usage:
  python scripts/run_scene_benchmark.py --blender /path/to/blender \
    --blend ./interior.blend --output ./acd_run --samples 64 \
    --reference-samples 2048 --device CPU

The original .blend is never saved. Rendering modifies the in-memory copy.
Outputs use the image's *raw scene-linear* EXR data; comparison is quantitative,
not a perceptual guarantee. For large scenes, pre-render a reference separately.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
BLENDER_SCRIPT = ROOT / "tests" / "blender_compare_smoke.py"


def parser() -> argparse.ArgumentParser:
    argp = argparse.ArgumentParser(description="ACD controlled existing-.blend denoiser benchmark")
    argp.add_argument("--blender", required=True, type=Path, help="Blender 5 executable")
    argp.add_argument("--blend", required=True, type=Path, help="Existing .blend file; NEVER overwritten")
    argp.add_argument("--output", required=True, type=Path, help="New or existing empty output directory")
    argp.add_argument("--scene-name", default=None, help="Scene name inside Blender project")
    argp.add_argument("--frame", type=int, help="Frame number (optional; default scene frame)")
    argp.add_argument("--width", type=int, help="Output width; default uses scene setting")
    argp.add_argument("--height", type=int, help="Output height; default uses scene setting")
    argp.add_argument("--samples", type=int, default=64, help="Samples per pixel, noisy render")
    argp.add_argument("--reference-samples", type=int, default=2048, help="Samples for high-spp reference")
    argp.add_argument("--seed", type=int, default=539, help="Noisy Cycles seed")
    argp.add_argument("--extra-seeds", default="", help="Additional noisy seeds, comma-separated")
    argp.add_argument("--reference-seed", type=int, default=8819, help="Independent reference Cycles seed")
    argp.add_argument("--reference-file", type=Path, help="Existing independent scene-linear reference EXR; skips expensive reference render")
    argp.add_argument("--second-reference", action="store_true", help="Render a second independent high-spp reference")
    argp.add_argument("--device", choices=("CPU", "OPTIX", "CUDA"), default="CPU")
    argp.add_argument("--methods", default="STANDARD,HIGH,SUPER", help="Comma-separated ACD methods")
    argp.add_argument("--regions", type=Path, help="JSON of normalized manual ROI rectangles")
    argp.add_argument("--no-aov", action="store_true", help="Don't export multilayer EXR of initial noisy render")
    argp.add_argument("--dry-run", action="store_true", help="Print Blender command without running")
    return argp


def validate(args) -> tuple[Path, Path, Path]:
    blender = args.blender.expanduser().resolve()
    blend = args.blend.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if not blender.is_file():
        raise ValueError(f"Blender executable not found: {blender}")
    if blend.suffix.lower() != ".blend" or not blend.is_file():
        raise ValueError(f"Source .blend not found: {blend}")
    if output == blend.parent:
        raise ValueError("Choose a separate benchmark subdirectory, not the scene folder")
    if args.reference_file:
        reference = args.reference_file.expanduser().resolve()
        if not reference.is_file() or reference.suffix.lower() != ".exr":
            raise ValueError("--reference-file must be an existing .exr")
        if args.second_reference:
            raise ValueError("--second-reference is incompatible with an externally supplied reference")
    if args.regions and not args.regions.expanduser().is_file():
        raise ValueError("ROI file does not exist")
    if any(v is not None and not 8 <= v <= 16384 for v in (args.width, args.height)):
        raise ValueError("Explicit resolution must be between 8 and 16384")
    if args.samples < 1 or args.reference_samples < 1:
        raise ValueError("Sample counts must be positive")
    if args.samples >= args.reference_samples and not args.reference_file:
        raise ValueError("Reference must use more samples than noisy render")
    extra = [int(v.strip()) for v in args.extra_seeds.split(",") if v.strip()]
    if len(extra) != len(set(extra)) or args.seed in extra:
        raise ValueError("Noisy input seeds must be unique")
    if args.reference_seed in [args.seed, *extra]:
        raise ValueError("Reference seed must not equal a noisy seed")
    methods = {s.strip() for s in args.methods.split(",") if s.strip()}
    if not {"STANDARD", "HIGH", "SUPER"} <= methods:
        raise ValueError("Batch report currently requires STANDARD,HIGH,SUPER")
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Output directory is not empty: {output}; choose a fresh one")
    return blender, blend, output


def make_command(args) -> tuple[list[str], dict[str, str]]:
    blender, blend, output = validate(args)
    command = [str(blender), "-b", str(blend)]
    if args.scene_name:
        command.extend(["-S", args.scene_name])
    command.extend(["-noaudio", "--python-exit-code", "1", "--python", str(BLENDER_SCRIPT)])
    env = os.environ.copy()
    env.update({
        "ACD_SCENE": "external",
        "ACD_BENCH_DIR": str(output),
        "ACD_INPUT_SPP": str(args.samples),
        "ACD_INPUT_SEED": str(args.seed),
        "ACD_EXTRA_SEEDS": args.extra_seeds,
        "ACD_REFERENCE_SPP": str(args.reference_samples),
        "ACD_REFERENCE_SEED": str(args.reference_seed),
        "ACD_DOUBLE_REFERENCE": "1" if args.second_reference else "0",
        "ACD_REFERENCE_FILE": str(args.reference_file.expanduser().resolve()) if args.reference_file else "",
        "ACD_DEVICE": args.device,
        "ACD_METHODS": args.methods,
        "ACD_CAPTURE_AOV": "0" if args.no_aov else "1",
    })
    if args.width:
        env["ACD_WIDTH"] = str(args.width)
    else:
        env.pop("ACD_WIDTH", None)
    if args.height:
        env["ACD_HEIGHT"] = str(args.height)
    else:
        env.pop("ACD_HEIGHT", None)
    if args.frame is not None:
        env["ACD_FRAME"] = str(args.frame)
    else:
        env.pop("ACD_FRAME", None)
    return command, env


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    command, env = make_command(args)
    print("Blender:", " ".join(f'"{part}"' if " " in part else part for part in command))
    print("Samples:", args.samples, "Reference:", args.reference_samples if not args.reference_file else str(args.reference_file))
    print("Device:", args.device, "Methods:", args.methods)
    if args.dry_run:
        return 0
    output = args.output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    subprocess.run(command, env=env, check=True)

    # Import here so --dry-run works without the optional OpenEXR dependency.
    from acd_lab.batch import evaluate_batch
    from acd_lab.io import write_report
    from acd_lab.region_cli import compare_regions_from_files
    from acd_lab.aggregate import aggregate_seed_reports
    report = evaluate_batch(output)
    write_report(output / "metrics.json", report)
    for folder in sorted(output.glob("seed_*")):
        if folder.is_dir():
            write_report(folder / "metrics.json", evaluate_batch(folder))
    if any(output.glob("seed_*/metrics.json")):
        write_report(output / "seed_aggregate.json", aggregate_seed_reports(output))

    if args.regions or not args.no_aov:
        passes_file = output / "raw_multilayer.exr" if not args.no_aov else None
        regions_result = compare_regions_from_files(
            output, passes_file=passes_file if passes_file and passes_file.is_file() else None,
            regions_file=args.regions, error_maps=output / "error_maps.npz"
        )
        write_report(output / "region_metrics.json", regions_result)
    print("Results:", output)
    print("Ranking (linear RMSE):", ", ".join(report["rank_by_rmse"]))
    if (output / "seed_aggregate.json").is_file():
        aggregate = json.loads((output / "seed_aggregate.json").read_text())
        print("Mean ranking over input seeds:", ", ".join(aggregate["rank_by_mean_rmse"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
