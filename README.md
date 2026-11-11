# ACD — Adaptive Compositional Denoiser

An **experimental** multi-pass denoising research system for Blender/Cycles, with an independent numerical evaluation lab. It is not a verified commercial SID 5.3 replica or a proven universal improvement over native OIDN.

## Research and persistent plan

- [Research foundations and source-to-hypothesis matrix](docs/research_foundations.md): original papers/source code, assumptions, licensing and ACD H-01 to H-06.
- [Development roadmap](docs/ROADMAP.md): milestones M0–M8, dependencies, relative effort and testable exit gates.
- [Experiment record](docs/experiments/): actual results, uncertainties and negative findings.
- [Current state](STATUS.md): what has actually been implemented and verified.

These documents separate scientific evidence, project hypotheses, the intended development plan, and observed execution results. Roadmap entries are **not** completed work.

## Project layout

- addon/acd_blender.py — experimental Blender 5.x Standard/High/Super compositor.
- acd_lab/ — OpenEXR ingest, raw-pass reconstruction, image-quality and regional diagnostics.
- scripts/run_scene_benchmark.py — controlled local comparisons using an existing .blend.
- docs/experiments/ — historical and current runs E0001–E0008, including negative findings.
- docs/regions.md — ROI versus AOV contribution-mask interpretation.
- docs/real_scenes.md — practical setup and scene provenance.
- STATUS.md — persistent project status, gates and current validation evidence.

## Evaluate a real Blender scene locally

Python 3.11+:

    python -m pip install -e ".[dev,exr]"
    python -m pytest -q

Run from the ACD repository root, adjusting paths:

    python scripts/run_scene_benchmark.py \
      --blender "/path/to/blender" \
      --blend "/path/to/classroom.blend" \
      --output "./experiments/classroom_001" \
      --samples 64 --reference-samples 2048 \
      --device CPU

For NVIDIA GPUs, pass --device OPTIX (requires compatible drivers).
The source .blend is loaded in memory and **not overwritten**. The runner
writes scene-linear EXRs, per-method reports, raw AOVs and optional ROI
error maps. A large reference at 1080p can be slow: see docs/real_scenes.md.

To define meaningful spatial ROIs, adapt examples/regions.json and pass
--regions examples/regions.json. Regional AOV masks describe how strongly
a type of radiance contributes, **not** which object material appears.

## Data and third-party code

No third-party SID code has been copied into this repository. The historical
public Super Image Denoiser implementation is GPL-3.0:
https://github.com/PidgeonTools/SuperImageDenoiser

The pipeline is inspired by public compositional denoising concepts, with
independently written source. No ACD redistribution license has been selected.
Public Blender demo scenes have their own licenses and are not bundled here.

## Evidence standard

All denoisers must process the *same noisy Cycles render*. Measure against
independently seeded high-spp references, checking convergence; compare more
than one scene, input seed, sample count and error metric, and inspect
material-specific crops before making quality claims.

The present research is preliminary. See STATUS.md before deciding which
pipeline is superior.
