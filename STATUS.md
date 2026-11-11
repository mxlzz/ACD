# Persistent project state

Date: 2026-11-11
Branch: dev/acd-core-lab-foundation
Milestone M0: begin Core + Lab in parallel.

Verified:
- Repository mxlzz/ACD is available and public.
- SID historical source is GPL-3.0, and uses family-level High and component-level Super denoising.
- Core and laboratory architecture has been specified.

Pending verification:
- Blender 5 compositor node creation and pass sockets, in an actual Blender 5 binary.
- Lab tests from GitHub Actions and actual HDR scenes.
- Numerical equivalence with original SID or any quality improvement.
- EXR multilayer import, full Alpha handling and photographic/upscale modules.

Next gates:
1. Commit initial Blender adapter and numerical lab with tests.
2. Run CI on the development branch and repair failures.
3. Run headless Blender 5 smoke test with a tiny Cycles scene.
4. Capture low-sample and independent reference EXR render sets.
5. Measure native OIDN, experimental High/Super and ablations.
6. Study uncertainty-driven blending, then upscale and photographic restoration.
