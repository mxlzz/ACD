# B1 living-room-3 — read-only independent-scene smoke

Candidate converted scene from cuteday/scenes_blender, pinned Git blob; original .blend not copied to ACD.
Blender 5.2.4, Cycles CPU 192x192 4 spp, no denoising.
Source SHA256: 416ef903e6a07b680379b005008ec3e5a87a058743988a70efd5c89aee7cb2b0
Smoke result: FAIL
Original identity and converted scene license: NOT YET VERIFIED, therefore NOT an accepted holdout.
No algorithm / fidelity conclusion.

Failure log tail:
~~~
00:00.448  blend            | Read blend: "/tmp/acd-b1-living3/living-room-3.blend"
/home/runner/work/ACD/ACD/scripts/audit_public_scene.py:51: DeprecationWarning: 'Material.use_nodes' is expected to be removed in Blender 6.0
  for x in collection if x.use_nodes and x.node_tree]
/home/runner/work/ACD/ACD/scripts/audit_public_scene.py:51: DeprecationWarning: 'World.use_nodes' is expected to be removed in Blender 6.0
  for x in collection if x.use_nodes and x.node_tree]
Traceback (most recent call last):
  File "/home/runner/work/ACD/ACD/scripts/audit_public_scene.py", line 67, in <module>
    raise RuntimeError("Missing unbundled texture resources: " + repr(missing[:20]))
RuntimeError: Missing unbundled texture resources: ['_unnamed_14', '_unnamed_7', '_unnamed_9']

Error: script failed, file: 'scripts/audit_public_scene.py', exiting.
Blender 5.2.4 LTS (hash cd5dc428cce1 built 2026-11-10 01:31:47)

Blender quit
~~~
