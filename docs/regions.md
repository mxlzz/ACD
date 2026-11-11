# ACD per-region diagnostics

## Why this is necessary
A denoiser can reduce mean RGB error while blurring architectural joints,
reflections, glass, and small light sources. Report both whole-image metrics
and spatially resolved diagnostic metrics.

**Two different definitions of region must not be confused:**
- **Spatial region of interest (ROI):** a user-authored rectangle, e.g. the
  metal trim next to a glazed partition.
- **AOV contribution-dominated region:** pixels where a given class of
  *radiance* accounts for a specified fraction of the available absolute
  contribution magnitude. This is not object segmentation or a "glass mask".
  Glossy paths can contribute in areas with non-glossy primary materials.

The AOV method computes scene-linear family radiance as
\`(direct + indirect) * color\`, then estimates the absolute luminance
energy from each contribution. The user specifies a fraction threshold and
minimum total signal. Masks overlap; empty masks yield null metrics.

ROIs are normalized 0–1 rectangles [x0,y0,x1,y1] with a top-left origin.
Maps are stored in .npz with both signed and absolute per-channel residuals.
This pipeline never tone maps or clips the base RGB data.

## Limits
- AOVs do not identify the primary material of a pixel. To measure physical
  surface classification, use explicit Blender Cryptomatte / object IDs or
  custom masks, not these masks.
- Colored contributions can be signed; we use absolute RGB magnitude only
  to define a diagnostic energy ratio, not a physical energy-conservation law.
- AOV masks derived from a noisy input can themselves fluctuate between seeds;
  for high-quality analysis derive the mask from the independent high-spp
  reference AOVs, or hold the same mask fixed across comparisons.
- Small ROI counts and thin edges can generate unstable rankings.
- HDR error maps must be inspected at a *declared* display transform and
  exposure. Don't call a log-luminance diagnostic HDR-FLIP.


## Blender multi-layer EXR

Blender may write both Composite and ViewLayer layers in a single EXR.
For illumination AOV masks, use the **render layer**, not Composite. The
region CLI defaults to the view_layer name recorded in metadata.json.
For an imported EXR without metadata, select it explicitly:

    python -m acd_lab.cli compare-regions --directory ./run \
      --passes ./run/raw_multilayer.exr --passes-layer ViewLayer \
      --regions examples/regions.json --output ./run/region_metrics.json

To list available channel names before selecting a layer:

    python -m acd_lab.cli inspect-exr --input ./run/raw_multilayer.exr
