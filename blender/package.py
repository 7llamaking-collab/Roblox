"""Package the exported library into download-ready ZIP files for Roblox Studio.

    python3 blender/package.py

Writes to downloads/:
    StudLowPoly_QuickStart_AllPacks.zip   one "all-in-one" FBX file per category
    StudLowPoly_<Category>.zip            every asset of a category as its own FBX (+ animations)
    StudLowPoly_BlenderSource.zip         editable .blend files
    StudLowPoly_Everything.zip            all of the above in one download
"""
import json
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "downloads")
CATS = ["Food", "Tools", "Weapons", "Furniture", "Nature", "Props", "Animals", "Vehicles", "Buildings", "Military",
        "Commercial", "Tycoon", "Holidays"]

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

RESTAURANTS, SHOPS, BANK... WITH INTERIORS (Commercial)
  Every building is a Model of separate MeshParts:
     <Name>            floor, walls and facade
     <Name>_Roof       the roof, ceiling lights and rooftop units - hide it (Transparency 1)
                       for a top-down / cutaway view of the inside
     <Name>_Glass      all the window glass
     <Name>_DoorL/R    door leaves you can hinge or slide open (also _BackDoor, _KitchenDoor...)
     <Name>_Kitchen, _Counter, _Dining, _Booths, _Aisles...   furniture groups you can move or delete
  After importing, select the building and run BuildingSetup.lua in the Command Bar: it makes the
  glass see-through and sets precise collisions so players can walk in through the doors.
  (Or by hand: Transparency 0.45 on _Glass, and CollisionFidelity = PreciseConvexDecomposition on
  the main wall part.) Scale: doors are 8 studs tall, ceilings 13 studs - made for normal avatars.
  Every piece of furniture is also available on its own (Fixtures groups in ASSET_LIST.txt).

TYCOON & SIMULATOR BUILDS (Tycoon)
  Scriptable pieces are separate parts: _Belt (conveyor belts), _Ore (the block a dropper makes),
  _Laser / _Lasers (laser doors, upgraders), _Button (buy / lock buttons), _Barrier (zone gates),
  _Slot1 ... _Slot14 (steal-base pedestals), _Dropper1..., _Button1... on the example plots.
  BuildingSetup.lua turns lasers and barriers into glowing Neon.

ANIMALS (rigged)
  Import Individual/<Animal>.fbx -> you get a skinned MeshPart with Bones.
  (Dragons, golems, yeti, treant, mimic... are in the "Mythical" group - see ASSET_LIST.txt.)
  To add motion: select the rig, open the Animation Editor, then
  "..." > Import > From FBX Animation > pick Animations/<Animal>/<Animal>_Walk.fbx
  (or _Idle / _Fly / _Swim), then Publish to Roblox.
"""


UI_HOW_TO = """SIMUI GENERATOR 2 - GAME UI FOR ROBLOX - HOW TO USE
=====================================================

1. INSTALL THE PLUGIN
   Roblox Studio > Plugins tab > "Plugins Folder" > copy SimUI_Plugin.lua into it > restart Studio.
   A "SimUI" button appears in the Plugins tab. Click it to open the panel.
   (No plugin? Open SimUI_Plugin.lua, copy everything into View > Command Bar, press Enter: it builds
   the default simulator UI once.)

2. BUILD
   Type what your game is and press "Build UI":
       simulator              "Bank Heist" simulator        tycoon         cartoon obby
       anime fighting         scary horror                  scifi racing   medieval rpg
       clean minimal shooter  cartoon tower defense         glass roleplay
   You get StarterGui > SimUI: the HUD, every window, and a LocalScript that opens/closes the windows,
   animates the buttons, blurs the world behind windows, scales for phones and shows leaderstats.
   Press Play to try it.

3. CUSTOMISE (the panel)
   Game      where things go: simulator, tycoon, obby, fighting, horror, racing, rpg, shooter, tower, roleplay
   Style     how things look: Sim (the big simulator-game look), Studs, Bubbly, Cartoon, Horror, Anime,
             SciFi, Fantasy, Minimal, Pixel, Glass
   Colours   26 palettes      Font   19 Roblox fonts
   Shape, Corners, Outline, Shadow, Surface, Studs, Menu buttons, Windows, Motion, Icons, Text, Size
   Everything starts on "auto" (= the style's choice). Right-click a value to set it back to auto.
   Shuffle = a new variation of the same look. Your settings are remembered.

4. 3D ICONS (recommended, one upload)
   Upload Icons/Atlas_Icons.png (Asset Manager > Import, or Create > Decals), copy its asset ID
   (right click > Copy Asset ID), paste it into "Icon sheet ID" in the panel, Build again.
   All menu buttons, currencies, cards, boosts and hotbar slots then use the 3D icons.
   Without it the UI uses emoji and still works.

5. USE IT FROM YOUR SCRIPTS (LocalScript)
   local gui = game.Players.LocalPlayer.PlayerGui:WaitForChild("SimUI")
   gui.OpenWindow:Fire("Shop")          -- open any window by name (e.g. "Machine" from a ProximityPrompt)
   gui.CloseWindow:Fire()               -- close the open one
   gui.ShowTip:Fire("Grab the cash!")   -- tutorial bubble;  gui.ShowTip:Fire() hides it
   Currency labels follow leaderstats values with the same name (Cash, Gems, Coins, Gold).
   Buttons carry attributes you can hook up: Action ("Buy", "Gift", "Redeem", "Rebirth", "Make"...),
   Opens, Tab, Toggle, Slot, Day.

Previews/ shows what the plugin makes for every game type and every style.
"""


KITS_README = """STUDDED UI IMAGE KITS
====================

Ready-made sprite sheets in 17 colour themes (Kits/<Theme>/): studded buttons, square menu buttons,
headers, panels, cards, rarity slots, bars, toggles, mutation buttons, shine effects and 45 title words.
Use them by hand in Roblox (ImageLabel.Image = the uploaded sheet, ImageRectOffset / ImageRectSize from
SimUIKit.lua, ScaleType = Slice with the listed margins) or cut them up in Photopea / Photoshop.
Each kit's Preview.jpg shows the look; the labelled sprite sheets are in StudLowPoly_GameUI_SpriteSheets.zip.

Make a new kit from a prompt (Python 3 + Pillow):
    python3 Generator/generate.py "candy pink simulator"
    python3 Generator/generate.py '"My Game" neon obby' --pieces      (also every sprite as its own PNG)

The SimUI plugin (StudLowPoly_GameUI.zip) does not need these: it draws its UI with native Roblox
objects. It uses a kit's Stud_Tile.png for the Studs style if you install the kit's SimUIKit.lua as a
ModuleScript named SimUIKit in ReplicatedStorage with the tile's ID filled in.
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
    z.write(os.path.join(ROOT, "roblox", "BuildingSetup.lua"), os.path.join(arc, "BuildingSetup.lua"))
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
    for a in catalog[cat]:
        if a.get("preview_inside"):
            for key, suffix in (("preview", ""), ("preview_inside", "_Inside")):
                add_preview(z, os.path.join(ROOT, a[key]), os.path.join(arc, "Previews", f"{a['name']}{suffix}.jpg"))
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

    ui = os.path.join(ROOT, "ui")
    if os.path.isdir(os.path.join(ui, "kits")):
        with zipf("StudLowPoly_GameUI.zip") as z:
            arc = "StudLowPoly_GameUI"
            z.writestr(os.path.join(arc, "HOW_TO_USE_THE_UI.txt"), UI_HOW_TO)
            z.write(os.path.join(ROOT, "roblox", "SimUI_Plugin.lua"), os.path.join(arc, "SimUI_Plugin.lua"))
            for f in sorted(os.listdir(os.path.join(ui, "icons"))):
                if f.endswith((".png", ".lua")):
                    z.write(os.path.join(ui, "icons", f), os.path.join(arc, "Icons", f))
            add_dir(z, os.path.join(ui, "previews"), os.path.join(arc, "Previews"))

        with zipf("StudLowPoly_GameUI_ImageKits.zip") as z:
            arc = "StudLowPoly_GameUI_ImageKits"
            z.writestr(os.path.join(arc, "README.txt"), KITS_README)
            for base, _, files in os.walk(os.path.join(ui, "kits")):
                for f in sorted(files):
                    p = os.path.join(base, f)
                    if f == "Sheet.jpg":
                        continue
                    z.write(p, os.path.join(arc, "Kits", os.path.relpath(p, os.path.join(ui, "kits"))))
            for f in ("generate.py", "art.py", "themes.py"):
                z.write(os.path.join(ui, f), os.path.join(arc, "Generator", f))
            add_dir(z, os.path.join(ui, "fonts"), os.path.join(arc, "Generator", "fonts"))

        with zipf("StudLowPoly_GameUI_SpriteSheets.zip") as z:
            for t in sorted(os.listdir(os.path.join(ui, "kits"))):
                sh = os.path.join(ui, "kits", t, "Sheet.jpg")
                if os.path.exists(sh):
                    z.write(sh, os.path.join("StudLowPoly_GameUI_SpriteSheets", f"{t}_Sheet.jpg"))

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
