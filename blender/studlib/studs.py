"""Render the stud overlay tile in Blender.

Matches the AnimalBundle look: a grid of small raised square / rectangular tiles
(1x1, 2x1, 1x2, 2x2 cells) lit from the top-left. The plate is rendered top-down
with an orthographic camera and converted to a transparent overlay: highlights
become white, shadows black, flat areas fully transparent. In Roblox it goes on
``Texture`` objects (one per face), so it can be switched off per game.

The layout is repeated 3x3 around the rendered tile so shadows wrap and the
texture tiles seamlessly.
"""
import math
import os
import random

import bpy
import numpy as np

CELLS = 8          # "tiles" mode: cells per side


def _layout(seed=7):
    rnd = random.Random(seed)
    used = [[False] * CELLS for _ in range(CELLS)]
    blocks = []
    for y in range(CELLS):
        for x in range(CELLS):
            if used[y][x]:
                continue
            if rnd.random() < 0.22:          # leave some cells flat
                used[y][x] = True
                continue
            w, h = rnd.choice([(1, 1), (1, 1), (1, 1), (2, 1), (1, 2), (2, 2)])
            if x + w > CELLS or y + h > CELLS or any(used[y + j][x + i] for i in range(w) for j in range(h)):
                w, h = 1, 1
            for i in range(w):
                for j in range(h):
                    used[y + j][x + i] = True
            blocks.append((x, y, w, h))
    return blocks


def render_stud_tile(out_dir, px=512, seed=7, mode="classic", studs=4):
    """Write Stud.png (overlay, RGBA). Returns its path.

    mode "classic": round Roblox/LEGO studs on a grid (``studs`` x ``studs`` per tile).
    mode "tiles": raised square / rectangular tiles.
    """
    from PIL import Image

    sc = bpy.data.scenes.new("StudTile")
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 64
    sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = px
    sc.render.film_transparent = False
    sc.view_settings.view_transform = "Standard"
    world = bpy.data.worlds.new("StudWorld")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (1, 1, 1, 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.45
    sc.world = world

    mat = bpy.data.materials.new("StudGrey")
    mat.use_nodes = True
    bs = mat.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value = (0.5, 0.5, 0.5, 1)
    bs.inputs["Roughness"].default_value = 0.45

    def link(ob):
        for c in ob.users_collection:
            c.objects.unlink(ob)
        sc.collection.objects.link(ob)
        ob.data.materials.append(mat)
        return ob

    bpy.ops.mesh.primitive_plane_add(size=6)
    link(bpy.context.active_object)
    if mode == "classic":
        cell = 1.0 / studs
        for i in range(-studs, 2 * studs):
            for j in range(-studs, 2 * studs):
                cx = -0.5 + (i + 0.5) * cell
                cy = -0.5 + (j + 0.5) * cell
                bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=cell * 0.3, depth=cell * 0.2,
                                                    location=(cx, cy, cell * 0.1))
                ob = link(bpy.context.active_object)
                bev = ob.modifiers.new("b", "BEVEL")
                bev.width = cell * 0.04
                bev.segments = 3
                bev.limit_method = "ANGLE"
                ob.data.polygons.foreach_set("use_smooth", [True] * len(ob.data.polygons))
    else:
        cell = 1.0 / CELLS
        gap = cell * 0.09
        height = cell * 0.16
        for bx, by, w, h in _layout(seed):
            for ox in (-1, 0, 1):
                for oy in (-1, 0, 1):
                    cx = -0.5 + (bx + w / 2) * cell + ox
                    cy = 0.5 - (by + h / 2) * cell + oy
                    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, height / 2))
                    ob = link(bpy.context.active_object)
                    ob.scale = (w * cell - gap, h * cell - gap, height)
                    bev = ob.modifiers.new("b", "BEVEL")
                    bev.width = cell * 0.05
                    bev.segments = 2

    sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN"))
    sun.data.energy = 3.4
    sun.data.angle = math.radians(6)
    sun.rotation_euler = (math.radians(55), 0, math.radians(-135))
    sc.collection.objects.link(sun)

    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 1.0
    cam.location = (0, 0, 5)
    sc.collection.objects.link(cam)
    sc.camera = cam

    shade_path = os.path.join(out_dir, "_stud_shading.png")
    sc.render.filepath = shade_path
    bpy.ops.render.render(write_still=True, scene=sc.name)

    g = np.asarray(Image.open(shade_path).convert("L"), np.float32) / 255.0
    bg = float(np.median(g))  # flat plate / stud tops
    d = g - bg
    k = 2.4
    rgba = np.zeros(g.shape + (4,), np.float32)
    rgba[..., :3] = np.where(d[..., None] > 0, 1.0, 0.0)
    rgba[..., 3] = np.clip(np.abs(d) * k, 0, 1)
    out = os.path.join(out_dir, "Stud.png")
    Image.fromarray((rgba * 255).astype(np.uint8), "RGBA").save(out)
    os.remove(shade_path)
    bpy.data.scenes.remove(sc)
    return out
