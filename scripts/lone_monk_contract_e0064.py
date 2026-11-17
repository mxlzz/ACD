"""E0064 contract for framing original Lone Monk camera, with no ROI cherry-picking.

This one low-spp Cycles preview is FOR SOURCE FRAMING ONLY, not a quality
benchmark or denoiser ranking. The full source camera aspect is retained.
"""
from __future__ import annotations
import hashlib
from pathlib import Path

SOURCE_SHA="eea2bbfb3f9271050f523c8351fca40f2f559ce84b42b0143e949ecdb4594c3b"
SOURCE_BYTES=33452252
SOURCE_URL="https://mirror.blender.org/demo/cycles/lone-monk_cycles_and_exposure-node_demo.blend"
SCENE="daylight"
CAMERA="cam.001"
WIDTH=960
SAMPLES=8
SEED=539


def sha256(path:Path)->str:
    d=hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda:stream.read(1048576),b""):
            d.update(chunk)
    return d.hexdigest()


def frame_size(original_width:int,original_height:int)->tuple[int,int]:
    if not 16<=original_width<=10000 or not 16<=original_height<=10000:
        raise ValueError("Source render resolution is invalid")
    height=max(8,round(WIDTH*original_height/original_width))
    if not 320<=height<=1400:
        raise ValueError("Original source camera aspect unsuitable for preview")
    return WIDTH,height


def inspect_source(path:Path)->None:
    if path.stat().st_size!=SOURCE_BYTES or sha256(path)!=SOURCE_SHA:
        raise ValueError("Expected exact original Lone Monk official source checksum")
