"""Render the SimUI plugin preview set into ui/previews/ (runs the real plugin in the Luau harness).

    python3 ui/sim/previews.py
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, "ui", "previews")
TMP = os.path.join(OUT, "_tmp")
FONT = os.path.join(ROOT, "ui", "fonts", "FredokaBold.woff")

GAMES = ["simulator", "tycoon", "obby", "fighting", "horror", "racing", "rpg", "shooter", "tower", "roleplay"]
STYLES = ["Sim", "Studs", "Bubbly", "Cartoon", "Horror", "Anime", "SciFi", "Fantasy", "Minimal", "Pixel", "Glass"]


def job(name, opts, open_=None, sheet=True, tip=False):
    cmd = [sys.executable, os.path.join(HERE, "run.py"), "--opts", json.dumps(opts), "--out", os.path.join(TMP, name + ".png")]
    if open_:
        cmd += ["--open", open_]
    if sheet:
        cmd.append("--sheet")
    if tip:
        cmd.append("--tip")
    return name, cmd


def tag(im, text):
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 26)
    w = d.textlength(text, font=f)
    d.rounded_rectangle((12, im.height - 48, 28 + w, im.height - 10), radius=10, fill=(20, 22, 30, 220))
    d.text((20, im.height - 45), text, font=f, fill=(255, 255, 255))
    return im


def grid(names, labels, cols, path, cell=(640, 360)):
    rows = (len(names) + cols - 1) // cols
    out = Image.new("RGB", (cols * cell[0], rows * cell[1]), (20, 22, 30))
    for i, (n, l) in enumerate(zip(names, labels)):
        im = Image.open(os.path.join(TMP, n + ".png")).convert("RGB").resize(cell, Image.LANCZOS)
        out.paste(tag(im, l), ((i % cols) * cell[0], (i // cols) * cell[1]))
    out.save(path, quality=86, optimize=True)


def main():
    os.makedirs(TMP, exist_ok=True)
    sim = {"prompt": "simulator"}
    jobs = [job("Sim_HUD", sim), job("Sim_Shop", sim, "Shop"), job("Sim_Machine", sim, "Machine"),
            job("Sim_Rebirth", sim, "Rebirth"), job("Sim_Index", sim, "Index"), job("Sim_Tip", sim, tip=True),
            job("Sim_NoUploads", sim, sheet=False)]
    jobs += [job("game_" + g, {"game": g}) for g in GAMES]
    jobs += [job("style_" + s, {"game": "simulator", "style": s}, "Shop") for s in STYLES]
    failed = []

    def run(j):
        name, cmd = j
        r = subprocess.run(cmd, capture_output=True, text=True)
        bad = [l for l in r.stdout.splitlines() if l.startswith(("FATAL", "WARN", "ERRORS", "STDERR"))]
        return name, bad

    with ThreadPoolExecutor(6) as ex:
        for name, bad in ex.map(run, jobs):
            print(name, "ok" if not bad else bad)
            if bad:
                failed.append(name)
    for n in ("Sim_HUD", "Sim_Shop", "Sim_Machine", "Sim_Rebirth", "Sim_Index", "Sim_Tip", "Sim_NoUploads"):
        Image.open(os.path.join(TMP, n + ".png")).convert("RGB").save(os.path.join(OUT, n + ".jpg"), quality=88, optimize=True)
    grid(["game_" + g for g in GAMES], [g.title() for g in GAMES], 2, os.path.join(OUT, "Games.jpg"), (960, 540))
    grid(["style_" + s for s in STYLES], STYLES, 3, os.path.join(OUT, "Styles.jpg"))
    for f in os.listdir(TMP):
        os.remove(os.path.join(TMP, f))
    os.rmdir(TMP)
    print("previews ->", OUT, "failed:", failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
