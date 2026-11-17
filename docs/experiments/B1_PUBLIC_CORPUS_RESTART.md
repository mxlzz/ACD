# B1 — Reanudación con corpus público (16-11-2026)

**Decisión:** no exigir `Prueba ACD.blend` ni ningún archivo propiedad del usuario. El fallo de acceso a la biblioteca afecta solo a esa entrada privada. El problema de investigación es la *representatividad y la confiabilidad de las referencias*, no la titularidad del .blend.

## Inventario con validación ya archivada en ACD

| Escena | Licencia / fuente | Estado observado | Uso permitido en ACD |
|---|---|---|---|
| Cozy Kitchen (Nicole Morena) | CC-BY-SA, [catálogo Blender](https://www.blender.org/download/demo-files/); [archivo oficial](https://download.blender.org/demo/splash/blender-3.5-splash.blend) | `benchmarks/scenes/cozy_kitchen.blend`, SHA256 `5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395`, 7.685.702 B. Auditoría: 1.077 objetos, 175 materiales, ningún recurso faltante ni biblioteca enlazada, smoke Cycles 192² 4spp aprobado | **Primer desarrollo y control de pipeline** sin descarga nueva; escena ya examinada E0020/E0021, NO holdout |
| Classroom (Christophe Seux) | CC0, [catálogo Blender](https://www.blender.org/download/demo-files/), [archivo público](https://download.blender.org/demo/test/classroom.zip) | Descarga pública establecida, pero E0007 documentó resultados casi idénticos entre semillas; invalida por ahora su uso como referencia estadística independiente | Diagnóstico de semillas, no ranking ni holdout hasta aislar el problema |
| Modern Hall (NewSee2l035; conversión cuteday) | Atribución y licencia original CC BY 3 según auditoría E0033; condiciones de redistribución de conversión no resueltas | [E0032/E0033](E0033.md): smoke aprobado, resultados OIDN vs ACD, refs 1024spp no convergentes | Comparador ya observado, sin reclamar validación externa ni redistribuir el .blend |
| Terraced Houses (Yunus Emre Karaman) | MIT, [fuente con licencia](https://github.com/emrelab/blender-projects) | `benchmarks/scenes/terraced_houses.blend`, SHA256 `37b39be2ae1fc8624110f57bf5dd38f77a0420139b4c9a89946a2db35dffab84`; smoke aprobado, 19 materiales | Control reproducible independiente, pero low-poly no representa por sí solo la complejidad archviz |

Datos de auditoría: `benchmarks/scenes/*.audit.json`, `docs/experiments/E0007.md`, `docs/experiments/E0020.md`, `docs/experiments/E0021.md` y `docs/experiments/E0033.md`. El cumplimiento de la licencia no prueba que las referencias de render hayan convergido.

## Nuevas fuentes candidatas, aún NO aceptadas

- **[Blender House of Chores](https://www.blender.org/download/demo-files/)**, Blender Studio, CC-BY, aprox. 238 MB según catálogo; candidato complejo con otro autor. Pendiente comprobar descarga, dependencias, motor de render y aptitud arquitectónica antes de incluirlo como nueva escena.
- **[Benedikt Bitterli Rendering Resources](https://benedikt-bitterli.me/resources/)**: 32 escenas gratuitas, muchas interiores arquitectónicas con iluminación indirecta y materiales PBR. Las licencias son *por escena*. La conversión a Blender de [cuteday/scenes_blender](https://github.com/cuteday/scenes_blender) incluye `living-room.blend` (23.015.976 B según árbol de GitHub), pero **no está aceptada**: verificar que coincide con una escena original, licencia del autor, restricciones de la conversión, recursos embebidos y funcionamiento Cycles. No interpretar "gratis" como dominio público.

## Orden de trabajo y puertas

1. **Ahora, sin intervención del usuario:** usar Cozy Kitchen ya descargada para reproducir un caso de error de OIDN *sin tocar el addon*. Control estricto de cámara/versión, hashes, AOV, semillas efectivamente distintas y observación 1:1 en zonas de vidrio, texturas y reflejos. Las referencias antiguas no constituyen ground truth por defecto.
2. **En paralelo, buscar un nuevo autor/escena licenciada y completa**, para reservar una validación externa. Rechazar si faltan texturas/IES, si la licencia no permite el uso pretendido o si la conversión cambia materiales de modo no auditable.
3. **Antes de un render pesado:** smoke 192px/4spp, presupuesto temporal y memoria; después escalera y replicación de semillas. Solo ejecutar benchmarks intensivos con una pregunta causal preinscrita y presupuesto aprobado por su valor informativo; mantenerlos `workflow_dispatch`.
4. **Para una posible mejora ACD:** mismo Raw exacto entre candidatas, dos referencias independientes con control de incertidumbre, medidas HDR y bordes, control de pérdida de detalle y costo vs más spp. Preinscribir regiones sobre referencias, separar escenas ya vistas de escenas retenidas. Si falla cualquier puerta, archivar resultado negativo y NO inventar un algoritmo.

**Estado del documento:** selección de fuentes y corrección del bloqueo, NO nuevo benchmark ejecutado ni evaluación de calidad. PR #10 sigue draft; addon estable sin cambios.
