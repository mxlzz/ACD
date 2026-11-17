# B1 Italian Flat — functional Blender 5.2.4 LTS check



Source official Cycles demo, Flavio Della Tommasa, CC-BY (version unspecified). Original 367,972,724-byte BLEND not redistributed.

SHA256 0027fcbd73411cce7f49b3d86c22c03d18980e22641083da9d8ba82d9fc94e25

Scene Scene; camera Cam Pouf Details 

Meshes 476, materials 109, images 81

Missing resources 0, linked libraries 0

Cycles CPU, 192×192, 4spp functional smoke passed; NOT a denoising quality result.

Next: pin hash; convergence/cost pilot before large renders.


> **Auditoría retrospectiva (2026-11-13):** la escena Italian Flat intenta leer el perfil fotométrico externo `IES_profiles/three-lobe-vee.ies`, ausente durante los renders de E0041/E0042/E0043 (comprobado en los logs de Cycles). La iluminación renderizada no es una reproducción fiel del archivo original. Estos números describen únicamente la variante efectivamente renderizada; no sirven para justificar fidelidad de iluminación ni superioridad de ningún denoiser. Fixture en cuarentena hasta recuperar y verificar la dependencia exacta.
