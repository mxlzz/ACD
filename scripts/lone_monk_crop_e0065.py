"""E0065: source-locked physical architectural portal/cornice ROI.

Fixed from E0064 original-camera preview (no OIDN or references viewed).
Image source 960x720; delivery virtual 1920x1440, same 4:3 FOV.
"""
SOURCE_SHA="eea2bbfb3f9271050f523c8351fca40f2f559ce84b42b0143e949ecdb4594c3b"
SOURCE_PREVIEW_SHA="22ab1cf8ebfd76078d5bd3f1e84ebe8ac9e812c1797eb1e0216a342cfb1a16b7"
SCENE="daylight"
CAMERA="cam.001"
SOURCE_RES=(1440,1080)
FULL=(1920,1440)
RECT=(700,430,512,512)
INNER=(64,64,384,384)
REGIONS={
    "portal_architecture":INNER,
    "portal_cornice_pediment":(64,64,384,160),
    "portal_columns_and_arch":(64,224,384,224),
    "full_crop_including_context":(0,0,512,512),
}

def contract(width:int,height:int)->dict:
    if (width,height)!=FULL:
        raise ValueError("E0065 requires full camera FOV 1920x1440")
    x,y,w,h=RECT
    if not (x>=0 and y>=0 and x+w<=width and y+h<=height):
        raise ValueError("E0065 crop outside virtual camera")
    a,b,c,d=INNER
    if not (a>=64 and b>=64 and a+c<=w-64 and b+d<=h-64):
        raise ValueError("E0065 ROI lacks 64px context margin")
    for name,(rx,ry,rw,rh) in REGIONS.items():
        if rx<0 or ry<0 or rw<16 or rh<16 or rx+rw>w or ry+rh>h:
            raise ValueError("E0065 invalid architectural region "+name)
    return {
        "name":"lone_monk_original_portal",
        "source_sha256":SOURCE_SHA,
        "original_camera":CAMERA,
        "source_preview_e0064_sha256":SOURCE_PREVIEW_SHA,
        "original_source_resolution":list(SOURCE_RES),
        "full_virtual_resolution":list(FULL),
        "crop_top_left_xywh":list(RECT),
        "expected_crop_resolution":[w,h],
        "fixed_regions_xywh":{k:list(v) for k,v in REGIONS.items()},
        "context_margin_pixels":64,
        "normalized_border":{
            "min_x":x/width,
            "max_x":(x+w)/width,
            "min_y":1-(y+h)/height,
            "max_y":1-y/height,
        },
        "semantic_definition":"central stone portal of the cloister, cornice/pediment, columns and arch, visible in original unfiltered E0064 camera preview",
        "development_only_not_holdout":True
    }
