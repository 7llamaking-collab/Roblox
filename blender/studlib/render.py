"""Preview renders (Cycles, CPU) with the Roblox-style stud overlay."""
import math
import os

import bpy
from mathutils import Vector

from . import output

PREVIEW_MAT = "StudPalette_Preview"


def preview_material(stud_png, pitch=2.0, strength=0.8):
    """Palette material + box-projected stud overlay (mimics Roblox Texture objects)."""
    mat = bpy.data.materials.get(PREVIEW_MAT)
    if mat is not None:
        return mat
    base = output.palette_material()
    mat = base.copy()
    mat.name = PREVIEW_MAT
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    col_node = bsdf.inputs["Base Color"].links[0].from_node
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1 / pitch, 1 / pitch, 1 / pitch)
    mp.inputs["Location"].default_value = (0.5, 0.5, 0.5)
    st = nt.nodes.new("ShaderNodeTexImage")
    st.image = bpy.data.images.load(stud_png, check_existing=True)
    st.projection = "BOX"
    st.projection_blend = 0.15
    st.interpolation = "Cubic"
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], st.inputs["Vector"])
    mul = nt.nodes.new("ShaderNodeMath")
    mul.operation = "MULTIPLY"
    mul.inputs[1].default_value = strength
    nt.links.new(st.outputs["Alpha"], mul.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MIX"
    nt.links.new(mul.outputs[0], mix.inputs[0])
    nt.links.new(col_node.outputs["Color"], mix.inputs[6])
    nt.links.new(st.outputs["Color"], mix.inputs[7])
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    return mat


class Stage:
    """A reusable photo stage: lights, shadow catcher and an auto-framing camera."""

    def __init__(self, res=384, samples=20):
        sc = bpy.context.scene
        self.sc = sc
        sc.render.engine = "CYCLES"
        sc.cycles.device = "CPU"
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        sc.cycles.max_bounces = 4
        sc.render.resolution_x = sc.render.resolution_y = res
        sc.render.film_transparent = True
        sc.view_settings.view_transform = "Standard"
        sc.view_settings.look = "None"
        sc.render.image_settings.file_format = "PNG"
        sc.render.image_settings.color_mode = "RGBA"

        self.col = bpy.data.collections.new("_Stage")
        sc.collection.children.link(self.col)
        w = bpy.data.worlds.new("StageWorld")
        w.use_nodes = True
        bg = w.node_tree.nodes["Background"]
        bg.inputs[0].default_value = (0.78, 0.84, 0.95, 1)
        bg.inputs[1].default_value = 0.62
        sc.world = w

        def light(name, kind, energy, rot, size=None, color=(1, 1, 1)):
            ld = bpy.data.lights.new(name, kind)
            ld.energy = energy
            ld.color = color
            if kind == "SUN":
                ld.angle = math.radians(size or 8)
            ob = bpy.data.objects.new(name, ld)
            ob.rotation_euler = [math.radians(a) for a in rot]
            self.col.objects.link(ob)
            return ob

        light("Key", "SUN", 2.7, (48, 0, -32), 10, (1.0, 0.97, 0.92))
        light("Rim", "SUN", 1.4, (60, 0, 150), 20, (0.85, 0.9, 1.0))

        bpy.ops.mesh.primitive_plane_add(size=1)
        g = bpy.context.active_object
        for c in g.users_collection:
            c.objects.unlink(g)
        self.col.objects.link(g)
        g.name = "_Ground"
        g.is_shadow_catcher = True
        g.scale = (500, 500, 1)
        self.ground = g

        cam = bpy.data.objects.new("_Cam", bpy.data.cameras.new("_Cam"))
        cam.data.lens = 50
        self.col.objects.link(cam)
        sc.camera = cam
        self.cam = cam

    def frame(self, objs, direction=(0.95, -1.55, 0.95), pad=1.08):
        """Point the camera along ``direction`` and fit the objects' bounding box tightly."""
        pts = []
        for ob in objs:
            for corner in ob.bound_box:
                pts.append(ob.matrix_world @ Vector(corner))
        lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
        hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
        center = (lo + hi) / 2
        d = Vector(direction).normalized()
        rot = (-d).to_track_quat("-Z", "Y")
        right = rot @ Vector((1, 0, 0))
        up = rot @ Vector((0, 1, 0))
        t = math.tan(self.cam.data.angle / 2)
        dist = 0.1
        for p in pts:
            v = p - center
            along = v.dot(d)
            need = max(abs(v.dot(right)), abs(v.dot(up))) * pad / t + along
            dist = max(dist, need)
        self.cam.location = center + d * dist
        self.cam.rotation_euler = rot.to_euler()
        self.cam.data.clip_start = dist * 0.01
        self.cam.data.clip_end = dist * 10
        self.ground.location = (center.x, center.y, lo.z)

    def shoot(self, objs, path, direction=(0.95, -1.55, 0.95), studs_mat=None, hide=()):
        """Render only ``objs`` (others hidden) to ``path``. ``hide``: child parts to leave out (cutaways)."""
        visible = set()
        for ob in objs:
            visible.add(ob)
            visible.update(ob.children_recursive)
        visible -= set(hide)
        saved = {}
        for ob in self.sc.objects:
            if ob.name.startswith("_") or ob.users_collection[0] == self.col:
                continue
            saved[ob] = ob.hide_render
            ob.hide_render = ob not in visible
        swaps = []
        if studs_mat is not None:
            for ob in visible:
                if ob.type == "MESH":
                    for slot in ob.material_slots:
                        if slot.material and slot.material.name == output.MAT_NAME:
                            swaps.append((slot, slot.material))
                            slot.material = studs_mat
        self.frame([o for o in visible if o.type == "MESH"], direction)
        self.sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        for slot, m in swaps:
            slot.material = m
        for ob, h in saved.items():
            ob.hide_render = h


def shrink(path, px):
    """Downscale a saved render in place (keeps the repo light)."""
    from PIL import Image
    im = Image.open(path)
    if im.width > px:
        im.resize((px, px), Image.LANCZOS).save(path, optimize=True)


def contact_sheet(items, path, title, cols=6, tile=256, bg=(236, 240, 246)):
    """items: list of (png_path, label). Composites renders onto a labelled grid."""
    from PIL import Image, ImageDraw, ImageFont
    rows = (len(items) + cols - 1) // cols
    head = 56
    lab = 26
    W, H = cols * tile, head + rows * (tile + lab)
    sheet = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        small = ImageFont.truetype("DejaVuSans.ttf", 15)
    except OSError:
        font = small = ImageFont.load_default()
    d.text((16, 12), title, fill=(40, 44, 56), font=font)
    for i, (p, label) in enumerate(items):
        x, y = (i % cols) * tile, head + (i // cols) * (tile + lab)
        card = Image.new("RGB", (tile - 8, tile + lab - 8), (214, 222, 234))
        sheet.paste(card, (x + 4, y + 4))
        if os.path.exists(p):
            im = Image.open(p).convert("RGBA").resize((tile - 16, tile - 16), Image.LANCZOS)
            sheet.paste(im, (x + 8, y + 8), im)
        tw = d.textlength(label, font=small)
        d.text((x + (tile - tw) / 2, y + tile - 4), label, fill=(60, 64, 76), font=small)
    sheet.save(path)
