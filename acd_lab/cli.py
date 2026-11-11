"""ACD laboratory entry point."""
from __future__ import annotations

import argparse
import json

from .core import compare_images, check_recomposition
from .io import read_arrays, write_report


def pick(arrays: dict, key: str, source: str):
    if key not in arrays:
        raise ValueError(f"{source}: missing array {key!r}, available: {sorted(arrays)}")
    return arrays[key]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="acd-lab")
    sub = parser.add_subparsers(dest="command", required=True)
    compare = sub.add_parser("compare", help="Compare a candidate with an independent reference")
    compare.add_argument("--reference", required=True)
    compare.add_argument("--candidate", required=True)
    compare.add_argument("--ref-key", default="image")
    compare.add_argument("--candidate-key", default="image")
    compare.add_argument("--data-range", type=float, help="Required if PSNR is desired")
    compare.add_argument("--output")
    check = sub.add_parser("check-passes", help="Compare raw AOV sum to raw beauty")
    check.add_argument("--input", required=True)
    check.add_argument("--beauty-key", default="image")
    check.add_argument("--output")
    args = parser.parse_args(argv)
    if args.command == "compare":
        ref = pick(read_arrays(args.reference), args.ref_key, args.reference)
        candidate = pick(read_arrays(args.candidate), args.candidate_key, args.candidate)
        result = compare_images(ref, candidate, data_range=args.data_range)
    else:
        arrays = read_arrays(args.input)
        beauty = pick(arrays, args.beauty_key, args.input)
        result = check_recomposition(
            beauty, {key: val for key, val in arrays.items() if key != args.beauty_key}
        )
    if args.output:
        write_report(args.output, result)
    print(json.dumps(result, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
