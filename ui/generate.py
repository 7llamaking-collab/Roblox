"""Studs-style UI kit generator - type a prompt, get a whole themed UI kit.

    python3 ui/generate.py "candy pink simulator"
    python3 ui/generate.py '"Pet Legends" galaxy simulator' --pieces
    python3 ui/generate.py --all                  # every preset theme (used for ui/kits/)
    python3 ui/generate.py --icons                # (re)process ui/icons_src -> ui/icons

Needs only Python 3 + Pillow (pip install pillow). No AI: the prompt is matched
against keywords (themes.py) - theme words (candy, lava, galaxy, spooky...), colour
words (pink, blue...), game type (simulator, tycoon, obby, fighting...) and an
optional "quoted title" for the logo.

Output (ui/kits/<Theme>/):
    Atlas_UI.png, Atlas_UI2.png   studded buttons, headers, panels, cards, slots, bars, tabs, toggles, FX
    Atlas_Titles.png              big stroked words (SHOP, PETS, REBIRTH...) + the logo if you gave a title
    SimUIKit.lua                  ModuleScript: theme colours + where every sprite is (for the Studio plugin)
    Preview.jpg                   what the HUD looks like with this kit
    Pieces/, Titles/              every sprite as its own PNG (with --pieces)
Shared icons (all themes): ui/icons/<Name>.png (256 px) and ui/icons/Atlas_Icons.png (+ Icons.lua).
"""
import argparse
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import art  # noqa: E402
from art import darker, lighter, mix, rgb, hexs  # noqa: E402
from themes import THEMES, theme_from_prompt  # noqa: E402

STD = {"Green": "#56D63B", "Blue": "#2FA4FF", "Orange": "#FF9A1F", "Red": "#F0443A", "Yellow": "#FFD21F",
       "Purple": "#A35CFF", "Pink": "#FF5FAE", "Cyan": "#27D8E8", "Gray": "#9AA3B2", "Gold": "#FFC21A"}
RARITY = {"Common": "#B8C0CC", "Uncommon": "#56D63B", "Rare": "#2FA4FF", "Epic": "#A35CFF", "Legendary": "#FFC21A",
          "Mythic": "#FF3B5C", "Secret": "#1C1C24"}
MUTATIONS = {"None": "checker_light", "Shocked": "electric", "Radioactive": "toxic", "Molten": "lava", "Icy": "ice",
             "Rainbow": "rainbow", "Galaxy": "galaxy", "Golden": "gold", "Diamond": "diamond"}
CARDS = {"Pink": ("#FF4FA0", "#FF3B5C"), "Orange": ("#FF9A1F", "#FFD21F"), "Purple": ("#A35CFF", "#E04FD8"),
         "Blue": ("#2F8BFF", "#27D8E8"), "Green": ("#3FBF3A", "#A6E23A"), "Gold": ("#FFB300", "#FFE14D")}
WORDS = ["SHOP", "PETS", "REBIRTH", "INVENTORY", "SETTINGS", "CODES", "DAILY REWARDS", "DAILY QUESTS!", "QUESTS",
         "UPGRADES", "TRADE", "EGGS", "BOOSTS", "INDEX", "TELEPORT", "GAMEPASSES", "STARTER PACK", "SELL", "BASE",
         "BUY", "EQUIP", "CLAIM", "FREE!", "NEW!", "BEST VALUE", "SALE", "MAX", "LOCKED", "LEVEL UP!", "VIP",
         "X2 LUCK", "X2 COINS", "REWARDS", "SPIN", "YOU WIN!", "HATCH", "AUTO", "CRAFT", "MUTATIONS", "FRIENDS",
         "STORE", "OPEN", "UNLOCK", "EVENT", "LIMITED!"]


# ----------------------------------------------------------------------------
# pieces
# ----------------------------------------------------------------------------
def pieces_for(theme):
    tp = {"Primary": theme["primary"], "Secondary": theme["secondary"], "Accent": theme["accent"]}
    studs = theme.get("studs", True)
    P = {}
    for name, c in list(tp.items()) + list(STD.items()):
        P[f"Button_{name}"] = lambda c=c: art.studded_box(200, 80, c, r=12, stroke=5, lip=7, stud_px=20, studs=studs,
                                                          stud_strength=0.8)
    P["Tab_Active"] = lambda: art.studded_box(160, 56, STD["Green"], r=10, stroke=4, lip=5, stud_px=16, studs=studs)
    P["Tab_Inactive"] = lambda: art.studded_box(160, 56, (160, 166, 178), r=10, stroke=4, lip=5, fill="checker",
                                                outline=(70, 74, 84), studs=False, gloss=0.15)
    for name, c in list(tp.items()) + [("Green", STD["Green"]), ("Blue", STD["Blue"]), ("Red", STD["Red"]),
                                        ("Purple", STD["Purple"]), ("Yellow", STD["Yellow"])]:
        P[f"Square_{name}"] = lambda c=c: art.studded_box(112, 112, c, r=14, stroke=5, lip=7, stud_px=18, studs=studs,
                                                          stud_strength=0.8)
    for name, c in (("Primary", theme["primary"]), ("Secondary", theme["secondary"]), ("Red", "#F0443A")):
        P[f"Header_{name}"] = lambda c=c: art.studded_box(256, 72, c, r=10, stroke=5, lip=5, stud_px=18, studs=studs)
    P["Panel"] = lambda: art.panel_body(192, 192, color=darker(theme["panel2"], 0.35), alpha=222,
                                        outline=theme["outline"], studs=studs)
    P["PanelLight"] = lambda: art.studded_box(192, 192, theme["panel"], r=12, stroke=5, lip=0, grad=0.1,
                                              outline=theme["outline"], stud_strength=0.6, gloss=0.08, studs=studs)
    P["PanelInner"] = lambda: art.slot_box(160, 160, rim=darker(theme["panel2"], 0.5), body=darker(theme["panel2"], 0.2))
    for name, (a, b) in CARDS.items():
        P[f"Card_{name}"] = lambda a=a, b=b: art.studded_box(192, 144, a, r=12, stroke=5, lip=5, gradient_to=b,
                                                             stud_px=18, studs=studs, gloss=0.2)
    P["Slot"] = lambda: art.slot_box(96, 96)
    for name, c in RARITY.items():
        P[f"Slot_{name}"] = lambda c=c: art.slot_box(96, 96, rim=c, body=(34, 38, 52), stroke=5, glow=c)
    P["Bar_Back"] = lambda: art.bar_box(256, 40, None, back=True)
    for name in ("Green", "Blue", "Gold", "Red", "Purple"):
        P[f"Bar_Fill_{name}"] = lambda c=STD[name]: art.bar_box(256, 40, c)
    P["Pill"] = lambda: art.panel_body(220, 64, color=(18, 20, 32), alpha=170, r=30, stroke=4, outline=(6, 8, 14),
                                       studs=False)
    P["Toggle_On"] = lambda: art.toggle_box(True)
    P["Toggle_Off"] = lambda: art.toggle_box(False)
    P["Close"] = lambda: art.close_button(72)
    P["Plus"] = lambda: art.plus_button(56)
    P["Badge"] = lambda: art.badge(48)
    for name, fill in MUTATIONS.items():
        if fill == "checker_light":
            P[f"Mutation_{name}"] = lambda: art.studded_box(200, 64, (225, 228, 235), r=10, stroke=4, lip=5,
                                                            fill="checker", outline=(90, 94, 104), studs=False)
        else:
            P[f"Mutation_{name}"] = lambda f=fill: art.studded_box(200, 64, (200, 200, 200), r=10, stroke=4, lip=5,
                                                                   fill=f, outline=art.FILL_OUTLINE[f], stud_px=16,
                                                                   stud_strength=0.6, studs=studs)
    P["FX_Sunburst"] = lambda: art.sunburst(256, lighter(theme["accent"], 0.5))
    P["FX_Glow"] = lambda: art.glow(256, lighter(theme["accent"], 0.3))
    P["FX_Sparkle"] = lambda: art.sparkle(64)
    return P


def titles_for(theme, title=None):
    font = theme.get("font", "FredokaBold")
    out = {}
    for w in WORDS:
        out[w] = art.text_image(w, 58, stroke=theme["outline"], gradient=theme["title"], font=font, extrude=3, gloss=0.3)
    if title:
        out["LOGO"] = art.text_image(title.upper() if font == "LuckiestGuy" else title, 120, stroke=theme["outline"],
                                     gradient=theme["title"], font=font, extrude=8, gloss=0.35, stroke_w=16)
    return out


# ----------------------------------------------------------------------------
# icons (shared)
# ----------------------------------------------------------------------------
TILT = {"Sword", "FishingRod"}


def build_icons(src=os.path.join(HERE, "icons_src"), dst=os.path.join(HERE, "icons")):
    os.makedirs(dst, exist_ok=True)
    names = sorted(f[:-4] for f in os.listdir(src) if f.endswith(".png"))
    cells = []
    for n in names:
        raw = Image.open(os.path.join(src, n + ".png")).convert("RGBA")
        bb = raw.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
        if bb and n in TILT:
            # long thin items read as "!" when small: tilt them like inventory icons
            raw = raw.crop(bb).rotate(-45, resample=Image.BICUBIC, expand=True)
        ic = art.process_icon(raw, 256, outline=(16, 18, 30))
        ic.save(os.path.join(dst, n + ".png"), optimize=True)
        cells.append((n, ic.resize((112, 112), Image.LANCZOS)))
    per = 9
    atlas = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    rects = {}
    for i, (n, im) in enumerate(cells[:per * per]):
        x, y = 2 + (i % per) * 113, 2 + (i // per) * 113
        atlas.paste(im, (x, y), im)
        rects[n] = (x, y, 112, 112)
    atlas.save(os.path.join(dst, "Atlas_Icons.png"), optimize=True)
    lua = ["-- Icon sprite sheet (generated by ui/generate.py). Upload Atlas_Icons.png, paste its id below.",
           "return {", '\tImage = "rbxassetid://0",', "\tSize = 1024,", "\tIcons = {"]
    for n, (x, y, w, h) in rects.items():
        lua.append(f"\t\t{n} = {{{x}, {y}, {w}, {h}}},")
    lua += ["\t},", "}", ""]
    open(os.path.join(dst, "Icons.lua"), "w").write("\n".join(lua))
    json.dump(rects, open(os.path.join(dst, "icons.json"), "w"), indent=0)
    print(f"icons: {len(cells)} -> {dst}")
    return rects


def load_icons():
    d = os.path.join(HERE, "icons")
    out = {}
    if os.path.isdir(d):
        for f in os.listdir(d):
            if f.endswith(".png") and not f.startswith("Atlas"):
                out[f[:-4]] = os.path.join(d, f)
    return out


# ----------------------------------------------------------------------------
# kit
# ----------------------------------------------------------------------------
def lua_color(c):
    r, g, b = rgb(c)
    return f"Color3.fromRGB({r}, {g}, {b})"


def write_lua(path, theme, game, title, ui_rects, n_ui_pages, title_rects, n_title_pages):
    L = [f'-- SimUIKit for theme "{theme["name"]}" (generated by ui/generate.py - do not edit the sprite tables).',
         "-- 1. Upload the Atlas_*.png images (Asset Manager > Bulk Import, or Create > Decals) and paste the ids.",
         "-- 2. Put this ModuleScript in ReplicatedStorage (name it SimUIKit), then use the SimUI plugin.",
         "local Kit = {}",
         "",
         "Kit.Theme = {",
         f'\tName = "{theme["name"]}",',
         f'\tGameType = "{game}",',
         f'\tTitle = {json.dumps(title or "")},',
         f'\tFont = "{"LuckiestGuy" if theme.get("font") == "LuckiestGuy" else "FredokaOne"}",']
    for key in ("primary", "secondary", "accent", "panel", "panel2", "inner", "outline"):
        L.append(f"\t{key.title()} = {lua_color(theme[key])},")
    L.append(f"\tTitleTop = {lua_color(theme['title'][0])},")
    L.append(f"\tTitleBottom = {lua_color(theme['title'][1])},")
    for name, c in STD.items():
        L.append(f"\t{name} = {lua_color(c)},")
    L += ["}", "", "-- paste your uploaded image ids here"]
    L.append("Kit.Images = {")
    for i in range(n_ui_pages):
        L.append(f'\tUI{"" if i == 0 else i + 1} = "rbxassetid://0",')
    for i in range(n_title_pages):
        L.append(f'\tTitles{"" if i == 0 else i + 1} = "rbxassetid://0",')
    L.append('\tIcons = "rbxassetid://0",')
    L.append('\tStud = "rbxassetid://0", -- optional: Stud_Tile.png, tiled over native frames')
    L.append("}")
    L += ["", "-- name = {image, x, y, width, height, sliceLeft, sliceTop, sliceRight, sliceBottom}"]
    L.append("Kit.UI = {")
    for n, (pi, x, y, w, h, sl) in sorted(ui_rects.items()):
        img = f'"UI{"" if pi == 0 else pi + 1}"'
        s = f", {sl[0]}, {sl[1]}, {sl[2]}, {sl[3]}" if sl else ""
        L.append(f"\t{n} = {{{img}, {x}, {y}, {w}, {h}{s}}},")
    L.append("}")
    L.append("Kit.Titles = {")
    for n, (pi, x, y, w, h, _) in sorted(title_rects.items()):
        img = f'"Titles{"" if pi == 0 else pi + 1}"'
        L.append(f'\t["{n}"] = {{{img}, {x}, {y}, {w}, {h}}},')
    L.append("}")
    icons = json.load(open(os.path.join(HERE, "icons", "icons.json"))) if os.path.exists(
        os.path.join(HERE, "icons", "icons.json")) else {}
    L.append("Kit.Icons = {")
    for n, (x, y, w, h) in sorted(icons.items()):
        L.append(f'\t{n} = {{"Icons", {x}, {y}, {w}, {h}}},')
    L += ["}", "", "return Kit", ""]
    open(path, "w").write("\n".join(L))


def slice9(img, sl, w, h):
    """Draw a 9-slice sprite at a new size (for the preview)."""
    l, t, r, b = sl
    W, H = img.size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    xs = [(0, l, 0, l), (l, W - r, l, w - r), (W - r, W, w - r, w)]
    ys = [(0, t, 0, t), (t, H - b, t, h - b), (H - b, H, h - b, h)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            if sx1 <= sx0 or sy1 <= sy0 or dx1 <= dx0 or dy1 <= dy0:
                continue
            part = img.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.LANCZOS)
            out.paste(part, (dx0, dy0), part)
    return out


def preview(theme, pieces, icons, path, title=None, W=1280, H=720):
    """Mock HUD in the reference layout: top tabs, side buttons, shop window, hotbar, currencies, boosts."""
    bg = art.vgrad(W, H, theme["bg"][0], theme["bg"][1]).convert("RGBA")
    bg.alpha_composite(art.stud_overlay(W, H, 40, 0.5))
    bg = bg.filter(ImageFilter.GaussianBlur(3))
    font = theme.get("font", "FredokaBold")
    P = {k: v for k, v in pieces.items()}

    def put(name, x, y, w=None, h=None):
        im, sl = P[name]
        if w and h and sl:
            im = slice9(im, sl, w, h)
        elif w and h:
            im = im.resize((w, h), Image.LANCZOS)
        bg.alpha_composite(im, (int(x), int(y)))
        return im.size

    def label(s, x, y, size=28, fill=(255, 255, 255), stroke=(15, 15, 25), center=True, grad=None):
        t = art.text_image(s, size, fill=fill, stroke=stroke, font=font, gradient=grad, shadow=True)
        bg.alpha_composite(t, (int(x - t.width / 2) if center else int(x), int(y - t.height / 2)))
        return t.size

    def icon(name, x, y, s):
        p = icons.get(name)
        if not p:
            return
        im = Image.open(p).convert("RGBA").resize((s, s), Image.LANCZOS)
        bg.alpha_composite(im, (int(x - s / 2), int(y - s / 2)))

    # top tabs
    for i, (nm, txt) in enumerate((("Button_Green", "Sell"), ("Button_Blue", "Base"), ("Button_Orange", "Upgrades"))):
        x = W / 2 - 330 + i * 230
        put(nm, x, 22, 210, 72)
        label(txt, x + 105, 52, 34)
    if title:
        label(title, W / 2, 125, 40, grad=theme["title"], stroke=theme["outline"])
    # left side buttons
    for i, (nm, ic, txt) in enumerate((("Square_Red", "Shop", "Shop"), ("Square_Green", "Rebirth", "Rebirth"),
                                       ("Square_Primary", "Pet", "Pets"), ("Square_Blue", "Settings", "Settings"))):
        y = 130 + i * 108
        put(nm, 30, y, 96, 96)
        icon(ic, 78, y + 44, 84)
        label(txt, 78, y + 92, 24)
    # shop window
    wx, wy, ww, wh = W / 2 - 250, 150, 500, 410
    put("Panel", wx, wy + 50, ww, wh - 50)
    put("Header_Primary", wx, wy, ww - 70, 66)
    icon("Gift", wx + 40, wy + 30, 54)
    label("Store", wx + 75, wy + 32, 34, center=False)
    put("Close", wx + ww - 68, wy, 66, 66)
    icon("Coin", wx + 250, wy + 31, 36)
    label("633,637", wx + 272, wy + 32, 22, center=False)
    cards = (("Card_Pink", "Heart", "Apple"), ("Card_Orange", "Energy", "Banana"), ("Card_Orange", "Chest", "Cookie"),
             ("Card_Purple", "Gem", "Berries"))
    for i, (cn, ic, nm) in enumerate(cards):
        cx = wx + 14 + (i % 2) * 240
        cy = wy + 76 + (i // 2) * 138
        put(cn, cx, cy, 232, 130)
        label(nm, cx + 12, cy + 24, 26, center=False)
        icon(ic, cx + 180, cy + 46, 78)
        icon("Coin", cx + 24, cy + 62, 30)
        label("3412", cx + 42, cy + 62, 20, center=False)
        label("+500 HP", cx + 12, cy + 108, 16, center=False)
        put("Button_Green", cx + 118, cy + 86, 104, 36)
        label("Buy", cx + 170, cy + 102, 22)
    for i, (nm, txt) in enumerate((("Tab_Active", "Food"), ("Tab_Inactive", "Swords"), ("Tab_Inactive", "Boosts"))):
        put(nm, wx + 10 + i * 162, wy + wh - 58, 156, 46)
        label(txt, wx + 88 + i * 162, wy + wh - 37, 22)
    # hotbar
    for i in range(9):
        x = W / 2 - 9 * 30 + i * 60
        put("Slot" if i != 2 else "Slot_Legendary", x, H - 104, 56, 56)
        icon("Sword", x + 28, H - 78, 44)
        label(str(i + 1), x + 10, H - 96, 14)
    put("Bar_Back", W / 2 - 300, H - 36, 600, 22)
    put("Bar_Fill_Green", W / 2 - 300, H - 36, 340, 22)
    label("56%", W / 2 - 320, H - 25, 18)
    # currencies
    put("Pill", 150, H - 128, 190, 46)
    icon("Gem", 172, H - 105, 48)
    label("96,597", 200, H - 105, 28, center=False)
    label("$2,482,102", 150, H - 58, 28, fill=(110, 230, 80), stroke=(20, 50, 10), center=False)
    put("Plus", 322, H - 76, 34, 34)
    # right side
    put("Square_Blue", W - 130, 150, 96, 96)
    icon("Index", W - 82, 194, 84)
    label("Index", W - 82, 242, 24)
    icon("Gift", W - 82, 320, 90)
    label("Starter Pack", W - 82, 372, 20, fill=(120, 220, 255))
    label("Daily Quests!", W - 150, 420, 28, grad=("#FFF3A0", "#FFB300"), stroke=(70, 40, 0))
    for i in range(2):
        put("Bar_Back", W - 250, 450 + i * 46, 200, 24)
        put("Bar_Fill_Gold", W - 250, 450 + i * 46, 120 - i * 50, 24)
    icon("Luck", W - 82, 575, 70)
    label("x2 Luck", W - 82, 530, 24, fill=(160, 255, 90))
    label("00:00", W - 82, 612, 20, fill=(255, 90, 90))
    for i, (sq, ic) in enumerate((("Square_Yellow", "PotionYellow"), ("Square_Green", "PotionGreen"),
                                  ("Square_Primary", "PotionBlue"), ("Square_Purple", "PotionRed"))):
        x = W - 300 + i * 70
        put(sq, x, H - 88, 62, 62)
        icon(ic, x + 31, H - 60, 48)
        label("59m", x + 31, H - 30, 16)
    bg.convert("RGB").save(path, quality=90)


def sheet(P, T, path, theme):
    """Labelled overview of every sprite in the kit."""
    from PIL import ImageFont
    items = [(k, im) for k, (im, _) in P.items()] + [(k, im) for k, im in T.items()]
    cols, cw, ch = 6, 260, 170
    rows = (len(items) + cols - 1) // cols
    W, H = cols * cw, rows * ch + 60
    bg = art.vgrad(W, H, darker(theme["panel2"], 0.55), darker(theme["panel2"], 0.75)).convert("RGBA")
    d = ImageDraw.Draw(bg)
    ft = ImageFont.truetype(art.font_path("FredokaBold"), 18)
    head = ImageFont.truetype(art.font_path("FredokaBold"), 30)
    d.text((16, 12), f"SimUI kit - {theme['name']}  ({len(P)} sprites, {len(T)} titles)", font=head, fill=(255, 255, 255))
    for i, (k, im) in enumerate(items):
        x, y = (i % cols) * cw, 60 + (i // cols) * ch
        sc = min((cw - 20) / im.width, (ch - 40) / im.height, 1.0)
        t = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
        bg.alpha_composite(t, (int(x + (cw - t.width) / 2), int(y + 6 + (ch - 40 - t.height) / 2)))
        d.text((x + cw / 2, y + ch - 20), k, font=ft, fill=(230, 235, 245), anchor="mm")
    bg.convert("RGB").save(path, quality=88)


def make_kit(theme, game, title, out_root, pieces_dir=False):
    name = theme["name"]
    out = os.path.join(out_root, name)
    os.makedirs(out, exist_ok=True)
    P = {k: fn() for k, fn in pieces_for(theme).items()}
    pages, rects = art.pack([(k, im, sl) for k, (im, sl) in P.items()], 1024, 4)
    for i, pg in enumerate(pages):
        pg.save(os.path.join(out, f"Atlas_UI{'' if i == 0 else i + 1}.png"), optimize=True)
    T = titles_for(theme, title)
    tpages, trects = art.pack([(k, im, None) for k, im in T.items()], 1024, 4)
    for i, pg in enumerate(tpages):
        pg.save(os.path.join(out, f"Atlas_Titles{'' if i == 0 else i + 1}.png"), optimize=True)
    write_lua(os.path.join(out, "SimUIKit.lua"), theme, game, title, rects, len(pages), trects, len(tpages))
    art.stud_overlay(64, 64, 32, 1.0).save(os.path.join(out, "Stud_Tile.png"))
    preview(theme, P, load_icons(), os.path.join(out, "Preview.jpg"), title)
    sheet(P, T, os.path.join(out, "Sheet.jpg"), theme)
    if pieces_dir:
        pd = os.path.join(out, "Pieces")
        os.makedirs(pd, exist_ok=True)
        for k, (im, sl) in P.items():
            im.save(os.path.join(pd, k + ".png"), optimize=True)
        td = os.path.join(out, "Titles")
        os.makedirs(td, exist_ok=True)
        for k, im in T.items():
            im.save(os.path.join(td, k.replace(" ", "_").replace("!", "") + ".png"), optimize=True)
    print(f"kit {name}: {len(P)} sprites on {len(pages)} UI page(s), {len(T)} titles on {len(tpages)} page(s) -> {out}")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prompt", nargs="?", default="classic simulator")
    ap.add_argument("--title", default=None, help="logo text (or put it in quotes inside the prompt)")
    ap.add_argument("--out", default=os.path.join(HERE, "kits"))
    ap.add_argument("--pieces", action="store_true", help="also save every sprite as its own PNG")
    ap.add_argument("--all", action="store_true", help="generate every preset theme")
    ap.add_argument("--icons", action="store_true", help="process ui/icons_src into ui/icons first")
    args = ap.parse_args()
    if args.icons or not os.path.exists(os.path.join(HERE, "icons", "icons.json")):
        if os.path.isdir(os.path.join(HERE, "icons_src")):
            build_icons()
    if args.all:
        for name in THEMES:
            theme, _, _ = theme_from_prompt(name.lower())
            make_kit(theme, "simulator", None, args.out, args.pieces)
        return
    theme, title, game = theme_from_prompt(args.prompt)
    make_kit(theme, game, args.title or title, args.out, args.pieces)


if __name__ == "__main__":
    main()
