"""Frozen linear EXR AOV fixture, for numerical SID High/Super parity only."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from scripts.sid_standard_numeric_fixture import make_arrays

def make_aovs():
    data = make_arrays()
    yy, xx = np.mgrid[0:64, 0:96]
    x, y = xx.astype(np.float32) / 95, yy.astype(np.float32) / 63
    highlight = ((x > .66) & (x < .9) & (y > .18) & (y < .53)).astype(np.float32)
    glass = (x > .65).astype(np.float32)
    alpha = data["noisy"][..., 3]
    rng = np.random.default_rng(20261111)
    def four(rgb, noise=0):
        if noise:
            rgb = np.clip(rgb + rng.normal(0, noise, rgb.shape), 0, None)
        return np.ascontiguousarray(np.concatenate(
            [np.asarray(rgb, dtype=np.float32), np.ones_like(alpha)[..., None]], -1
        ), dtype=np.float32)
    a = {
        "diffuse_direct": four(np.stack([.2+.2*x, .1+.2*y, .12+.08*x], -1), .035),
        "diffuse_indirect": four(np.stack([.1+.05*y, .1+.07*x, .09+.03*y], -1), .035),
        "diffuse_color": four(np.stack([.55+.25*x, .4+.4*y, .35+.2*x], -1)),
        "glossy_direct": four(np.stack([.05+1.2*highlight, .04+1.8*highlight, .05+2.5*highlight], -1), .035),
        "glossy_indirect": four(np.stack([.03+.15*x, .02+.12*y, .01+.1*x], -1), .035),
        "glossy_color": four(np.stack([.7+.1*x, .75+.1*y, .7+.15*x], -1)),
        "transmission_direct": four(np.stack([.01+.35*glass, .02+.45*glass, .02+.5*glass], -1), .035),
        "transmission_indirect": four(np.stack([.02+.1*glass, .02+.15*glass, .01+.1*glass], -1), .035),
        "transmission_color": four(np.stack([.3+.6*glass, .4+.5*glass, .45+.4*glass], -1)),
        "emission": four(np.stack([6*highlight, 3*highlight, 1.5*highlight], -1)),
        "environment": four(np.stack([.05+.03*x, .06+.02*y, .07+.04*x], -1)),
        # Historical SID Alpha input is a grayscale Color converted from scalar.
        "alpha": four(np.repeat(alpha[..., None], 3, -1)),
    }
    a.update(data)
    return a

def save(directory):
    import OpenEXR
    directory.mkdir(parents=True, exist_ok=True)
    result = {"source":"synthetic fixed-seed HDR/AOV, not converged ground truth","files":{}}
    for name, value in make_aovs().items():
        path = directory / (name + ".exr")
        with OpenEXR.File({}, {c:np.ascontiguousarray(value[..., i], dtype=np.float32)
                               for i,c in enumerate("RGBA")}) as f:
            f.write(str(path))
        result["files"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (directory/"input_manifest.json").write_text(json.dumps(result, indent=2)+"\n")
    return result

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps({"inputs":len(save(args.output)["files"])}))
