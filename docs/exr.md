# M1: Multi-layer OpenEXR ingestion

## CLI

~~~sh
python -m pip install -e ".[dev,exr]"
python -m acd_lab.cli inspect-exr --input /path/to/raw.exr
python -m acd_lab.cli check-passes --input /path/to/raw.exr --layer ViewLayer --output pass_report.json
python -m acd_lab.cli compare --reference converged.exr --candidate denoised.exr --ref-layer ViewLayer --candidate-layer ViewLayer --output comparison.json
~~~

The EXR reader uses OpenEXR v3.3+ and reads separate channel arrays. It supports common Cycles naming conventions such as ViewLayer.Combined.R, ViewLayer.DiffDir.R, ViewLayer.GlossInd.G, ViewLayer.TransCol.B, ViewLayer.Emit.R, etc. It does not guess about unmatched channel names: use inspect-exr to inspect the raw channels. A file with two view layers needs an explicit --layer.

All arrays are kept in scene-linear RGB. The alpha channel is exported as a separate 1-channel 'alpha' array. The laboratory's reconstruction and comparison functions intentionally evaluate RGB only. The exported beauty must be an **unfiltered** reference; do not turn on built-in Cycles denoising when generating AOV datasets.

The initial parser is strict about incomplete RGB triplets. Multi-part EXR files are supported when their channel and part labels identify the same view layer consistently. Deep/subsampled channels, custom AOV semantics, color-space conversions, EXR streaming, and Blender vector encoding are NOT yet supported.

## Reconstruction notes

The pass reconstruction is only approximate until compared with raw beauty in the same EXR. Missing or unknown renderer contributions cause residual error. Do not add denoised 'Combined' to its own filtered component sum.

Always compare two denoisers on exactly the same noisy input render and reference at the same resolution, seed, and color management. A reference output that has also been denoised is not an unbiased measure of reconstruction quality.
