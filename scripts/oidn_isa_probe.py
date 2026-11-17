"""Fixed-input OIDN CPU ISA diagnostic, independent of Blender and render noise."""
from __future__ import annotations
import argparse, hashlib, json, platform, re, subprocess, time
from pathlib import Path
import numpy as np
from acd_lab.pfm import read_pfm, write_pfm
from acd_lab.io import write_report


def hashfile(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""): h.update(block)
    return h.hexdigest()


def make_inputs(out: Path):
    h,w=144,192
    y,x=np.mgrid[0:h,0:w].astype(np.float64)
    nx=x/(w-1);ny=y/(h-1)
    stripe=(np.sin(2*np.pi*42*nx)>0).astype(float)
    noise=np.sin(x*14.39+y*2.73)*np.cos(y*3.17-x*0.99)
    highlight=11.0*np.exp(-((nx-.72)**2+(ny-.38)**2)/.001)
    c=np.stack((.25+.30*stripe+.03*noise+highlight,
                .19+.35*(ny>.5)+.027*noise+.7*highlight,
                .12+.17*nx+.034*noise+.5*highlight),-1).astype("f4")
    a=np.stack((np.full((h,w),.5),np.full((h,w),.4),np.full((h,w),.35)),-1).astype("f4")
    n=np.zeros((h,w,3),dtype="f4");n[...,2]=1
    write_pfm(out/"color.pfm",c)
    write_pfm(out/"albedo.pfm",a)
    write_pfm(out/"normal.pfm",n)
    return out/"color.pfm",out/"albedo.pfm",out/"normal.pfm"


def run(binfile, color, albedo, normal, output):
    args=[str(binfile),"-d","cpu","--hdr",str(color),"--alb",str(albedo),
          "--nrm",str(normal),"-q","high","-v","2","-o",str(output)]
    t=time.perf_counter()
    p=subprocess.run(args,check=True,text=True,stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT)
    arr=read_pfm(output)
    return {"isa": re.findall(r"ISA\s*:\s*([^\n]+)",p.stdout),
            "device_name": re.findall(r"Device\s*:\s*([^\n]+)",p.stdout),
            "wall_seconds":time.perf_counter()-t,
            "output_sha256":hashfile(output),
            "log":p.stdout[-9000:]},arr


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--oidn233",type=Path,required=True)
    parser.add_argument("--oidn251",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    path=args.output_dir.resolve()
    path.mkdir(parents=True,exist_ok=True)
    color,alb,nrm=make_inputs(path)
    versions={}
    images={}
    for label,binary in (("2.3.3",args.oidn233),("2.5.1",args.oidn251)):
        outfile=path/("oidn"+label.replace(".","")+".pfm")
        report,img=run(binary.resolve(),color,alb,nrm,outfile)
        report["binary_sha256"]=hashfile(binary)
        versions[label]=report
        images[label]=img.astype("f8")
    diff=images["2.3.3"]-images["2.5.1"]
    cpu=subprocess.run(["lscpu"],check=True,text=True,stdout=subprocess.PIPE).stdout
    data={"input_sha256":{p.name:hashfile(p) for p in (color,alb,nrm)},
          "software_os":platform.platform(),
          "lscpu":cpu,
          "versions":versions,
          "output_diff_rmse":float(np.sqrt(np.mean(diff*diff))),
          "output_diff_max_abs":float(np.max(np.abs(diff))),
          "interpretation":"Fixed PFM repeated across runners: if hash matches but output differs, assess ISA, AMX-FP16 and CPU precision before assigning quality to OIDN version."}
    write_report(path/"isa_probe.json",data)
    print("OIDN_ISA_PROBE",json.dumps({
        "input_sha":data["input_sha256"],"cpu":[line for line in cpu.splitlines()
        if line.startswith(("Model name:","Architecture:","Vendor ID:"))],
        "versions":{k:{"isa":v["isa"],"device":v["device_name"],"time":v["wall_seconds"],
                       "sha":v["output_sha256"]} for k,v in versions.items()},
        "diff_rmse":data["output_diff_rmse"],"diff_max":data["output_diff_max_abs"]},indent=2))

if __name__=="__main__":main()
