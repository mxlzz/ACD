"""Reproducible glass/metal test scene, deliberately unlike the small desk room.

No external assets, no textures, no learned image synthesis.
Purpose: stress transmission, crisp and rough specular components, small
highlight sources, thin geometry, and mixed direct/indirect illumination.
This remains a *procedural benchmark*, not a production architectural scene.
"""
from __future__ import annotations

from mathutils import Vector
import bpy

from scene_factory import box, material, point_camera


def add_area(scene, name, location, target, power, width, height, tint=(1, 1, 1)):
    source = bpy.data.lights.new(name, type="AREA")
    source.energy = power
    source.shape = "RECTANGLE"
    source.size = width
    source.size_y = height
    source.color = tint
    lamp = bpy.data.objects.new(name, source)
    scene.collection.objects.link(lamp)
    lamp.location = location
    lamp.rotation_euler = (Vector(target) - lamp.location).to_track_quat("-Z", "Y").to_euler()
    return lamp


def sphere(name, location, size, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, radius=size, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(mat)
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def make_glass_lobby(scene):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)

    plaster = material("lobby ivory plaster", (.73, .72, .65), roughness=.84)
    concrete = material("lobby dark polished stone", (.12, .16, .21), metallic=.14, roughness=.17)
    dark = material("black anodized aluminium", (.08, .105, .13), metallic=.85, roughness=.30)
    chrome = material("nearly mirror chrome", (.78, .83, .9), metallic=1, roughness=.048)
    satin = material("satin metal", (.55, .42, .28), metallic=.94, roughness=.34)
    glass_clear = material("clear transmission glass", (.93, .96, 1), transmission=.98, roughness=.035)
    glass_frost = material("rough transmission glass", (.78, .91, .99), transmission=.90, roughness=.22)
    wood = material("timber partition", (.29, .13, .060), roughness=.58)

    box("floor dark reflective", (0, 0, -.14), (7.2, 9.2, .28), concrete)
    box("rear wall", (0, 4.36, 1.62), (7.2, .22, 3.25), plaster)
    box("left wall", (-3.50, 0, 1.62), (.20, 9.2, 3.25), wood)
    box("right wall", (3.50, 0, 1.62), (.20, 9.2, 3.25), plaster)
    box("ceiling", (0, 0, 3.32), (7.2, 9.2, .16), plaster)

    # Hard and soft reflections: rails, polished balls, rough metal panels.
    box("vertical metallic column", (-1.65, .40, 1.45), (.15, .15, 2.9), chrome)
    box("horizontal metallic frame", (.0, .36, 2.9), (3.7, .13, .10), dark)
    sphere("mirror ball foreground", (-.85, -0.65, 1.05), .63, chrome)
    sphere("satin reflective ball back", (1.55, 2.3, 1.07), .58, satin)

    # Different glass roughness, with distinct objects behind the panes.
    box("glass partition clear", (.10, .45, 1.38), (2.65, .045, 2.60), glass_clear)
    box("glass partition frosted", (2.25, 1.4, 1.37), (.045, 2.05, 2.48), glass_frost)
    box("glass door mullion", (1.50, .42, 1.45), (.055, .09, 2.88), dark)
    box("wood display wall", (.0, 3.3, 1.45), (1.35, .35, 2.50), wood)
    box("aluminium artwork", (-1.76, 4.1, 1.65), (1.26, .07, 1.4), chrome)
    box("thin metal shelf", (.7, 2.3, 1.15), (2.4, .50, .045), satin)

    for i in range(7):
        box("parallel narrow floor inlay %02d" % i, (-2.9 + i * .85, -.05, .003),
            (.018, 7.3, .006), chrome)

    # Mixed cool and warm area illumination, including a thin highlight.
    add_area(scene, "broad cool facade source",
             (-.8, -3.7, 2.35), (0, .0, 1.4),
             720, 2.9, 1.8, tint=(.66, .80, 1.0))
    add_area(scene, "narrow warm strip",
             (1.7, 2.2, 2.9), (0.5, 1.2, 1.0),
             270, 1.8, .15, tint=(1.0, .69, .43))
    add_area(scene, "small glint emitter",
             (-2.2, 2.45, 2.7), (-.8, .0, 1.0),
             100, .38, .38, tint=(1.0, 1.0, 1.0))

    world = bpy.data.worlds.new("lobby cool ambient")
    world.use_nodes = True
    world.node_tree.nodes.get("Background").inputs["Color"].default_value = (.09, .13, .18, 1)
    world.node_tree.nodes.get("Background").inputs["Strength"].default_value = .18
    scene.world = world

    point_camera(scene, (2.8, -6.7, 2.12), target=(0, .65, 1.35))
    scene.camera.data.lens = 34
    scene.camera.data.dof.use_dof = False
    print("ACD FIXTURE BUILT: glass_lobby; no external dependencies")
