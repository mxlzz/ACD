"""RGB32 PFM interchange for OIDN CLI. Rows on disk are bottom-up."""
from pathlib import Path
import numpy as np

def write_pfm(path: str | Path, image: np.ndarray) -> None:
    a = np.asarray(image)
    if a.ndim != 3 or a.shape[-1] != 3 or min(a.shape[:2]) < 1:
        raise ValueError("PFM needs nonempty HxWx3 array")
    if not np.issubdtype(a.dtype, np.number) or np.iscomplexobj(a) or not np.isfinite(a).all():
        raise ValueError("PFM needs finite real numbers")
    h,w,_ = a.shape
    with open(path,"wb") as f:
        f.write(f"PF\n{w} {h}\n-1.0\n".encode("ascii"))
        f.write(np.ascontiguousarray(np.flipud(a),dtype="<f4").tobytes())

def read_pfm(path: str | Path) -> np.ndarray:
    with open(path,"rb") as f:
        if f.readline().strip() != b"PF":
            raise ValueError("Not a RGB PFM file")
        w,h = map(int,f.readline().split())
        scale = float(f.readline())
        if w < 1 or h < 1 or not np.isfinite(scale) or scale == 0:
            raise ValueError("Invalid PFM dimensions or scale")
        payload=f.read()
    if len(payload) != w*h*3*4:
        raise ValueError("Invalid PFM payload length")
    dtype="<f4" if scale<0 else ">f4"
    return (np.flipud(np.frombuffer(payload,dtype=dtype).reshape(h,w,3)).astype("f4")*abs(scale)).copy()
