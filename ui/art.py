"""Studs-style UI art (Pillow only): studded buttons & panels, textured fills,
cards, rarity slots, bars, icons with outline + shine, stroked titles, FX.

Everything is drawn 3x supersampled and scaled down for smooth edges.
"""
import math
import os
import random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SS = 3
FONTS = {"FredokaBold": "FredokaBold.woff", "LuckiestGuy": "LuckiestGuy.woff", "LilitaOne": "LilitaOne.woff"}


# ----------------------------------------------------------------------------
# colour helpers
# ----------------------------------------------------------------------------
def rgb(c):
    if isinstance(c, tuple):
        return c[:3]
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def darker(c, t):
    return mix(c, (0, 0, 0), t)


def lighter(c, t):
    return mix(c, (255, 255, 255), t)


def hexs(c):
    return "#%02X%02X%02X" % rgb(c)


# ----------------------------------------------------------------------------
# basic shapes (supersampled)
# ----------------------------------------------------------------------------
def mask_round(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=max(0, r), fill=255)
    return m


def vgrad(w, h, top, bottom):
    top, bottom = rgb(top), rgb(bottom)
    g = Image.new("RGB", (1, h))
    for y in range(h):
        g.putpixel((0, y), mix(top, bottom, y / max(1, h - 1)))
    return g.resize((w, h))


def hgrad(w, h, left, right):
    return vgrad(h, w, left, right).rotate(90, expand=True).transpose(Image.FLIP_TOP_BOTTOM)


def alpha_ramp(w, h, a0, a1, frac=1.0):
    """L image: a0 at top fading to a1 at frac*h, a1 below."""
    m = Image.new("L", (1, h))
    for y in range(h):
        t = min(1.0, y / max(1, frac * h))
        m.putpixel((0, y), int(a0 + (a1 - a0) * t))
    return m.resize((w, h))


def paste_masked(dst, src, mask, xy=(0, 0)):
    layer = Image.new("RGBA", dst.size, (0, 0, 0, 0))
    s = src.convert("RGBA")
    layer.paste(s, xy)
    full = Image.new("L", dst.size, 0)
    full.paste(mask, xy)
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), full))
    dst.alpha_composite(layer)


# ----------------------------------------------------------------------------
# the stud texture
# ----------------------------------------------------------------------------
_STUD_CACHE = {}


def stud_tile(px):
    """One stud cell as an RGBA overlay (white highlights / black shadows)."""
    if px in _STUD_CACHE:
        return _STUD_CACHE[px]
    c = px * 4
    tile = Image.new("RGBA", (c, c), (0, 0, 0, 0))
    ins = int(c * 0.17)
    r = int(c * 0.2)
    d = max(2, int(c * 0.07))

    def rect(off, inset, fill):
        lay = Image.new("RGBA", (c, c), (0, 0, 0, 0))
        ImageDraw.Draw(lay).rounded_rectangle((inset + off, inset + off, c - inset + off, c - inset + off), radius=r,
                                              fill=fill)
        return lay
    tile.alpha_composite(rect(d, ins, (0, 0, 0, 70)))                    # shadow bottom-right
    tile.alpha_composite(rect(-d // 2, ins, (255, 255, 255, 95)))        # rim top-left
    tile.alpha_composite(rect(0, ins, (255, 255, 255, 40)))              # stud face
    tile.alpha_composite(rect(0, ins + d, (255, 255, 255, 18)))          # soft top
    tile = tile.resize((px, px), Image.LANCZOS)
    _STUD_CACHE[px] = tile
    return tile


def stud_overlay(w, h, px, strength=1.0):
    t = stud_tile(px)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for y in range(0, h, px):
        for x in range(0, w, px):
            lay.paste(t, (x, y))
    if strength != 1.0:
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * strength)))
    return lay


# ----------------------------------------------------------------------------
# textured fills (mutations, rarities, special buttons)
# ----------------------------------------------------------------------------
def fill_lava(w, h, seed=1):
    rnd = random.Random(seed)
    im = vgrad(w, h, (255, 120, 40), (190, 40, 10))
    d = ImageDraw.Draw(im)
    for _ in range(int(w * h / 900) + 6):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        pts = [(x, y)]
        for _ in range(4):
            x += rnd.uniform(-w * 0.12, w * 0.12)
            y += rnd.uniform(-h * 0.2, h * 0.2)
            pts.append((x, y))
        d.line(pts, fill=(255, 225, 90), width=max(2, w // 60))
    return im.filter(ImageFilter.GaussianBlur(0.6))


def fill_ice(w, h, seed=2):
    rnd = random.Random(seed)
    im = vgrad(w, h, (200, 240, 255), (120, 200, 245))
    d = ImageDraw.Draw(im)
    for _ in range(int(w * h / 1400) + 6):
        x, y = rnd.uniform(-10, w), rnd.uniform(-10, h)
        s = rnd.uniform(w * 0.06, w * 0.2)
        d.polygon([(x, y), (x + s, y + s * 0.3), (x + s * 0.4, y + s)], fill=(235, 250, 255))
    return im


def fill_electric(w, h, seed=3):
    rnd = random.Random(seed)
    im = vgrad(w, h, (255, 236, 90), (240, 190, 20))
    d = ImageDraw.Draw(im)
    for _ in range(int(w / 40) + 3):
        x, y = rnd.uniform(0, w), 0
        pts = [(x, y)]
        while y < h:
            x += rnd.uniform(-h * 0.25, h * 0.25)
            y += rnd.uniform(h * 0.15, h * 0.35)
            pts.append((x, y))
        d.line(pts, fill=(255, 255, 220), width=max(2, w // 80))
    return im


def fill_toxic(w, h, seed=4):
    rnd = random.Random(seed)
    im = vgrad(w, h, (60, 170, 40), (20, 110, 20))
    d = ImageDraw.Draw(im)
    for _ in range(int(w * h / 700) + 6):
        x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(h * 0.05, h * 0.18)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(120, 230, 60))
    return im.filter(ImageFilter.GaussianBlur(1.2))


def fill_rainbow(w, h, seed=5):
    cols = [(255, 80, 80), (255, 160, 60), (255, 230, 70), (90, 220, 90), (70, 190, 255), (150, 110, 255),
            (255, 110, 210)]
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for x in range(w):
        t = (x / w) * (len(cols) - 1)
        i = int(t)
        c = mix(cols[i], cols[min(i + 1, len(cols) - 1)], t - i)
        d.line([(x, 0), (x, h)], fill=c)
    return im


def fill_galaxy(w, h, seed=6):
    rnd = random.Random(seed)
    im = vgrad(w, h, (70, 40, 150), (20, 10, 60))
    neb = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(neb)
    for _ in range(5):
        x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(h * 0.3, h * 0.8)
        d.ellipse((x - r, y - r, x + r, y + r), fill=rnd.choice([(200, 60, 200), (60, 120, 255), (120, 60, 255)]))
    im = ImageChops.add(im, neb.filter(ImageFilter.GaussianBlur(h * 0.25)).point(lambda v: int(v * 0.5)))
    d = ImageDraw.Draw(im)
    for _ in range(int(w * h / 300)):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        s = rnd.choice((1, 1, 1, 2))
        d.rectangle((x, y, x + s, y + s), fill=(255, 255, 255))
    return im


def fill_gold(w, h, seed=7):
    im = vgrad(w, h, (255, 226, 110), (214, 150, 20))
    d = ImageDraw.Draw(im)
    for k in range(-2, int(w / (h * 0.9)) + 2):
        x = k * h * 0.9
        d.polygon([(x, h), (x + h * 0.3, h), (x + h * 0.9, 0), (x + h * 0.6, 0)], fill=(255, 244, 190))
    return im


def fill_diamond(w, h, seed=8):
    rnd = random.Random(seed)
    im = vgrad(w, h, (170, 245, 255), (70, 190, 240))
    d = ImageDraw.Draw(im)
    for _ in range(int(w * h / 1100) + 4):
        x, y, s = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(h * 0.15, h * 0.45)
        d.polygon([(x, y - s), (x + s * 0.6, y), (x, y + s), (x - s * 0.6, y)],
                  fill=rnd.choice([(220, 252, 255), (120, 220, 250), (250, 255, 255)]))
    return im


def fill_checker(w, h, a=(170, 176, 186), b=(150, 156, 168), cell=None):
    cell = cell or max(4, h // 5)
    im = Image.new("RGB", (w, h), a)
    d = ImageDraw.Draw(im)
    for y in range(0, h, cell):
        for x in range(0, w, cell):
            if (x // cell + y // cell) % 2:
                d.rectangle((x, y, x + cell - 1, y + cell - 1), fill=b)
    return im


FILLS = {"lava": fill_lava, "ice": fill_ice, "electric": fill_electric, "toxic": fill_toxic, "rainbow": fill_rainbow,
         "galaxy": fill_galaxy, "gold": fill_gold, "diamond": fill_diamond, "checker": fill_checker}
FILL_OUTLINE = {"lava": (90, 15, 5), "ice": (40, 110, 160), "electric": (130, 90, 0), "toxic": (15, 60, 10),
                "rainbow": (70, 40, 110), "galaxy": (15, 8, 40), "gold": (110, 70, 0), "diamond": (20, 90, 140),
                "checker": (70, 74, 84)}


# ----------------------------------------------------------------------------
# the studded box: buttons, headers, cards, tabs...
# ----------------------------------------------------------------------------
def studded_box(w, h, color, r=12, stroke=5, outline=None, studs=True, gloss=0.28, lip=6, stud_px=20, grad=0.16,
                fill=None, alpha=255, stud_strength=1.0, gradient_to=None, inner_line=True):
    """Returns (RGBA image, (left, top, right, bottom) 9-slice margins)."""
    S = SS
    W, H, R, ST, LP = w * S, h * S, r * S, stroke * S, lip * S
    outline = rgb(outline) if outline else darker(color, 0.62)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    outer = Image.new("RGBA", (W, H), outline + (alpha,))
    img.paste(outer, (0, 0), mask_round(W, H, R))
    iw, ih = W - 2 * ST, H - 2 * ST
    ir = max(0, R - ST)
    lip_img = Image.new("RGBA", (iw, ih), darker(color, 0.32) + (alpha,)) if not fill else \
        Image.new("RGBA", (iw, ih), mix(FILL_OUTLINE[fill], color, 0.35) + (alpha,))
    img.paste(lip_img, (ST, ST), mask_round(iw, ih, ir))
    fh = ih - LP
    fmask = mask_round(iw, fh, ir)
    if fill:
        face = FILLS[fill](iw, fh).convert("RGB")
    elif gradient_to:
        face = hgrad(iw, fh, lighter(color, grad * 0.5), gradient_to)
    else:
        face = vgrad(iw, fh, lighter(color, grad), darker(color, grad * 0.55))
    face = face.convert("RGBA")
    if alpha < 255:
        face.putalpha(alpha)
    if studs:
        face.alpha_composite(stud_overlay(iw, fh, stud_px * S, stud_strength))
    if gloss > 0:
        g = Image.new("RGBA", (iw, fh), (255, 255, 255, 0))
        g.putalpha(alpha_ramp(iw, fh, int(255 * gloss), 0, 0.55))
        face.alpha_composite(g)
    if inner_line:
        ln = Image.new("RGBA", (iw, fh), (255, 255, 255, 0))
        ImageDraw.Draw(ln).rounded_rectangle((0, 0, iw - 1, fh - 1), radius=ir, outline=(255, 255, 255, 110),
                                             width=max(2, S * 2))
        ln.putalpha(ImageChops.multiply(ln.getchannel("A"), alpha_ramp(iw, fh, 255, 0, 0.5)))
        face.alpha_composite(ln)
    paste_masked(img, face, fmask, (ST, ST))
    out = img.resize((w, h), Image.LANCZOS)
    m = r + stroke + 3
    return out, (m, m, m, m + lip)


def panel_body(w, h, color=(20, 26, 48), alpha=215, r=12, stroke=5, outline=(8, 10, 20), studs=True):
    img, sl = studded_box(w, h, color, r=r, stroke=stroke, outline=outline, studs=studs, gloss=0.0, lip=0, grad=0.0,
                          alpha=alpha, stud_strength=0.35, inner_line=False)
    return img, sl


def slot_box(w, h, rim=(60, 66, 84), body=(34, 38, 52), stroke=4, r=10, glow=None):
    S = SS
    W, H = w * S, h * S
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.paste(Image.new("RGBA", (W, H), rgb(rim) + (255,)), (0, 0), mask_round(W, H, r * S))
    ins = stroke * S
    inner = vgrad(W - 2 * ins, H - 2 * ins, lighter(body, 0.08), darker(body, 0.1)).convert("RGBA")
    if glow:
        gl = Image.new("RGBA", inner.size, rgb(glow) + (0,))
        gm = Image.new("L", inner.size, 0)
        ImageDraw.Draw(gm).ellipse((inner.width * 0.1, inner.height * 0.1, inner.width * 0.9, inner.height * 0.9),
                                   fill=150)
        gl.putalpha(gm.filter(ImageFilter.GaussianBlur(inner.width * 0.18)))
        inner.alpha_composite(gl)
    paste_masked(img, inner, mask_round(W - 2 * ins, H - 2 * ins, max(0, (r - stroke) * S)), (ins, ins))
    out = img.resize((w, h), Image.LANCZOS)
    m = r + stroke + 2
    return out, (m, m, m, m)


def bar_box(w, h, color, back=False):
    if back:
        return slot_box(w, h, rim=(12, 14, 22), body=(40, 44, 58), stroke=4, r=h // 2 - 2)
    return studded_box(w, h, color, r=h // 2 - 2, stroke=4, lip=4, stud_px=14, gloss=0.35)


def toggle_box(on=True):
    w, h = 120, 56
    base, sl = studded_box(w, h, (70, 210, 90) if on else (150, 156, 168), r=h // 2 - 2, stroke=4, lip=4, stud_px=14)
    knob, _ = studded_box(44, 44, (255, 255, 255), r=20, stroke=4, outline=(40, 44, 60), lip=4, studs=False, gloss=0.2)
    base.alpha_composite(knob, (w - 50 if on else 6, 4))
    return base, sl


def close_button(size=72, color=(232, 60, 60)):
    img, sl = studded_box(size, size, color, r=10, stroke=5, lip=5, stud_px=18)
    x = text_image("X", int(size * 0.62), fill=(255, 255, 255), stroke=(60, 10, 10), font="FredokaBold")
    img.alpha_composite(x, ((size - x.width) // 2, (size - 5 - x.height) // 2))
    return img, sl


def plus_button(size=56, color=(80, 210, 70)):
    img, sl = studded_box(size, size, color, r=8, stroke=4, lip=4, stud_px=14)
    x = text_image("+", int(size * 0.75), fill=(255, 255, 255), stroke=(20, 70, 10), font="FredokaBold")
    img.alpha_composite(x, ((size - x.width) // 2, (size - 4 - x.height) // 2))
    return img, sl


def badge(size=48, color=(235, 50, 50)):
    S = SS
    img = Image.new("RGBA", (size * S, size * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse((0, 0, size * S - 1, size * S - 1), fill=darker(color, 0.6) + (255,))
    d.ellipse((4 * S, 4 * S, size * S - 4 * S, size * S - 4 * S), fill=rgb(color) + (255,))
    d.ellipse((10 * S, 7 * S, size * S - 16 * S, size * S * 0.45), fill=(255, 255, 255, 80))
    return img.resize((size, size), Image.LANCZOS), None


# ----------------------------------------------------------------------------
# text
# ----------------------------------------------------------------------------
def font_path(name):
    return os.path.join(HERE, "fonts", FONTS.get(name, FONTS["FredokaBold"]))


def text_image(s, size, fill=(255, 255, 255), stroke=(20, 20, 30), stroke_w=None, font="FredokaBold", gradient=None,
               shadow=True, extrude=0, gloss=0.0):
    """Stroked text as RGBA. gradient=(top, bottom) colours the fill; extrude adds a 3D side."""
    S = 2
    ft = ImageFont.truetype(font_path(font), size * S)
    sw = int((stroke_w if stroke_w is not None else max(2, size * 0.11)) * S)
    l, t, r, b = ft.getbbox(s, stroke_width=sw)
    pad = sw + (extrude + 6) * S
    W, H = r - l + pad * 2, b - t + pad * 2
    org = (pad - l, pad - t)

    def layer(fill_rgba, dx=0, dy=0, stroke_on=True):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((org[0] + dx, org[1] + dy), s, font=ft, fill=fill_rgba,
                                 stroke_width=sw if stroke_on else 0, stroke_fill=fill_rgba)
        return lay
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    stroke = rgb(stroke)
    if shadow:
        sh = layer((0, 0, 0, 110), 0, int(size * 0.08 * S) + extrude * S)
        img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(size * 0.03 * S)))
    for k in range(extrude, 0, -1):
        img.alpha_composite(layer(darker(stroke, 0.2) + (255,), 0, k * S))
    img.alpha_composite(layer(stroke + (255,)))
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).text(org, s, font=ft, fill=255)
    if gradient:
        g = vgrad(W, H, gradient[0], gradient[1])
        ys = [y for y in range(H) if mask.crop((0, y, W, y + 1)).getbbox()]
        if ys:
            g = Image.new("RGB", (W, H), rgb(gradient[1]))
            g.paste(vgrad(W, ys[-1] - ys[0] + 1, gradient[0], gradient[1]), (0, ys[0]))
        fill_img = g.convert("RGBA")
    else:
        fill_img = Image.new("RGBA", (W, H), rgb(fill) + (255,))
    fill_img.putalpha(mask)
    img.alpha_composite(fill_img)
    if gloss:
        bb = mask.getbbox()
        if bb:
            gl = Image.new("RGBA", (W, H), (255, 255, 255, 0))
            ramp = Image.new("L", (W, H), 0)
            ramp.paste(alpha_ramp(W, bb[3] - bb[1], int(255 * gloss), 0, 0.5), (0, bb[1]))
            gl.putalpha(ImageChops.multiply(ramp, mask))
            img.alpha_composite(gl)
    img = img.resize((W // S, H // S), Image.LANCZOS)
    bb = img.getbbox()
    return img.crop(bb) if bb else img


# ----------------------------------------------------------------------------
# icons
# ----------------------------------------------------------------------------
def dilate(alpha, radius):
    """Soft, fast dilation of an alpha mask by roughly ``radius`` px."""
    sig = max(0.5, radius / 1.45)
    b = alpha.filter(ImageFilter.GaussianBlur(sig))
    return b.point(lambda v: 0 if v < 6 else 255 if v > 26 else int((v - 6) * 255 / 20))


def process_icon(raw, size=256, outline=(16, 18, 30), inner_white=False, shine=0.35, shadow=True):
    """Crop, fit, then add a dark outline, a soft shine and a drop shadow."""
    im = raw.convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 12 else 0).getbbox()
    if bb:
        im = im.crop(bb)
    work = 512
    fit = int(work * 0.8)
    sc = fit / max(im.width, im.height)
    im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    can = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    ox, oy = (work - im.width) // 2, (work - im.height) // 2 - 6
    can.paste(im, (ox, oy), im)
    a = can.getchannel("A")
    out = Image.new("RGBA", (work, work), (0, 0, 0, 0))
    ring = dilate(a, 16)
    if shadow:
        sh = Image.new("RGBA", (work, work), (0, 0, 0, 0))
        sh.putalpha(ring.point(lambda v: int(v * 0.4)))
        sh = ImageChops.offset(sh, 0, 14).filter(ImageFilter.GaussianBlur(6))
        out.alpha_composite(sh)
    ol = Image.new("RGBA", (work, work), rgb(outline) + (0,))
    ol.putalpha(ring)
    out.alpha_composite(ol)
    if inner_white:
        wl = Image.new("RGBA", (work, work), (255, 255, 255, 0))
        wl.putalpha(dilate(a, 7))
        out.alpha_composite(wl)
    out.alpha_composite(can)
    if shine:
        bb = a.getbbox() or (0, 0, work, work)
        gl = Image.new("RGBA", (work, work), (255, 255, 255, 0))
        ramp = Image.new("L", (work, work), 0)
        hh = bb[3] - bb[1]
        ramp.paste(alpha_ramp(work, hh, int(255 * shine), 0, 0.5), (0, bb[1]))
        diag = Image.linear_gradient("L").rotate(45).resize((work, work)).point(lambda v: 255 - v)
        gl.putalpha(ImageChops.multiply(ImageChops.multiply(ramp, a), diag))
        out.alpha_composite(gl)
    return out.resize((size, size), Image.LANCZOS)


# ----------------------------------------------------------------------------
# FX
# ----------------------------------------------------------------------------
def sunburst(size=256, color=(255, 240, 160), rays=16):
    S = SS
    W = size * S
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = W / 2
    for k in range(rays):
        a0 = 2 * math.pi * k / rays
        a1 = a0 + math.pi / rays
        d.polygon([(c, c), (c + W * math.cos(a0), c + W * math.sin(a0)), (c + W * math.cos(a1), c + W * math.sin(a1))],
                  fill=rgb(color) + (170,))
    fade = Image.radial_gradient("L").resize((W, W)).point(lambda v: 255 - v)
    im.putalpha(ImageChops.multiply(im.getchannel("A"), fade))
    return im.resize((size, size), Image.LANCZOS), None


def glow(size=256, color=(255, 230, 120)):
    fade = Image.radial_gradient("L").resize((size, size)).point(lambda v: max(0, 255 - int(v * 1.1)))
    im = Image.new("RGBA", (size, size), rgb(color) + (0,))
    im.putalpha(fade)
    return im, None


def sparkle(size=64, color=(255, 255, 255)):
    S = SS
    W = size * S
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = W / 2
    d.polygon([(c, 0), (c + W * 0.1, c - W * 0.1), (W, c), (c + W * 0.1, c + W * 0.1), (c, W), (c - W * 0.1, c + W * 0.1),
               (0, c), (c - W * 0.1, c - W * 0.1)], fill=rgb(color) + (255,))
    return im.filter(ImageFilter.GaussianBlur(S * 0.6)).resize((size, size), Image.LANCZOS), None


# ----------------------------------------------------------------------------
# atlas packing
# ----------------------------------------------------------------------------
def pack(items, size=1024, pad=4):
    """Shelf-pack [(name, image, slice)] into as many size x size pages as needed."""
    order = sorted(items, key=lambda it: (-it[1].height, -it[1].width))
    pages, rects = [], {}
    page = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = y = pad
    row_h = 0
    pi = 0
    for name, im, sl in order:
        if x + im.width + pad > size:
            x, y = pad, y + row_h + pad
            row_h = 0
        if y + im.height + pad > size:
            pages.append(page)
            page = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            pi += 1
            x = y = pad
            row_h = 0
        page.paste(im, (x, y), im)
        rects[name] = (pi, x, y, im.width, im.height, sl)
        x += im.width + pad
        row_h = max(row_h, im.height)
    pages.append(page)
    return pages, rects
