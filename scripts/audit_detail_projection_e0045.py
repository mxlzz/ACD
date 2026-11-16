"""E0045 — camera-projected sampling audit for the known ACD detail fixture.

Calculates *ideal pinhole projection* of specified world-space geometry in
tests/scene_factory.py and tests/scene_detail_target.py. It is NOT an
evaluation of image quality, nor a substitute for Blender's pixel filtering.
Change these fixture coordinates only alongside the original source.
"""
from __future__ import annotations
import json
import math
import statistics
from pathlib import Path

CAMERA=(3.0,-5.8,2.15)
TARGET=(0.0,0.0,1.2)
LENS_MM=32.0
SENSOR_WIDTH_MM=36.0
BASE_WIDTH,BASE_HEIGHT=320,240

def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def normalized(a):
    length=math.sqrt(dot(a,a))
    return tuple(x/length for x in a)

FORWARD=normalized(sub(TARGET,CAMERA))
RIGHT=normalized(cross(FORWARD,(0.0,0.0,1.0)))
UP=cross(RIGHT,FORWARD)

def project(point,width=BASE_WIDTH,height=BASE_HEIGHT):
    """Pixel center-coordinate projection, upper-left image origin."""
    offset=sub(point,CAMERA)
    depth=dot(offset,FORWARD)
    if depth<=0:
        raise ValueError("Geometry behind camera")
    px=(width/2)+(width*LENS_MM/SENSOR_WIDTH_MM)*dot(offset,RIGHT)/depth
    py=(height/2)-(width*LENS_MM/SENSOR_WIDTH_MM)*dot(offset,UP)/depth
    return (px,py)

def stats(values):
    return {"min":min(values), "median":statistics.median(values), "max":max(values)}

def audit():
    slats=[-1.53+i*2.56/52 for i in range(52)]
    grout=[1.40+i*.96/13 for i in range(13)]
    slat_center=[project((x,2.52,1.57))[0] for x in slats]
    slat_pitch=[b-a for a,b in zip(slat_center,slat_center[1:])]
    slat_width=[project((x+.033/2,2.52,1.57))[0]-project((x-.033/2,2.52,1.57))[0] for x in slats]
    grout_center=[project((x,2.405,1.53))[0] for x in grout]
    grout_pitch=[b-a for a,b in zip(grout_center,grout_center[1:])]
    grout_width=[project((x+.010/2,2.405,1.53))[0]-project((x-.010/2,2.405,1.53))[0] for x in grout]
    measures={"slat_pitch_px_320":stats(slat_pitch),
              "slat_width_px_320":stats(slat_width),
              "grout_pitch_px_320":stats(grout_pitch),
              "grout_width_px_320":stats(grout_width)}
    def min_width_for(minimum_px,observed):
        return math.ceil(BASE_WIDTH * minimum_px / observed)
    requirements={
        "slat_pitch_at_least_2px":min_width_for(2,measures["slat_pitch_px_320"]["min"]),
        "slat_pitch_at_least_4px":min_width_for(4,measures["slat_pitch_px_320"]["min"]),
        "grout_line_at_least_1px":min_width_for(1,measures["grout_width_px_320"]["min"]),
        "grout_line_at_least_2px":min_width_for(2,measures["grout_width_px_320"]["min"]),
    }
    return {"experiment":"E0045",
            "source_fixture":"tests/scene_detail_target.py + tests/scene_factory.py",
            "source_blender_result":"E0044 5.2.4 output, same camera and geometry",
            "method":"pinhole lens 32mm, sensor width 36mm, camera looks at (0,0,1.2) from (3,-5.8,2.15); zero shift, 4:3 aspect; project world-space slat/grout centerline and physical width",
            "sample_resolution":[BASE_WIDTH,BASE_HEIGHT],
            "camera_position":CAMERA,"look_at":TARGET,
            "num_slats":len(slats),"num_vertical_grout_lines":len(grout),
            "measures":measures,"minimum_full_frame_widths":requirements,
            "at_1920px":{"min_slat_pitch_px":measures["slat_pitch_px_320"]["min"]*6,
                         "min_grout_width_px":measures["grout_width_px_320"]["min"]*6},
            "interpretation":"Slat pitch <2px at 320-wide, below ideal periodic Nyquist sampling. Grout line subpixel. This does not mean features are always invisible: pixel anti-aliasing can encode fractional coverage. However 320px cannot support strong fidelity claims about recoverable geometric detail or justify a novel denoiser.",
            "limitations":"No Blender rasterizer, pixel filter, depth-of-field, anti-aliasing or visibility/occlusion modeled; geometry idealizations match fixture definitions. Resolution target alone does not prove denoiser quality.",
            "next_gate":"Test a small crop at >=1920-wide full-frame pixel density with complete geometry and original field of view; verify crop registration and actual detail before expensive references; use separate held-out scene before integrating algorithm."
    }

if __name__=="__main__":
    print(json.dumps(audit(),indent=2))
