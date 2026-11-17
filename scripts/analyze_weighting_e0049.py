"""E0049: same-Raw native Cycles roughness weighting switch, reuse E0048 guards."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from acd_lab.core import rgb
from acd_lab.io import read_arrays,write_report
from scripts.analyze_reflections_e0048 import load,compare,digest

def run(original,switched,manifest,output):
    source=json.loads(manifest.read_text())
    baseline=source["source_metadata"]
    new=json.loads((switched/"metadata.json").read_text())
    for m in (baseline,new):
        if (m["scene"]!="detail_target" or not m["blender"].startswith("5.2.4")
            or m["resolution"]!=[1920,1440] or m["samples"]!=24 or m["seed"]!=539
            or m["e0046_crop"]["top_left_origin_rect"]!=[928,320,512,512]):
            raise ValueError("E0049 source/camera/spp mismatch")
    if new.get("e0049_roughness_weighting") is not False or new.get("e0048_follow_reflections") is not True:
        raise ValueError("E0049 did not isolate albedo roughness weighting")
    a=load(original,baseline,source["output_sha256"])
    b=load(switched,new)
    refs={}
    for key,name in (("ref1","reference.exr"),("ref2","reference_check.exr")):
        path=original/name
        if digest(path)!=source["output_sha256"][name]:raise ValueError("Reference checksum mismatch")
        refs[key]=rgb(read_arrays(path)["image"])
    stats=compare(a,b,refs)
    if stats["causal_interpretation_allowed"]:
        stats["scores"]={"weight_true" if k=="follow_true" else "weight_false":v
                         for k,v in stats["scores"].items()}
    output.mkdir(parents=True,exist_ok=True)
    from PIL import Image,ImageDraw
    from scripts.analyze_cozy_e0020 import display_rgb
    sheet=Image.new("RGB",(668,748),(25,25,25))
    pen=ImageDraw.Draw(sheet)
    for i,(name,img) in enumerate((("weighted True",a["oidn"]),("weighted False",b["oidn"]),
                                  ("reference 1",refs["ref1"]),("reference 2",refs["ref2"]))):
        x=12+332*(i%2);y=12+366*(i//2)
        sheet.paste(Image.fromarray(display_rgb(img[96:416,96:416])),(x,y+28))
        pen.text((x+5,y+6),name,fill=(245,245,245))
    sheet.save(output/"E0049_comparison.png",optimize=True)
    result={"experiment":"E0049","source_run":43883209135,"algorithm_new":False,
            "setting":"native Cycles roughness weighted albedo: True to False; follow reflections stays True",
            "reference_convergence_proven":False,"metrics":stats,
            "source_hashes":{n:digest(switched/n) for n in ("acd_compare_Raw.exr","acd_compare_NATIVE_COMP_OIDN.exr","raw_multilayer.exr")}}
    write_report(output/"E0049_RESULTS.json",result)
    print("E0049_CONTROL",json.dumps({"RawMax":stats["raw_max_abs"],"valid":stats["causal_interpretation_allowed"],"decision":stats["decision"]}))
def main():
    p=argparse.ArgumentParser()
    for key in ("original","switched","manifest","output"):
        p.add_argument("--"+key,required=True,type=Path)
    z=p.parse_args()
    run(z.original,z.switched,z.manifest,z.output)
if __name__=="__main__":main()
