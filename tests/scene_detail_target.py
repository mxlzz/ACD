"""High-frequency architectural material fixture, synthetic and fully procedural.

No reference textures or files; no claim of real-production validity.
"""
from __future__ import annotations

import bpy
from scene_factory import make_interior, material, box


def make_detail_target(scene):
    make_interior(scene)
    grout = material("ACD dark fine grout", (.018, .018, .020), roughness=.82)
    light = material("ACD light grout", (.87, .76, .56), roughness=.75)
    wood = material("ACD oak vertical slats", (.40, .21, .09), roughness=.34)
    metal = material("ACD precision metal groove", (.64, .66, .68), metallic=.95, roughness=.09)
    glass = material("ACD textured wall glass foreground", (.96, .97, 1), roughness=.05, transmission=.91)

    # Two spatial frequencies: high-frequency vertical ribs and tile joints.
    box("Slatted wall board", (-.25, 2.62, 1.57), (2.65, .11, 1.55), grout)
    for index in range(52):
        x = -1.53 + index * (2.56 / 52)
        box(f"Slat #{index:02d}", (x, 2.52, 1.57), (.033, .05, 1.44),
            light if index % 5 == 0 else wood)

    box("Tile panel substrate", (1.88, 2.49, 1.53), (1.02, .10, 1.47), light)
    for index in range(26):
        z = .83 + index * (1.38 / 26)
        box(f"Grout row #{index:02d}", (1.88, 2.408, z), (1.0, .022, .010), grout)
    for index in range(13):
        x = 1.40 + index * (0.96 / 13)
        box(f"Grout col #{index:02d}", (x, 2.405, 1.53), (.010, .022, 1.41), grout)

    box("Specular bar for fine highlight", (-.3, .20, 1.24), (1.65, .12, .08), metal)
    box("Glass overlay in front of slats", (-.40, 1.96, 1.52), (1.63, .027, 1.29), glass)

    bump_mat = material("ACD procedural micro-bump", (.45, .42, .39), roughness=.7)
    nodes = bump_mat.node_tree.nodes
    links = bump_mat.node_tree.links
    shader = nodes.get("Principled BSDF")
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 160
    bump = nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = .24
    bump.inputs["Distance"].default_value = .018
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], shader.inputs["Normal"])
    box("Microbump board", (1.89, 1.42, .65), (.90, .16, .50), bump_mat)
    print("ACD DETAIL TARGET: 52 slats, 26+13 joint lines, metal, glass, microbump")
