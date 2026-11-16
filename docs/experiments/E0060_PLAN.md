# E0060 — CAM Office 256x144 reference/cost pilot, internal only (pre-registered 2026-11-16)

E0059 crossed the two noisy 512spp Cozy references to avoid selecting/evaluating the same edge mask, and native OIDN had far lower held-out edge-gradient RMSE than Raw: central 0.088 versus 0.392. No regression sufficient to justify sharpening or new method. E0058 on independent author's Surat CAM Office exhibited large seed variation (relative RMSE0.2448), but is not yet converged or permitted as a public holdout.

**Goal:** Evaluate whether source-pinned full architectural interior camera can support a *feasible* future controlled OIDN study, BEFORE spending on output-scale converged reference renders. This is only a cost/reference-noise pilot, not a method ranking or visual quality claim.

**Inputs:** Surat Diamond Bourse v1.0.1 ZIP public SHA256 721e77b401fba0fa5c3b9df13b09279c6d05781af865f2b63945e7e032e991a8 and size166627773, Blender5.2.4 LTS official, scene Scene / original camera CAM Office. No geometry, camera location or material edit, no save. Renderer Cycles CPU adaptive OFF internal denoise OFF, 256x144 8spp seed539 noisy, two 64spp independent-seed references8819/8922. Native compositor OIDN High/Accurate/HDR on exactly same Raw; original albedo and normal AOV. Prior camera sampling difference E0058 provides only sample-variation evidence, not proof of statistical independence.

**Acceptance:** SHA/bytes validated before load; explicit camera present, metadata SHA of extracted blend equals render source, exact 256x144 float EXRs, Raw equals multilayer AOV max <=1e-5, AOV albedo/normal present, reference images measurably different, total wall time positive. If any gate fails stop. Output only numeric reference disagreement, time, hashes and trace; no RMSE ranking, no JPG/PNG/EXR/BLEND uploaded.

**Rights:** Contributor's own 3D reconstruction declared CC0 but underlying real architectural design rights unresolved; treat as *internal technical only*, do NOT publish model or render previews or claim public holdout validity. No code borrowed from GPL scripts, no fork/weights.

**Next:** If the tiny pilot is stable and low cost, evaluate whether stronger 512+ spp reference at output pixel density would actually change the decision, but only after rationale and source-rights gate. Stop if progress is merely repeated scene demos. Main addon untouched, PR #10 draft.
