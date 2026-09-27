"""Shared colour palette for every asset.

All meshes are UV-mapped onto one small palette atlas (``StudPalette.png``) so a
single texture upload colours the whole library in Roblox. Each named colour is
one flat cell of the atlas; matching metalness / roughness atlases give metals
and gems their shine when used as a SurfaceAppearance.

Colours are sRGB hex. ``metal`` is 0..1, ``rough`` is 0..1.
"""
import os

CELL = 16          # pixels per palette cell
GRID = 32          # cells per row / column -> 512 x 512 atlas

# name: (hex, metal, rough)
_C = {}


def _add(group, rough=0.6, metal=0.0, **cols):
    for name, hx in cols.items():
        _C[name] = (hx, metal, rough)


# --- neutrals -------------------------------------------------------------
_add("neutral", rough=0.55,
     white="F4F4F2", offwhite="E9E3D6", lightgray="C9C9CE", gray="9A9AA2",
     darkgray="62626B", charcoal="3B3B42", black="1E1E23", eye_black="141417",
     eye_white="FFFFFF", paper="F7F2E4", ceramic="F2F0EA")
# --- wood -----------------------------------------------------------------
_add("wood", rough=0.8,
     wood_pale="EACB93", wood_light="DDA467", wood="C88744", wood_mid="A96C37",
     wood_dark="7C4B27", wood_deep="5A3419", bark="6E4A2F", bark_dark="4E3220",
     plank_red="A8472E", plank_gray="8E8578")
# --- stone / earth ----------------------------------------------------------
_add("stone", rough=0.9,
     stone_light="BDBDB5", stone="8F8F89", stone_dark="68685F", stone_deep="4A4A44",
     sandstone="DCC38D", sand="EFD9A2", dirt="8B5F3B", dirt_dark="694629",
     clay="C9744A", brick="B85A3D", brick_dark="8D3C28", snow="FBFDFF",
     coal="2E2E33", obsidian="2A2138")
# --- metals -----------------------------------------------------------------
_add("metal", rough=0.32, metal=1.0,
     iron="D2D6DC", iron_dark="8F97A1", steel="B4BDC8", silver="EDEFF3",
     gold="FFC83D", gold_dark="D8921A", gold_light="FFE58A", copper="DD8752",
     bronze="BC7736", chrome="F2F4F7")
# --- gems (glossy, non metal) -------------------------------------------------
_add("gem", rough=0.12,
     diamond="6FE6F7", diamond_light="C8F7FF", diamond_dark="2BA7D8",
     emerald="3FE07C", emerald_light="A6F5C3", emerald_dark="14A04A",
     ruby="F4455C", ruby_light="FFA3AE", ruby_dark="B3143C",
     amethyst="AE72F7", amethyst_dark="7134C9", sapphire="3E6DF2",
     topaz="FFB22E", crystal_pink="FF8AD8", ice="D2F4FF", glass="B3E6F7")
# --- rainbow (for Rainbow tier) ---------------------------------------------
_add("rainbow", rough=0.25,
     rb_red="FF3B3B", rb_orange="FF9A2E", rb_yellow="FFE83B", rb_green="4BE35A",
     rb_cyan="3BD8FF", rb_blue="4A6BFF", rb_purple="B04BFF", rb_pink="FF5FC8")
# --- plants -----------------------------------------------------------------
_add("plant", rough=0.7,
     leaf_light="9BE04F", leaf="62C23C", leaf_dark="3D922C", leaf_deep="2B6C24",
     grass="72CD41", moss="708F3B", pine="2F7B4B", pine_dark="1F5B39",
     autumn_orange="EB8A2C", autumn_red="D4472F", autumn_yellow="F2C43A",
     blossom="FF9EC6", blossom_light="FFD1E4", cactus="4FA84A", cactus_dark="357A35",
     lily="5DBB63", vine="4E9A32")
# --- fruit & veg (slightly glossy) -------------------------------------------
_add("fruit", rough=0.4,
     apple_red="E53530", apple_red_dark="B51F22", apple_green="9ED63B",
     banana="FFE24E", banana_dark="D8B42A", orange="FF9B1F", orange_dark="E07A10",
     lemon="FFF250", lime="8FE03A", strawberry="F2324B", strawberry_seed="FFE7A0",
     grape="8B40C8", grape_dark="5F2697", blueberry="4050B5", cherry="CB1230",
     peach="FFB48A", peach_dark="F2866A", watermelon="FF4F60", melon_rind="3BA93B",
     melon_dark="1F6E29", melon_pale="D8F2B0", pineapple="EDBB3B",
     pineapple_dark="B98819", coconut="7B4F2B", coconut_meat="F6F1E7", mango="FFB33F",
     mango_red="F2653A", pear="CADC4B", pumpkin="F2801B", pumpkin_dark="C9600E",
     carrot="FF8B20", corn="FFD93B", corn_husk="B7D65A", tomato="E83A2F",
     eggplant="6C2F90", potato="CA9B5C", potato_dark="A67B42", onion="D98FC0",
     pepper_green="4DB33A", pepper_red="E3332B", broccoli="4AA83F", cabbage="A8DB7A",
     radish="E8456B", kiwi_brown="8C6B3A", kiwi_green="8FCF3A", avocado_dark="355E26",
     avocado="C3E07A", seed_brown="6B3E1F", dragonfruit="F2468E")
# --- food ---------------------------------------------------------------------
_add("food", rough=0.6,
     bread="DDA35B", bread_crust="AD672C", cheese="FFD54B", cheese_dark="E8B42A",
     chocolate="6C3B22", chocolate_dark="4A2616", frosting_pink="FF92C2",
     frosting_white="FFF6EE", cream="FFF1D2", caramel="D98B32", meat="A9472F",
     meat_light="D97A5B", bacon="C9533F", lettuce="7FDA58", sauce_red="D93A2A",
     candy_blue="52B9FF", candy_pink="FF6FB5", candy_green="6AE36A", egg_yolk="FFC21F",
     milk="FAFAFF", honey="F5A623", jam="C21A3F", sprinkle_blue="4FA3FF",
     sprinkle_yellow="FFE14F", cone="E0A45A", cone_dark="B77A34", icecream_mint="A8F0CF",
     icecream_straw="FFB8CF", icecream_van="FFF0C4", cookie="D69A52",
     cookie_chip="4A2A18", donut="E3A55B", pizza_sauce="C8361F", pepperoni="B32C22",
     fish_orange="FF8C4A", sushi_rice="FAF7F0", nori="1F3A2A")
# --- fur / skin / animal ------------------------------------------------------
_add("fur", rough=0.85,
     fur_white="F3F0EA", fur_cream="EDDBBA", fur_tan="D8A96C", fur_orange="E9832F",
     fur_ginger="D2692A", fur_brown="9B6337", fur_darkbrown="5F3B21",
     fur_gray="9E9C9A", fur_lightgray="C9C7C4", fur_darkgray="5B5957",
     fur_black="2F2C2B", fur_red="C9552A", fur_gold="E8B84A",
     pink_nose="F29BAF", pink_skin="F6B9B1", pink_inner="F7A7B8",
     pig="F8A9B9", pig_dark="E3819A", beak="FFA52F", beak_yellow="FFD43F",
     flamingo="F68BB1", hippo="8D90AA", hippo_belly="C8A8B8", rhino="9C9B97",
     elephant="9EA3AE", camel="D4A96A", deer="B37B49", moose="6E4B2E",
     antler="E9D7B0", horn="EDE3CC", hoof="4A3A30", bee="FFCD20",
     ladybug="E62B2B", octopus="EC6B8B", octopus_dark="C94468", dolphin="80A9CA",
     dolphin_belly="DCE8F0", axolotl="F8B3C9", axolotl_gill="E9587C",
     penguin_black="2A2D36", tongue="E8587A", scale_green="5DBB4A",
     scale_dark="3A8A34", shell_green="4E8A3A", shell_brown="8A6A3A",
     feather_blue="3A86E8", feather_teal="21B3A5", feather_green="3CBF4A",
     feather_purple="7A4FD6", butterfly_blue="4AA8FF", butterfly_orange="FF8A1F",
     jelly="B98CFF", slime="7CE85A")
# --- fabric / furniture -------------------------------------------------------
_add("fabric", rough=0.92,
     fabric_red="D94646", fabric_blue="4C80DA", fabric_navy="2F4B90",
     fabric_green="50A95F", fabric_yellow="F5C644", fabric_purple="8B5DD2",
     fabric_pink="F28EB3", fabric_teal="30B4A7", fabric_orange="F08B3B",
     fabric_gray="8D8D95", fabric_cream="EEE4D0", fabric_brown="8B5B3B",
     fabric_white="F7F5F0", rug_red="B83A3A", rug_blue="3A5FB8")
# --- plastics / misc --------------------------------------------------------------
_add("plastic", rough=0.45,
     plastic_red="E63B3B", plastic_blue="3B7BE6", plastic_green="3BBF55",
     plastic_yellow="FFD23B", plastic_orange="FF8C2E", plastic_purple="9A52E6",
     plastic_pink="FF74B5", plastic_white="F5F6F8", plastic_black="2B2C31",
     rubber="2A2A2F", screen="1D2837", screen_glow="4FD4FF", water="4FB4F2",
     water_dark="2A86C9", lava="FF5B1F", fire="FFB31F", fire_light="FFE87A",
     glow="FFF37A", potion_red="FF3B5C", potion_blue="3B8BFF", potion_green="5BEA4A",
     potion_purple="B84BFF", potion_yellow="FFE23B", cork="C89B63",
     roof_red="C4403F", roof_blue="3F63C4", roof_green="3F9A52", tile_white="EDEFF2",
     tile_blue="7FB8E8", marble="EFEDEA", marble_dark="C9C4BD", leather="8A4F2A",
     leather_dark="5E321A", rope="CFAF74", string="EFEFEF", neon_pink="FF4FD8",
     neon_green="4FFF7A", neon_blue="4FC8FF")

NAMES = list(_C.keys())
assert len(NAMES) <= GRID * GRID, len(NAMES)
INDEX = {n: i for i, n in enumerate(NAMES)}


def srgb(name):
    hx = _C[name][0]
    return tuple(int(hx[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def linear(name):
    def c(x):
        return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4
    return tuple(c(x) for x in srgb(name))


def uv(name):
    """UV coordinate at the centre of a colour's palette cell."""
    i = INDEX[name]
    col, row = i % GRID, i // GRID
    return ((col + 0.5) / GRID, 1.0 - (row + 0.5) / GRID)


def cell_of_uv(u, v):
    col = min(GRID - 1, max(0, int(u * GRID)))
    row = min(GRID - 1, max(0, int((1.0 - v) * GRID)))
    return row * GRID + col


def write_atlases(out_dir):
    """Write colour / metalness / roughness atlases as PNG. Returns paths."""
    import numpy as np
    from PIL import Image
    size = CELL * GRID
    color = np.zeros((size, size, 4), np.uint8)
    color[..., 3] = 255
    metal = np.zeros((size, size), np.uint8)
    rough = np.full((size, size), 200, np.uint8)
    # unused cells: magenta so mistakes are obvious
    color[..., 0] = 255; color[..., 2] = 255
    for name, i in INDEX.items():
        col, row = i % GRID, i // GRID
        ys, xs = slice(row * CELL, (row + 1) * CELL), slice(col * CELL, (col + 1) * CELL)
        hx, m, r = _C[name]
        color[ys, xs, :3] = [int(hx[k:k + 2], 16) for k in (0, 2, 4)]
        metal[ys, xs] = int(m * 255)
        rough[ys, xs] = int(r * 255)
    os.makedirs(out_dir, exist_ok=True)
    paths = {}
    for key, arr in (("color", color), ("metal", metal), ("rough", rough)):
        p = os.path.join(out_dir, {"color": "StudPalette.png", "metal": "StudPalette_Metalness.png",
                                   "rough": "StudPalette_Roughness.png"}[key])
        Image.fromarray(arr).save(p)
        paths[key] = p
    return paths


def swatch_sheet(path):
    """Human-readable palette reference with names."""
    from PIL import Image, ImageDraw
    cols = 8
    w, h = 190, 26
    rows = (len(NAMES) + cols - 1) // cols
    img = Image.new("RGB", (cols * w, rows * h), (30, 30, 34))
    d = ImageDraw.Draw(img)
    for i, n in enumerate(NAMES):
        x, y = (i % cols) * w, (i // cols) * h
        c = tuple(int(v * 255) for v in srgb(n))
        d.rectangle([x + 2, y + 2, x + 24, y + h - 3], fill=c)
        d.text((x + 30, y + 7), n, fill=(230, 230, 230))
    img.save(path)
