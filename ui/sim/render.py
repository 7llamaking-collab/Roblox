"""Draw a Roblox GUI instance tree (JSON from roblox_shim.luau) to an image, the way Studio lays it out.

Covers what the SimUI plugin uses: UDim2 size/position/anchor, UIScale, UIPadding, UIListLayout,
UIGridLayout, UIAspectRatioConstraint, ScrollingFrame/ClipsDescendants clipping, Rotation, ZIndex
(sibling mode), UICorner, UIStroke (border and text), UIGradient (colour multiply + transparency),
TextLabel/TextButton/TextBox text with RichText colours, TextScaled, wrapping and colour emoji.
It is a preview tool, not a pixel-exact copy of the Roblox renderer.
"""
import math
import os
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
FONT_DIR = os.path.join(HERE, ".fonts")
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

GUI = {"Frame", "TextLabel", "TextButton", "TextBox", "ImageLabel", "ImageButton", "ScrollingFrame", "CanvasGroup"}
TEXT = {"TextLabel", "TextButton", "TextBox"}
WEIGHTS = {"Thin": 100, "ExtraLight": 200, "Light": 300, "Regular": 400, "Medium": 500, "SemiBold": 600,
           "Bold": 700, "ExtraBold": 800, "Heavy": 900}

# Roblox font family -> fontsource file stem (weights are picked by nearest match)
FAMILIES = {
    "GothamSSm": "montserrat", "Montserrat": "montserrat", "BuilderSans": "montserrat", "Bangers": "bangers",
    "Creepster": "creepster", "SpecialElite": "special-elite", "Michroma": "michroma", "Sarpanch": "sarpanch",
    "Jura": "jura", "Oswald": "oswald", "Fondamento": "fondamento", "Merriweather": "merriweather",
    "GrenzeGotisch": "grenze-gotisch", "PressStart2P": "press-start-2p", "RobotoMono": "roboto-mono",
    "Inconsolata": "roboto-mono", "Nunito": "nunito", "DenkOne": "denk-one", "PermanentMarker": "permanent-marker",
    "TitilliumWeb": "titillium-web", "SourceSansPro": "nunito", "Arial": "montserrat", "Arimo": "montserrat",
    "Roboto": "montserrat", "LegacyArial": "montserrat",
}
FIXED = {"FredokaOne": os.path.join(ROOT, "ui", "fonts", "FredokaBold.woff"),
         "LuckiestGuy": os.path.join(ROOT, "ui", "fonts", "LuckiestGuy.woff")}

_font_cache = {}
_emoji_cache = {}
IMAGES = {}  # asset id -> PIL image, for previewing uploaded sprite sheets


def font_file(family, weight):
    fam = re.sub(r".*/|\.json$", "", family or "")
    if fam in FIXED:
        return FIXED[fam]
    stem = FAMILIES.get(fam, "montserrat")
    want = WEIGHTS.get(weight, 400)
    best, bd = None, 1e9
    for f in os.listdir(FONT_DIR):
        m = re.match(re.escape(stem) + r"-latin-(\d+)-normal\.woff$", f)
        if m:
            d = abs(int(m.group(1)) - want) + (0.5 if int(m.group(1)) < want else 0)
            if d < bd:
                best, bd = f, d
    if not best:
        return FIXED["FredokaOne"]
    return os.path.join(FONT_DIR, best)


def get_font(path, size):
    key = (path, int(size))
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, max(1, int(size)))
    return _font_cache[key]


def emoji_image(ch):
    if ch not in _emoji_cache:
        f = ImageFont.truetype(EMOJI_FONT, 109)
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
        bb = im.getbbox()
        _emoji_cache[ch] = im.crop(bb) if bb else im
    return _emoji_cache[ch]


def is_emoji(ch):
    o = ord(ch)
    return (0x1F000 <= o <= 0x1FAFF or 0x2600 <= o <= 0x27BF or 0x2B00 <= o <= 0x2BFF or 0x2190 <= o <= 0x21FF
            or 0x2300 <= o <= 0x23FF or o in (0x00A9, 0x00AE, 0x203C, 0x2049, 0x2122, 0x2139, 0x3030, 0x303D))


def clusters(text):
    """Split text into (is_emoji, string) runs, keeping variation selectors / ZWJ sequences together."""
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        if is_emoji(ch):
            j = i + 1
            while j < len(text) and (text[j] in "️‍" or 0x1F3FB <= ord(text[j]) <= 0x1F3FF or
                                     (text[j - 1] == "‍" and is_emoji(text[j]))):
                j += 1
            out.append((True, text[i:j]))
            i = j
        elif ch == "️":
            i += 1
        else:
            j = i + 1
            while j < len(text) and not is_emoji(text[j]) and text[j] != "️":
                j += 1
            out.append((False, text[i:j]))
            i = j
    return out


# ------------------------------------------------------------------------------------------------
# tree helpers
# ------------------------------------------------------------------------------------------------
def val(p, k, default=None):
    v = p.get(k, default)
    if isinstance(v, dict) and "t" in v:
        t = v["t"]
        if t in ("UDim2", "UDim", "Vector2", "Color3", "Rect"):
            return v["v"]
        if t == "Enum":
            return v["v"].split(".", 1)[1]
        return v
    return v


def child(node, cls):
    for c in node["k"]:
        if c["c"] == cls:
            return c
    return None


def enabled(node):
    return node is not None and val(node["p"], "Enabled", True)


def c255(c, a=255):
    return (int(round(c[0] * 255)), int(round(c[1] * 255)), int(round(c[2] * 255)), int(a))


def seq_eval(kps, t, n):
    """Evaluate ColorSequence / NumberSequence keypoints at array t."""
    kps = sorted(kps, key=lambda k: k[0])
    ts = np.array([k[0] for k in kps])
    out = []
    for i in range(1, n + 1):
        vs = np.array([k[i] for k in kps])
        out.append(np.interp(t, ts, vs))
    return out


class Xf:
    """screen = k * p + (tx, ty)"""

    def __init__(self, k=1.0, tx=0.0, ty=0.0):
        self.k, self.tx, self.ty = k, tx, ty

    def pt(self, x, y):
        return self.k * x + self.tx, self.k * y + self.ty

    def scaled_about(self, s, ax, ay):
        # p -> a + s (p - a), then self
        return Xf(self.k * s, self.k * (ax - s * ax) + self.tx, self.k * (ay - s * ay) + self.ty)


class Surface:
    def __init__(self, w, h, ox=0, oy=0):
        self.img = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0))
        self.ox, self.oy = ox, oy

    def paste(self, im, x, y):
        x, y = int(round(x - self.ox)), int(round(y - self.oy))
        W, H = self.img.size
        if x >= W or y >= H or x + im.width <= 0 or y + im.height <= 0:
            return
        l, t = max(0, -x), max(0, -y)
        r, b = min(im.width, W - x), min(im.height, H - y)
        crop = im.crop((l, t, r, b)) if (l or t or r < im.width or b < im.height) else im
        self.img.alpha_composite(crop, (x + l, y + t))


# ------------------------------------------------------------------------------------------------
# primitives
# ------------------------------------------------------------------------------------------------
def shape_mask(w, h, r, pad=0):
    """Rounded-rect mask of size (w+2pad, h+2pad) with the shape inset by pad."""
    W, H = max(1, int(math.ceil(w + 2 * pad))), max(1, int(math.ceil(h + 2 * pad)))
    m = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(m)
    x0, y0, x1, y1 = pad, pad, pad + w - 1, pad + h - 1
    if x1 < x0 or y1 < y0:
        return m
    r = max(0, min(r, w / 2, h / 2))
    if r >= 0.5:
        d.rounded_rectangle((x0, y0, x1, y1), radius=r, fill=255)
    else:
        d.rectangle((x0, y0, x1, y1), fill=255)
    return m


def gradient_arrays(grad, w, h):
    """UIGradient colour (h,w,3) and transparency (h,w) over a w x h box."""
    rot = math.radians(val(grad["p"], "Rotation", 0))
    off = val(grad["p"], "Offset", [0, 0])
    u = (np.arange(int(w)) + 0.5) / max(1, w)
    v = (np.arange(int(h)) + 0.5) / max(1, h)
    U, V = np.meshgrid(u, v)
    t = (U - 0.5 - off[0]) * math.cos(rot) + (V - 0.5 - off[1]) * math.sin(rot) + 0.5
    t = np.clip(t, 0, 1)
    col = grad["p"].get("Color", {"v": [[0, 1, 1, 1], [1, 1, 1, 1]]})["v"]
    tr = grad["p"].get("Transparency", {"v": [[0, 0], [1, 0]]})["v"]
    r, g, b = seq_eval(col, t, 3)
    (a,) = seq_eval(tr, t, 1)
    return np.stack([r, g, b], -1), a


def fill_image(w, h, color, transp, grad, mask):
    """RGBA image: colour * gradient, alpha = (1-transp) * (1-gradT) * mask."""
    W, H = mask.size
    base = np.array(color[:3], dtype=np.float32).reshape(1, 1, 3)
    alpha = (1 - transp) * np.asarray(mask, dtype=np.float32) / 255
    rgb = np.broadcast_to(base, (H, W, 3)).copy()
    if grad is not None:
        gc, ga = gradient_arrays(grad, W, H)
        rgb = rgb * gc
        alpha = alpha * (1 - ga)
    out = np.dstack([np.clip(rgb * 255, 0, 255), np.clip(alpha * 255, 0, 255)]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def draw_box(surf, sx, sy, sw, sh, r, color, transp, grad, stroke, k):
    """Background + border stroke at screen coords."""
    if sw < 0.5 or sh < 0.5:
        return
    if transp < 1:
        m = shape_mask(sw, sh, r)
        surf.paste(fill_image(sw, sh, color, transp, grad, m), sx, sy)
    if stroke:
        t = max(0.5, stroke["t"] * k)
        rr = r + t if (r > 0 or stroke["join"] == "Round") else 0
        if stroke["join"] != "Round" and r <= 0:
            rr = 0
        outer = shape_mask(sw + 2 * t, sh + 2 * t, rr)
        inner = shape_mask(sw, sh, r, pad=t)
        ring = Image.fromarray(np.clip(np.asarray(outer, np.int16) - np.asarray(inner, np.int16), 0, 255).astype(np.uint8))
        surf.paste(fill_image(sw + 2 * t, sh + 2 * t, stroke["color"], stroke["transp"], stroke["grad"], ring),
                   sx - t, sy - t)


# ------------------------------------------------------------------------------------------------
# text
# ------------------------------------------------------------------------------------------------
def parse_rich(text, rich, color):
    """-> list of lines, each a list of (string, rgb) runs."""
    if not rich:
        return [[(ln, color)] for ln in text.split("\n")]
    text = re.sub(r"<br\s*/?>", "\n", text)
    runs, stack = [], [color]
    pos = 0
    for m in re.finditer(r"<(/?)(\w+)([^>]*)>", text):
        if m.start() > pos:
            runs.append((text[pos:m.start()], stack[-1]))
        pos = m.end()
        closing, tag, attrs = m.group(1), m.group(2).lower(), m.group(3)
        if tag == "font":
            if closing:
                if len(stack) > 1:
                    stack.pop()
            else:
                cm = re.search(r'color\s*=\s*["\']#?([0-9a-fA-F]{6})["\']', attrs)
                rm = re.search(r'color\s*=\s*["\']rgb\((\d+),\s*(\d+),\s*(\d+)\)["\']', attrs)
                if cm:
                    h = cm.group(1)
                    stack.append(tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)))
                elif rm:
                    stack.append(tuple(int(rm.group(i)) / 255 for i in (1, 2, 3)))
                else:
                    stack.append(stack[-1])
    if pos < len(text):
        runs.append((text[pos:], stack[-1]))
    lines = [[]]
    for s, c in runs:
        s = s.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&quot;", '"')
        parts = s.split("\n")
        for i, p in enumerate(parts):
            if i:
                lines.append([])
            if p:
                lines[-1].append((p, c))
    return lines


def run_width(s, font, size):
    w = 0
    for emo, part in clusters(s):
        if emo:
            w += size * 1.12 * len([c for c in part if is_emoji(c) and c != "‍"][:1] or [1])
        else:
            w += font.getlength(part)
    return w


def wrap_lines(lines, font, size, width, wrap):
    if not wrap:
        return lines
    out = []
    for ln in lines:
        cur, cw = [], 0
        for s, c in ln:
            for word in re.split(r"(\s+)", s):
                if not word:
                    continue
                ww = run_width(word, font, size)
                if cw + ww > width + 0.5 and cur and not word.isspace():
                    out.append(cur)
                    cur, cw = [], 0
                if not cur and word.isspace():
                    continue
                cur.append((word, c))
                cw += ww
        out.append(cur)
    return out


def text_layer(node, sw, sh, k, text, color):
    p = node["p"]
    font_v = p.get("FontFace")
    if isinstance(font_v, dict):
        path = font_file(font_v["family"], font_v["weight"])
    else:
        path = font_file("FredokaOne", "Regular")
    rich = val(p, "RichText", False)
    lines0 = parse_rich(text, rich, color)
    wrap = val(p, "TextWrapped", False)
    lh = val(p, "LineHeight", 1)
    size = val(p, "TextSize", 14) * k
    if val(p, "TextScaled", False):
        tsc = child(node, "UITextSizeConstraint")
        mx = (val(tsc["p"], "MaxTextSize", 100) if tsc else 100) * k
        mn = (val(tsc["p"], "MinTextSize", 1) if tsc else 1) * k
        lo, hi = max(1, mn), max(1, mx)
        for _ in range(14):
            mid = (lo + hi) / 2
            f = get_font(path, mid)
            ls = wrap_lines(lines0, f, mid, sw, True)
            fits = len(ls) * mid * 1.0 * lh <= sh + 0.5 and all(
                sum(run_width(s, f, mid) for s, _ in ln) <= sw + 0.5 for ln in ls) and (
                wrap or len(ls) == len(lines0))
            if fits:
                lo = mid
            else:
                hi = mid
        size = lo
        wrap = True
    font = get_font(path, size)
    lines = wrap_lines(lines0, font, size, sw, wrap)
    if val(p, "TextTruncate", "None") != "None" and lines:
        ln = lines[0]
        s = "".join(x for x, _ in ln)
        if run_width(s, font, size) > sw:
            while s and run_width(s + "...", font, size) > sw:
                s = s[:-1]
            lines = [[(s + "...", ln[0][1] if ln else color)]]
    asc, desc = font.getmetrics()
    line_h = size * lh * 1.0
    total_h = line_h * len(lines)
    pad = int(size * 0.6) + 8
    W, H = int(sw + 2 * pad), int(max(sh, total_h) + 2 * pad)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    ya = val(p, "TextYAlignment", "Center")
    xa = val(p, "TextXAlignment", "Center")
    if ya == "Top":
        y0 = pad
    elif ya == "Bottom":
        y0 = pad + sh - total_h
    else:
        y0 = pad + (sh - total_h) / 2
    for i, ln in enumerate(lines):
        lw = sum(run_width(s, font, size) for s, _ in ln)
        if xa == "Left":
            x = pad
        elif xa == "Right":
            x = pad + sw - lw
        else:
            x = pad + (sw - lw) / 2
        cy = y0 + line_h * i + line_h / 2
        for s, c in ln:
            for emo, part in clusters(s):
                if emo:
                    base = part.replace("‍", "")
                    first = next((ch for ch in part if is_emoji(ch)), None)
                    em = emoji_image(part if len(part) <= 8 else first)
                    es = size * 1.05
                    im = em.resize((max(1, int(es * em.width / max(em.height, 1))), max(1, int(es))), Image.LANCZOS)
                    layer.alpha_composite(im, (int(x + size * 0.04), int(cy - es / 2)))
                    x += size * 1.12
                else:
                    d.text((x, cy), part, font=font, fill=c255(c), anchor="lm")
                    x += font.getlength(part)
    return layer, pad


def dilate_alpha(a, r):
    if r <= 0:
        return a
    big = a.filter(ImageFilter.GaussianBlur(r * 0.55))
    return big.point(lambda v: 255 if v > 18 else int(v * 255 / 18))


def draw_text(surf, node, sx, sy, sw, sh, k, text, color, transp):
    if not text or transp >= 1:
        return
    layer, pad = text_layer(node, sw, sh, k, text, color)
    a = layer.getchannel("A")
    grad = child(node, "UIGradient")
    if enabled(grad):
        gc, ga = gradient_arrays(grad, layer.width - 2 * pad, layer.height - 2 * pad)
        arr = np.asarray(layer, np.float32)
        H, W = gc.shape[:2]
        gcf = np.ones_like(arr[..., :3])
        gaf = np.zeros(arr.shape[:2], np.float32)
        gcf[pad:pad + H, pad:pad + W] = gc
        gaf[pad:pad + H, pad:pad + W] = ga
        arr[..., :3] *= gcf
        arr[..., 3] *= (1 - gaf)
        layer = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    if transp > 0:
        layer.putalpha(a.point(lambda v: int(v * (1 - transp))))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    st = None
    for c in node["k"]:
        if c["c"] == "UIStroke" and enabled(c) and val(c["p"], "ApplyStrokeMode", "Contextual") == "Contextual":
            st = c
    legacy = val(node["p"], "TextStrokeTransparency", 1)
    if st is not None:
        t = val(st["p"], "Thickness", 1) * k
        sc = val(st["p"], "Color", [0, 0, 0])
        stt = val(st["p"], "Transparency", 0)
        ring = dilate_alpha(a, t)
        sl = Image.new("RGBA", layer.size, c255(sc, 0))
        sl.putalpha(ring.point(lambda v: int(v * (1 - stt) * (1 - transp))))
        out.alpha_composite(sl)
    elif legacy < 1:
        sc = val(node["p"], "TextStrokeColor3", [0, 0, 0])
        ring = dilate_alpha(a, max(1, k))
        sl = Image.new("RGBA", layer.size, c255(sc, 0))
        sl.putalpha(ring.point(lambda v: int(v * (1 - legacy) * (1 - transp))))
        out.alpha_composite(sl)
    out.alpha_composite(layer)
    surf.paste(out, sx - pad, sy - pad)


# ------------------------------------------------------------------------------------------------
# layout
# ------------------------------------------------------------------------------------------------
def udim2(p, k, default):
    v = val(p, k, default)
    return v


def natural_size(node, R):
    xs, xo, ys, yo = udim2(node["p"], "Size", [0, 100, 0, 100])
    w, h = R[2] * xs + xo, R[3] * ys + yo
    sc = val(node["p"], "SizeConstraint", "RelativeXY")
    if sc == "RelativeXX":
        h = R[2] * ys + yo
    elif sc == "RelativeYY":
        w = R[3] * xs + xo
    ar = child(node, "UIAspectRatioConstraint")
    if ar is not None:
        ratio = val(ar["p"], "AspectRatio", 1)
        if val(ar["p"], "AspectType", "FitWithinMaxSize") == "FitWithinMaxSize":
            if h > 0 and w / h > ratio:
                w = h * ratio
            else:
                h = w / ratio
        else:
            if val(ar["p"], "DominantAxis", "Width") == "Width":
                h = w / ratio
            else:
                w = h * ratio
    szc = child(node, "UISizeConstraint")
    if szc is not None:
        mn, mx = val(szc["p"], "MinSize", [0, 0]), val(szc["p"], "MaxSize", [1e30, 1e30])
        w, h = min(max(w, mn[0]), mx[0]), min(max(h, mn[1]), mx[1])
    return max(0, w), max(0, h)


def content_rect(node, B):
    pad = child(node, "UIPadding")
    x, y, w, h = B
    if pad is not None:
        pl, pr = val(pad["p"], "PaddingLeft", [0, 0]), val(pad["p"], "PaddingRight", [0, 0])
        pt, pb = val(pad["p"], "PaddingTop", [0, 0]), val(pad["p"], "PaddingBottom", [0, 0])
        L, Rr = pl[0] * w + pl[1], pr[0] * w + pr[1]
        T, Bt = pt[0] * h + pt[1], pb[0] * h + pb[1]
        return (x + L, y + T, w - L - Rr, h - T - Bt)
    return B


def gui_kids(node):
    ks = [c for c in node["k"] if c["c"] in GUI]
    return ks


def sort_layout(kids, layout):
    order = val(layout["p"], "SortOrder", "LayoutOrder")
    idx = {id(c): i for i, c in enumerate(kids)}
    if order == "Name":
        return sorted(kids, key=lambda c: (c["n"], idx[id(c)]))
    return sorted(kids, key=lambda c: (val(c["p"], "LayoutOrder", 0), idx[id(c)]))


def layout_children(node, R):
    """-> {id(child): (x, y, w, h)} for children placed by a layout, plus content extent (w, h)."""
    kids = [c for c in gui_kids(node) if val(c["p"], "Visible", True)]
    lst, grid = child(node, "UIListLayout"), child(node, "UIGridLayout")
    boxes = {}
    if lst is not None:
        kids = sort_layout(kids, lst)
        horiz = val(lst["p"], "FillDirection", "Vertical") == "Horizontal"
        padv = val(lst["p"], "Padding", [0, 0])
        padp = padv[0] * (R[2] if horiz else R[3]) + padv[1]
        sizes = [natural_size(c, R) for c in kids]
        total = sum(s[0] if horiz else s[1] for s in sizes) + padp * max(0, len(kids) - 1)
        ha = val(lst["p"], "HorizontalAlignment", "Left")
        va = val(lst["p"], "VerticalAlignment", "Top")
        if horiz:
            cur = R[0] + {"Left": 0, "Center": (R[2] - total) / 2, "Right": R[2] - total}[ha]
            for c, (w, h) in zip(kids, sizes):
                y = R[1] + {"Top": 0, "Center": (R[3] - h) / 2, "Bottom": R[3] - h}[va]
                boxes[id(c)] = (cur, y, w, h)
                cur += w + padp
            ext = (total, max([s[1] for s in sizes] or [0]))
        else:
            cur = R[1] + {"Top": 0, "Center": (R[3] - total) / 2, "Bottom": R[3] - total}[va]
            for c, (w, h) in zip(kids, sizes):
                x = R[0] + {"Left": 0, "Center": (R[2] - w) / 2, "Right": R[2] - w}[ha]
                boxes[id(c)] = (x, cur, w, h)
                cur += h + padp
            ext = (max([s[0] for s in sizes] or [0]), total)
        return boxes, ext
    if grid is not None:
        kids = sort_layout(kids, grid)
        cs = val(grid["p"], "CellSize", [0, 100, 0, 100])
        cp = val(grid["p"], "CellPadding", [0, 5, 0, 5])
        cw, ch = R[2] * cs[0] + cs[1], R[3] * cs[2] + cs[3]
        px, py = R[2] * cp[0] + cp[1], R[3] * cp[2] + cp[3]
        horiz = val(grid["p"], "FillDirection", "Horizontal") == "Horizontal"
        mx = int(val(grid["p"], "FillDirectionMaxCells", 0))
        if horiz:
            cols = max(1, int((R[2] + px + 0.01) // (cw + px))) if cw + px > 0 else 1
            if mx > 0:
                cols = min(cols, mx)
            rows = max(1, math.ceil(len(kids) / cols))
            used_c = min(cols, len(kids)) if kids else 0
        else:
            rows = max(1, int((R[3] + py + 0.01) // (ch + py))) if ch + py > 0 else 1
            if mx > 0:
                rows = min(rows, mx)
            cols = max(1, math.ceil(len(kids) / rows))
            used_c = cols
        gw = used_c * cw + max(0, used_c - 1) * px
        gh = rows * ch + max(0, rows - 1) * py
        ha = val(grid["p"], "HorizontalAlignment", "Left")
        va = val(grid["p"], "VerticalAlignment", "Top")
        x0 = R[0] + {"Left": 0, "Center": (R[2] - gw) / 2, "Right": R[2] - gw}[ha]
        y0 = R[1] + {"Top": 0, "Center": (R[3] - gh) / 2, "Bottom": R[3] - gh}[va]
        for i, c in enumerate(kids):
            if horiz:
                r, col = divmod(i, cols)
            else:
                col, r = divmod(i, rows)
            boxes[id(c)] = (x0 + col * (cw + px), y0 + r * (ch + py), cw, ch)
        return boxes, (gw, gh)
    return boxes, (0, 0)


def place(node, R, forced=None):
    if forced is not None:
        return forced
    w, h = natural_size(node, R)
    px, pxo, py, pyo = udim2(node["p"], "Position", [0, 0, 0, 0])
    ax, ay = val(node["p"], "AnchorPoint", [0, 0])
    return (R[0] + R[2] * px + pxo - ax * w, R[1] + R[3] * py + pyo - ay * h, w, h)


# ------------------------------------------------------------------------------------------------
# drawing the tree
# ------------------------------------------------------------------------------------------------
class Renderer:
    def __init__(self, ss=2):
        self.ss = ss
        self.count = 0

    def draw_node(self, surf, node, B, X):
        p = node["p"]
        if not val(p, "Visible", True):
            return
        self.count += 1
        cls = node["c"]
        scale = child(node, "UIScale")
        if scale is not None:
            s = val(scale["p"], "Scale", 1)
            ax, ay = val(p, "AnchorPoint", [0, 0])
            X = X.scaled_about(s, B[0] + ax * B[2], B[1] + ay * B[3])
        rot = val(p, "Rotation", 0) or 0
        if abs(rot) > 0.01:
            cx, cy = X.pt(B[0] + B[2] / 2, B[1] + B[3] / 2)
            ext = max(B[2], B[3]) * X.k * 0.75 + 80 * X.k
            sub = Surface(2 * ext, 2 * ext, cx - ext, cy - ext)
            self._draw_self_and_kids(sub, node, B, X)
            rotated = sub.img.rotate(-rot, resample=Image.BICUBIC, center=(ext, ext))
            surf.paste(rotated, cx - ext, cy - ext)
            return
        self._draw_self_and_kids(surf, node, B, X)

    def _draw_self_and_kids(self, surf, node, B, X):
        p = node["p"]
        cls = node["c"]
        sx, sy = X.pt(B[0], B[1])
        sw, sh = B[2] * X.k, B[3] * X.k
        corner = child(node, "UICorner")
        r = 0
        if corner is not None:
            cr = val(corner["p"], "CornerRadius", [0, 8])
            r = (cr[0] * min(B[2], B[3]) + cr[1]) * X.k
            r = min(r, sw / 2, sh / 2)
        is_text = cls in TEXT
        stroke = None
        for c in node["k"]:
            if c["c"] == "UIStroke" and enabled(c):
                mode = val(c["p"], "ApplyStrokeMode", "Contextual")
                if mode == "Border" or not is_text:
                    g = child(c, "UIGradient")
                    stroke = {"t": val(c["p"], "Thickness", 1), "color": val(c["p"], "Color", [0, 0, 0]),
                              "transp": val(c["p"], "Transparency", 0), "join": val(c["p"], "LineJoinMode", "Round"),
                              "grad": g if enabled(g) else None}
        grad = child(node, "UIGradient")
        grad = grad if enabled(grad) else None
        bgt = val(p, "BackgroundTransparency", 0)
        if cls == "CanvasGroup":
            pass
        draw_box(surf, sx, sy, sw, sh, r, val(p, "BackgroundColor3", [0.64, 0.64, 0.65]), bgt,
                 grad if not is_text else None, stroke, X.k)
        if bgt < 1 and corner is None and val(p, "BorderSizePixel", 1) > 0 and stroke is None:
            bs = val(p, "BorderSizePixel", 1) * X.k
            bc = val(p, "BorderColor3", [0.1, 0.16, 0.2])
            draw_box(surf, sx, sy, sw, sh, 0, bc, 1, None,
                     {"t": val(p, "BorderSizePixel", 1), "color": bc, "transp": bgt, "join": "Miter", "grad": None},
                     X.k)
        if cls in ("ImageLabel", "ImageButton"):
            src = IMAGES.get(val(p, "Image", ""))
            if src is not None and sw >= 1 and sh >= 1:
                off = val(p, "ImageRectOffset", [0, 0])
                size = val(p, "ImageRectSize", [0, 0])
                im = src
                if size[0] > 0 and size[1] > 0:
                    im = src.crop((int(off[0]), int(off[1]), int(off[0] + size[0]), int(off[1] + size[1])))
                im = im.convert("RGBA").resize((max(1, int(sw)), max(1, int(sh))), Image.LANCZOS)
                col = val(p, "ImageColor3", [1, 1, 1])
                it = val(p, "ImageTransparency", 0)
                if col != [1, 1, 1] or it > 0:
                    arr = np.asarray(im, np.float32)
                    arr[..., :3] *= np.array(col, np.float32)
                    arr[..., 3] *= (1 - it)
                    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
                surf.paste(im, sx, sy)
        if is_text:
            text = val(p, "Text", "")
            color = val(p, "TextColor3", [0, 0, 0])
            if cls == "TextBox" and not text:
                text = val(p, "PlaceholderText", "")
                color = val(p, "PlaceholderColor3", [0.7, 0.7, 0.7])
            draw_text(surf, node, sx, sy, sw, sh, X.k, text, color, val(p, "TextTransparency", 0))

        # children
        R = content_rect(node, B)
        clip = cls in ("ScrollingFrame", "CanvasGroup") or val(p, "ClipsDescendants", False)
        if cls == "ScrollingFrame":
            cs = val(p, "CanvasSize", [0, 0, 2, 0])
            cw = B[2] * cs[0] + cs[1]
            chh = B[3] * cs[2] + cs[3]
            CR = content_rect(node, (B[0], B[1], max(cw, B[2]) if cw > 0 else B[2], max(chh, 0) or B[3]))
            auto = val(p, "AutomaticCanvasSize", "None")
            boxes, ext = layout_children(node, CR)
            if auto in ("Y", "XY"):
                CR = (CR[0], CR[1], CR[2], max(CR[3], ext[1]))
            R = CR
        kids = [c for c in node["k"] if c["c"] in GUI]
        boxes, _ = layout_children(node, R)
        order = sorted(range(len(kids)), key=lambda i: (val(kids[i]["p"], "ZIndex", 1), i))
        target = surf
        if clip:
            target = Surface(max(1, sw), max(1, sh), sx, sy)
        for i in order:
            c = kids[i]
            CB = place(c, R, boxes.get(id(c)))
            self.draw_node(target, c, CB, X)
        if clip:
            surf.paste(target.img, sx, sy)
        if cls == "ScrollingFrame" and val(p, "ScrollBarThickness", 12) > 0:
            _, ext = layout_children(node, R)
            if ext[1] > B[3] + 1:
                th = val(p, "ScrollBarThickness", 12) * X.k
                frac = B[3] / max(ext[1], 1)
                bar = shape_mask(th, sh * frac, th / 2)
                col = val(p, "ScrollBarImageColor3", [1, 1, 1])
                surf.paste(fill_image(th, sh * frac, col, val(p, "ScrollBarImageTransparency", 0), None, bar),
                           sx + sw - th, sy)


def render_gui(tree, W, H, background=None, ss=2, topbar=True):
    """tree: dumped ScreenGui / widget. Returns an RGB image W x H."""
    surf = Surface(W * ss, H * ss)
    if background is not None:
        surf.img.paste(background.convert("RGBA").resize((W * ss, H * ss)))
    R = (0, 0, W, H)
    rd = Renderer(ss)
    X = Xf(ss)
    kids = [c for c in tree["k"] if c["c"] in GUI]
    order = sorted(range(len(kids)), key=lambda i: (val(kids[i]["p"], "ZIndex", 1), i))
    for i in order:
        c = kids[i]
        rd.draw_node(surf, c, place(c, R), X)
    img = surf.img.resize((W, H), Image.LANCZOS)
    if topbar:
        overlay_topbar(img)
    return img.convert("RGB"), rd.count


def overlay_topbar(img):
    """The Roblox top bar buttons, so overlaps with the menu/chat buttons are visible."""
    d = ImageDraw.Draw(img, "RGBA")
    for i, x in enumerate((12, 64)):
        d.rounded_rectangle((x, 12, x + 44, 56), radius=12, fill=(18, 18, 21, 150))
        if i == 0:
            d.rounded_rectangle((x + 13, 25, x + 31, 43), radius=3, outline=(255, 255, 255, 230), width=3)
        else:
            d.rounded_rectangle((x + 11, 23, x + 33, 39), radius=6, outline=(255, 255, 255, 230), width=3)
            d.polygon([(x + 16, 38), (x + 16, 45), (x + 22, 38)], fill=(255, 255, 255, 230))
