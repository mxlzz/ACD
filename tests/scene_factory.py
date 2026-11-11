"""Deterministic mini architectural interior used ONLY for denoising experiments.

Built entirely from primitives: no external assets or third-party textures.
Full-sized evaluation scenes are a later milestone.
"""
from __future__ import annotations

import math

import bpy
from mathutils import Vector


def material(name, color, *, roughness=0.55, metallic=0.0, transmission=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    node = m.node_tree.nodes.get("Principled BSDF")
    node.inputs["Base Color"].default_value = (*color, 1.0)
    node.inputs["Roughness"].default_value = roughness
    node.inputs["Metallic"].default_value = metallic
    if transmission:
        node.inputs["Transmission Weight"].default_value = transmission
        node.inputs["IOR"].default_value = 1.46
    return m


def box(name, location, dimensions, mat):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj


def point_camera(scene, position, target=(0, 0, 1.2)):
    bpy.ops.object.camera_add(location=position)
    cam = bpy.context.object
    cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = 32
    scene.camera = cam


def make_interior(scene):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    white = material("warm offwhite plaster", (.77, .70, .59), roughness=.88)
    floor = material("matte light concrete", (.49, .5, .51), roughness=.79)
    wood = material("brown wood", (.32, .13, .06), roughness=.45)
    metal = material("brushed metal", (.48, .50, .55), metallic=.9, roughness=.19)
    glass = material("clear glass", (.91, .96, 1.0), roughness=.05, transmission=.97)
    box("Floor", (0, 0, -.1), (5.5, 6.0, .2), floor)
    box("Rear plaster wall", (0, 2.85, 1.35), (5.5, .18, 2.7), white)
    box("Left wall", (-2.66, 0, 1.35), (.18, 6.0, 2.7), white)
    box("Right wall", (2.66, 0, 1.35), (.18, 6.0, 2.7), white)
    box("Ceiling", (0, 0, 2.76), (5.5, 6.0, .16), white)
    box("Desk top", (-.2, .4, .8), (1.9, .85, .08), wood)
    for x in (-1.0, .6):
        for y in (.08, .72):
            box("Desk leg", (x, y, .4), (.08, .08, .8), metal)
    box("Mirror", (1.2, 2.73, 1.4), (1.1, .05, 1.2), metal)
    box("Glass panel", (1.1, -.45, 1.1), (.055, 1.2, 1.9), glass)
    box("Cabinet", (-1.7, 1.8, .62), (.9, .7, 1.25), wood)
    box("Countertop", (-1.7, 1.8, 1.26), (1.0, .78, .09), metal)
    point_camera(scene, (3.0, -5.8, 2.15))
    # Diffuse source entering open front, aimed toward the rear of the room.
    light_data = bpy.data.lights.new(name="soft window", type="AREA")
    light = bpy.data.objects.new(name="soft window", object_data=light_data)
    scene.collection.objects.link(light)
    light.location = (-.8, -2.15, 2.15)
    light.rotation_euler = (math.radians(90), 0, 0)
    light_data.energy = 380
    light_data.shape = "DISK"
    light_data.size = 2.0
    scene.world = bpy.data.worlds.new("neutral ambient")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (.16, .18, .20, 1.0)
    background.inputs["Strength"].default_value = .25
    scene.camera.data.dof.use_dof = False
    print("ACD FIXTURE BUILT: interior")
