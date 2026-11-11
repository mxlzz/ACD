# Running ACD on existing Blender scenes (M2)

The purpose is to move from 48–96px synthetic smoke scenes to **real,
complex scene data** while preserving comparison validity. The input .blend
is loaded into memory and is **never saved or overwritten**.

## Scene sources

Official Blender demo files: https://www.blender.org/download/demo-files/

Suggested initial independent test scenes:
- **Classroom** (Christophe Seux; CC0 per Blender demo listing). Useful
  for lighting and architectural geometry. Original asset ~72 MB.
- **Barcelona Pavilion** (eMirage; CC-BY per Blender demo listing). Relevant
  for modernist architecture, glass and stone surfaces; attribution required.
- **Agent 327 Barbershop** (CC-BY per Blender demo listing; ~280 MB).
  Useful for complex GI and high-frequency objects after initial tests.

Download files and extract them **locally**, not into ACD Git. Keep any
associated textures and external libraries with the scene. Record attribution
and source URL in your experiment notes. Large third-party scenes are not
checked into this code repository.

## Local execution

Install Python 3.11+ with:

    python -m pip install -e ".[dev,exr]"

Then from the ACD project root, using an existing Blender 5 executable:

    python scripts/run_scene_benchmark.py \
      --blender "/path/to/blender" \
      --blend "/path/to/classroom.blend" \
      --output "./experiments/classroom_run_001" \
      --width 1920 --height 1080 \
      --samples 64 --reference-samples 2048 \
      --seed 539 --extra-seeds 911,1337,2026 \
      --device OPTIX --second-reference \
      --regions examples/regions.json

On Windows use quoted full executable and .blend paths.
Try --dry-run to verify the invocation without starting Blender.
A Blender 5 GPU/OPTIX configuration may require a working NVIDIA driver
and should be checked on your machine. CPU mode is supported too.

**Important:** Full-HD 2048 spp reference images can be expensive even on
an RTX 4050 with limited VRAM. Test first with modest samples and resolution.
For formal final comparisons, raise reference quality *and* check convergence.

To skip re-rendering a known independent reference EXR, add:

    --reference-file "/path/to/my_reference.exr"

The reference must represent the same camera, frame, geometry, lights,
resolution, and color convention. A generic previous render is not a valid
reference if anything material has changed.

## Outputs

- acd_compare_Raw.exr
- acd_compare_STANDARD.exr / HIGH.exr / SUPER.exr
- acd_compare_RawRecomposed.exr — raw, unfiltered pass sum
- raw_multilayer.exr — raw Cycles AOVs (unless --no-aov)
- reference.exr — high-spp image (or explicitly provided reference)
- optional reference_check.exr, seed_NNN/ outputs
- metrics.json, seed_aggregate.json, region_metrics.json, error_maps.npz
- metadata.json — Blender version, seeds, settings, source .blend SHA-256

The scripts never apply display/view transforms before computing metrics.

## Failure and interpretation

- Missing external textures cause an explicit error; pack resources in
  Blender or fix their paths before rendering.
- AOV contribution masks are *radiance attribution* diagnostics, not
  object/material segmentation. Manual ROIs help inspect details.
- Complex scene compositing, volumes, transparency, motion blur and
  external AOVs can make a simple pass sum incomplete. Reject claims of
  superior quality until a raw pass-recomposition check succeeds.
- All processing is experimental; the code is not yet a faithful clone
  of the commercial SID 5.3.
- An independently rendered reference at finite spp is not automatically
  ground truth. Comparing two reference seeds quantifies disagreement,
  not actual bias or convergence.
- A representative evaluation requires several scenes, input seeds,
  sample budgets, reference seeds and visually examined crops.
