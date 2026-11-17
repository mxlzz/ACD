# E0049 — último control de guía nativa: ponderación de albedo por rugosidad

**Preinscripción:** 16-11-2026, antes de ejecutar. **No es un método nuevo.** Blender 5.2.4 ya proporciona `ViewLayer.cycles.denoising_pass_use_albedo_roughness_weighting=True` por defecto, alternativa de clasificación por BSDF; ver https://github.com/blender/blender/blob/v5.2.4/intern/cycles/blender/addon/properties.py y commit upstream 79f6f5c793991e277d8a29b6867bbfe7abf30a0f .

**Antecedente probado:** E0048 (run43893867618) demostró que, con Raw idéntico, dejar de seguir reflexiones empeora la zona tras vidrio (RMSE0.07040 →0.07580, contraste 0.501→0.449). Por eso E0049 **mantiene follow_reflections=True**, no combina switches.

**Único cambio:** desactivar `denoising_pass_use_albedo_roughness_weighting` en el fixture procedural E0046, Blender 5.2.4, FOV virtual 1920×1440/crop512², 24spp seed539. Misma imagen Raw, compositor OIDN Accurate/High/HDR. Reutilizar E0046 Raw/AOV/OIDN, referencias512spp y ROI E0047. Nuevas referencias **no**; un solo render nuevo.

**Puerta 1:** comparar Raw max canal <=1e-5. Si no coincide, análisis causal inválido. **Puerta 2:** cambios de albedo/normal >1e-5. Si no hay diferencia, opción irrelevante en esta escena y detener. **Puerta 3:** solo con ambas se miden RMSE HDR, gradientes y contraste sobre glass_overlap/uncovered_slats/interior contra las dos refs originales E0046, sin variar nada más.

**Decisión ya fijada:** si el switch empeora o su efecto no es significativo frente a incertidumbre de referencias, detener exploración de controles nativos de guías. No ajustar otros parámetros, no hacer un tercer cambio. Si mejora local, documentar como **configuración ya existente de Cycles**, sin reclamar innovación de ACD: requerir prueba holdout y referencias convergentes antes de considerarlo útil. No cambiar addon estable.
