# E0052 — Cozy Kitchen: referencia-consenso de gradientes (preinscripción 2026-11-16)

**Pregunta:** ¿existen bordes reproducibles en ambas referencias 1024spp que OIDN atenúe a lo largo de tres semillas 24spp? La salida es una pantalla diagnóstica, nunca una demostración perceptual ni de calidad superior a OIDN.

**Fuente fija:** E0021 run 43289852695, Blender 5.0.1, Cozy Kitchen © Nicole Morena CC BY-SA, SHA256 del .blend 5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395; 512x482, seeds539/911/1337, refs8819/8922. EXR original disponible hasta 2026-11-19. No hacer render nuevo.

**Control previo obligatorio:** metadata/spp/seeds/resolución/fuente, AOV Raw exacto con output Raw por seed (max diferencia 1e-5), salida Standard idéntica a nodo OIDN nativo por seed (max diferencia 1e-5), diferencias reales entre semillas, hashes SHA256 de entradas. Si falla, STOP sin ranking.

**ROI congelada de E0021 (x,y,w,h):** detalle 1 (192,288,96,96), 2 (320,192,96,96), 3 (288,96,96,96) y fotograma completo (0,0,512,482). No seleccionar sobre imágenes denoised. Gradientes horizontales/verticales de asinh(luminancia lineal); máscara a partir de ambas referencias: mismo signo, fuerza mínima en el percentil superior 20% de gradientes concordantes, y mayor a 2× la discrepancia de gradiente de las refs. Calcular amplitud proyectada OIDN y Raw sobre gradientes medios de referencia, error de gradiente y RMSE lineal contra cada ref, con tres seeds.

**Pantalla exploratoria positiva:** al menos 32 pares de borde consistentes, discrepancia RMS entre refs inferior a 0.35 veces RMS del gradiente medio y gain OIDN >=0 y <0.85 en TODAS las tres semillas. No hay p-valores; ni siquiera una pantalla positiva autoriza modificar el addon. Se requiere referencia convergida, mayor densidad de píxeles y holdout independiente antes de formular corrección. La pantalla negativa no prueba ausencia de pérdida.

**Coste:** solo Python + OpenEXR de los 139MB de artifacts previos; no nuevo cómputo Cycles/GPU. Workflow se activa al añadirse el archivo y queda posteriormente manual. Archivar JSON/hashes y decisión permanentemente; EXR continúa temporal. PR #10 draft, main intacto.
