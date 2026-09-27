"""Render the stud overlay tile in Blender.

A stud plate is modelled and lit from the top-left, rendered top-down with an
orthographic camera, then converted to a transparent overlay: highlights become
white, shadows black, the flat plate fully transparent. In Roblox the result is
used on ``Texture`` objects (one per face) exactly like the studs on the animal
bundle, so it can be switched off for games that do not want studs.
"""
import math
import os

import bpy
import numpy as np


def render_stud_tile(out_dir, px=256, studs=1):
    """Write Stud.png (overlay, RGBA) and Stud_Shading.png (grey render)."""
    from PIL import Image

    scene = bpy.data.scenes.new("StudTile")
    win_scene = bpy.context.window.scene if bpy.context.window else None
    sc = scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 64
    sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = px * studs
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("StudWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.35
    sc.world = world

    mat = bpy.data.materials.new("StudWhite")
    mat.use_nodes = True
    bs = mat.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1)
    bs.inputs["Roughness"].default_value = 0.55

    def add(ob):
        sc.collection.objects.link(ob)
        ob.data.materials.append(mat)
        return ob

    # plate much larger than the frame so the edges never show
    bpy.ops.mesh.primitive_plane_add(size=studs * 5)
    plate = bpy.context.active_object
    for c in plate.users_collection:
        c.objects.unlink(plate)
    add(plate)
    for i in range(-1, studs + 1):
        for j in range(-1, studs + 1):
            bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.3, depth=0.17,
                                                location=(i - (studs - 1) / 2, j - (studs - 1) / 2, 0.085))
            cy = bpy.context.active_object
            for c in cy.users_collection:
                c.objects.unlink(cy)
            add(cy)
            bev = cy.modifiers.new("b", "BEVEL")
            bev.width = 0.035
            bev.segments = 4
            bev.limit_method = "ANGLE"
            cy.data.polygons.foreach_set("use_smooth", [True] * len(cy.data.polygons))

    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.2
    sun.data.angle = math.radians(12)
    sun.rotation_euler = (math.radians(42), 0, math.radians(-135))
    sc.collection.objects.link(sun)

    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = studs
    cam.location = (0, 0, 5)
    sc.collection.objects.link(cam)
    sc.camera = cam

    shade_path = os.path.join(out_dir, "Stud_Shading.png")
    sc.render.filepath = shade_path
    with bpy.context.temp_override(scene=sc):
        bpy.ops.render.render(write_still=True, scene=sc.name)

    g = np.asarray(Image.open(shade_path).convert("L"), np.float32) / 255.0
    c = g.shape[0] // 2
    bg = float(np.median(g[c - 6:c + 6, c - 6:c + 6]))  # flat stud top == plate value
    d = g - bg
    k = 1.8
    a_hi = np.clip(d * k, 0, 1)
    a_lo = np.clip(-d * k, 0, 1)
    rgba = np.zeros(g.shape + (4,), np.float32)
    rgba[..., :3] = np.where(d[..., None] > 0, 1.0, 0.0)
    rgba[..., 3] = np.maximum(a_hi, a_lo)
    out = os.path.join(out_dir, "Stud.png")
    Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").save(out)
    bpy.data.scenes.remove(sc)
    return out
