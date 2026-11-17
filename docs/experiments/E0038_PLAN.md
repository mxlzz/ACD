# E0038 — Aislar versiones standalone OIDN

## 2026-11-13 — E0038 control versión OIDN 2.5.0 vs 2.5.1

- Fuente Blender v5.2.4/v5.3.0 build_files/build_environment/cmake/versions.cmake establece OIDN_VERSION 2.5.0. E0037 usó standalone 2.5.1 y no igualó al compositor, incluso con guías prefiltradas. El release OIDN 2.5.0 x86_64 linux tiene digest SHA256 254a8355856f8cd433edb7dd832b5fb02e7157d073f7d22e331ce06533fb491f según GitHub release asset.
- E0038 compara ambos binarios oficiales sobre PFM idénticos y misma configuración; verifica hashes de E0035/E0037, y separa distancia versión vs distancia Blender. **No mide calidad**. El workflow se inicia con este commit.

Source 5.2: https://github.com/blender/blender/blob/v5.2.4/build_files/build_environment/cmake/versions.cmake ; OIDN 2.5.0 release https://github.com/RenderKit/oidn/releases/tag/v2.5.0 . Datos base E0035_RESULTS.json y E0037_RESULTS.json; no referencia convergida. Puede requerirse identificar guía compositor/sockets si la versión no explica la divergencia.
