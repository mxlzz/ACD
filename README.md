# ACD — Adaptive Compositional Denoiser

Experimental image reconstruction and denoising research for Blender/Cycles.

**Status: research prototype. No quality improvement over OIDN or SID has yet been demonstrated.**

## Repository
- addon/acd_blender.py: Blender 5.x compositor addon (experimental).
- acd_lab/: independent numerical evaluation utilities.
- tests/: deterministic tests and an optional Blender headless smoke test.
- docs/: algorithm specifications, sources and experiment protocol.
- STATUS.md: persistent milestone and verification state.

## Laboratory setup

Python 3.11+:

~~~sh
python -m pip install -e ".[dev]"
python -m pytest -q
python -m acd_lab.cli compare --reference reference.npz --candidate candidate.npz
python -m acd_lab.cli check-passes --input render_passes.npz
~~~

The initial laboratory accepts .npy/.npz files with linear-light RGB or RGBA arrays. Multilayer EXR ingestion is a **next milestone**, not implemented yet.

## Blender
Install addon/acd_blender.py with Edit > Preferences > Add-ons > Install from Disk. Select Cycles, then open Render Properties > ACD. Do not use the experimental addon for production until tested on Blender 5.x.

## Third-party research
ACD studies the publicly documented compositional methods in Pidgeon Tools Super Image Denoiser: https://github.com/PidgeonTools/SuperImageDenoiser . That project's source is GPL-3.0. The code in this repository is independently written and does not include its source files. No license has yet been granted to redistribute ACD's own code; review license obligations before importing external code.

## Scientific standard
Compare exactly the same noisy input (resolution, sample count, seed, color management) against independent converged references. Visual smoothness by itself is not evidence of higher quality.
