"""Verify linked Blender libraries live only inside a checksum-verified archive.

Pure Python helper, independent of bpy, used by audit_public_scene.py.
"""
from pathlib import Path


def verify_archived_libraries(paths, root):
    archive=Path(root).resolve(strict=True)
    if not archive.is_dir():
        raise ValueError("Verified library root must be a directory")
    accepted=[]
    for item in paths:
        path=Path(item).resolve()
        if not path.is_file():
            raise ValueError("Missing linked .blend library: "+str(item))
        if not path.is_relative_to(archive):
            raise ValueError("Linked library outside verified source archive: "+str(item))
        accepted.append(str(path.relative_to(archive)))
    return accepted
