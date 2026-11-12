# Public reproducible Cycles reference scenes

## Cozy Kitchen — Blender 3.5 official splash artwork

- **Author:** Nicole Morena. Published in Blender's official 3.5 splash-art/demo collection.
- **Origin:** <https://www.blender.org/download/demo-files/>; original <https://download.blender.org/demo/splash/blender-3.5-splash.blend>.
- **Work license:** **CC BY-SA** as explicitly labeled by Blender. The site's summary does not specify the CC license *version*. Maintain proper artist attribution and the ShareAlike conditions for modifications; this asset is not licensed under ACD's software license.
- **Tracked source:** `cozy_kitchen.blend`, 7,685,702 bytes (7.33 MiB), original bytes **unmodified**.
- **SHA-256:** `5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395`.
- **Provenance:** `cozy_kitchen.audit.json` records source, license, author, blob SHA256, Blender5.0.1 smoke, camera and missing dependencies.
- **Functional verification:** [GitHub Actions #43285518302](https://github.com/mxlzz/ACD/actions/runs/43285518302) opened the scene under Blender 5.0.1 with auto-execution disabled and successfully rendered Cycles at 192×192, 4 spp. No unbundled image files or external .blend libraries were missing. Also see [E0019](../../docs/experiments/E0019.md).
- **Manual recheck:** `.github/workflows/acd-import-public-scene.yml` is now **read-only and workflow_dispatch only**, for SHA integrity and Cycles smoke; it no longer has permission to push binaries to the repository.
- **Benchmark:** use `scripts/run_scene_benchmark.py` (see exact invocation in [E0019](../../docs/experiments/E0019.md)) with same raw EXR and AOVs across compared denoisers and independent high-spp reference renders. A 4-spp smoke is **not** a quality benchmark.
- Attribution does not imply sponsorship or endorsement by Nicole Morena or Blender.

`Prueba ACD.blend` from the user is intentionally **not** part of this public repository. Its third-party assets and paths have not been cleared for public redistribution.
