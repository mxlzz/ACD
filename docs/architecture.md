# ACD technical architecture — draft

Core is a Blender adapter that creates a separate compositor node group with Standard, High and Super pipelines. It must preserve the previous compositor and avoid copying third-party code.

The independent Lab accepts explicit, linear-light arrays and measures differences to raw beauty and converged references. Its outputs are data and JSON reports, not subjective quality claims.

For each Cycles lighting family F in diffuse, glossy, transmission:

    raw_F = (direct_F + indirect_F) * color_F

Approximate full reconstruction:

    reconstructed = sum(raw_F) + emission + environment + volume_direct + volume_indirect

The pipeline must **measure** disagreement with raw beauty, not assume the sum is exact. Transparency, missing passes, emission, alpha and renderer configuration need investigation.

- Standard: one OIDN on the raw beauty with Denoising Albedo and Normal.
- High (public SID 4.x-style): denoise each family's recombined radiance.
- Super (public SID 4.x-style): denoise each family's direct and indirect separately; add and multiply by material color.
- High/Super: second denoising step on the composed image, optionally disabled for ablation.
- Preserve HDR RGB values; Alpha requires a distinct explicit policy.
- Both High and Super have optional emission, environment and volume terms.

The historical public SID source is **not proof of equivalence with SID 5.3**. Differences between OIDN versions, Blender passes and compositor behavior may change results.

Next extension points: OpenEXR pass adapter, image-quality metrics including perceptual HDR evaluation, statistical variance maps, and later superresolution / photographic noise models.
