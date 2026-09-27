"""Build the whole stud low-poly library with Blender.

Run with the Blender Python module (pip install bpy) or inside Blender:

    python3 blender/build.py                      # everything
    python3 blender/build.py --only Food,Tools    # some categories
    python3 blender/build.py --names Apple,Banana --out /tmp/test   # quick test
    blender -b -P blender/build.py -- --only Food # same, with a Blender install

Outputs (relative to --out, default = repo root):
    textures/                 palette atlas (+ metalness/roughness) and stud overlay
    exports/fbx/<Category>/   one FBX per asset, ready for the Roblox 3D Importer
    exports/packs/            one FBX per category (imports as a Model of MeshParts)
    blend/<Category>.blend    editable Blender source, all assets laid out on a grid
    previews/                 renders + contact sheets
    catalog.json              every asset with its size in studs and triangle count
"""
import argparse
import importlib
import json
import math
import os
import sys
import time

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from studlib import output, palette, registry, render, studs  # noqa: E402
from studlib.geo import Builder, set_style  # noqa: E402

CATEGORY_MODULES = ["food", "tools", "weapons", "furniture", "nature", "props", "animals", "vehicles",
                    "buildings", "military", "commercial", "tycoon"]
CATEGORY_ORDER = ["Food", "Tools", "Weapons", "Furniture", "Nature", "Props", "Animals", "Vehicles", "Buildings",
                  "Military", "Commercial", "Tycoon"]
PART_TRI_LIMIT = 20000   # Roblox MeshPart triangle limit


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else argv[1:]
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="comma separated categories")
    ap.add_argument("--names", default="", help="comma separated asset names")
    ap.add_argument("--out", default=os.path.dirname(HERE))
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--no-export", action="store_true")
    ap.add_argument("--res", type=int, default=384)
    ap.add_argument("--samples", type=int, default=20)
    ap.add_argument("--pitch", type=float, default=2.0, help="studs per Stud.png tile in previews")
    ap.add_argument("--style", default="blocky", choices=["blocky", "round"],
                    help="blocky = AnimalBundle look (default), round = smooth low poly")
    ap.add_argument("--stud-strength", type=float, default=0.8, help="overlay opacity (Roblox: 1 - Transparency)")
    return ap.parse_args(argv)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0


def load_modules():
    sys.path.insert(0, os.path.join(HERE, "assets"))
    for m in CATEGORY_MODULES:
        importlib.import_module(m)


def build_category(cat, items, args, tex_dir, stud_png):
    reset()
    output.init(tex_dir)
    coll = bpy.data.collections.new(cat)
    bpy.context.scene.collection.children.link(coll)
    rig_mod = None
    if any(a["rig"] for a in items):
        from studlib import rig as rig_mod
        bpy.context.scene.render.fps = rig_mod.FPS
    stage = None if args.no_render else render.Stage(res=args.res, samples=args.samples)
    studs_mat = None if args.no_render else render.preview_material(stud_png, args.pitch, args.stud_strength)
    prev_dir = os.path.join(args.out, "previews", cat)
    os.makedirs(prev_dir, exist_ok=True)
    catalog = []
    placed = []
    for a in items:
        t0 = time.time()
        b = Builder(a["name"])
        a["fn"](b)
        sub = coll
        if a["sub"]:
            sub = bpy.data.collections.get(f"{cat}/{a['sub']}")
            if sub is None:
                sub = bpy.data.collections.new(f"{cat}/{a['sub']}")
                coll.children.link(sub)
        bones = dict(b.bones)
        groups = list(b.groups)
        if a.get("split"):
            ob = output.finish_split(b, origin=a["origin"], collection=sub)
        else:
            ob = output.finish(b, origin=a["origin"], collection=sub)
        root = ob
        if a["rig"] and bones:
            root = rig_mod.rig(ob, bones, groups, a["rig"], sub)
        info = dict(name=a["name"], category=cat, group=a["sub"], tris=ob["tris"],
                    size_studs=[round(v, 2) for v in ob.dimensions], rigged=root is not ob,
                    parts=list(ob.get("parts", [])),
                    tags=a["tags"])
        if not args.no_export:
            p = os.path.join(args.out, "exports", "fbx", cat, a["name"] + ".fbx")
            output.export_fbx([root], p, armature=root is not ob)
            info["fbx"] = os.path.relpath(p, args.out)
            if root is not ob:
                info["animations"] = {}
                for clip in root["clips"]:
                    act = bpy.data.actions[f"{root.name}_{clip}"]
                    root.animation_data.action = act
                    bpy.context.scene.frame_start, bpy.context.scene.frame_end = 1, act["frames"] + 1
                    pa = os.path.join(args.out, "exports", "animations", a["name"], f"{a['name']}_{clip}.fbx")
                    output.export_fbx([root], pa, armature=True, anim=True, embed=False, rig_only=True)
                    info["animations"][clip] = os.path.relpath(pa, args.out)
                root.animation_data.action = bpy.data.actions[f"{root.name}_{root['clips'][0]}"]
                bpy.context.scene.frame_set(1)
        for po in [ob] + list(ob.children):
            if po.type == "MESH":
                pt = sum(len(p.vertices) - 2 for p in po.data.polygons)
                if pt > PART_TRI_LIMIT:
                    print(f"WARNING: {po.name} has {pt} triangles (Roblox limit {PART_TRI_LIMIT})", flush=True)
        if stage is not None:
            big = "interior" in a["tags"]
            res0 = stage.sc.render.resolution_x
            if big:   # buildings with interiors get sharper renders
                stage.sc.render.resolution_x = stage.sc.render.resolution_y = max(res0, 768)
            pp = os.path.join(prev_dir, a["name"] + ".png")
            stage.shoot([root], pp, studs_mat=studs_mat)
            render.shrink(pp, 512 if big else 256)
            info["preview"] = os.path.relpath(pp, args.out)
            if big:
                # cutaway: lift the roof off and look down into the rooms
                roof = [c for c in ob.children if c.name.endswith("_Roof")]
                pi = os.path.join(prev_dir, a["name"] + "_Inside.png")
                stage.shoot([root], pi, direction=(0.6, -0.95, 2.4), studs_mat=studs_mat, hide=roof)
                render.shrink(pi, 512)
                info["preview_inside"] = os.path.relpath(pi, args.out)
            stage.sc.render.resolution_x = stage.sc.render.resolution_y = res0
        placed.append((root, ob))
        catalog.append(info)
        print(f"[{cat}] {a['name']:<28} tris={ob['tris']:<6} size={info['size_studs']} "
              f"{time.time() - t0:.1f}s", flush=True)

    # lay everything out on a grid for the .blend and the category pack
    cols = max(1, int(math.ceil(math.sqrt(len(placed)))))
    x = y = 0.0
    row_h = 0.0
    for i, (root, ob) in enumerate(placed):
        w, d = ob.dimensions.x, ob.dimensions.y
        if i % cols == 0 and i:
            x = 0.0
            y -= row_h + 2.0
            row_h = 0.0
        root.location = (x + w / 2, y - d / 2, 0)
        x += w + 2.0
        row_h = max(row_h, d)

    if not args.no_export:
        pack = os.path.join(args.out, "exports", "packs", cat + ".fbx")
        output.export_fbx([r for r, _ in placed], pack, armature=any(r is not o for r, o in placed))
        if stage is not None:
            bpy.data.objects.remove(stage.cam)
            bpy.data.objects.remove(stage.ground)
            for o in list(stage.col.objects):
                bpy.data.objects.remove(o)
            bpy.data.collections.remove(stage.col)
        bpy.data.materials.remove(bpy.data.materials[render.PREVIEW_MAT]) \
            if render.PREVIEW_MAT in bpy.data.materials else None
        blend = os.path.join(args.out, "blend", cat + ".blend")
        os.makedirs(os.path.dirname(blend), exist_ok=True)
        bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=blend, compress=True)

    if stage is not None and catalog:
        items_png = []
        for c in catalog:
            items_png.append((os.path.join(args.out, c["preview"]), c["name"]))
            if c.get("preview_inside"):
                items_png.append((os.path.join(args.out, c["preview_inside"]), c["name"] + " (inside)"))
        render.contact_sheet(items_png, os.path.join(args.out, "previews", f"{cat}.png"),
                             f"{cat} — {len(catalog)} assets (stud low poly)")
    return catalog


def main():
    args = parse_args()
    set_style(args.style)
    t0 = time.time()
    reset()
    tex_dir = os.path.join(args.out, "textures")
    os.makedirs(tex_dir, exist_ok=True)
    palette.write_atlases(tex_dir)
    palette.swatch_sheet(os.path.join(tex_dir, "PaletteReference.png"))
    stud_png = os.path.join(tex_dir, "Stud.png")
    if not os.path.exists(stud_png):
        studs.render_stud_tile(tex_dir)
    load_modules()
    only = [c.strip().lower() for c in args.only.split(",") if c.strip()]
    names = [n.strip() for n in args.names.split(",") if n.strip()]
    cats = {}
    for a in registry.ASSETS:
        if only and a["category"].lower() not in only:
            continue
        if names and a["name"] not in names:
            continue
        cats.setdefault(a["category"], []).append(a)
    cat_path = os.path.join(args.out, "catalog.json")
    catalog = {}
    if os.path.exists(cat_path) and (only or names):
        catalog = json.load(open(cat_path))
    for cat in sorted(cats, key=lambda c: CATEGORY_ORDER.index(c) if c in CATEGORY_ORDER else 99):
        catalog[cat] = build_category(cat, cats[cat], args, tex_dir, stud_png)
    with open(cat_path, "w") as f:
        json.dump(catalog, f, indent=1)
    n = sum(len(v) for v in catalog.values())
    print(f"done: {n} assets in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
