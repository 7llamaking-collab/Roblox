# Stud Low Poly Asset Library (Blender → Roblox)

**642 stud low-poly assets** for simulator games, modelled in **Blender** to match
`AnimalBundle_1.rbxl` and its screenshots: blocky chamfered shapes, square pixel eyes, flat
shading, a shared colour palette and the same square-tile **stud overlay** your animals use.
Every model is a real Blender mesh, ready for the Roblox 3D Importer.

**Just want the files?** Grab the ZIPs in [`downloads/`](downloads): one per category, a
Quick Start ZIP with the 10 all-in-one category FBX files, and the Blender source. Every ZIP
includes a `HOW_TO_IMPORT.txt`.

| Category | Count | What's inside |
|---|---:|---|
| [Food](previews/Food.png) | 60 | 24 fruits, 12 vegetables, 24 snacks & meals |
| [Tools](previews/Tools.png) | 90 | Pickaxe, Heavy Pickaxe, Drill, Axe, Shovel, Hammer, Hoe, Scythe × 8 tiers, 4 Legendary pickaxes (Flame, Frost, Crystal, Void), 22 everyday / farm / simulator tools |
| [Weapons](previews/Weapons.png) | 119 | Sword, Greatsword, Scimitar, Katana, Dagger, Mace, Halberd, BattleAxe, Spear, WarHammer, Bow, Staff, Shield × 8 tiers, 6 Legendary swords (Flame, Frost, Thunder, Shadow, Nature, Crystal), 9 specials |
| [Furniture](previews/Furniture.png) | 60 | seating, tables, bedroom, kitchen, bathroom, living room, lighting, decor, storage |
| [Nature](previews/Nature.png) | 58 | 14 trees (incl. fruit trees), bushes, flowers, plants, rocks, 9 ores, 7 crystal clusters, clouds |
| [Props](previews/Props.png) | 91 | 21 pet eggs + egg stand, 8 tiered chests, 8 tiered backpacks, currency, pickups, potions, pads & portal, awards, town & farm props |
| [Animals](previews/Animals.png) | 65 | **rigged & animated**: 44 pets, farm and wild animals, birds, sea creatures and bugs, plus 21 **mythical** creatures (6 dragons, 3 golems, Treant, Yeti, Mimic, Sea Serpent, Basilisk, Frost Wolf, Jackalope, Salamander, Fairy, Phoenix Chick, Baby Dragon, Slimes, Ghost) |
| [Vehicles](previews/Vehicles.png) | 27 | cars, sports car, police car, taxi, jeep, pickup, van, ambulance, ice-cream truck, delivery & fire trucks, buses, tractor, monster truck, golf cart, go-kart, motorcycle, scooter, boats, helicopter, airplane, hot-air balloon, rocket, train |
| [Buildings](previews/Buildings.png) | 45 | houses, apartments, skyscraper, shops (shop, cafe, pizza, toy store), gas station, police, fire station, hospital, school, bank, market / fruit / fish stalls, hot-dog & lemonade stands, ticket booth, kiosk, street signs, traffic light, billboard, bus stop, neon sign, barn, silo, windmill, lighthouse, castle tower & gate, fountain, bunker, barracks, watch tower, hangar, helipad, radar tower, guard post, command tent |
| [Military](previews/Military.png) | 27 | cannon, howitzer, mortar, machine-gun turret, anti-air gun, missile launcher, rocket launcher, catapult, ballista, trebuchet, tanks, armored car, military jeep & truck, attack helicopter, fighter jet, ammo, explosive barrel, sandbags, tank trap, landmine, grenade, barbed wire, flag |

The animals complement the 115 already in AnimalBundle (Pig, Sheep, Fox, Panda, Penguin,
Dolphin, Bee, Fire/Ice/Shadow/Crystal/Golden/Forest dragons, golems, and more), with no duplicates.

![Animals](previews/Animals.png)

## The style: "stud low poly"

Measured from `AnimalBundle_1.rbxl` and reproduced here:

* **Blocky low poly.** Like the bundle's lion, bear and elephant: chamfered boxes, square pixel eyes
  (black square with a white highlight), boxy muzzles and ears, square-section tails and limbs, and
  flat shading. Curved things use few sides (8 or fewer). Assets are 100–4,000 triangles.
* **Studs.** Each animal in the bundle carries 6 `Texture` objects (one per face,
  `rbxassetid://9527811247`, 9 studs per tile, Transparency 0.4). `roblox/StudStyle.lua` adds
  exactly that in one click. The previews use this library's own classic round-stud texture, rendered
  in Blender (`textures/Stud.png`, StudsPerTile = 2, i.e. studs every half stud). Because the studs are a separate overlay,
  you can leave them off for games that don't want the stud look.
* **One palette for everything.** All meshes are UV-mapped to one 512×512 atlas
  (`textures/StudPalette.png`, 278 named colours; see `textures/PaletteReference.png`).
  One texture upload colours the whole library. Matching metalness and roughness atlases make
  metals and gems shine when used as a `SurfaceAppearance`.
* **Tiers match your animals.** Wood → Stone → Iron → **Gold → Diamond → Emerald → Ruby → Rainbow**.
  The gem tiers use the same tints as the Gold, Diamond, Emerald, Ruby and Rainbow animal sets.
* **Real stud scale.** 1 Blender unit = 1 stud. A chair seat is ~1.8 studs high, a table ~3, a door
  ~7, pets 2–5 studs long, trees ~12–16 studs tall.

## Folder layout

```
downloads/                                  ready-made ZIPs to download (see top of this page)
exports/fbx/<Category>/<Asset>.fbx          one FBX per asset (palette texture embedded)
exports/packs/<Category>.fbx                whole category in one FBX -> imports as a Model of MeshParts
exports/animations/<Animal>/<Animal>_<Clip>.fbx   Idle / Walk (+ Fly or Swim) per animal
blend/<Category>.blend                      editable Blender files, every asset laid out on a grid
textures/                                   StudPalette (+ Metalness/Roughness), Stud.png overlay
previews/                                   contact sheets + a render of every asset
catalog.json                                every asset: size in studs, triangle count, files
roblox/StudStyle.lua                        optional one-click stud overlay for Studio
blender/                                    the Blender build scripts that made everything
```

## Importing into Roblox Studio

1. **File → Import 3D** (3D Importer) → pick an FBX from `exports/fbx/...`, or a whole
   category from `exports/packs/...`.
2. In the importer, keep the scale unit at **Studs**. Check the size against `catalog.json`
   (for example, `Apple` is about 1.3 × 1.3 × 1.6 studs). If it looks 100× off, change the file's
   scale unit in the import settings.
3. The embedded palette texture comes in automatically. For extra shine on metals and gems, upload
   the three `textures/StudPalette*.png` files and put them in a `SurfaceAppearance`
   (ColorMap / MetalnessMap / RoughnessMap). `StudStyle.lua` can do this for you.
4. **Studs:** select the imported models, paste `roblox/StudStyle.lua` into the Command Bar and
   press Enter. It adds the same 6-face stud overlay as AnimalBundle.
5. If a model faces backwards, set the importer's **World Forward** option (Blender models face −Y).

**Vehicles, machines & military** come in as a Model whose moving pieces are separate MeshParts
(`<Name>_WheelFL`, `_Rotor`, `_Propeller`, `_Turret`, `_Barrel`, `_Blades`, `_Dish`...) with their
origin at their own centre, ready for HingeConstraints or any vehicle chassis.

**Tools and weapons** stand upright with their pivot on the grip, where the hand holds them.
Put the MeshPart in a `Tool` as `Handle` and adjust `Tool.Grip`, for example with a grip editor plugin.

**Rigged animals.** Import `exports/fbx/Animals/<Animal>.fbx`: the 3D Importer creates a skinned
MeshPart with Bones and an AnimationController. To add motion, open the **Animation Editor**
on the rig → **⋯ → Import → From FBX Animation** → pick
`exports/animations/<Animal>/<Animal>_Walk.fbx` (or `_Idle`, `_Fly`, `_Swim`), then publish.
Bones are named `Root`, `Body`, `Head`, `LegFL`, `LegFR`, `LegBL`, `LegBR`, `Tail`, `WingL`,
`WingR`, `FinL`, `FinR`, `ArmL`, `ArmR`, `Tentacle1..8`. Each body part follows one bone
rigidly, which is the cleanest deformation for low poly.

## Editing in Blender

Open `blend/<Category>.blend` (Blender 4.2+). Each asset is its own object, grouped in
collections by sub-category (Fruit, Pickaxe, Seating...). Animals are armatures, and their
actions (`<Animal>_Idle`, `_Walk`, ...) are in the Action editor.

* **Recolour:** in the UV editor, move a face's UVs onto another palette cell, or edit
  `StudPalette.png`.
* **Re-export for Roblox:** File → Export → FBX with *Apply Scalings: FBX Units Scale*,
  *Forward: −Z*, *Up: Y*, *Apply Transform* on (off for armatures), *Path Mode: Copy* and embed
  textures.

## Making more assets (optional)

Everything was produced by Blender itself, driven by the scripts in `blender/`. To rebuild or add
assets, you need Blender, or `pip install bpy pillow numpy` (Python 3.11):

```bash
python3 blender/build.py                        # rebuild everything (~30 min on 4 cores)
python3 blender/build.py --style round          # softer, rounded low-poly variant of everything
python3 blender/package.py                      # re-make the download ZIPs
python3 blender/build.py --only Food,Props      # just some categories
python3 blender/build.py --names Apple --out /tmp/test   # quick test render
blender -b -P blender/build.py -- --only Tools  # same thing with a normal Blender install
```

A new asset is a few lines in `blender/assets/<category>.py`:

```python
@asset("Plum", CAT, sub="Fruit")
def plum(m):
    m.sphere(r=0.5, seg=14, rings=10, color="grape", loc=(0, 0, 0.5))
    stem_leaf(m, (0, 0, 0.98))
```

Tiered variants come for free: register the builder once for every tier in `studlib/tiers.py`.
