"""ACD laboratory: EXR inspection, raw-pass diagnostics, controlled comparisons."""
from __future__ import annotations

import argparse
import json

from .core import compare_images, check_recomposition
from .io import read_arrays, write_report


def pick(arrays: dict, key: str, source: str):
    if key not in arrays:
        raise ValueError(f"{source}: missing {key!r}; available: {sorted(arrays)}")
    return arrays[key]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acd-lab")
    sub = parser.add_subparsers(dest="command", required=True)

    compare = sub.add_parser("compare", help="Compare candidate against independent reference")
    compare.add_argument("--reference", required=True)
    compare.add_argument("--candidate", required=True)
    compare.add_argument("--ref-key", default="image")
    compare.add_argument("--candidate-key", default="image")
    compare.add_argument("--ref-layer", help="View layer in reference .exr")
    compare.add_argument("--candidate-layer", help="View layer in candidate .exr")
    compare.add_argument("--data-range", type=float, help="Explicit PSNR range")
    compare.add_argument("--output")

    check = sub.add_parser("check-passes", help="Compare unfiltered AOV sum with raw beauty")
    check.add_argument("--input", required=True)
    check.add_argument("--layer", help="View layer in input .exr")
    check.add_argument("--beauty-key", default="image")
    check.add_argument("--output")

    inspect = sub.add_parser("inspect-exr", help="List all raw EXR part and channel names")
    inspect.add_argument("--input", required=True)
    inspect.add_argument("--output")

    batch = sub.add_parser("compare-batch", help="Compare same-input results against a separate reference EXR")
    batch.add_argument("--directory", required=True)
    batch.add_argument("--output")
    aggregate = sub.add_parser("aggregate-seeds", help="Summarize multiple noisy seeds with common reference")
    aggregate.add_argument("--directory", required=True)
    aggregate.add_argument("--output")
    region_cmd = sub.add_parser("compare-regions", help="Measure ACD methods within ROI and AOV contribution masks")
    region_cmd.add_argument("--directory", required=True)
    region_cmd.add_argument("--passes", help="Raw Cycles multilayer EXR with auxiliary light contributions")
    region_cmd.add_argument("--regions", help="Optional JSON with named normalized rectangles")
    region_cmd.add_argument("--energy-fraction", type=float, default=.35)
    region_cmd.add_argument("--min-signal", type=float, default=.01)
    region_cmd.add_argument("--error-maps", help="Write signed and absolute HDR differences as .npz")
    region_cmd.add_argument("--output")
    args = parser.parse_args(argv)
    if args.command == "compare":
        ref_arrays = read_arrays(args.reference, layer=args.ref_layer)
        cand_arrays = read_arrays(args.candidate, layer=args.candidate_layer)
        reference = pick(ref_arrays, args.ref_key, args.reference)
        candidate = pick(cand_arrays, args.candidate_key, args.candidate)
        result = compare_images(reference, candidate, data_range=args.data_range)
    elif args.command == "check-passes":
        arrays = read_arrays(args.input, layer=args.layer)
        beauty = pick(arrays, args.beauty_key, args.input)
        result = check_recomposition(
            beauty, {
                name: value for name, value in arrays.items()
                if name != args.beauty_key and name != "alpha"
            }
        )
    elif args.command == "inspect-exr":
        from .exr import describe_exr
        result = describe_exr(args.input)
    elif args.command == "compare-batch":
        from .batch import evaluate_batch
        result = evaluate_batch(args.directory)
    elif args.command == "aggregate-seeds":
        from .aggregate import aggregate_seed_reports
        result = aggregate_seed_reports(args.directory)
    else:
        from .region_cli import compare_regions_from_files
        result = compare_regions_from_files(
            args.directory, passes_file=args.passes, regions_file=args.regions,
            energy_fraction=args.energy_fraction, min_signal=args.min_signal,
            error_maps=args.error_maps,
        )

    if args.output:
        write_report(args.output, result)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
