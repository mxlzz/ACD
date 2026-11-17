# E0053 — high-density Cozy Kitchen pilot (pre-registered 2026-11-16)

**Purpose:** Test whether the E0052 detail_2 ROI can be sampled with actual Blender 5.2.4 Cycles at delivery-scale pixel density without an entire 1920px render. **Not** a denoiser quality evaluation.

Source © Nicole Morena CC BY-SA (Blender 3.5 Cozy Kitchen), stored in benchmarks/scenes/cozy_kitchen.blend, SHA256 5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395; scene Main, camera CAM-wide, original render resolution 2655×2500. Same source and camera; no edits to geometry, material or lights.

**Crop geometry:** full virtual render 1920×1808 (rounded aspect from E0021 512×482), border top-left (1124,644,512,512), actual generated image 512×512, center evaluation region (76,76,360,360) corresponds approximately to E0021 ROI detail_2 (320,192,96,96). Margin 76px reduces but does not prove absence of denoiser border effects. The aspect rounding and pixel/sample context make E0021 vs E0053 pixelwise comparison invalid.

**Tiny sample budget:** single noisy input 8 spp seed 539, two 32 spp raw references seeds 8819 and 8922, Cycles adaptive OFF/CPU; same RLayers Raw+original AOV through native compositor OIDN Accurate/High/HDR. No High/Super/F5 algorithm and no reference ranking. Record actual Blender wall seconds (including loading/writes) and process success; avoid automatic extrapolation of fullHD cost.

**Pass/fail:** source SHA, scene/camera, exact 512² EXR, Blender version 5.2.4, crop contract, same-seed raw vs multilayer max difference <=1e-5, both references different, valid AOV and elapsed wall >0. Any failure stops; no quality inference. Original .blend unchanged.

**Decision:** if functional and computationally feasible, pre-register a distinct higher-reference study with uncertainty and at least two independent scenes before algorithm development. If not, archive failure and switch to another public scene. Artifacts expire in 7 days, JSON/hashes/report permanent. Workflow pushed once then manual for heavy work. PR #10 remains draft; addon product unchanged.
