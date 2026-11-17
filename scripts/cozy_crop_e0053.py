"""E0053: fixed high-pixel-density ROI derived from frozen E0021 detail_2."""
FULL=(1920,1808)
RECT=(1124,644,512,512)  # top-left, 76px margin around mapped 360px detail
INNER=(76,76,360,360)
OLD=(320,192,96,96)
SOURCE_SHA="5f27c41cf828ca15ffd06fc3ad3d971343f6af4a29828c834252229a26dce395"

def contract(width:int,height:int):
    if (width,height)!=FULL:
        raise ValueError("E0053 requires full-frame virtual resolution 1920x1808")
    x,y,w,h=RECT
    if not (0<=x<x+w<=width and 0<=y<y+h<=height):
        raise ValueError("ROI outside full frame")
    u,v,iw,ih=INNER
    if not (u>0 and v>0 and u+iw<w and v+ih<h):
        raise ValueError("ROI margin invalid")
    return {
        "name":"cozy_detail_2", "full_frame_resolution":list(FULL),
        "top_left_origin_rect":list(RECT), "interior_relative_xywh":list(INNER),
        "source_e0021_roi":list(OLD), "expected_crop_resolution":[512,512],
        "pixel_scale_from_e0021":[width/512,height/482],
        "normalized_border":{
            "min_x":x/width, "max_x":(x+w)/width,
            "min_y":1-(y+h)/height,"max_y":1-y/height
        },
        "caveats":[
            "The 512px E0021 source was rounded from a different full aspect ratio; no pixelwise cross-resolution parity.",
            "76px crop margin reduces but cannot prove absence of OIDN receptive-field border effects.",
            "This ROI was already observed in E0021/E0052 and is development, not holdout."
        ]
    }
