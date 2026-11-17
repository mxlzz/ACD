"""E0034: compare saved E0033 EXRs with reference-only, disjoint ROIs."""
from __future__ import annotations
import argparse,json
from pathlib import Path
import numpy as np
from acd_lab.core import rgb, compare_images
from acd_lab.io import read_arrays, write_report
from scripts.analyze_hall_e0033 import SOURCE_SHA256, build_candidates
from scripts.analyze_cozy_e0020 import display_rgb

RUN_ID=43416607737

def select_disjoint_rois(first,second,*,size=128,count=4):
    a,b=rgb(first),rgb(second)
    if a.shape!=b.shape or not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("References must be finite and aligned")
    h,w=a.shape[:2]
    if size<4 or size>min(h,w) or count<1: raise ValueError("Invalid ROI size or count")
    mean=(a+b)*.5
    luma=mean @ np.array([.2126,.7152,.0722])
    cy,cx=np.unravel_index(np.argmax(luma),luma.shape)
    x=max(0,min(w-size,int(cx)-size//2))
    y=max(0,min(h-size,int(cy)-size//2))
    chosen=[("brightest",(x,y,size,size))]
    mapped=np.arcsinh(mean)
    grad=np.zeros((h,w),dtype=np.float64)
    grad[:,1:]+=np.linalg.norm(mapped[:,1:]-mapped[:,:-1],axis=2)
    grad[1:,:]+=np.linalg.norm(mapped[1:]-mapped[:-1],axis=2)
    step=max(1,size//4)
    xs=sorted(set([*range(0,w-size+1,step),w-size]))
    ys=sorted(set([*range(0,h-size+1,step),h-size]))
    options=sorted(((float(np.mean(grad[yy:yy+size,xx:xx+size])),xx,yy)
                    for yy in ys for xx in xs),
                   key=lambda z:(-z[0],z[2],z[1]))
    for _,xx,yy in options:
        if any(not (xx+size<=x0 or x0+rw<=xx or yy+size<=y0 or y0+rh<=yy)
               for _,(x0,y0,rw,rh) in chosen): continue
        chosen.append((f"detail_{len(chosen)}",(xx,yy,size,size)))
        if len(chosen)>=count: break
    return chosen

def save_strip(panels,bounds,dest,zoom=1):
    from PIL import Image,ImageDraw
    x,y,w,h=bounds
    gap,header=10,32
    frame=Image.new("RGB",(len(panels)*(w*zoom+gap)+gap,
                           h*zoom+header+2*gap),(29,29,29))
    draw=ImageDraw.Draw(frame)
    for i,(name,source) in enumerate(panels):
        p=Image.fromarray(display_rgb(source[y:y+h,x:x+w]))
        if zoom>1:p=p.resize((w*zoom,h*zoom),Image.Resampling.NEAREST)
        xx=gap+i*(w*zoom+gap)
        frame.paste(p,(xx,header+gap))
        draw.text((xx+2,9),name,fill=(240,240,240))
    frame.save(dest)

def analyze(root:Path,out:Path):
    meta=json.loads((root/"metadata.json").read_text())
    if (meta.get("source_blend_sha256")!=SOURCE_SHA256
        or meta.get("second_reference") is not True
        or meta.get("capture_aov") is not True):
        raise ValueError("Wrong E0033 source or missing two references/AOV")
    first=read_arrays(root/"reference.exr")["image"]
    second=read_arrays(root/"reference_check.exr")["image"]
    read=lambda name:read_arrays(root/f"acd_compare_{name}.exr")["image"]
    raw,oidn=read("Raw"),read("NATIVE_COMP_OIDN")
    layer=read_arrays(root/"raw_multilayer.exr",layer=meta["view_layer"])
    if "emission" not in layer or not np.allclose(rgb(raw),rgb(layer["image"]),rtol=0,atol=1e-5):
        raise ValueError("Emission missing or same-seed Raw mismatch")
    methods,stats=build_candidates(raw,oidn,read("STANDARD"),read("HIGH"),read("SUPER"),layer["emission"])
    panels=[("Reference 1",first),("Raw 24spp",raw),("OIDN",oidn),
            ("Emission50",methods["Emission50"]),("ACD High",methods["ACD High"]),
            ("ACD Super",methods["ACD Super"]),("Reference 2",second)]
    h,w=rgb(first).shape[:2]
    if any(rgb(a).shape[:2]!=(h,w) for _,a in panels):raise ValueError("Panel shape mismatch")
    out.mkdir(parents=True,exist_ok=True)
    save_strip(panels,(0,0,w,h),out/"hall_full_1to1.png")
    regions=[]
    for name,box in select_disjoint_rois(first,second,size=min(128,h,w),count=4):
        fname=f"hall_{name}_3x.png"
        save_strip(panels,box,out/fname,zoom=3)
        x,y,bw,bh=box
        crop=lambda a:a[y:y+bh,x:x+bw]
        local={key:{"ref1":compare_images(crop(first),crop(a))["rmse_linear"],
                    "ref2":compare_images(crop(second),crop(a))["rmse_linear"]}
               for key,a in methods.items()}
        regions.append({"name":name,"bbox_xywh":list(box),"file":fname,
                        "seed539_local_rmse":local})
    result={"experiment":"E0034","source_run_id":RUN_ID,
            "source_sha256":SOURCE_SHA256,"full":"hall_full_1to1.png",
            "regions":regions,"emission50":stats["Emission50"],
            "roi_rule":"Reference mean strongest luminance and asinh-RGB gradient, all boxes disjoint",
            "display":"same max(0,RGB)/(1+max(0,RGB))^(1/2.2), not Blender OCIO",
            "credit":"Modern Hall by NewSee2l035, CC BY 3.0, via Bitterli/cuteday",
            "limit":"Only seed539 PNG panels; 3-seed numeric summary separate. References not converged."}
    write_report(out/"E0034_VISUAL.json",result)
    print("E0034_VISUAL_READY",json.dumps({"roi": [z["bbox_xywh"] for z in regions],
           "files":[result["full"]]+[z["file"] for z in regions]}))
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--directory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    analyze(a.directory.resolve(),a.output.resolve())
if __name__=="__main__":main()
