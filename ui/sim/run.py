"""Run the SimUI Studio plugin outside Studio and render what it builds.

    python3 ui/sim/run.py --opts '{"game":"horror"}' --out horror.png [--open Journal] [--widget w.png]

1. Loads roblox/SimUI_Plugin.lua in the Luau CLI on top of roblox_shim.luau (a stand-in for the
   engine that errors on unknown properties / enum items like Studio does).
2. Gives it a fake `plugin` whose saved settings are --opts, then clicks the widget's Build button.
3. Clones StarterGui.SimUI into PlayerGui, runs the generated LocalScript (the in-game controller),
   waits, optionally clicks the button that opens --open, waits again.
4. Renders the in-game UI (and optionally the plugin widget) with render.py.

The Luau CLI and the preview fonts are downloaded on first use into ui/sim/.bin and ui/sim/.fonts.
"""
import argparse
import json
import os
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import render  # noqa: E402

BIN = os.path.join(HERE, ".bin")
LUAU = os.path.join(BIN, "luau")
PLUGIN = os.path.join(ROOT, "roblox", "SimUI_Plugin.lua")
FONT_PACKAGES = ["bangers", "creepster", "special-elite", "michroma", "sarpanch", "jura", "oswald", "fondamento",
                 "merriweather", "grenze-gotisch", "press-start-2p", "roboto-mono", "montserrat", "nunito", "denk-one",
                 "permanent-marker", "titillium-web"]


def ensure_luau():
    if os.path.exists(LUAU):
        return LUAU
    os.makedirs(BIN, exist_ok=True)
    url = "https://github.com/luau-lang/luau/releases/latest/download/luau-ubuntu.zip"
    zp = os.path.join(BIN, "luau.zip")
    urllib.request.urlretrieve(url, zp)
    with zipfile.ZipFile(zp) as z:
        z.extract("luau", BIN)
    os.chmod(LUAU, 0o755)
    os.remove(zp)
    return LUAU


def ensure_fonts():
    os.makedirs(render.FONT_DIR, exist_ok=True)
    have = os.listdir(render.FONT_DIR)
    for pkg in FONT_PACKAGES:
        if any(f.startswith(pkg + "-latin-") for f in have):
            continue
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["npm", "pack", f"@fontsource/{pkg}", "--silent"], cwd=td, check=True,
                           stdout=subprocess.DEVNULL)
            tgz = [f for f in os.listdir(td) if f.endswith(".tgz")][0]
            with tarfile.open(os.path.join(td, tgz)) as t:
                for m in t.getmembers():
                    base = os.path.basename(m.name)
                    if base.startswith(pkg + "-latin-") and base.endswith("-normal.woff"):
                        with open(os.path.join(render.FONT_DIR, base), "wb") as f:
                            f.write(t.extractfile(m).read())


def lua_str(s):
    level = 8
    while ("]" + "=" * level + "]") in s:
        level += 1
    eq = "=" * level
    return "[" + eq + "[\n" + s + "]" + eq + "]"


def lua_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v)
    if isinstance(v, dict):
        return "{" + ", ".join(f"[{json.dumps(k)}] = {lua_value(x)}" for k, x in v.items()) + "}"
    if isinstance(v, list):
        return "{" + ", ".join(lua_value(x) for x in v) + "}"
    return "nil"


DRIVER = r"""

local SETTINGS = __SETTINGS__
local OPEN = __OPEN__
local PLAY = __PLAY__
local CLICKS = __CLICKS__
local TIP = __TIP__
local function emit(tag, s) print("@@" .. tag .. " " .. s) end
plugin = SHIM.makePlugin(SETTINGS)
local src = __SOURCE__
local fn, err = loadstring(src, "=SimUI_Plugin")
if not fn then
	emit("FATAL", '"' .. tostring(err):gsub('"', "'") .. '"')
	return
end
task.spawn(fn)
SHIM.Sched.run(0.2)
local widget = plugin.widgets[1]
local function findButton(root, pred)
	for _, d in ipairs(root:GetDescendants()) do
		if d:IsA("GuiButton") and pred(d) then return d end
	end
end
local function click(b)
	b.MouseEnter:_fire()
	b.MouseButton1Down:_fire()
	b.MouseButton1Up:_fire()
	b.MouseButton1Click:_fire()
	b.Activated:_fire()
	b.MouseLeave:_fire()
end
if widget then
	for _, name in ipairs(CLICKS) do
		local b = findButton(widget, function(d)
			return d.Name == name or d:GetAttribute("Action") == name or (d:IsA("TextButton") and d.Text == name)
		end)
		if b then click(b) else emit("WARN", '"widget button not found: ' .. name .. '"') end
		SHIM.Sched.run(SHIM.Sched.now + 0.3)
	end
	emit("WIDGET", SHIM.dump(widget))
	emit("WIDGETSIZE", ("[%d,%d]"):format(widget._size.X, widget._size.Y))
end
local gui = game:GetService("StarterGui"):FindFirstChild("SimUI")
if not gui then
	emit("FATAL", '"no StarterGui.SimUI was built"')
else
	emit("EDIT", SHIM.dump(gui))
	emit("COUNT", tostring(#gui:GetDescendants()))
	if PLAY then
		local g2 = gui:Clone()
		g2.Parent = SHIM.player.PlayerGui
		SHIM.running = true
		for _, d in ipairs(g2:GetDescendants()) do
			if d:IsA("LocalScript") then SHIM.runScript(d) end
		end
		SHIM.Sched.run(SHIM.Sched.now + 3)
		if TIP and g2:FindFirstChild("ShowTip") then
			g2.ShowTip:Fire("Shut off the lasers and RUN BACK!")
			SHIM.Sched.run(SHIM.Sched.now + 0.5)
		end
		if OPEN then
			local b = findButton(g2, function(d) return d:GetAttribute("Opens") == OPEN end)
			if b then
				click(b)
			elseif g2:FindFirstChild("OpenWindow") then
				g2.OpenWindow:Fire(OPEN)
			else
				emit("WARN", '"no button opens ' .. OPEN .. '"')
			end
			SHIM.Sched.run(SHIM.Sched.now + 2)
		end
		emit("PLAY", SHIM.dump(g2))
		local blur = workspace.CurrentCamera:FindFirstChildOfClass("BlurEffect")
		emit("BLUR", tostring(blur and blur.Enabled and blur.Size or 0))
	end
end
local errs = {}
for _, e in ipairs(SHIM.Sched.errors) do table.insert(errs, (e:gsub("\\", "/"):gsub('"', "'"):gsub("\n", " | "))) end
emit("ERRORS", #errs == 0 and "[]" or ('["' .. table.concat(errs, '","') .. '"]'))
emit("WAYPOINTS", '["' .. table.concat(SHIM.waypoints, '","') .. '"]')
"""


def run_plugin(opts=None, open_window=None, play=True, clicks=("Build",), plugin_path=PLUGIN, tip=False):
    ensure_luau()
    shim = open(os.path.join(HERE, "roblox_shim.luau")).read()
    src = open(plugin_path).read()
    settings = {"SimUIOptions": opts} if opts is not None else {}
    drv = (DRIVER.replace("__SETTINGS__", lua_value(settings))
           .replace("__OPEN__", json.dumps(open_window) if open_window else "nil")
           .replace("__PLAY__", "true" if play else "false")
           .replace("__CLICKS__", lua_value(list(clicks)))
           .replace("__TIP__", "true" if tip else "false")
           .replace("__SOURCE__", lua_str(src)))
    with tempfile.NamedTemporaryFile("w", suffix=".luau", delete=False) as f:
        f.write(shim + "\n" + drv)
        path = f.name
    try:
        r = subprocess.run([LUAU, path], capture_output=True, text=True, timeout=300)
    finally:
        os.remove(path)
    out = {"stdout": [], "stderr": r.stderr}
    for line in r.stdout.splitlines():
        if line.startswith("@@"):
            tag, _, body = line[2:].partition(" ")
            try:
                out[tag] = json.loads(body)
            except json.JSONDecodeError:
                out[tag] = body
        else:
            out["stdout"].append(line)
    return out


def background(kind, W, H):
    from PIL import Image, ImageFilter
    import numpy as np
    bgs = {
        "simulator": ((126, 206, 255), (94, 190, 90)), "tycoon": ((150, 214, 255), (120, 170, 110)),
        "obby": ((110, 190, 255), (255, 170, 90)), "fighting": ((70, 80, 120), (30, 30, 50)),
        "horror": ((24, 26, 30), (6, 6, 8)), "racing": ((140, 190, 240), (70, 70, 80)),
        "rpg": ((150, 200, 230), (80, 120, 70)), "shooter": ((170, 180, 190), (90, 95, 90)),
        "tower": ((140, 210, 140), (90, 150, 80)), "roleplay": ((160, 215, 255), (140, 190, 130)),
    }
    top, bot = bgs.get(kind, bgs["simulator"])
    t = np.linspace(0, 1, H).reshape(H, 1, 1)
    arr = (np.array(top) * (1 - t) + np.array(bot) * t) * np.ones((1, W, 1))
    rng = np.random.default_rng(3)
    img = Image.fromarray(arr.astype(np.uint8), "RGB")
    from PIL import ImageDraw
    d = ImageDraw.Draw(img, "RGBA")
    horizon = int(H * 0.55)
    for i in range(24):
        x = int(rng.uniform(0, W))
        w = int(rng.uniform(60, 220))
        h = int(rng.uniform(80, 300))
        c = tuple(int(v) for v in (np.array(bot) * rng.uniform(0.6, 1.1)).clip(0, 255)) + (160,)
        d.rectangle((x, horizon - h, x + w, horizon + 40), fill=c)
    d.rectangle((0, horizon, W, H), fill=tuple(int(v * 0.85) for v in bot) + (255,))
    return img.filter(ImageFilter.GaussianBlur(6))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--opts", default="{}")
    ap.add_argument("--out", default="preview.png")
    ap.add_argument("--open", default=None)
    ap.add_argument("--widget", default=None)
    ap.add_argument("--edit", action="store_true", help="render the StarterGui copy instead of the played one")
    ap.add_argument("--plugin", default=PLUGIN)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--clicks", default="Build", help="comma separated widget buttons to click")
    ap.add_argument("--sheet", action="store_true", help="pretend the icon sheet is uploaded (renders the 3D icons)")
    ap.add_argument("--tip", action="store_true", help="show the tutorial tip")
    args = ap.parse_args()
    ensure_fonts()
    opts = json.loads(args.opts)
    if args.sheet:
        from PIL import Image
        opts["iconSheet"] = "rbxassetid://1001"
        render.IMAGES["rbxassetid://1001"] = Image.open(os.path.join(ROOT, "ui", "icons", "Atlas_Icons.png")).convert("RGBA")
    res = run_plugin(opts or None, args.open, plugin_path=args.plugin, clicks=args.clicks.split(","), tip=args.tip)
    for k in ("FATAL", "WARN", "ERRORS"):
        if res.get(k):
            print(k, json.dumps(res[k], indent=1)[:4000])
    if res.get("stderr"):
        print("STDERR", res["stderr"][:4000])
    if res.get("stdout"):
        print("\n".join(res["stdout"])[:3000])
    W, H = (int(v) for v in args.size.split("x"))
    tree = res.get("EDIT") if args.edit else res.get("PLAY") or res.get("EDIT")
    if tree:
        kind = (tree.get("a") or {}).get("GameType", "simulator")
        bg = background(kind, W, H)
        blur = float(res.get("BLUR") or 0) if not args.edit else 0
        if blur > 0:
            from PIL import ImageFilter
            bg = bg.filter(ImageFilter.GaussianBlur(blur * 0.9))
        img, n = render.render_gui(tree, W, H, bg)
        img.save(args.out)
        print("rendered", args.out, "nodes", n, "instances", res.get("COUNT"))
    if args.widget and res.get("WIDGET"):
        ws = res.get("WIDGETSIZE", [380, 600])
        img, _ = render.render_gui(res["WIDGET"], ws[0], ws[1], None, topbar=False)
        img.save(args.widget)
        print("widget", args.widget)


if __name__ == "__main__":
    main()
