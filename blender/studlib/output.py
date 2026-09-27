"""Turn a Builder into a Blender object, and export it for Roblox."""
import os

import bmesh
import bpy
import numpy as np
from mathutils import Vector

from . import palette

TEX_DIR = None  # set by init()
MAT_NAME = "StudPalette"


def init(tex_dir):
    """Load the palette textures (written beforehand) and build the material."""
    global TEX_DIR
    TEX_DIR = tex_dir
    palette_material()


def _img(fname, non_color=False):
    path = os.path.join(TEX_DIR, fname)
    img = bpy.data.images.get(fname)
    if img is None:
        img = bpy.data.images.load(path, check_existing=True)
    if non_color:
        img.colorspace_settings.name = "Non-Color"
    return img


def palette_material():
    mat = bpy.data.materials.get(MAT_NAME)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(MAT_NAME)
    mat.use_nodes = True
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.location = (300, 0)
    col = nt.nodes.new("ShaderNodeTexImage")
    col.image = _img("StudPalette.png")
    col.interpolation = "Closest"
    col.location = (-200, 200)
    met = nt.nodes.new("ShaderNodeTexImage")
    met.image = _img("StudPalette_Metalness.png", True)
    met.interpolation = "Closest"
    met.location = (-200, -80)
    rou = nt.nodes.new("ShaderNodeTexImage")
    rou.image = _img("StudPalette_Roughness.png", True)
    rou.interpolation = "Closest"
    rou.location = (-200, -360)
    nt.links.new(col.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(met.outputs["Color"], bsdf.inputs["Metallic"])
    nt.links.new(rou.outputs["Color"], bsdf.inputs["Roughness"])
    return mat


def finish(b, origin="bottom", collection=None, weighted=True):
    """Build the mesh object from a Builder. ``origin``: 'bottom', 'center' or (x,y,z)."""
    bm = b.bm
    bm.normal_update()  # triangulation projects along face normals; they must be valid
    ngons = [f for f in bm.faces if len(f.verts) > 4]
    if ngons:
        bmesh.ops.triangulate(bm, faces=ngons, quad_method="BEAUTY", ngon_method="BEAUTY")
    # drop exact duplicate / degenerate faces that can break importers
    bad = [f for f in bm.faces if f.calc_area() < 1e-9]
    if bad:
        bmesh.ops.delete(bm, geom=bad, context="FACES_ONLY")
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")

    # origin
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]
    zs = [v.co.z for v in bm.verts]
    if origin == "bottom":
        off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    elif origin == "center":
        off = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2))
    else:
        off = Vector(origin)
    for v in bm.verts:
        v.co -= off

    me = bpy.data.meshes.new(b.name)
    bm.to_mesh(me)
    bm.free()

    # palette UVs from the per-face colour index
    npoly = len(me.polygons)
    pal = np.zeros(npoly, np.int32)
    me.attributes["pal"].data.foreach_get("value", pal)
    uvs_per_cell = np.array([palette.uv(n) for n in palette.NAMES], np.float32)
    poly_uv = uvs_per_cell[pal]
    totals = np.zeros(npoly, np.int32)
    me.polygons.foreach_get("loop_total", totals)
    loop_uv = np.repeat(poly_uv, totals, axis=0)
    uvl = me.uv_layers.new(name="UVMap")
    uvl.data.foreach_set("uv", loop_uv.ravel())

    me.materials.append(palette_material())
    ob = bpy.data.objects.new(b.name, me)
    (collection or bpy.context.scene.collection).objects.link(ob)

    if weighted:
        mod = ob.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL")
        mod.mode = "FACE_AREA"
        mod.weight = 50
        mod.keep_sharp = True
        with bpy.context.temp_override(object=ob, active_object=ob, selected_objects=[ob]):
            bpy.ops.object.modifier_apply(modifier=mod.name)
    # keep the grp attribute for rigging; drop 'pal' (baked into UVs)
    ob["origin_offset"] = list(off)
    ob["tris"] = sum(len(p.vertices) - 2 for p in me.polygons)
    ob["studs"] = [round(d, 2) for d in ob.dimensions]
    return ob


def finish_split(b, origin="bottom", collection=None):
    """Like finish(), but every rig group other than the first becomes its own
    object parented to the main one, with its origin at its own centre.

    Used for vehicles and machines: wheels, rotors, propellers and turrets come in
    as separate MeshParts so they can be driven by constraints in Roblox.
    """
    ob = finish(b, origin=origin, collection=collection)
    me = ob.data
    if "grp" not in me.attributes:
        return ob
    npoly = len(me.polygons)
    grp = np.zeros(npoly, np.int32)
    me.attributes["grp"].data.foreach_get("value", grp)
    used = sorted(set(grp.tolist()))
    main = used[0] if 0 not in used else 0
    parts = []
    for gi in used:
        if gi == main:
            continue
        name = f"{b.name}_{b.groups[gi]}"
        bm = bmesh.new()
        bm.from_mesh(me)
        lay = bm.faces.layers.int.get("grp")
        bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[lay] != gi], context="FACES")
        loose = [v for v in bm.verts if not v.link_faces]
        if loose:
            bmesh.ops.delete(bm, geom=loose, context="VERTS")
        c = Vector((0, 0, 0))
        for v in bm.verts:
            c += v.co
        c /= max(1, len(bm.verts))
        lo = Vector((min(v.co.x for v in bm.verts), min(v.co.y for v in bm.verts), min(v.co.z for v in bm.verts)))
        hi = Vector((max(v.co.x for v in bm.verts), max(v.co.y for v in bm.verts), max(v.co.z for v in bm.verts)))
        c = (lo + hi) / 2
        for v in bm.verts:
            v.co -= c
        pm = bpy.data.meshes.new(name)
        bm.to_mesh(pm)
        bm.free()
        pm.materials.append(palette_material())
        po = bpy.data.objects.new(name, pm)
        (collection or bpy.context.scene.collection).objects.link(po)
        po.location = c
        po.parent = ob
        parts.append(po)
    # remove the split-off faces from the main body
    bm = bmesh.new()
    bm.from_mesh(me)
    lay = bm.faces.layers.int.get("grp")
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f[lay] != main], context="FACES")
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context="VERTS")
    bm.to_mesh(me)
    bm.free()
    total = sum(len(p.vertices) - 2 for p in me.polygons)
    for po in parts:
        total += sum(len(p.vertices) - 2 for p in po.data.polygons)
    ob["tris"] = total
    ob["parts"] = [po.name for po in parts]
    return ob


def export_fbx(objects, path, armature=False, anim=False, embed=True, rig_only=False):
    """Export objects (with children) to FBX: 1 Blender unit = 1 stud, Y-up."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects:
        ob.select_set(True)
        for c in ob.children_recursive:
            c.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.export_scene.fbx(
        filepath=path,
        use_selection=True,
        object_types={"ARMATURE"} if rig_only else {"MESH", "ARMATURE"},
        apply_scale_options="FBX_SCALE_UNITS",
        axis_forward="-Z",
        axis_up="Y",
        bake_space_transform=not armature,
        use_mesh_modifiers=True,
        mesh_smooth_type="OFF",
        use_tspace=False,
        add_leaf_bones=False,
        primary_bone_axis="Y",
        secondary_bone_axis="X",
        use_armature_deform_only=True,
        bake_anim=anim,
        bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False,
        bake_anim_simplify_factor=0.0,
        path_mode="COPY" if embed else "AUTO",
        embed_textures=embed,
    )
    bpy.ops.object.select_all(action="DESELECT")
