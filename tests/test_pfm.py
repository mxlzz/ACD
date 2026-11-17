import numpy as np
import pytest
from acd_lab.pfm import read_pfm, write_pfm

def test_roundtrip_hdr_signed_and_orientation(tmp_path):
    x=np.array([[[10,-1,2],[3,4,5]], [[6,7,8],[9,10,100]]], dtype="f4")
    path=tmp_path/"x.pfm"
    write_pfm(path,x)
    np.testing.assert_array_equal(read_pfm(path),x)

def test_invalid_pfm_rejected(tmp_path):
    f=tmp_path/"bad.pfm"
    f.write_bytes(b"xx")
    with pytest.raises(ValueError,match="PFM"):
        read_pfm(f)
    with pytest.raises(ValueError,match="nonempty"):
        write_pfm(f,np.zeros((0,2,3),dtype="f4"))
    invalid=np.ones((2,2,3),dtype="f4")
    invalid[0,0,0]=np.inf
    with pytest.raises(ValueError,match="finite"):
        write_pfm(f,invalid)

def test_big_endian_pfm(tmp_path):
    x=np.arange(18,dtype="f4").reshape((2,3,3))
    f=tmp_path/"big.pfm"
    f.write_bytes(b"PF\n3 2\n1.0\n"+np.flipud(x).astype(">f4").tobytes())
    np.testing.assert_array_equal(read_pfm(f),x)
