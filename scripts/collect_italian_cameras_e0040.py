"""Create a compact contact sheet from E0040 actual camera PNGs."""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    source=args.input
    report=json.loads((source/"e0040_camera_audit.json").read_text())
    rows=report["cameras"]
    cols=4
    w,h=320,200
    pad,header=10,28
    nrows=(len(rows)+cols-1)//cols
    canvas=Image.new("RGB",(cols*(w+pad)+pad,nrows*(h+header+pad)+pad),(24,24,24))
    draw=ImageDraw.Draw(canvas)
    for i,entry in enumerate(rows):
        row,col=divmod(i,cols)
        x=pad+col*(w+pad)
        y=pad+row*(h+header+pad)
        image=Image.open(source/entry["png"]).convert("RGB")
        if image.size!=(w,h):raise ValueError("Wrong camera render dimensions")
        canvas.paste(image,(x,y+header))
        draw.text((x+2,y+5),entry["camera_name"][:42],fill=(250,250,250))
    args.output.mkdir(parents=True,exist_ok=True)
    canvas.save(args.output/"italian_camera_contact_sheet.png")
    for entry in rows:
        (args.output/entry["png"]).write_bytes((source/entry["png"]).read_bytes())
    (args.output/"e0040_camera_audit.json").write_text(json.dumps(report,indent=2)+"\n")
    print("E0040_CAMERA_GALLERY",len(rows),str(args.output/"italian_camera_contact_sheet.png"))

if __name__=="__main__":main()
