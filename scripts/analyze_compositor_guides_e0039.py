"""E0039 compare actual Blender compositor RLayers socket values with raw EXR passes."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from acd_lab.io import read_arrays, write_report
from acd_lab.core import compare_images, rgb


def analyze(root):
    meta=json.loads((root/"metadata.json").read_text())
    if (meta["scene"]!="detail_target" or not meta["blender"].startswith("5.2.4")
        or meta["samples"]!=16 or meta["resolution"]!=[128,96]
        or not meta["capture_aov"] or not meta["native_compositor_oidn"]):
        raise ValueError("E0039 must use pinned real Blender 5.2.4 tiny source")
    aov=read_arrays(root/"raw_multilayer.exr",layer=meta["view_layer"])
    mapping={
        "NoisyImage": ("SOCKET_NoisyImage","image"),
        "Albedo": ("SOCKET_Albedo","denoising_albedo"),
        "Normal": ("SOCKET_Normal","denoising_normal"),
    }
    report={}
    for label,(name,canonical) in mapping.items():
        if canonical not in aov:
            raise ValueError("Missing AOV "+canonical)
        from_file=rgb(aov[canonical])
        from_socket=rgb(read_arrays(root/f"acd_compare_{name}.exr")["image"])
        if from_file.shape!=from_socket.shape or not np.isfinite(from_file).all() or not np.isfinite(from_socket).all():
            raise ValueError("Socket/AOV invalid shape/nonfinite")
        delta=np.abs(from_file-from_socket)
        report[label]={
            "aov_vs_socket":compare_images(from_file,from_socket),
            "max_abs":float(np.max(delta)),
            "p99_abs":float(np.quantile(delta,0.99)),
            "nonzero_channel_fraction":float(np.count_nonzero(delta)/delta.size),
            "aov_sample_00":from_file[0,0].tolist(),
            "socket_sample_00":from_socket[0,0].tolist(),
        }
    raw=rgb(read_arrays(root/"acd_compare_Raw.exr")["image"])
    native=rgb(read_arrays(root/"acd_compare_NATIVE_COMP_OIDN.exr")["image"])
    report["Raw_vs_socket_NoisyImage"]=compare_images(
        raw,read_arrays(root/"acd_compare_SOCKET_NoisyImage.exr")["image"])
    return {
        "experiment":"E0039",
        "blender":meta["blender"],"input_spp":meta["samples"],
        "resolution":meta["resolution"],"input_seed":meta["seed"],
        "source":"one Blender Cycles render, own file output sockets and original multilayer EXR",
        "passes":report,
        "native_renders":True,
        "quality_reference":False,
        "warning":"AOV-to-socket consistency only; different scene seed/build from archived E0035, not an algorithm winner."
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    result=analyze(args.directory)
    write_report(args.output,result)
    print("E0039_GUIDE_CONTRACT",json.dumps({
        k:{"rmse":v["aov_vs_socket"]["rmse_linear"],"max_abs":v["max_abs"]}
        for k,v in result["passes"].items() if k in ("NoisyImage","Albedo","Normal")},sort_keys=True))


if __name__=="__main__":main()
