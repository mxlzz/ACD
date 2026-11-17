# B1 — Living Room 3: auditoría de fuente pública independiente (2026-11-16)

Objetivo: evaluar solo la integridad técnica de una segunda escena de interior con otro autor, para futuros tests de ACD. No hay nuevo denoiser, ranking ni entrenamiento.

Candidato convertido: cuteday/scenes_blender, commit 4271a729fdc7b8db23ad1c2f8a8f530c74f6a63c, archivo living-room-3.blend, Git blob 466772ffbebf19a5f7fad52a4313420a1207edb7, 96.421.460 bytes. Fuente de origen probable: The Modern Living Room de Wig42 (CC BY 3.0, https://blendswap.com/blend/13491); catálogo paralelo LuisaRenderScenes atribuye living-room-3 a Wig42. El README de cuteday describe conversiones Mitsuba/Blender, pero NO especifica licencias de cada conversión ni prueba identidad exacta con la fuente original. Estos dos puntos quedan SIN VERIFICAR.

Prueba congelada: descargar a /tmp el blob de commit exacto, verificar tamaño y git hash-object SHA1, registrar SHA256. Abrir con Blender 5.2.4 LTS --disable-autoexec; reutilizar scripts/audit_public_scene.py para rechazar cámara ausente, imágenes o bibliotecas externas faltantes, IES ausentes y materiales vacíos. Si pasa, generar un solo smoke Cycles CPU de 192x192 a 4 spp, sin denoising. Guardar metadatos y resultado de error, sin subir la escena, sin modificarla y sin claims de calidad.

Fallo o éxito se archivan como resultado científico de aceptación. Si el smoke pasa, la escena sigue SIN SER HOLDOUT hasta resolver su licencia/identidad y revisar que sea relevante para arquitectura, materiales y reflejos. Si falla, descartar esta conversión y usar otra escena, sin inventar recursos. E0054 Cozy permanece development-only; el addon estable y PR #10 draft no cambian.

Motivo del siguiente paso: E0054 confirmó que gran parte de la atenuación seleccionada ya existe en Raw, y que la referencia dual de 512 spp difiere RMSE 0.077947 frente a RMSE nativo 0.092270. No justificar un algoritmo nuevo sobre esa evidencia.
