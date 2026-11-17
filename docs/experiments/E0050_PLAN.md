# E0050 — Reconstruct OIDN compositor offline and swap guide AOV on identical Raw

**Motivation (2026-11-16):** E0048 confirmed same Raw and native follow-reflections improves detail under glass; E0049 attempting native roughness-albedo weighting changed beauty Raw by max 0.077223, invalidating any native same-noise comparison. This experiment reuses both already rendered multilayer EXRs, **no Cycles scene rendering**.

**Prior art:** Blender Compositor Image node can read OpenEXR multilayer; Denoise node already accepts image/albedo/normal and has Accurate/High/HDR. This is a controlled replay of existing functionality, **not a new denoising technique** (https://docs.blender.org/manual/en/5.2/compositing/types/filter/denoise.html).

**Two-stage verification:**
1. Recover exact E0046 (run43883209135) and E0049 (run43894800865) EXRs by SHA from permanent E0046_RESULTS/E0049_RESULTS. Original E0046 Raw 512×512 24spp, same pixel density as 1920px FOV. Load E0046 Raw and both multilayer EXRs as image nodes; use file-source sockets for Albedo and Normal. Build compositor nodes High/Accurate/HDR for both AOV sets. Output *identical* Raw passthrough, replayed baseline OIDN, and swapped-guides OIDN from **one compositor execution**.
2. Verify raw passthrough max pixel delta <=1e-5; verify baseline replay against E0046 native OIDN with max <=1e-4. If either fails, the backend is **not equivalent**; record the failure and **do not claim guide improvement**, though report output deltas. If both pass, compare baseline/swapped OIDN against both original E0046 512spp refs, using frozen E0047 glass/direct ROIs and full interior. Retain reference disagreement caveat.

**Stop:** if no meaningful reduction of error across both finite references without loss elsewhere, close investigation into pre-existing Cycles guide flags. Even if favorable, this is a *configuration* of existing Cycles, not an original algorithm or proof of superiority over native default. No more brute-force toggle searches; next advancement requires a concrete residual weakness beyond features documented by OIDN/Cycles. Stable addon untouched, no GPU training.
