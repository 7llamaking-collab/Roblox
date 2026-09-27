"""Package the exported library into download-ready ZIP files for Roblox Studio.

    python3 blender/package.py

Writes to downloads/:
    StudLowPoly_QuickStart_AllPacks.zip   7 "all-in-one" FBX files, one per category
    StudLowPoly_<Category>.zip            every asset of a category as its own FBX (+ animations)
    StudLowPoly_BlenderSource.zip         editable .blend files
    StudLowPoly_Everything.zip            all of the above in one download
"""
import json
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "downloads")
CATS = ["Food", "Tools", "Weapons", "Furniture", "Nature", "Props", "Animals", "Vehicles", "Buildings", "Military"]

HOW_TO = """STUD LOW POLY ASSETS - HOW TO PUT THEM IN ROBLOX STUDIO
=====================================================

1. Unzip this file.
2. Open your place in Roblox Studio.
3. Go to the HOME (or AVATAR) tab and click  "Import 3D"
   (or File > Import 3D).
4. Pick a .fbx file:
     *_AllInOne.fbx     = the WHOLE category in one go (one Model full of MeshParts)
     Individual/*.fbx   = one single asset
5. In the import window:
     - keep the scale unit on "Studs" (1 Blender unit = 1 stud)
     - if a model faces backwards, change "World Forward"
     - click Import. The colours (StudPalette texture) come in automatically.
6. The model appears in the Workspace. Move it to ReplicatedStorage / ServerStorage
   if you want to spawn copies from your game.

STUDS (optional, matches your AnimalBundle)
  Select the imported models, open View > Command Bar, paste everything from
  StudStyle.lua and press Enter. It adds the stud overlay (6 Textures) to every MeshPart,
  using the same stud texture as your AnimalBundle. (Or upload Textures/Stud.png and use
  StudsPerTile = 2 - that is exactly how the preview pictures look.)

SHINY METALS & GEMS (optional)
  Upload the 3 PNGs in Textures/ (StudPalette, _Metalness, _Roughness) and paste their ids
  into the top of StudStyle.lua before running it.

VEHICLES, MACHINES & MILITARY
  Wheels, rotors, propellers, turrets, barrels, windmill blades and radar dishes come in as
  separate MeshParts inside the model (origin at their centre), ready for HingeConstraints
  or any Roblox vehicle chassis.

TOOLS & WEAPONS
  They stand upright with the pivot on the grip. Put the MeshPart inside a Tool,
  name it "Handle", and adjust Tool.Grip.

ANIMALS (rigged)
  Import Individual/<Animal>.fbx -> you get a skinned MeshPart with Bones.
  (Dragons, golems, yeti, treant, mimic... are in the "Mythical" group - see ASSET_LIST.txt.)
  To add motion: select the rig, open the Animation Editor, then
  "..." > Import > From FBX Animation > pick Animations/<Animal>/<Animal>_Walk.fbx
  (or _Idle / _Fly / _Swim), then Publish to Roblox.
"""


def add_preview(z, png, arc_jpg):
    """Contact sheets as JPEG: same picture, a fraction of the download size."""
    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.open(png).convert("RGB").save(buf, "JPEG", quality=88, optimize=True)
    z.writestr(arc_jpg, buf.getvalue())


def add_dir(z, src, arc):
    for base, _, files in os.walk(src):
        for f in sorted(files):
            p = os.path.join(base, f)
            z.write(p, os.path.join(arc, os.path.relpath(p, src)))


def common(z, arc):
    z.writestr(os.path.join(arc, "HOW_TO_IMPORT.txt"), HOW_TO)
    z.write(os.path.join(ROOT, "roblox", "StudStyle.lua"), os.path.join(arc, "StudStyle.lua"))
    for f in ("StudPalette.png", "StudPalette_Metalness.png", "StudPalette_Roughness.png", "Stud.png",
              "PaletteReference.png"):
        z.write(os.path.join(ROOT, "textures", f), os.path.join(arc, "Textures", f))


def category(z, cat, arc, catalog):
    z.write(os.path.join(ROOT, "exports", "packs", cat + ".fbx"), os.path.join(arc, f"{cat}_AllInOne.fbx"))
    add_dir(z, os.path.join(ROOT, "exports", "fbx", cat), os.path.join(arc, "Individual"))
    add_preview(z, os.path.join(ROOT, "previews", cat + ".png"), os.path.join(arc, f"Preview_{cat}.jpg"))
    lines = [f"{'Asset':<26}{'Group':<12}{'Size in studs (X x Y x Z)':<30}Triangles"]
    for a in catalog[cat]:
        size = " x ".join(f"{v:g}" for v in a["size_studs"])
        lines.append(f"{a['name']:<26}{a['group']:<12}{size:<30}{a['tris']}")
    z.writestr(os.path.join(arc, "ASSET_LIST.txt"), "\n".join(lines) + "\n")
    if cat == "Animals":
        add_dir(z, os.path.join(ROOT, "exports", "animations"), os.path.join(arc, "Animations"))


def zipf(name):
    return zipfile.ZipFile(os.path.join(OUT, name), "w", zipfile.ZIP_DEFLATED, compresslevel=9)


def main():
    os.makedirs(OUT, exist_ok=True)
    catalog = json.load(open(os.path.join(ROOT, "catalog.json")))

    with zipf("StudLowPoly_QuickStart_AllPacks.zip") as z:
        arc = "StudLowPoly_QuickStart"
        common(z, arc)
        for cat in CATS:
            z.write(os.path.join(ROOT, "exports", "packs", cat + ".fbx"), os.path.join(arc, f"{cat}_AllInOne.fbx"))
            add_preview(z, os.path.join(ROOT, "previews", cat + ".png"), os.path.join(arc, "Previews", f"{cat}.jpg"))

    for cat in CATS:
        with zipf(f"StudLowPoly_{cat}.zip") as z:
            arc = f"StudLowPoly_{cat}"
            common(z, arc)
            category(z, cat, arc, catalog)

    with zipf("StudLowPoly_BlenderSource.zip") as z:
        arc = "StudLowPoly_BlenderSource"
        add_dir(z, os.path.join(ROOT, "blend"), arc)
        for f in ("StudPalette.png", "StudPalette_Metalness.png", "StudPalette_Roughness.png", "Stud.png"):
            z.write(os.path.join(ROOT, "textures", f), os.path.join(arc, "Textures", f))

    with zipf("StudLowPoly_Everything.zip") as z:
        arc = "StudLowPoly_Everything"
        common(z, arc)
        for cat in CATS:
            category(z, cat, os.path.join(arc, cat), catalog)
        add_dir(z, os.path.join(ROOT, "blend"), os.path.join(arc, "BlenderSource"))

    for f in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, f)
        with zipfile.ZipFile(p) as z:
            bad = z.testzip()
            n = len(z.namelist())
        print(f"{f:<42}{os.path.getsize(p) / 1e6:6.1f} MB  {n:4d} files  {'OK' if bad is None else 'CORRUPT: ' + bad}")


if __name__ == "__main__":
    main()
