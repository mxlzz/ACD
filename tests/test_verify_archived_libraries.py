import pytest
from scripts.verify_archived_libraries import verify_archived_libraries

def test_accept_present_linked_blend_only_under_checksum_verified_root(tmp_path):
    archive=tmp_path/"verified"
    archive.mkdir()
    file=archive/"lamps.blend"
    file.write_bytes(b"valid")
    assert verify_archived_libraries([str(file)],archive)==["lamps.blend"]

def test_reject_unpacked_library_path(tmp_path):
    archive=tmp_path/"verified"
    archive.mkdir()
    file=tmp_path/"external.blend"
    file.write_bytes(b"valid")
    with pytest.raises(ValueError,match="outside verified"):
        verify_archived_libraries([str(file)],archive)

def test_reject_missing_library(tmp_path):
    archive=tmp_path/"verified"
    archive.mkdir()
    with pytest.raises(ValueError,match="Missing linked"):
        verify_archived_libraries([str(archive/"absent.blend")],archive)

def test_symlink_escape_rejected(tmp_path):
    archive=tmp_path/"verified"
    archive.mkdir()
    external=tmp_path/"other.blend"
    external.write_bytes(b"data")
    link=archive/"link.blend"
    link.symlink_to(external)
    with pytest.raises(ValueError,match="outside verified"):
        verify_archived_libraries([str(link)],archive)
