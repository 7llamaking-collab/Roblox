--[[
	SimUI Generator 2 - a whole game UI for Roblox from a prompt and a few controls.
	No AI: it is keyword matching plus hand-made presets, and everything it makes is plain Roblox UI
	you can edit afterwards.

	INSTALL
	  Studio > Plugins tab > Plugins Folder: drop this file in (keep the .lua ending), restart Studio.
	  Click "SimUI" in the Plugins tab to open the panel. (Or paste the file into the Command Bar once:
	  it builds the PROMPT below with every option on "auto".)

	WHAT CHANGES WHAT
	  Game    where things go: simulator, tycoon, obby, fighting, horror, racing, rpg, shooter,
	          tower defense, roleplay. Each has its own HUD placement and its own windows.
	  Style   how things look and feel: Studs, Bubbly, Cartoon, Horror, Anime, SciFi, Fantasy,
	          Minimal, Pixel, Glass. Each draws buttons, panels, bars, headers, menus and icons
	          differently and has its own fonts and animations.
	  Colours 26 palettes. Colour words ("red", "pink"...) recolour the main buttons.
	  Then every detail can be overridden: font, shape, corners, outline, shadow, surface, studs,
	  menu buttons, windows, motion, icons, text case, size, and Shuffle for variations.

	PROMPT EXAMPLES
	  '"Pet Legends" candy simulator'   'scary horror'   'anime fighting'   'neon scifi shooter'
	  'medieval rpg'   'clean minimal tycoon'   'retro pixel obby'   'glass roleplay'   'cartoon tower defense'

	The result goes to StarterGui > SimUI, with a LocalScript that opens and closes the windows,
	animates the buttons in the style's own way, scales the UI for every screen and shows leaderstats.
]]

local PROMPT = "simulator"
local VERSION = "2.0"

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterGui = game:GetService("StarterGui")
local ChangeHistoryService = game:GetService("ChangeHistoryService")
local SelectionService = game:GetService("Selection")

-----------------------------------------------------------------------------------------------
-- helpers
-----------------------------------------------------------------------------------------------
local WHITE, BLACK = Color3.new(1, 1, 1), Color3.new(0, 0, 0)

local function hex(h)
	h = h:gsub("#", "")
	return Color3.fromRGB(tonumber(h:sub(1, 2), 16), tonumber(h:sub(3, 4), 16), tonumber(h:sub(5, 6), 16))
end

local function darker(c, t)
	return c:Lerp(BLACK, t)
end

local function lighter(c, t)
	return c:Lerp(WHITE, t)
end

local function lum(c)
	return 0.299 * c.R + 0.587 * c.G + 0.114 * c.B
end

local function saturate(c, f)
	local h, s, v = c:ToHSV()
	return Color3.fromHSV(h, math.clamp(s * f, 0, 1), v)
end

local function commas(n)
	local s = tostring(math.floor(n))
	local out = s:reverse():gsub("(%d%d%d)", "%1,"):reverse()
	return (out:gsub("^,", ""))
end

local function copy(t)
	local o = {}
	for k, v in pairs(t) do
		o[k] = v
	end
	return o
end

local function new(class, props)
	local o = Instance.new(class)
	if o:IsA("GuiObject") then
		o.BorderSizePixel = 0
	end
	local parent = nil
	for k, v in pairs(props or {}) do
		if k == "Parent" then
			parent = v
		else
			o[k] = v
		end
	end
	if parent then
		o.Parent = parent
	end
	return o
end

local function frame(parent, name, props)
	props = props or {}
	props.Name = name
	props.Parent = parent
	if props.BackgroundTransparency == nil then
		props.BackgroundTransparency = 1
	end
	return new("Frame", props)
end

local function wordList(s)
	local out = {}
	for w in s:lower():gmatch("[%a%d]+") do
		table.insert(out, w)
	end
	return out
end

local function hasWord(list, w)
	for _, x in ipairs(list) do
		if x == w then
			return true
		end
	end
	return false
end

-----------------------------------------------------------------------------------------------
-- colour palettes (roles: buttons, panels, outline, title gradient)
-----------------------------------------------------------------------------------------------
local PALETTES = {
	Classic = {"2FA4FF", "43D162", "FFC933", "3E8EF7", "2361D6", "9FD2FF", "10275C", "FFFFFF", "FFE25A"},
	Candy = {"FF6FB5", "B57BFF", "6FE3FF", "FF9ACB", "E75CA8", "FFE0F0", "6A1B4D", "FFFFFF", "FFB3E0"},
	Ocean = {"1FC8E8", "2BD9A4", "FFD85A", "1AA7D9", "0B6FB0", "A9ECFF", "06304F", "FFFFFF", "8FF3FF"},
	Lava = {"FF5A2A", "FFB02E", "FFE14D", "D8431E", "8E1D0E", "FFC0A0", "3A0A04", "FFF3B0", "FF7A1A"},
	Forest = {"4CC94F", "A9D13C", "FFC94A", "5BAA3C", "357A26", "D6F5B8", "173A10", "FFFFFF", "C8FF6A"},
	Galaxy = {"8A5CFF", "3FD2FF", "FF6BE6", "3A2A8C", "1B1248", "8C7BE0", "0A0620", "FFFFFF", "C9A6FF"},
	Neon = {"FF2FD0", "28F0FF", "F7FF3C", "26214A", "110E26", "4B3F8E", "05030F", "FFFFFF", "28F0FF"},
	Winter = {"5CC8FF", "A6E6FF", "FFFFFF", "E6F6FF", "A8D8F5", "FFFFFF", "1B4A73", "FFFFFF", "9FE3FF"},
	Spooky = {"FF8A1F", "9B4DFF", "7CFF4D", "3A2450", "1C1028", "6B4A8C", "0C0612", "FFE7B0", "FF8A1F"},
	Holiday = {"E8323C", "2DB34A", "FFD24A", "C9252E", "7E1219", "FFE3C4", "3B0507", "FFFFFF", "FFD24A"},
	Royal = {"FFC21A", "B884FF", "FFFFFF", "2B2440", "141022", "4E4466", "1A1200", "FFF6C0", "FFB300"},
	Desert = {"F2A53A", "E3683B", "56C7D9", "E3B878", "B77D3E", "FFE9C2", "4A2A0E", "FFF6D8", "FFB54A"},
	Toxic = {"8CFF2E", "C04DFF", "FFE93A", "2E3A1E", "141A0C", "4D6630", "060A02", "F3FFB0", "8CFF2E"},
	Pastel = {"8FD3FF", "FFB3C7", "FFE38A", "FFF4E8", "F2D9C4", "FFFFFF", "6B4E5E", "FFFFFF", "FFC9D9"},
	Military = {"7A8F3C", "C9A55A", "E8D27A", "4A5530", "2A3119", "7A8757", "121608", "F2F0D0", "C9D17A"},
	Midnight = {"4F7CFF", "3DDC97", "FFD166", "2A2E3A", "171A22", "3C4252", "07080C", "FFFFFF", "A9B8FF"},
	Sunset = {"FF7A45", "FF4F8B", "FFD24A", "FF9A5A", "E0507A", "FFE3C9", "4A1024", "FFFFFF", "FFD24A"},
	Blood = {"B3121E", "5E0B10", "E8E0D0", "141214", "0A090A", "2A2426", "000000", "E8E0D0", "B3121E"},
	Fog = {"7FA38C", "5C6770", "D9D2B8", "1A1D1E", "0E1011", "2C3234", "050606", "D9D2B8", "7FA38C"},
	Crimson = {"FF2E4D", "3D5AFE", "FFD23F", "15182B", "0B0D19", "262B4A", "05060C", "FFFFFF", "FF2E4D"},
	Cyber = {"20E3FF", "FF3DF2", "B6FF3D", "0B1622", "050B12", "12324A", "001018", "E8FDFF", "20E3FF"},
	Medieval = {"8B5A2B", "A51C1C", "E8B64A", "EFDDB2", "D8BE88", "F7EBCB", "3B2412", "FFF1C9", "E8B64A"},
	Clean = {"3B82F6", "10B981", "F59E0B", "FFFFFF", "F1F4F9", "E6EBF2", "D5DCE6", "1F2937", "1F2937"},
	Dark = {"6C8CFF", "3DDC97", "FFB84D", "1E2028", "16181E", "2A2D38", "0C0D11", "FFFFFF", "C9D1FF"},
	Retro = {"E4572E", "2E86DE", "F3A712", "1D1B2F", "0F0E1A", "3A3760", "000000", "FFFFFF", "F3A712"},
	Speed = {"FF6B00", "2F80ED", "FFD400", "1C1C1E", "0F0F10", "2C2C2E", "000000", "FFFFFF", "FF6B00"},
}
local PALETTE_ORDER = {"Classic", "Candy", "Ocean", "Lava", "Forest", "Galaxy", "Neon", "Winter", "Spooky", "Holiday",
	"Royal", "Desert", "Toxic", "Pastel", "Military", "Midnight", "Sunset", "Blood", "Fog", "Crimson", "Cyber",
	"Medieval", "Clean", "Dark", "Retro", "Speed"}
local PALETTE_WORDS = {
	Classic = "classic default bright blue", Candy = "candy sweet pink cute kawaii bubblegum sugar",
	Ocean = "ocean sea water aqua beach fish fishing island teal", Lava = "lava fire volcano hell inferno flame magma dragon",
	Forest = "forest nature jungle green farm garden wood tree plant", Galaxy = "galaxy space cosmic star alien planet universe purple moon",
	Neon = "neon synthwave arcade", Winter = "winter ice snow frost frozen cold arctic",
	Spooky = "spooky halloween pumpkin", Holiday = "christmas xmas holiday festive santa gift",
	Royal = "royal gold golden luxury rich king vip premium", Desert = "desert sand egypt pyramid western cowboy canyon",
	Toxic = "toxic slime radioactive acid lime mutant poison", Pastel = "pastel cozy cottage bunny spring easter",
	Military = "military army soldier tank camo tactical", Midnight = "midnight night shadow ninja",
	Sunset = "sunset tropical orange summer vibes paradise", Blood = "blood gore dread", Fog = "fog mist asylum backrooms",
	Crimson = "crimson", Cyber = "cyber cyberpunk hologram hacker matrix", Medieval = "medieval castle knight kingdom",
	Clean = "light white", Dark = "dark black", Retro = "retro nes", Speed = "speed nitro",
}
local ROLE_NAMES = {"Primary", "Secondary", "Accent", "Panel", "Panel2", "Inner", "Outline", "TitleTop", "TitleBottom"}
local COLOR_WORDS = {red = "E8323C", orange = "FF8A1F", yellow = "FFD21F", gold = "FFC21A", green = "43D162",
	lime = "8CFF2E", teal = "1FC8C0", cyan = "28F0FF", blue = "2F7BFF", navy = "1F3F9E", purple = "8A5CFF",
	violet = "A35CFF", pink = "FF6FB5", magenta = "FF2FD0", brown = "9A6A3A"}

-----------------------------------------------------------------------------------------------
-- fonts (FontFace with weights; anything missing falls back to Gotham)
-----------------------------------------------------------------------------------------------
local FONT_CHOICES = {"FredokaOne", "LuckiestGuy", "Bangers", "Creepster", "SpecialElite", "Michroma", "Sarpanch",
	"Jura", "Oswald", "Fondamento", "Merriweather", "GrenzeGotisch", "Arcade", "GothamBold", "Nunito", "DenkOne",
	"PermanentMarker", "TitilliumWeb", "RobotoMono"}

local fontCache = {}
local function fontFace(name, weight)
	local key = name .. "/" .. tostring(weight)
	if fontCache[key] then
		return fontCache[key]
	end
	local ok, f = pcall(function()
		return Font.fromEnum(Enum.Font[name])
	end)
	if not ok or not f then
		f = Font.fromEnum(Enum.Font.GothamBold)
	end
	if weight then
		local ok2, f2 = pcall(function()
			return Font.new(f.Family, Enum.FontWeight[weight])
		end)
		if ok2 and f2 then
			f = f2
		end
	end
	fontCache[key] = f
	return f
end

-----------------------------------------------------------------------------------------------
-- icons: emoji, or flat vector icons built from Frames (for the cleaner styles)
-- shapes are in a 100 x 100 box: {"r", cx, cy, w, h, rotation, radius, tone}
-- {"c", cx, cy, diameter, tone}  {"o", cx, cy, diameter, thickness, tone}  tone 2 = second colour
-----------------------------------------------------------------------------------------------
local EMOJI = {
	shop = "🛒", pets = "🐾", rebirth = "🔁", settings = "⚙️", codes = "🎟️", index = "📘", daily = "🎁", quests = "📜",
	bag = "🎒", map = "🗺️", star = "⭐", trophy = "🏆", home = "🏠", lock = "🔒", heart = "❤️", bolt = "⚡", coin = "🪙",
	gem = "💎", cash = "💵", skull = "💀", car = "🏎️", sword = "⚔️", shield = "🛡️", target = "🎯", flag = "🚩",
	clock = "⏱️", user = "👤", phone = "📱", shirt = "👕", jobs = "💼", journal = "📓", ammo = "🔫", gauge = "🏁",
	egg = "🥚", friends = "👥", upgrade = "⬆️", tower = "🏰", strength = "💪", luck = "🍀", potion = "🧪",
	fire = "🔥", water = "💧", music = "🎵", close = "✖️", plus = "➕", check = "✔️", key = "🔑", battery = "🔋",
	light = "🔦", eye = "👁️", house = "🏡", apple = "🍎", banana = "🍌", cookie = "🍪", berry = "🫐", pet = "🐶",
	fish = "🐡", unknown = "❔", crown = "👑", rocket = "🚀", wrench = "🔧", magnet = "🧲", dice = "🎲",
	bow = "🏹", staff = "🪄", note = "📝", paw = "🐾", robux = "💠", speed = "💨", nitro = "🔥", fishing = "🎣",
	goldbars = "💰", ufo = "🛸", heli = "🚁", hammer = "🔨", bat = "🏏", crate = "📦", mushroom = "🍄", taco = "🌮",
	basket = "🧺", vip = "👑", timer = "⏳",
}

local ICONS = {
	shop = {{"r", 50, 46, 62, 34, 0, 6}, {"r", 22, 24, 22, 8, 0, 3}, {"c", 34, 78, 16, 2}, {"c", 68, 78, 16, 2},
		{"r", 50, 46, 44, 5, 0, 2, 2}},
	pets = {{"c", 50, 64, 40}, {"c", 24, 40, 18}, {"c", 41, 24, 18}, {"c", 60, 24, 18}, {"c", 77, 40, 18}},
	rebirth = {{"o", 50, 50, 62, 13}, {"r", 72, 26, 26, 26, 45, 4}, {"r", 28, 74, 26, 26, 45, 4}},
	settings = "gear",
	codes = {{"r", 50, 50, 76, 44, -14, 7}, {"r", 50, 50, 6, 30, -14, 2, 2}, {"c", 34, 53, 8, 2}, {"c", 66, 45, 8, 2}},
	index = {{"r", 31, 50, 34, 64, -4, 5}, {"r", 69, 50, 34, 64, 4, 5}, {"r", 50, 52, 6, 66, 0, 2, 2}},
	daily = {{"r", 50, 62, 62, 42, 0, 5}, {"r", 50, 38, 72, 16, 0, 4}, {"r", 50, 56, 12, 56, 0, 0, 2},
		{"c", 40, 24, 18, 2}, {"c", 60, 24, 18, 2}},
	quests = {{"r", 50, 50, 54, 72, 0, 7}, {"r", 50, 34, 34, 6, 0, 2, 2}, {"r", 50, 48, 34, 6, 0, 2, 2},
		{"r", 44, 62, 22, 6, 0, 2, 2}},
	bag = {{"r", 50, 58, 62, 50, 0, 14}, {"o", 50, 30, 30, 8}, {"r", 50, 58, 30, 14, 0, 4, 2}},
	map = {{"r", 50, 50, 76, 60, 0, 5}, {"r", 36, 50, 5, 60, 0, 0, 2}, {"r", 64, 50, 5, 60, 0, 0, 2},
		{"c", 72, 38, 16, 2}},
	star = {{"r", 50, 50, 50, 50, 0, 8}, {"r", 50, 50, 50, 50, 45, 8}, {"c", 50, 50, 22, 2}},
	trophy = {{"r", 50, 34, 46, 38, 0, 16}, {"r", 50, 60, 12, 18}, {"r", 50, 76, 40, 12, 0, 3}, {"o", 26, 34, 22, 6},
		{"o", 74, 34, 22, 6}},
	home = {{"r", 50, 64, 54, 40, 0, 4}, {"r", 50, 40, 44, 44, 45, 5}, {"r", 50, 72, 14, 24, 0, 3, 2}},
	lock = {{"o", 50, 36, 38, 9}, {"r", 50, 64, 58, 44, 0, 8}, {"c", 50, 62, 12, 2}},
	heart = {{"c", 34, 40, 38}, {"c", 66, 40, 38}, {"r", 50, 56, 44, 44, 45, 5}},
	bolt = {{"r", 56, 30, 16, 44, 28, 2}, {"r", 44, 70, 16, 44, 28, 2}, {"r", 50, 50, 36, 12, -8, 2}},
	coin = {{"c", 50, 50, 74}, {"o", 50, 50, 50, 6, 2}, {"r", 50, 50, 8, 24, 0, 2, 2}},
	gem = {{"r", 50, 52, 52, 52, 45, 6}, {"r", 50, 42, 20, 20, 45, 3, 2}},
	cash = {{"r", 50, 50, 80, 48, 0, 6}, {"c", 50, 50, 22, 2}, {"r", 20, 50, 8, 8, 45, 1, 2}, {"r", 80, 50, 8, 8, 45, 1, 2}},
	skull = {{"c", 50, 42, 62}, {"r", 50, 66, 38, 24, 0, 6}, {"c", 38, 44, 14, 2}, {"c", 62, 44, 14, 2},
		{"r", 50, 70, 4, 14, 0, 1, 2}},
	car = {{"r", 50, 58, 84, 26, 0, 10}, {"r", 48, 40, 46, 22, 0, 10}, {"c", 28, 72, 20, 2}, {"c", 72, 72, 20, 2}},
	sword = {{"r", 58, 42, 11, 62, 45, 3}, {"r", 32, 68, 32, 9, 45, 3}, {"r", 24, 76, 9, 20, 45, 3, 2}},
	shield = {{"r", 50, 40, 58, 44, 0, 10}, {"r", 50, 58, 42, 42, 45, 6}, {"r", 50, 50, 8, 44, 0, 2, 2},
		{"r", 50, 44, 36, 8, 0, 2, 2}},
	target = {{"o", 50, 50, 70, 8}, {"o", 50, 50, 38, 8}, {"c", 50, 50, 12}},
	flag = {{"r", 24, 52, 7, 80, 0, 2}, {"r", 52, 32, 50, 32, 0, 4}},
	clock = {{"o", 50, 55, 64, 9}, {"r", 50, 46, 6, 22, 0, 2}, {"r", 57, 57, 18, 6, 0, 2}, {"r", 50, 16, 16, 8, 0, 2}},
	user = {{"c", 50, 32, 34}, {"r", 50, 74, 60, 36, 0, 18}},
	phone = {{"r", 50, 50, 42, 76, 0, 9}, {"r", 50, 47, 30, 52, 0, 3, 2}, {"c", 50, 80, 7, 2}},
	shirt = {{"r", 50, 58, 42, 54, 0, 6}, {"r", 28, 36, 18, 28, 50, 4}, {"r", 72, 36, 18, 28, -50, 4},
		{"r", 50, 32, 16, 8, 0, 3, 2}},
	jobs = {{"r", 50, 58, 74, 46, 0, 8}, {"o", 50, 34, 28, 7}, {"r", 50, 56, 74, 5, 0, 0, 2}},
	journal = {{"r", 52, 50, 56, 74, 0, 6}, {"r", 29, 50, 8, 74, 0, 2, 2}, {"r", 56, 34, 28, 8, 0, 2, 2}},
	ammo = {{"r", 36, 58, 16, 50, 0, 3}, {"c", 36, 32, 16}, {"r", 64, 58, 16, 50, 0, 3}, {"c", 64, 32, 16}},
	gauge = {{"o", 50, 58, 70, 10}, {"r", 60, 48, 6, 34, 40, 2}, {"c", 50, 58, 12}},
	egg = {{"c", 50, 58, 60}, {"c", 50, 42, 46}},
	friends = {{"c", 36, 34, 26}, {"r", 36, 68, 42, 32, 0, 14}, {"c", 66, 38, 24, 2}, {"r", 68, 70, 36, 28, 0, 12, 2}},
	upgrade = {{"r", 50, 64, 18, 40, 0, 3}, {"r", 50, 40, 40, 40, 45, 5}},
	tower = {{"r", 50, 60, 44, 56, 0, 3}, {"r", 32, 26, 12, 14}, {"r", 50, 26, 12, 14}, {"r", 68, 26, 12, 14},
		{"r", 50, 70, 14, 22, 0, 6, 2}},
	strength = {{"r", 50, 50, 56, 10, 0, 3}, {"r", 20, 50, 12, 36, 0, 3}, {"r", 80, 50, 12, 36, 0, 3},
		{"r", 30, 50, 8, 24, 0, 2}, {"r", 70, 50, 8, 24, 0, 2}},
	luck = {{"c", 36, 36, 30}, {"c", 64, 36, 30}, {"c", 36, 62, 30}, {"c", 64, 62, 30}, {"r", 62, 80, 6, 26, -30, 2}},
	potion = {{"c", 50, 62, 52}, {"r", 50, 30, 18, 26, 0, 3}, {"r", 50, 18, 26, 8, 0, 3, 2}, {"r", 50, 66, 38, 8, 0, 3, 2}},
	fire = {{"c", 50, 64, 46}, {"r", 50, 44, 34, 34, 45, 6}, {"c", 50, 66, 22, 2}},
	music = {{"c", 34, 70, 22}, {"c", 70, 62, 22}, {"r", 43, 44, 6, 50, 0, 2}, {"r", 79, 36, 6, 50, 0, 2},
		{"r", 61, 22, 42, 8, -10, 2}},
	close = {{"r", 50, 50, 14, 74, 45, 5}, {"r", 50, 50, 14, 74, -45, 5}},
	plus = {{"r", 50, 50, 16, 66, 0, 5}, {"r", 50, 50, 66, 16, 0, 5}},
	check = {{"r", 36, 60, 14, 34, -45, 5}, {"r", 60, 50, 14, 58, 40, 5}},
	key = {{"o", 32, 50, 34, 9}, {"r", 64, 50, 44, 10, 0, 3}, {"r", 78, 60, 8, 16, 0, 2}},
	battery = {{"r", 46, 50, 64, 38, 0, 6}, {"r", 82, 50, 8, 16, 0, 2}, {"r", 32, 50, 22, 26, 0, 2, 2}},
	light = {{"r", 40, 50, 46, 22, 0, 4}, {"r", 72, 50, 20, 38, 0, 4}, {"r", 90, 50, 6, 44, 0, 2, 2}},
	eye = {{"c", 50, 50, 64}, {"c", 50, 50, 30, 2}, {"c", 56, 44, 10}},
	crown = {{"r", 50, 64, 64, 26, 0, 4}, {"r", 22, 42, 18, 18, 45, 3}, {"r", 50, 36, 20, 20, 45, 3}, {"r", 78, 42, 18, 18, 45, 3}},
	rocket = {{"r", 50, 46, 26, 52, 0, 12}, {"r", 50, 22, 18, 18, 45, 4}, {"r", 34, 70, 14, 22, 20, 3},
		{"r", 66, 70, 14, 22, -20, 3}, {"c", 50, 44, 12, 2}},
	unknown = {{"o", 50, 38, 40, 10}, {"r", 50, 62, 10, 16, 0, 3}, {"c", 50, 80, 10}},
}
ICONS.paw = ICONS.pets
ICONS.pet = ICONS.pets
ICONS.house = ICONS.home
ICONS.nitro = ICONS.fire
ICONS.speed = ICONS.gauge
ICONS.robux = ICONS.gem
ICONS.apple = ICONS.heart
ICONS.banana = ICONS.bolt
ICONS.cookie = ICONS.coin
ICONS.berry = ICONS.gem
ICONS.fish = ICONS.egg
ICONS.water = ICONS.potion
ICONS.wrench = ICONS.settings
ICONS.magnet = ICONS.upgrade
ICONS.dice = ICONS.star
ICONS.bow = ICONS.sword
ICONS.staff = ICONS.sword
ICONS.note = ICONS.quests
ICONS.fishing = ICONS.sword
ICONS.goldbars = ICONS.coin
ICONS.ufo = ICONS.rocket
ICONS.heli = ICONS.rocket
ICONS.hammer = {{"r", 40, 60, 12, 66, -35, 4}, {"r", 62, 30, 50, 24, -35, 5}, {"r", 73, 22, 14, 28, -35, 3, 2}}
ICONS.bat = ICONS.sword
ICONS.crate = ICONS.daily
ICONS.mushroom = {{"r", 50, 72, 26, 40, 0, 8}, {"c", 50, 44, 76}, {"r", 50, 62, 80, 20, 0, 6}, {"c", 36, 36, 14, 2},
	{"c", 62, 30, 12, 2}}
ICONS.taco = ICONS.coin
ICONS.basket = ICONS.shop
ICONS.vip = ICONS.crown
ICONS.timer = ICONS.clock

-- the icon sheet from ui/icons (Atlas_Icons.png, 1024 px): names in order, 9 per row, 112 px cells
local ICON_SHEET = {"Alert", "ArrowDown", "ArrowLeft", "ArrowRight", "ArrowUp", "Backpack", "Basket", "Bat",
	"Battery", "Bell", "Bomb", "Boost", "Cash", "Check", "Chest", "Clock", "Close", "Codes", "Coin", "Crate",
	"Crown", "Daily", "Dice", "Egg", "Energy", "Fire", "FishingRod", "Friends", "Gem", "Gift", "GoldBars",
	"GoldenEgg", "Hammer", "Heart", "Helicopter", "Home", "Index", "Info", "Key", "Lock", "Luck", "Magnet", "Map",
	"Medal", "Minus", "MoneyBag", "Mushroom", "Music", "Paw", "Pet", "Pickaxe", "Plus", "PotionBlue", "PotionGreen",
	"PotionRed", "PotionYellow", "Question", "Quests", "RainbowEgg", "Rebirth", "Search", "Settings", "Shield",
	"Shop", "Skull", "Sound", "Star", "Strength", "Sword", "Taco", "Teleport", "Timer", "Trade", "Trophy", "UFO",
	"Unlock", "Upgrade", "VIP", "World"}
local ICON_RECT = {}
for i, n in ipairs(ICON_SHEET) do
	ICON_RECT[n] = {2 + ((i - 1) % 9) * 113, 2 + math.floor((i - 1) / 9) * 113, 112, 112}
end

-- icon key -> name in that sheet
local KIT_ICON = {fishing = "FishingRod", goldbars = "GoldBars", ufo = "UFO", heli = "Helicopter", hammer = "Hammer",
	bat = "Bat", crate = "Crate", mushroom = "Mushroom", taco = "Taco", basket = "Basket", cart = "Shop", vip = "VIP",
	tip = "Pet", shop = "Shop", pets = "Paw", rebirth = "Rebirth", settings = "Settings", codes = "Codes",
	index = "Index", daily = "Gift", quests = "Quests", bag = "Backpack", map = "Map", star = "Star", trophy = "Trophy",
	home = "Home", lock = "Lock", heart = "Heart", bolt = "Energy", coin = "Coin", gem = "Gem", cash = "Cash",
	skull = "Skull", sword = "Sword", shield = "Shield",
	strength = "Strength", luck = "Luck", potion = "PotionGreen", fire = "Fire", music = "Music", key = "Key",
	egg = "Egg", crown = "Crown", battery = "Battery", magnet = "Magnet", dice = "Dice", pet = "Pet", paw = "Paw",
	clock = "Clock", timer = "Timer", journal = "Quests", note = "Quests", unknown = "Question", friends = "Friends",
	upgrade = "Upgrade", water = "PotionBlue", user = "Pet"}

-----------------------------------------------------------------------------------------------
-- styles: each one draws every piece differently (shape, surface, outline, shadow, decorations,
-- fonts, menus, windows, bars, motion). paint(T, key, role) colours a surface for a colour key.
-----------------------------------------------------------------------------------------------
local STD = {Green = "56D63B", Blue = "2FA4FF", Orange = "FF9A1F", Red = "F0443A", Yellow = "FFD21F",
	Purple = "A35CFF", Pink = "FF5FAE", Cyan = "27D8E8", Gray = "9AA3B2", Gold = "FFC21A"}

local function P(T, key)
	return T.color(key)
end

local STYLES = {}
local STYLE_ORDER = {"Sim", "Studs", "Bubbly", "Cartoon", "Horror", "Anime", "SciFi", "Fantasy", "Minimal", "Pixel",
	"Glass"}
local INK = hex("1B1B22")

-- the look of today's big simulator / "steal a" games: white windows with a thick dark outline and the
-- title on the border, gradient buttons with halftone dots, dark round menu buttons with 3D icons,
-- currencies on fading bars, hexagon badges
STYLES.Sim = {
	fonts = {title = {"FredokaOne"}, button = {"FredokaOne"}, body = {"FredokaOne"}, number = {"FredokaOne"}},
	case = "title", shape = "rounded", radius = 12, outline = "ink", outlineW = 3.5, shadow = "none", shadowD = 0,
	surface = "vivid", studs = false, gloss = false, shine = true, deco = {"rim", "dots"}, tilt = 0,
	menu = "rings", windows = "popup", header = "border", close = "square", bars = "pill", currency = "fade",
	motion = "bouncy", icons = "emoji", textStroke = 3, palette = "Classic", colorful = true, cards = "hex",
	blur = true, hotbar = "slate", boosts = "hex",
	std = {Green = "4FD62C", Blue = "3AA0F5", Orange = "FF9A1F", Red = "EE3B3B", Yellow = "F2C23A", Purple = "B25CF0",
		Pink = "F24FC8", Cyan = "35CFF0", Gray = "9AA3B2", Gold = "E9B83C"},
	paint = function(T, key, role)
		local c = T.color(key)
		if role == "tabOff" then c = hex("AEB5C2") end
		return {fill = c, stroke = INK, strokeW = 3.5, text = WHITE, textStroke = INK, accent = c}
	end,
	panel = function(T)
		return {fill = WHITE, t = 0, stroke = INK, strokeW = 5, text = INK, dim = hex("8C8FA6"), inner = hex("F4F1FB"),
			innerT = 0, line = hex("DCD6EC"), tint = hex("EEE7FF")}
	end,
}

STYLES.Studs = {
	fonts = {title = {"FredokaOne"}, button = {"FredokaOne"}, body = {"FredokaOne"}, number = {"FredokaOne"}},
	case = "title", shape = "rounded", radius = 12, outline = "dark", outlineW = 3, shadow = "lip", shadowD = 6,
	surface = "gradient", studs = true, gloss = true, shine = true, deco = {}, tilt = 0,
	menu = "tiles", windows = "popup", header = "bar", close = "square", bars = "studded", currency = "pill",
	motion = "bouncy", icons = "emoji", textStroke = 2.5, palette = "Classic", colorful = true,
	paint = function(T, key, role)
		local c = P(T, key)
		if role == "tabOff" then c = T.color("Gray") end
		return {fill = c, stroke = darker(c, 0.55), text = WHITE, textStroke = darker(c, 0.62), accent = c}
	end,
	panel = function(T)
		return {fill = darker(T.Panel2, 0.35), t = 0.1, stroke = T.Outline, strokeW = 3, text = WHITE,
			dim = lighter(T.Inner, 0.2), inner = darker(T.Panel2, 0.15), innerT = 0.2, line = T.Inner}
	end,
}

STYLES.Bubbly = {
	fonts = {title = {"FredokaOne"}, button = {"FredokaOne"}, body = {"FredokaOne"}, number = {"FredokaOne"}},
	case = "title", shape = "pill", radius = 26, outline = "white", outlineW = 4, shadow = "soft", shadowD = 7,
	surface = "glossy", studs = false, gloss = true, shine = true, deco = {"spot"}, tilt = 0,
	menu = "circles", windows = "popup", header = "tag", close = "round", bars = "pill", currency = "bubble",
	motion = "squish", icons = "emoji", textStroke = 2.5, palette = "Candy", colorful = true,
	paint = function(T, key, role)
		local c = lighter(P(T, key), 0.1)
		if role == "tabOff" then c = lighter(T.color("Gray"), 0.3) end
		return {fill = c, stroke = WHITE, text = WHITE, textStroke = darker(c, 0.45), accent = c}
	end,
	panel = function(T)
		return {fill = lighter(T.Inner, 0.35), t = 0, stroke = WHITE, strokeW = 5, text = darker(T.Outline, 0.1),
			dim = T.Outline:Lerp(WHITE, 0.35), inner = WHITE, innerT = 0.15, line = T.Panel, outer = T.Panel2}
	end,
}

STYLES.Cartoon = {
	fonts = {title = {"LuckiestGuy"}, button = {"LuckiestGuy"}, body = {"LuckiestGuy"}, number = {"LuckiestGuy"}},
	case = "upper", shape = "rounded", radius = 9, outline = "black", outlineW = 4, shadow = "hard", shadowD = 6,
	surface = "flat", studs = false, gloss = false, shine = false, deco = {"spot", "halftone"}, tilt = -2,
	menu = "tiles", windows = "popup", header = "tag", close = "round", bars = "thick", currency = "sticker",
	motion = "press", icons = "emoji", textStroke = 3, palette = "Classic", colorful = true,
	paint = function(T, key, role)
		local c = P(T, key)
		if role == "tabOff" then c = hex("C9CED8") end
		return {fill = c, stroke = hex("141414"), text = WHITE, textStroke = hex("141414"), accent = c}
	end,
	panel = function(T)
		return {fill = hex("FFF6E0"), t = 0, stroke = hex("141414"), strokeW = 4, text = hex("2A2320"),
			dim = hex("7A6F66"), inner = WHITE, innerT = 0, line = hex("141414")}
	end,
}

STYLES.Horror = {
	fonts = {title = {"Creepster"}, button = {"SpecialElite"}, body = {"SpecialElite"}, number = {"SpecialElite"}},
	case = "lower", shape = "square", radius = 2, outline = "thin", outlineW = 1, shadow = "none", shadowD = 0,
	surface = "flat", studs = false, gloss = false, shine = false, deco = {"scratches"}, tilt = 0,
	menu = "rows", windows = "fullscreen", header = "title", close = "text", bars = "line", currency = "text",
	motion = "flicker", icons = "none", textStroke = 0, palette = "Blood", vignette = true,
	std = {Green = "5E7A55", Blue = "4F6573", Orange = "9A5B2A", Red = "8A1C1C", Yellow = "A89A5B", Purple = "5E4A6E",
		Pink = "8A4A5A", Cyan = "4E7373", Gray = "5A5552", Gold = "A8894A"},
	paint = function(T, key, role)
		local a = P(T, key)
		local bone = T.Accent
		if role == "action" then
			return {fill = darker(T.Primary, 0.55), t = 0.05, stroke = T.Primary, strokeW = 1, text = bone, accent = T.Primary}
		end
		return {fill = hex("100E0E"), t = 0.25, stroke = bone, strokeT = 0.78, strokeW = 1, text = bone, accent = a}
	end,
	panel = function(T)
		return {fill = hex("080707"), t = 0.12, stroke = T.Accent, strokeW = 1, strokeT = 0.8, text = T.Accent,
			dim = T.Accent:Lerp(BLACK, 0.45), inner = hex("151212"), innerT = 0.3, line = T.Primary}
	end,
}

STYLES.Anime = {
	fonts = {title = {"Bangers"}, button = {"Sarpanch", "ExtraBold"}, body = {"Sarpanch", "Bold"},
		number = {"Sarpanch", "ExtraBold"}},
	case = "upper", shape = "square", radius = 0, outline = "accent", outlineW = 2, shadow = "colored", shadowD = 7,
	surface = "gradient", studs = false, gloss = false, shine = true, deco = {"stripe", "slash"}, tilt = -5,
	menu = "bars", windows = "side", header = "banner", close = "square", bars = "slanted", currency = "slanted",
	motion = "slide", icons = "vector", textStroke = 2, palette = "Crimson",
	paint = function(T, key, role)
		local a = P(T, key)
		if role == "action" then
			return {fill = a, stroke = WHITE, strokeW = 2, text = WHITE, textStroke = darker(a, 0.6), accent = WHITE}
		end
		if role == "tabOff" then a = T.color("Gray") end
		return {fill = T.Panel, stroke = a, text = WHITE, textStroke = BLACK, accent = a}
	end,
	panel = function(T)
		return {fill = T.Panel2, t = 0.08, stroke = T.Primary, strokeW = 2, text = WHITE, dim = hex("9AA3C7"),
			inner = T.Panel, innerT = 0.1, line = T.Primary}
	end,
}

STYLES.SciFi = {
	fonts = {title = {"Michroma"}, button = {"Jura", "Bold"}, body = {"Jura", "Bold"}, number = {"Jura", "Bold"}},
	case = "upper", shape = "square", radius = 3, outline = "accent", outlineW = 1.5, shadow = "glow", shadowD = 0,
	surface = "dark", studs = false, gloss = false, shine = false, deco = {"brackets", "scan"}, tilt = 0,
	menu = "chips", windows = "side", header = "line", close = "square", bars = "segments", currency = "readout",
	motion = "glitch", icons = "vector", textStroke = 0, palette = "Cyber", charW = 0.8,
	std = {Green = "3DFF9A", Blue = "3DB8FF", Orange = "FF9A3D", Red = "FF3D5A", Yellow = "FFE83D", Purple = "B45CFF",
		Pink = "FF5CD6", Cyan = "3DF2FF", Gray = "8FA3B8", Gold = "FFD23D"},
	paint = function(T, key, role)
		local a = P(T, key)
		if role == "tabOff" then a = T.color("Gray") end
		if role == "action" then
			return {fill = a, t = 0.55, stroke = a, strokeW = 1.5, text = WHITE, accent = a}
		end
		return {fill = darker(a, 0.86), t = 0.2, stroke = a, strokeW = 1.5, text = lighter(a, 0.55), accent = a}
	end,
	panel = function(T)
		return {fill = T.Panel2, t = 0.18, stroke = T.Primary, strokeW = 1.5, strokeT = 0.2, text = lighter(T.Primary, 0.7),
			dim = T.Primary:Lerp(hex("5A6B7A"), 0.6), inner = T.Panel, innerT = 0.35, line = T.Primary}
	end,
}

STYLES.Fantasy = {
	fonts = {title = {"GrenzeGotisch", "Bold"}, button = {"Merriweather", "Bold"}, body = {"Merriweather", "Bold"},
		number = {"Merriweather", "Heavy"}},
	case = "title", shape = "rounded", radius = 6, outline = "gold", outlineW = 2, shadow = "frame", shadowD = 4,
	surface = "wood", studs = false, gloss = false, shine = false, deco = {"rivets", "ornaments"}, tilt = 0,
	menu = "plaques", windows = "popup", header = "ribbon", close = "round", bars = "framed", currency = "plank",
	motion = "smooth", icons = "emoji", textStroke = 1.5, palette = "Medieval",
	std = {Green = "3E7A2E", Blue = "2B4C8C", Orange = "B8641E", Red = "8E1B1B", Yellow = "C9A227", Purple = "5B2F7A",
		Pink = "9A3F66", Cyan = "2E7A7A", Gray = "6E6256", Gold = "C9962E"},
	paint = function(T, key, role)
		local c
		if role == "action" or key == "Green" or key == "Red" or key == "Blue" or key == "Purple" then
			c = P(T, key)
		else
			c = T.Primary
		end
		if role == "tabOff" then c = darker(T.Primary, 0.35) end
		return {fill = c, stroke = T.Accent, strokeW = 2, text = hex("FFF1C9"), textStroke = hex("2A170A"),
			accent = T.Accent, frame = hex("2A170A")}
	end,
	panel = function(T)
		return {fill = T.Panel, t = 0, stroke = T.Outline, strokeW = 3, text = hex("3B2412"), dim = hex("7A5A3A"),
			inner = T.Inner, innerT = 0, line = T.Accent, outer = T.Primary}
	end,
}

STYLES.Minimal = {
	fonts = {title = {"GothamBold"}, button = {"GothamBold"}, body = {"GothamMedium"}, number = {"GothamBold"}},
	case = "title", shape = "rounded", radius = 14, outline = "none", outlineW = 1, shadow = "soft", shadowD = 4,
	surface = "flat", studs = false, gloss = false, shine = false, deco = {}, tilt = 0,
	menu = "chips", windows = "side", header = "title", close = "round", bars = "pill", currency = "chip",
	motion = "smooth", icons = "vector", textStroke = 0, palette = "Clean", dim = true,
	std = {Green = "10B981", Blue = "3B82F6", Orange = "F97316", Red = "EF4444", Yellow = "EAB308", Purple = "8B5CF6",
		Pink = "EC4899", Cyan = "06B6D4", Gray = "94A3B8", Gold = "F59E0B"},
	paint = function(T, key, role)
		local dark = lum(T.Panel) < 0.4
		if role == "action" or role == "tab" then
			local c = P(T, key)
			return {fill = c, text = WHITE, accent = c}
		end
		local bg = dark and T.Inner or WHITE
		return {fill = bg, text = dark and WHITE or hex("1F2937"), accent = P(T, key),
			stroke = dark and T.Outline or hex("E3E8EF"), strokeW = 1}
	end,
	panel = function(T)
		local dark = lum(T.Panel) < 0.4
		return {fill = T.Panel, t = 0, text = dark and WHITE or hex("111827"), dim = dark and hex("9AA3B5") or hex("6B7280"),
			inner = T.Panel2, innerT = 0, line = dark and T.Inner or hex("E5E7EB"), stroke = dark and T.Outline or nil,
			strokeW = 1}
	end,
}

STYLES.Pixel = {
	fonts = {title = {"Arcade"}, button = {"Arcade"}, body = {"Arcade"}, number = {"Arcade"}},
	case = "upper", shape = "square", radius = 0, outline = "black", outlineW = 4, shadow = "hard", shadowD = 5,
	surface = "flat", studs = false, gloss = false, shine = false, deco = {"bevel"}, tilt = 0,
	menu = "tiles", windows = "popup", header = "bar", close = "square", bars = "segments", currency = "box",
	motion = "retro", icons = "vector", textStroke = 0, textShadow = true, palette = "Retro", colorful = true,
	textScale = 0.7, charW = 1,
	std = {Green = "38B764", Blue = "3B5DC9", Orange = "EF7D57", Red = "B13E53", Yellow = "FFCD75", Purple = "5D275D",
		Pink = "F77FBE", Cyan = "41A6F6", Gray = "94B0C2", Gold = "FFCD75"},
	paint = function(T, key, role)
		local c = P(T, key)
		if role == "tabOff" then c = T.color("Gray") end
		return {fill = c, stroke = BLACK, strokeW = 4, text = WHITE, accent = c}
	end,
	panel = function(T)
		return {fill = T.Panel, t = 0, stroke = BLACK, strokeW = 4, text = WHITE, dim = hex("94B0C2"), inner = T.Inner,
			innerT = 0, line = T.Accent}
	end,
}

STYLES.Glass = {
	fonts = {title = {"GothamBlack"}, button = {"GothamBold"}, body = {"GothamMedium"}, number = {"GothamBold"}},
	case = "title", shape = "rounded", radius = 18, outline = "white", outlineW = 1.5, shadow = "soft", shadowD = 5,
	surface = "glass", studs = false, gloss = true, shine = true, deco = {}, tilt = 0,
	menu = "tiles", windows = "popup", header = "title", close = "round", bars = "pill", currency = "chip",
	motion = "smooth", icons = "emoji", textStroke = 0, palette = "Galaxy", blur = true, dim = true,
	paint = function(T, key, role)
		local c = P(T, key)
		if role == "action" or role == "tab" then
			return {fill = c, t = 0.25, stroke = WHITE, strokeT = 0.4, strokeW = 1.5, text = WHITE, accent = c, glass = false}
		end
		return {fill = hex("141828"), t = 0.5, stroke = WHITE, strokeT = 0.55, strokeW = 1.5, text = WHITE, accent = c}
	end,
	panel = function(T)
		return {fill = darker(T.Panel2, 0.35), t = 0.3, stroke = WHITE, strokeW = 1.5, strokeT = 0.55, text = WHITE,
			dim = hex("C9D0EE"), inner = WHITE, innerT = 0.9, line = WHITE}
	end,
}

-- what a game type uses when style / colours are left on auto
local GAMES = {}
local GAME_ORDER = {"simulator", "tycoon", "obby", "fighting", "horror", "racing", "rpg", "shooter", "tower", "roleplay"}
local GAME_LABELS = {simulator = "Simulator", tycoon = "Tycoon", obby = "Obby", fighting = "Fighting", horror = "Horror",
	racing = "Racing", rpg = "RPG", shooter = "Shooter", tower = "Tower Defense", roleplay = "Roleplay"}
local GAME_WORDS = {
	simulator = "simulator sim clicker pet pets egg eggs collect mining farm incremental",
	tycoon = "tycoon factory business restaurant store empire money",
	obby = "obby parkour tower jump platformer stage stages",
	fighting = "fighting fight pvp combat anime boss arena battlegrounds brawl",
	horror = "horror scary survival escape creepy backrooms",
	racing = "racing race car cars drift kart driving",
	rpg = "rpg adventure quest quests dungeon fantasy mmo",
	shooter = "shooter fps gun guns war tps sniper",
	tower = "td defense defence waves",
	roleplay = "roleplay rp town life city brookhaven",
}
local GAME_STYLE = {simulator = "Sim", tycoon = "Sim", obby = "Cartoon", fighting = "Anime", horror = "Horror",
	racing = "SciFi", rpg = "Fantasy", shooter = "Minimal", tower = "Cartoon", roleplay = "Glass"}
local GAME_PALETTE = {racing = "Speed", shooter = "Dark", roleplay = "Sunset", tower = "Forest", tycoon = "Classic",
	obby = "Sunset"}
local STYLE_WORDS = {
	Sim = "steal brainrot popular", Studs = "studs stud lego brick bricks studded", Bubbly = "bubbly cute kawaii bubble round soft squishy",
	Cartoon = "cartoon comic toon cartoony", Horror = "horror scary creepy dread", Anime = "anime manga",
	SciFi = "scifi futuristic hologram tech hud", Fantasy = "fantasy medieval magic wizard",
	Minimal = "minimal clean modern simple sleek", Pixel = "pixel retro 8bit pixelated arcade", Glass = "glass frosted blur",
}

-- the option controls (value lists for the panel). "auto" = the style's own choice.
local OPTIONS = {
	{key = "game", label = "Game", values = {"auto", "simulator", "tycoon", "obby", "fighting", "horror", "racing", "rpg",
		"shooter", "tower", "roleplay"}},
	{key = "style", label = "Style", values = {"auto", "Sim", "Studs", "Bubbly", "Cartoon", "Horror", "Anime", "SciFi", "Fantasy",
		"Minimal", "Pixel", "Glass"}},
	{key = "palette", label = "Colours", values = {"auto", "Classic", "Candy", "Ocean", "Lava", "Forest", "Galaxy", "Neon",
		"Winter", "Spooky", "Holiday", "Royal", "Desert", "Toxic", "Pastel", "Military", "Midnight", "Sunset", "Blood",
		"Fog", "Crimson", "Cyber", "Medieval", "Clean", "Dark", "Retro", "Speed"}},
	{key = "font", label = "Font", values = {"auto", "FredokaOne", "LuckiestGuy", "Bangers", "Creepster", "SpecialElite",
		"Michroma", "Sarpanch", "Jura", "Oswald", "Fondamento", "Merriweather", "GrenzeGotisch", "Arcade", "GothamBold",
		"Nunito", "DenkOne", "PermanentMarker", "TitilliumWeb", "RobotoMono"}},
	{key = "shape", label = "Shape", values = {"auto", "rounded", "pill", "square", "slanted"}},
	{key = "corners", label = "Corners", values = {"auto", "sharp", "small", "medium", "large"}},
	{key = "outline", label = "Outline", values = {"auto", "ink", "none", "thin", "thick", "dark", "white", "glow"}},
	{key = "shadow", label = "Shadow", values = {"auto", "none", "lip", "hard", "soft", "glow", "colored", "frame"}},
	{key = "surface", label = "Surface", values = {"auto", "vivid", "gradient", "flat", "glossy", "glass", "dark",
		"wood"}},
	{key = "studs", label = "Studs", values = {"auto", "on", "off"}},
	{key = "menu", label = "Menu buttons", values = {"auto", "rings", "tiles", "circles", "rows", "bars", "chips",
		"plaques"}},
	{key = "windows", label = "Windows", values = {"auto", "popup", "side", "fullscreen"}},
	{key = "motion", label = "Motion", values = {"auto", "bouncy", "squish", "press", "smooth", "slide", "flicker",
		"glitch", "retro", "none"}},
	{key = "icons", label = "Icons", values = {"auto", "emoji", "vector", "none"}},
	{key = "case", label = "Text", values = {"auto", "upper", "title", "lower"}},
	{key = "size", label = "Size", values = {"S", "M", "L"}},
}
local DEFAULT_OPTIONS = {prompt = PROMPT, seed = 0, size = "M"}
for _, o in ipairs(OPTIONS) do
	if DEFAULT_OPTIONS[o.key] == nil then
		DEFAULT_OPTIONS[o.key] = "auto"
	end
end

-----------------------------------------------------------------------------------------------
-- prompt + options -> the resolved look (R), style parameters (ST) and colours (T)
-----------------------------------------------------------------------------------------------
local FONT_WORDS = {fredoka = "FredokaOne", luckiest = "LuckiestGuy", bangers = "Bangers", creepster = "Creepster",
	typewriter = "SpecialElite", michroma = "Michroma", sarpanch = "Sarpanch", jura = "Jura", oswald = "Oswald",
	fondamento = "Fondamento", merriweather = "Merriweather", gothic = "GrenzeGotisch", gotham = "GothamBold",
	nunito = "Nunito", marker = "PermanentMarker", titillium = "TitilliumWeb", mono = "RobotoMono", denk = "DenkOne"}
local MOD_WORDS = {
	shape = {pill = "pill", pills = "pill", rounded = "rounded", square = "square", sharp = "square", boxy = "square",
		slanted = "slanted", angled = "slanted", tilted = "slanted"},
	surface = {flat = "flat", matte = "flat", glossy = "glossy", shiny = "glossy", wooden = "wood", wood = "wood",
		gradient = "gradient"},
	motion = {bouncy = "bouncy", bounce = "bouncy", squishy = "squish", jelly = "squish", smooth = "smooth",
		snappy = "press", glitch = "glitch", glitchy = "glitch", flicker = "flicker", flickering = "flicker",
		still = "none", static = "none"},
	outline = {outlined = "thick", thick = "thick", thin = "thin", glow = "glow", glowing = "glow", nooutline = "none"},
	shadow = {shadow = "hard", shadows = "hard", shadowless = "none"},
	case = {caps = "upper", uppercase = "upper", allcaps = "upper", lowercase = "lower"},
	size = {big = "L", large = "L", huge = "L", small = "S", compact = "S", tiny = "S"},
	icons = {emoji = "emoji", emojis = "emoji", vector = "vector", flaticons = "vector", noicons = "none"},
	windows = {fullscreen = "fullscreen", drawer = "side", sidebar = "side", popup = "popup", popups = "popup"},
	menu = {tiles = "tiles", circles = "circles", circle = "circles", bars = "bars", chips = "chips", plaques = "plaques"},
}

local function bestOf(order, lists, ws)
	local best, score = nil, 0
	for _, name in ipairs(order) do
		local kw = wordList(lists[name] or "")
		local s = 0
		for _, w in ipairs(ws) do
			if w == name:lower() then
				s = s + 2
			elseif hasWord(kw, w) then
				s = s + 1
			end
		end
		if s > score then
			best, score = name, s
		end
	end
	return best
end

local function parsePrompt(prompt)
	local title = prompt:match('"([^"]+)"') or prompt:match("'([^']+)'")
	local rest = prompt:gsub('"[^"]*"', " "):gsub("'[^']*'", " ")
	local ws = wordList(rest)
	local found = {}
	found.game = bestOf(GAME_ORDER, GAME_WORDS, ws)
	found.style = bestOf(STYLE_ORDER, STYLE_WORDS, ws)
	found.palette = bestOf(PALETTE_ORDER, PALETTE_WORDS, ws)
	for i, w in ipairs(ws) do
		if FONT_WORDS[w] then
			found.font = FONT_WORDS[w]
		end
		for key, map in pairs(MOD_WORDS) do
			if map[w] then
				found[key] = map[w]
			end
		end
		if w == "studs" or w == "studded" or w == "lego" then
			found.studs = (ws[i - 1] == "no" or ws[i - 1] == "without") and "off" or "on"
		elseif w == "nostuds" or w == "smooth" then
			found.studs = "off"
		end
		if COLOR_WORDS[w] and not found.colour then
			found.colour = w
		end
	end
	return found, title
end

local R, ST, T -- current build: resolved options, style parameters, colours

local function resolve(opts)
	local found, title = parsePrompt(opts.prompt or "")
	local function pick(key)
		local v = opts[key]
		if v ~= nil and v ~= "auto" then
			return v, true
		end
		if found[key] then
			return found[key], true
		end
		return nil, false
	end
	local gameType = pick("game") or "simulator"
	if not GAMES[gameType] then
		gameType = "simulator"
	end
	local styleName, styleChosen = pick("style")
	styleName = styleName or GAME_STYLE[gameType]
	if not STYLES[styleName] then
		styleName = "Studs"
	end
	local st = copy(STYLES[styleName])
	st.deco = copy(st.deco)
	local palName, palChosen = pick("palette")
	if not palChosen then
		palName = (not styleChosen and GAME_PALETTE[gameType]) or st.palette
	end
	if not PALETTES[palName] then
		palName = st.palette
	end

	-- colours
	local colours = {}
	for i, role in ipairs(ROLE_NAMES) do
		colours[role] = hex(PALETTES[palName][i])
	end
	local cw = found.colour
	if cw and not hasWord(wordList(PALETTE_WORDS[palName] or ""), cw) then
		colours.Primary = hex(COLOR_WORDS[cw])
	end

	-- overrides
	local seed = tonumber(opts.seed) or 0
	local rng = Random.new(seed ~= 0 and seed or 1)
	local shape, shapeChosen = pick("shape")
	if shapeChosen then
		st.shape = shape
		if shape == "slanted" then
			st.tilt = -5
			st.radius = 0
		else
			st.tilt = 0
			if shape == "square" then
				st.radius = math.min(st.radius, 3)
			elseif shape == "rounded" and st.radius < 8 then
				st.radius = 12
			end
		end
	end
	local corners = pick("corners")
	if corners then
		st.radius = ({sharp = 0, small = 6, medium = 12, large = 22})[corners] or st.radius
		if corners == "sharp" and st.shape ~= "slanted" then
			st.shape = "square"
		elseif corners ~= "sharp" and st.shape == "square" then
			st.shape = "rounded"
		end
	end
	for _, key in ipairs({"outline", "shadow", "surface", "menu", "windows", "motion", "icons", "case"}) do
		local v = pick(key)
		if v then
			st[key] = v
		end
	end
	local studs = pick("studs")
	if studs then
		st.studs = studs == "on"
	end
	if st.outline == "glow" and st.shadow ~= "none" then
		st.shadow = "glow"
	end
	local fontName = pick("font")
	local fonts = {}
	for role, f in pairs(st.fonts) do
		if fontName then
			fonts[role] = fontFace(fontName, (fontName == "Sarpanch" or fontName == "Merriweather" or fontName == "Jura")
				and "Bold" or nil)
		else
			fonts[role] = fontFace(f[1], f[2])
		end
	end
	local sizeOpt = opts.size or "M"
	if found.size and (opts.size == nil or opts.size == "M") then
		sizeOpt = found.size
	end

	-- shuffle: variations that keep the style's identity
	local menuSide = "left"
	local variant = 1
	if seed ~= 0 then
		if rng:NextNumber() < 0.45 then
			colours.Primary, colours.Secondary = colours.Secondary, colours.Primary
		end
		if st.shape == "rounded" then
			st.radius = math.floor(st.radius * rng:NextNumber(0.6, 1.5) + 0.5)
		end
		if st.tilt ~= 0 then
			st.tilt = st.tilt * (rng:NextNumber() < 0.5 and -1 or 1) * rng:NextNumber(0.7, 1.3)
		end
		if st.shadowD > 0 then
			st.shadowD = math.max(2, st.shadowD + rng:NextInteger(-2, 2))
		end
		menuSide = rng:NextNumber() < 0.35 and "right" or "left"
		variant = rng:NextInteger(1, 3)
		if rng:NextNumber() < 0.3 then
			colours.TitleTop, colours.TitleBottom = colours.TitleBottom, colours.TitleTop
		end
	end

	local Tc = colours
	Tc.color = function(key)
		if Tc[key] and typeof(Tc[key]) == "Color3" then
			return Tc[key]
		end
		local h = (st.std and st.std[key]) or STD[key] or STD.Gray
		return hex(h)
	end
	return {
		game = gameType, style = styleName, palette = palName, title = title, fonts = fonts, seed = seed, rng = rng,
		scale = ({S = 0.86, M = 1, L = 1.16})[sizeOpt] or 1, size = sizeOpt, menuSide = menuSide, variant = variant,
		case = st.case, icons = st.icons, windows = st.windows, motion = st.motion, studPx = 18 + (seed % 3) * 2,
	}, st, Tc
end

-----------------------------------------------------------------------------------------------
-- optional sprite kit (ui/generate.py) - used for icons and the stud tile when it is installed
-----------------------------------------------------------------------------------------------
local Kit = nil

local function loadKit()
	Kit = nil
	local mod = ReplicatedStorage:FindFirstChild("SimUIKit")
	if mod and mod:IsA("ModuleScript") then
		local ok, k = pcall(function()
			return require(mod:Clone())
		end)
		if ok and type(k) == "table" then
			Kit = k
		end
	end
end

local function kitImage(key)
	if not Kit or not Kit.Images then
		return nil
	end
	local id = Kit.Images[key]
	if not id or id == "" or id == "rbxassetid://0" then
		return nil
	end
	return id
end

local function kitSprite(tableName, name)
	if not Kit or not Kit[tableName] then
		return nil
	end
	local s = Kit[tableName][name]
	if not s then
		return nil
	end
	local img = kitImage(s[1])
	if not img then
		return nil
	end
	return img, s
end

-----------------------------------------------------------------------------------------------
-- drawing primitives
-----------------------------------------------------------------------------------------------
local function corner(o, r)
	if r == "pill" then
		new("UICorner", {CornerRadius = UDim.new(0.5, 0), Parent = o})
	elseif r and r >= 1 then
		new("UICorner", {CornerRadius = UDim.new(0, r), Parent = o})
	end
end

local function stroke(o, color, thick, transp, miter)
	return new("UIStroke", {Color = color, Thickness = thick or 2, Transparency = transp or 0,
		ApplyStrokeMode = Enum.ApplyStrokeMode.Border,
		LineJoinMode = miter and Enum.LineJoinMode.Miter or Enum.LineJoinMode.Round, Parent = o})
end

local function gradient(o, c1, c2, c3, rot)
	o.BackgroundColor3 = WHITE -- UIGradient multiplies with the background colour
	local seq
	if c3 then
		seq = ColorSequence.new({ColorSequenceKeypoint.new(0, c1), ColorSequenceKeypoint.new(0.55, c2),
			ColorSequenceKeypoint.new(1, c3)})
	else
		seq = ColorSequence.new(c1, c2)
	end
	return new("UIGradient", {Color = seq, Rotation = rot or 90, Parent = o})
end

local function radiusFor(h, kind)
	if ST.shape == "square" or ST.shape == "slanted" then
		return math.min(ST.radius, 3)
	end
	if ST.shape == "pill" and kind ~= "panel" and kind ~= "card" and kind ~= "tile" then
		return "pill"
	end
	local r = ST.radius
	if kind == "panel" then
		r = r * 1.4
	elseif kind == "small" or kind == "chip" then
		r = r * 0.8
	elseif kind == "tile" and ST.shape == "pill" then
		r = r * 1.1
	end
	return math.min(r, h / 2)
end

local function outlineFor(pnt, fillC)
	local mode = ST.outline
	local own = STYLES[R.style].outline
	local w = pnt.strokeW or ST.outlineW
	if mode == own then
		if not pnt.stroke then
			return nil
		end
		return {c = pnt.stroke, w = w, t = pnt.strokeT or 0}
	end
	if mode == "none" then
		return nil
	elseif mode == "thin" then
		return {c = pnt.stroke or darker(fillC, 0.5), w = 1.5, t = pnt.strokeT or 0}
	elseif mode == "thick" then
		return {c = darker(fillC, 0.62), w = 5, t = 0}
	elseif mode == "dark" then
		return {c = darker(fillC, 0.55), w = math.max(2, w), t = 0}
	elseif mode == "black" then
		return {c = hex("141414"), w = math.max(3, w), t = 0}
	elseif mode == "ink" then
		return {c = INK, w = math.max(3, w), t = 0}
	elseif mode == "white" then
		return {c = WHITE, w = math.max(3, w), t = 0}
	elseif mode == "glow" then
		return {c = lighter(pnt.accent or fillC, 0.2), w = 2, t = 0}
	elseif mode == "gold" then
		return {c = T.Accent, w = 2, t = 0}
	end
	return {c = pnt.stroke or pnt.accent or darker(fillC, 0.5), w = w, t = pnt.strokeT or 0}
end

local DECO = {}

function DECO.spot(face, box, pnt, c, w, h, r, kind)
	if kind == "panel" or kind == "card" or h < 36 then
		return
	end
	local sp = frame(face, "Spot", {BackgroundTransparency = 0.3, BackgroundColor3 = WHITE,
		Size = UDim2.fromOffset(math.max(8, math.floor(w * 0.16)), math.max(5, math.floor(h * 0.11))),
		Position = UDim2.fromOffset(math.max(7, math.floor(w * 0.09)), math.max(5, math.floor(h * 0.13))),
		Rotation = -18, ZIndex = 3})
	corner(sp, "pill")
end

function DECO.halftone(face, box, pnt, c, w, h, r, kind)
	if kind == "chip" or kind == "small" or h < 44 then
		return
	end
	for i = 0, 2 do
		for j = 0, 2 - i do
			local sz = 7 - (i + j) * 2
			local dot = frame(face, "Dot", {BackgroundTransparency = 0.5, BackgroundColor3 = darker(c, 0.3),
				Size = UDim2.fromOffset(sz, sz), Position = UDim2.new(1, -12 - i * 10, 1, -12 - j * 10),
				AnchorPoint = Vector2.new(0.5, 0.5), ZIndex = 3})
			corner(dot, "pill")
		end
	end
end

function DECO.stripe(face, box, pnt, c, w, h, r, kind)
	if kind == "panel" or kind == "chip" then
		return
	end
	frame(face, "Stripe", {BackgroundTransparency = 0, BackgroundColor3 = pnt.accent or T.Primary,
		Size = UDim2.new(0, 7, 1, 0), ZIndex = 3})
end

function DECO.slash(face, box, pnt, c, w, h, r, kind)
	if kind ~= "button" and kind ~= "tile" then
		return
	end
	frame(face, "Slash", {BackgroundTransparency = 0.82, BackgroundColor3 = WHITE, Size = UDim2.new(0, 12, 1, 0),
		Position = UDim2.new(1, -34, 0, 0), ZIndex = 3})
	frame(face, "Slash", {BackgroundTransparency = 0.7, BackgroundColor3 = WHITE, Size = UDim2.new(0, 4, 1, 0),
		Position = UDim2.new(1, -16, 0, 0), ZIndex = 3})
end

function DECO.brackets(face, box, pnt, c, w, h, r, kind)
	local col = pnt.accent or pnt.stroke or T.Primary
	local big = kind == "panel" or kind == "card"
	local L, th, o = big and 26 or 12, big and 3 or 2, big and -7 or -5
	for _, cn in ipairs({{0, 0}, {1, 0}, {0, 1}, {1, 1}}) do
		local ax, ay = cn[1], cn[2]
		local pos = UDim2.new(ax, ax == 0 and o or -o, ay, ay == 0 and o or -o)
		frame(box, "Bracket", {BackgroundTransparency = 0, BackgroundColor3 = col, Size = UDim2.fromOffset(L, th),
			Position = pos, AnchorPoint = Vector2.new(ax, ay), ZIndex = 9})
		frame(box, "Bracket", {BackgroundTransparency = 0, BackgroundColor3 = col, Size = UDim2.fromOffset(th, L),
			Position = pos, AnchorPoint = Vector2.new(ax, ay), ZIndex = 9})
	end
end

function DECO.bevel(face, box, pnt, c, w, h, r, kind)
	local b = (kind == "panel") and 6 or 4
	frame(face, "Bevel", {BackgroundTransparency = 0.5, BackgroundColor3 = WHITE, Size = UDim2.new(1, 0, 0, b), ZIndex = 3})
	frame(face, "Bevel", {BackgroundTransparency = 0.5, BackgroundColor3 = WHITE, Size = UDim2.new(0, b, 1, 0), ZIndex = 3})
	frame(face, "Bevel", {BackgroundTransparency = 0.55, BackgroundColor3 = BLACK, Size = UDim2.new(1, 0, 0, b),
		Position = UDim2.new(0, 0, 1, -b), ZIndex = 3})
	frame(face, "Bevel", {BackgroundTransparency = 0.55, BackgroundColor3 = BLACK, Size = UDim2.new(0, b, 1, 0),
		Position = UDim2.new(1, -b, 0, 0), ZIndex = 3})
end

function DECO.rivets(face, box, pnt, c, w, h, r, kind)
	if kind == "panel" or kind == "chip" or kind == "small" or h < 40 or w < 60 then
		return
	end
	local col = pnt.accent or T.Accent
	for _, p in ipairs({{0, 0}, {1, 0}, {0, 1}, {1, 1}}) do
		local rv = frame(face, "Rivet", {BackgroundTransparency = 0, BackgroundColor3 = col, Size = UDim2.fromOffset(8, 8),
			Position = UDim2.new(p[1], p[1] == 0 and 10 or -10, p[2], p[2] == 0 and 10 or -10),
			AnchorPoint = Vector2.new(0.5, 0.5), ZIndex = 3})
		corner(rv, "pill")
		stroke(rv, darker(col, 0.6), 1)
	end
end

function DECO.ornaments(face, box, pnt, c, w, h, r, kind)
	if kind ~= "panel" then
		return
	end
	for _, p in ipairs({{0, 0}, {1, 0}, {0, 1}, {1, 1}}) do
		local o = frame(box, "Ornament", {BackgroundTransparency = 0, BackgroundColor3 = T.Accent,
			Size = UDim2.fromOffset(22, 22), Position = UDim2.new(p[1], p[1] == 0 and 4 or -4, p[2], p[2] == 0 and 4 or -4),
			AnchorPoint = Vector2.new(0.5, 0.5), Rotation = 45, ZIndex = 9})
		stroke(o, hex("2A170A"), 2)
		local i = frame(o, "Gem", {BackgroundTransparency = 0, BackgroundColor3 = T.Secondary, Size = UDim2.fromScale(0.4, 0.4),
			Position = UDim2.fromScale(0.5, 0.5), AnchorPoint = Vector2.new(0.5, 0.5), ZIndex = 2})
	end
end

function DECO.scratches(face, box, pnt, c, w, h, r, kind)
	if h < 40 or w < 80 then
		return
	end
	for _, a in ipairs({{0.18, 0.3, 12}, {0.6, 0.64, -8}, {0.4, 0.8, 4}}) do
		frame(face, "Scratch", {BackgroundTransparency = 0.88, BackgroundColor3 = T.Accent,
			Size = UDim2.new(0.32, 0, 0, 1), Position = UDim2.fromScale(a[1], a[2]), Rotation = a[3], ZIndex = 3})
	end
end

function DECO.grain(face, box, pnt, c, w, h, r, kind)
	if h < 30 then
		return
	end
	for i, y in ipairs({0.28, 0.52, 0.76}) do
		frame(face, "Grain", {BackgroundTransparency = 0.55, BackgroundColor3 = darker(c, 0.3),
			Size = UDim2.new(0.55 + 0.12 * i, 0, 0, 2), Position = UDim2.new(0.08 * i, 0, y, 0), ZIndex = 1})
	end
end

function DECO.scan(face, box, pnt, c, w, h, r, kind)
	if kind ~= "panel" then
		return
	end
	local ln = frame(face, "Scan", {BackgroundTransparency = 0.75, BackgroundColor3 = pnt.accent or T.Primary,
		Size = UDim2.new(1, 0, 0, 2), ZIndex = 3})
	ln:SetAttribute("Scan", true)
end

function DECO.rim(face, box, pnt, c, w, h, r, kind)
	if kind == "panel" or kind == "card" or h < 30 then
		return
	end
	local rim = frame(face, "Rim", {BackgroundTransparency = 0.45, BackgroundColor3 = WHITE, Size = UDim2.new(1, -14, 0, 3),
		Position = UDim2.fromOffset(7, 4), ZIndex = 3})
	corner(rim, "pill")
end

-- halftone dots: big at the bottom left, fading out to the right and upwards
function DECO.dots(face, box, pnt, c, w, h, r, kind)
	if kind == "panel" or kind == "chip" or kind == "pill" or kind == "small" or h < 60 or w < 90 then
		return
	end
	-- every dot is an instance, so keep it to about 30 per surface
	local sp = math.clamp(math.floor(h / 7), 10, 18)
	local cols, rows
	repeat
		cols = math.max(2, math.floor(w * 0.7 / sp))
		rows = math.max(2, math.floor(h * (kind == "card" and 0.36 or 0.5) / sp))
		sp = sp + 2
	until cols * rows <= 30
	sp = sp - 2
	local col = lighter(c, 0.4)
	local holder = frame(face, "Dots", {Size = UDim2.fromScale(1, 1), ClipsDescendants = true, ZIndex = 1})
	for j = 0, rows - 1 do
		for i = 0, cols - 1 do
			local f = (1 - 0.8 * i / math.max(1, cols)) * (1 - 0.45 * j / rows)
			local d = math.floor(sp * 0.72 * f + 0.5)
			if d >= 2 then
				local dot = frame(holder, "Dot", {BackgroundTransparency = 0.45, BackgroundColor3 = col,
					Size = UDim2.fromOffset(d, d), Position = UDim2.new(0, 6 + i * sp + (j % 2) * sp / 2, 1, -8 - j * sp),
					AnchorPoint = Vector2.new(0.5, 0.5)})
				corner(dot, "pill")
			end
		end
	end
end

-- a hexagon made of three rotated frames (with an optional darker edge behind it)
local function hexagon(parent, name, pos, size, fill, edge, edgeW, z, rot)
	local g = frame(parent, name, {Size = UDim2.fromOffset(size, size), Position = pos, AnchorPoint = Vector2.new(0.5, 0.5),
		ZIndex = z or 1, Rotation = rot or 0})
	local function layer(R, col, nm, zz)
		for i = 0, 2 do
			local f = frame(g, nm, {BackgroundTransparency = 0, BackgroundColor3 = col,
				Size = UDim2.fromOffset(math.floor(R * 1.732 + 0.5), math.floor(R + 0.5)), Position = UDim2.fromScale(0.5, 0.5),
				AnchorPoint = Vector2.new(0.5, 0.5), Rotation = i * 60, ZIndex = zz})
			corner(f, math.max(1, math.floor(R * 0.1)))
		end
	end
	if edge then
		layer(size / 2 + (edgeW or 3), edge, "Edge", 1)
	end
	layer(size / 2, fill, "Hex", 2)
	return g
end

local function studs(face, w, h, c)
	local inset = 5
	local img = kitImage("Stud")
	if img then
		new("ImageLabel", {Name = "Studs", Image = img, ScaleType = Enum.ScaleType.Tile,
			TileSize = UDim2.fromOffset(R.studPx, R.studPx), Size = UDim2.new(1, -inset * 2, 1, -inset * 2),
			Position = UDim2.fromOffset(inset, inset), BackgroundTransparency = 1, ImageTransparency = 0.25, ZIndex = 1,
			Parent = face})
		return
	end
	local px = R.studPx
	if h < 70 then
		px = math.max(12, math.floor((h - inset * 2) / 2.2))
	end
	local cols = math.max(1, math.floor((w - inset * 2) / px))
	local rows = math.max(1, math.floor((h - inset * 2) / px))
	while cols * rows > 44 do
		px = px + 2
		cols = math.max(1, math.floor((w - inset * 2) / px))
		rows = math.max(1, math.floor((h - inset * 2) / px))
	end
	local dot = math.floor(px * 0.62)
	local grid = frame(face, "Studs", {Size = UDim2.new(1, -inset * 2, 1, -inset * 2), Position = UDim2.fromOffset(inset, inset),
		ZIndex = 1})
	new("UIGridLayout", {CellSize = UDim2.fromOffset(dot, dot), CellPadding = UDim2.fromOffset(px - dot, px - dot),
		HorizontalAlignment = Enum.HorizontalAlignment.Center, VerticalAlignment = Enum.VerticalAlignment.Center,
		Parent = grid})
	local sc = lighter(c, 0.18)
	for i = 1, cols * rows do
		local d = frame(grid, "Stud", {BackgroundTransparency = 0.35, BackgroundColor3 = sc, LayoutOrder = i})
		corner(d, "pill")
		stroke(d, darker(c, 0.25), 1, 0.45)
	end
end

local function gloss(face, r, strong)
	local g = frame(face, "Gloss", {BackgroundTransparency = strong and 0.3 or 0.55, BackgroundColor3 = WHITE,
		Size = UDim2.new(1, -8, 0.46, 0), Position = UDim2.fromOffset(4, 3), ZIndex = 2})
	corner(g, r == "pill" and "pill" or math.max(2, (r or 0) - 3))
	new("UIGradient", {Rotation = 90, Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0.15),
		NumberSequenceKeypoint.new(1, 1)}), Parent = g})
end

local function shine(face, r)
	local sh = frame(face, "Shine", {BackgroundTransparency = 0, BackgroundColor3 = WHITE, Size = UDim2.fromScale(1, 1),
		ZIndex = 4})
	corner(sh, r)
	new("UIGradient", {Rotation = 20, Offset = Vector2.new(-1, 0), Transparency = NumberSequence.new({
		NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.42, 1), NumberSequenceKeypoint.new(0.5, 0.45),
		NumberSequenceKeypoint.new(0.58, 1), NumberSequenceKeypoint.new(1, 1)}), Parent = sh})
end

-- One surface (button, tile, panel, card, slot...). Returns box, body, content, face, paint.
-- box: the Frame/ImageButton you position. Body: fill + outline. Content: where text and icons go.
local function surface(parent, s)
	local pnt = s.paint or ST.paint(T, s.key or "Primary", s.role or "button")
	local fillC = pnt.fill
	local w, h = s.w or 100, s.h or 60
	local kind = s.kind or "button"
	local r = s.radius
	if r == nil then
		r = radiusFor(h, kind)
	end
	local box = new(s.button and "ImageButton" or "Frame", {Name = s.name or "Surface",
		Size = s.size or UDim2.fromOffset(w, h), Position = s.pos or UDim2.new(), AnchorPoint = s.anchor or Vector2.new(0, 0),
		BackgroundTransparency = 1, ZIndex = s.z or 1, Parent = parent})
	if s.button then
		box.Image = ""
		box.AutoButtonColor = false
	end
	local tilt = s.tilt
	if tilt == nil then
		tilt = (kind == "button" or kind == "tile" or kind == "chip" or kind == "tag") and ST.tilt or 0
	end
	if tilt ~= 0 then
		box.Rotation = tilt * (s.tiltSign or 1)
	end
	local shadowMode = s.shadow or ST.shadow
	local d = ST.shadowD
	local ol = outlineFor(pnt, fillC)
	local miter = ST.shape == "square" and ST.radius < 1
	if shadowMode == "hard" or shadowMode == "colored" then
		local hard = shadowMode == "hard"
		local col = hard and (pnt.shadow or hex("141414")) or (pnt.accent or T.Primary)
		if not hard and pnt.accent == WHITE then
			col = T.Primary
		end
		local sh = frame(box, "Shadow", {BackgroundTransparency = hard and 0 or 0.12, BackgroundColor3 = col,
			Size = UDim2.fromScale(1, 1), Position = UDim2.fromOffset(d, hard and d or math.floor(d * 0.6)), ZIndex = 1})
		corner(sh, r)
		if ol and hard then
			stroke(sh, col, ol.w, 0, miter)
		end
		box:SetAttribute("PressX", d)
		box:SetAttribute("PressY", hard and d or math.floor(d * 0.6))
	elseif shadowMode == "soft" then
		for i, a in ipairs({0.84, 0.9, 0.95}) do
			local g = i * 2
			local sh = frame(box, i == 1 and "Shadow" or "Shadow" .. i, {BackgroundTransparency = a, BackgroundColor3 = BLACK,
				Size = UDim2.new(1, g * 2, 1, g * 2), Position = UDim2.fromOffset(-g, -g + d), ZIndex = 1})
			corner(sh, r == "pill" and "pill" or r + g)
		end
	elseif shadowMode == "glow" then
		local gc = pnt.accent or pnt.stroke or T.Primary
		for i, a in ipairs({0.8, 0.9}) do
			local g = i * 4
			local sh = frame(box, "Glow", {BackgroundTransparency = a, BackgroundColor3 = gc,
				Size = UDim2.new(1, g * 2, 1, g * 2), Position = UDim2.fromOffset(-g, -g), ZIndex = 1})
			corner(sh, r == "pill" and "pill" or r + g)
		end
	elseif shadowMode == "frame" then
		local fc = pnt.frame or darker(fillC, 0.55)
		local fd = math.max(3, d)
		local sh = frame(box, "Shadow", {BackgroundTransparency = 0, BackgroundColor3 = fc,
			Size = UDim2.new(1, fd * 2, 1, fd * 2), Position = UDim2.fromOffset(-fd, -fd + 2), ZIndex = 1})
		corner(sh, r == "pill" and "pill" or r + fd)
		stroke(sh, darker(fc, 0.5), 1, 0.2)
	end

	local body = frame(box, "Body", {BackgroundTransparency = pnt.t or 0, BackgroundColor3 = fillC,
		Size = UDim2.fromScale(1, 1), ZIndex = 2})
	corner(body, r)
	if ol then
		stroke(body, ol.c, ol.w, ol.t, miter)
	end
	local face = body
	local lip = shadowMode == "lip" and d > 0
	if lip then
		body.BackgroundColor3 = darker(fillC, 0.42)
		face = frame(body, "Face", {BackgroundTransparency = pnt.t or 0, BackgroundColor3 = fillC,
			Size = UDim2.new(1, 0, 1, -d), ZIndex = 1})
		corner(face, r)
	end
	local mode = s.surface or ST.surface
	if not s.plain then
		if mode == "gradient" then
			gradient(face, lighter(fillC, 0.22), fillC, darker(fillC, 0.1))
		elseif mode == "glossy" then
			gradient(face, lighter(fillC, 0.38), fillC, darker(fillC, 0.05))
		elseif mode == "vivid" then
			face.BackgroundColor3 = WHITE
			new("UIGradient", {Rotation = 90, Color = ColorSequence.new({ColorSequenceKeypoint.new(0, lighter(fillC, 0.42)),
				ColorSequenceKeypoint.new(0.5, lighter(fillC, 0.08)), ColorSequenceKeypoint.new(1, darker(fillC, 0.08))}),
				Parent = face})
		elseif mode == "card" then
			gradient(face, lighter(fillC, 0.8), lighter(fillC, 0.32), fillC)
		elseif mode == "wood" then
			gradient(face, lighter(fillC, 0.14), fillC, darker(fillC, 0.24))
			DECO.grain(face, box, pnt, fillC, w, h, r, kind)
		elseif mode == "glass" then
			new("UIGradient", {Rotation = 90, Transparency = NumberSequence.new(0, 0.6), Parent = face})
		elseif mode == "dark" then
			new("UIGradient", {Rotation = 0, Transparency = NumberSequence.new(0, 0.35), Parent = face})
		end
	end
	if not s.noDeco then
		local fh = lip and (h - d) or h
		if ST.studs and not s.noStuds and kind ~= "panel" and kind ~= "chip" and w >= 30 and fh >= 24 then
			studs(face, w, fh, fillC)
		end
		if ST.gloss and not s.noGloss and kind ~= "panel" and kind ~= "card" then
			gloss(face, r, mode == "glossy")
		end
		for _, dn in ipairs(ST.deco) do
			if DECO[dn] then
				DECO[dn](face, box, pnt, fillC, w, fh, r, kind)
			end
		end
		if ST.shine and s.button and kind ~= "small" then
			shine(face, r)
			box:SetAttribute("Shine", true)
		end
	end
	local content = frame(body, "Content", {Size = UDim2.new(1, 0, 1, lip and -d or 0), ZIndex = 8})
	return box, body, content, face, pnt
end

-----------------------------------------------------------------------------------------------
-- text and icons
-----------------------------------------------------------------------------------------------
local function caseText(s, role)
	if role == "number" then
		return s
	end
	local mode = R.case
	if mode ~= "upper" and mode ~= "lower" then
		return s
	end
	local function conv(x)
		return mode == "upper" and x:upper() or x:lower()
	end
	local parts = {}
	local i = 1
	while i <= #s do
		local a, b = s:find("<[^>]*>", i)
		if not a then
			table.insert(parts, conv(s:sub(i)))
			break
		end
		table.insert(parts, conv(s:sub(i, a - 1)))
		table.insert(parts, s:sub(a, b))
		i = b + 1
	end
	return table.concat(parts)
end

local function label(parent, text, o)
	o = o or {}
	local role = o.role or "body"
	local props = {Name = o.name or "Label", Text = caseText(text, role), Size = o.size or UDim2.fromScale(1, 1),
		Position = o.pos or UDim2.new(), AnchorPoint = o.anchor or Vector2.new(0, 0), BackgroundTransparency = 1,
		FontFace = R.fonts[role] or R.fonts.body, TextSize = math.floor((o.ts or 24) * (ST.textScale or 1) + 0.5),
		TextColor3 = o.gradient and WHITE or (o.color or WHITE), TextXAlignment = o.x or Enum.TextXAlignment.Center,
		TextYAlignment = o.y or Enum.TextYAlignment.Center, TextWrapped = o.wrap or false, TextScaled = o.scaled or false,
		RichText = true, ZIndex = o.z or 3, Rotation = o.rot or 0, TextTransparency = o.transp or 0, Parent = parent}
	local inLayout = parent:FindFirstChildOfClass("UIListLayout") or parent:FindFirstChildOfClass("UIGridLayout")
	if ST.textShadow and o.shadow ~= false and not inLayout and (role == "title" or role == "button" or role == "number") then
		local sp = copy(props)
		sp.Name = props.Name .. "Shadow"
		sp.TextColor3 = BLACK
		sp.TextTransparency = 0.05
		sp.ZIndex = props.ZIndex - 1
		sp.Position = props.Position + UDim2.fromOffset(3, 3)
		new("TextLabel", sp)
	end
	local l = new("TextLabel", props)
	local sw = o.strokeW or ST.textStroke
	if o.stroke and sw and sw > 0 then
		new("UIStroke", {Color = o.stroke, Thickness = sw, Transparency = o.strokeT or 0,
			LineJoinMode = Enum.LineJoinMode.Round, Parent = l})
	end
	if o.gradient then
		new("UIGradient", {Rotation = 90, Color = ColorSequence.new(o.gradient[1], o.gradient[2]), Parent = l})
	end
	if o.flicker then
		l:SetAttribute("Flicker", true)
	end
	return l
end

local function vicon(parent, key, px, c1, c2, o)
	o = o or {}
	local z = o.z or 4
	local box = frame(parent, o.name or "Icon", {Size = UDim2.fromOffset(px, px), Position = o.pos or UDim2.fromScale(0.5, 0.5),
		AnchorPoint = o.anchor or Vector2.new(0.5, 0.5), ZIndex = z, Rotation = o.rot or 0})
	local def = ICONS[key] or ICONS.star
	if key == "robux" then
		hexagon(box, "Outer", UDim2.fromScale(0.5, 0.5), px * 0.96, c1, INK, 2, z, 30)
		hexagon(box, "Inner", UDim2.fromScale(0.5, 0.5), px * 0.58, c2, nil, 0, z + 1, 30)
		local sq = frame(box, "Core", {BackgroundTransparency = 0, BackgroundColor3 = c1, Size = UDim2.fromScale(0.3, 0.3),
			Position = UDim2.fromScale(0.5, 0.5), AnchorPoint = Vector2.new(0.5, 0.5), ZIndex = z + 2})
		corner(sq, math.floor(px * 0.05))
		return box
	end
	if def == "gear" then
		for i = 0, 7 do
			local a = math.rad(i * 45)
			frame(box, "Tooth", {BackgroundTransparency = 0, BackgroundColor3 = c1, Size = UDim2.fromScale(0.17, 0.22),
				Position = UDim2.fromScale(0.5 + 0.35 * math.sin(a), 0.5 - 0.35 * math.cos(a)),
				AnchorPoint = Vector2.new(0.5, 0.5), Rotation = i * 45, ZIndex = z})
		end
		local ring = frame(box, "Ring", {BackgroundTransparency = 0, BackgroundColor3 = c1, Size = UDim2.fromScale(0.66, 0.66),
			Position = UDim2.fromScale(0.5, 0.5), AnchorPoint = Vector2.new(0.5, 0.5), ZIndex = z})
		corner(ring, "pill")
		local hole = frame(box, "Hole", {BackgroundTransparency = 0, BackgroundColor3 = c2, Size = UDim2.fromScale(0.28, 0.28),
			Position = UDim2.fromScale(0.5, 0.5), AnchorPoint = Vector2.new(0.5, 0.5), ZIndex = z + 1})
		corner(hole, "pill")
		return box
	end
	for _, s in ipairs(def) do
		local kind = s[1]
		if kind == "r" then
			local two = s[8] == 2
			local f = frame(box, "P", {BackgroundTransparency = 0, BackgroundColor3 = two and c2 or c1,
				Size = UDim2.fromScale(s[4] / 100, s[5] / 100), Position = UDim2.fromScale(s[2] / 100, s[3] / 100),
				AnchorPoint = Vector2.new(0.5, 0.5), Rotation = s[6] or 0, ZIndex = z + (two and 1 or 0)})
			if s[7] and s[7] > 0 then
				corner(f, s[7] / 100 * px)
			end
		elseif kind == "c" then
			local two = s[5] == 2
			local f = frame(box, "P", {BackgroundTransparency = 0, BackgroundColor3 = two and c2 or c1,
				Size = UDim2.fromScale(s[4] / 100, s[4] / 100), Position = UDim2.fromScale(s[2] / 100, s[3] / 100),
				AnchorPoint = Vector2.new(0.5, 0.5), ZIndex = z + (two and 1 or 0)})
			corner(f, "pill")
		elseif kind == "o" then
			local two = s[6] == 2
			local t = s[5] / 100 * px
			local d = s[4] / 100 * px - 2 * t
			local f = frame(box, "P", {Size = UDim2.fromOffset(d, d), Position = UDim2.fromScale(s[2] / 100, s[3] / 100),
				AnchorPoint = Vector2.new(0.5, 0.5), ZIndex = z + (two and 1 or 0)})
			corner(f, "pill")
			stroke(f, two and c2 or c1, t)
		end
	end
	return box
end

-- o.color / o.tone2: colours for vector icons. o.mode forces a mode.
local function icon(parent, key, px, o)
	o = o or {}
	local mode = o.mode or R.icons
	if mode == "none" then
		return nil
	end
	local kname = KIT_ICON[key]
	if kname and mode == "emoji" then
		local img, rect = nil, nil
		if R.sheet and ICON_RECT[kname] then
			img, rect = R.sheet, ICON_RECT[kname]
		else
			local i2, s = kitSprite("Icons", kname)
			if i2 then
				img, rect = i2, {s[2], s[3], s[4], s[5]}
			end
		end
		if img then
			return new("ImageLabel", {Name = o.name or "Icon", Image = img, ImageRectOffset = Vector2.new(rect[1], rect[2]),
				ImageRectSize = Vector2.new(rect[3], rect[4]), Size = UDim2.fromOffset(px, px),
				Position = o.pos or UDim2.fromScale(0.5, 0.5), AnchorPoint = o.anchor or Vector2.new(0.5, 0.5),
				BackgroundTransparency = 1, ZIndex = o.z or 4, Rotation = o.rot or 0, Parent = parent})
		end
	end
	if mode == "vector" then
		return vicon(parent, key, px, o.color or WHITE, o.tone2 or BLACK, o)
	end
	local ep = math.floor(px * 0.8)
	return new("TextLabel", {Name = o.name or "Icon", Text = EMOJI[key] or "⭐", TextScaled = true,
		FontFace = fontFace("GothamBold"), BackgroundTransparency = 1, TextColor3 = WHITE, Size = UDim2.fromOffset(ep, ep),
		Position = o.pos or UDim2.fromScale(0.5, 0.5), AnchorPoint = o.anchor or Vector2.new(0.5, 0.5), ZIndex = o.z or 4,
		Rotation = o.rot or 0, Parent = parent})
end

-----------------------------------------------------------------------------------------------
-- components
-----------------------------------------------------------------------------------------------
local function cluster(root, name, anchor, pos, w, h)
	local f = frame(root, name, {AnchorPoint = anchor, Position = pos, Size = UDim2.fromOffset(w, h)})
	local s = new("UIScale", {Name = "AutoScale", Scale = R.scale, Parent = f})
	s:SetAttribute("AutoScale", true)
	return f
end

local function hover(box)
	new("UIScale", {Name = "HoverScale", Parent = box})
	box:SetAttribute("Fx", true)
	return box
end

-- a button: o.role ("button", "action", "tab", "tabOff"), o.icon, o.ts, o.kind, o.anchor, o.opens
local function button(parent, name, text, key, w, h, pos, o)
	o = o or {}
	local role = o.role or "button"
	local box, body, content, face, pnt = surface(parent, {name = name, w = w, h = h, pos = pos, anchor = o.anchor,
		key = key, role = role, kind = o.kind or "button", button = true, tiltSign = o.tiltSign, radius = o.radius,
		noDeco = o.noDeco, shadow = o.shadow, tilt = o.tilt, z = o.z})
	local ts = o.ts or math.floor(h * 0.44)
	local left = 0
	if o.icon and R.icons ~= "none" then
		local ip = math.floor(h * 0.6)
		icon(content, o.icon, ip, {pos = UDim2.new(0, math.floor(h * 0.18) + ip / 2 + 4, 0.5, 0), color = pnt.text,
			tone2 = pnt.fill})
		left = ip + math.floor(h * 0.18)
	end
	if text and text ~= "" then
		label(content, text, {name = "Text", size = UDim2.new(1, -(left + 12), 1, 0), pos = UDim2.fromOffset(left + 6, 0),
			ts = ts, role = "button", color = pnt.text, stroke = pnt.textStroke, z = 6})
	end
	if o.opens then
		box:SetAttribute("Opens", o.opens)
	end
	if o.action then
		box:SetAttribute("Action", o.action)
	end
	hover(box)
	return box, pnt, content
end

local function pnl()
	return ST.panel(T)
end

-- the small round/square close button of a window
local function closeButton(parent, winName, pos, anchor, size)
	local form = ST.close
	local b
	size = size or 60
	if form == "text" then
		b = new("ImageButton", {Name = "Close", Image = "", BackgroundTransparency = 1, AutoButtonColor = false,
			Size = UDim2.fromOffset(150, 40), Position = pos, AnchorPoint = anchor or Vector2.new(0, 0), ZIndex = 20,
			Parent = parent})
		local l = label(b, "[ close ]", {name = "Text", ts = 24, color = pnl().dim, x = Enum.TextXAlignment.Right})
		l:SetAttribute("Flicker", true)
		b:SetAttribute("Fx", "row")
		new("UIScale", {Name = "HoverScale", Parent = b})
	else
		local c
		b, _, c = surface(parent, {name = "Close", w = size, h = size, pos = pos, anchor = anchor, key = "Red",
			role = "action", kind = "small", button = true, radius = form == "round" and "pill" or nil, tilt = 0, z = 20})
		if R.icons == "vector" then
			vicon(c, "close", math.floor(size * 0.5), WHITE, BLACK)
		else
			label(c, "X", {name = "Text", ts = math.floor(size * 0.6), role = "button", color = WHITE,
				stroke = darker(T.color("Red"), 0.6), z = 6})
		end
		hover(b)
	end
	b:SetAttribute("Closes", winName)
	return b
end

-----------------------------------------------------------------------------------------------
-- HUD pieces, drawn per style
-----------------------------------------------------------------------------------------------
local MENU_SIZE = {rings = {128, 176}, tiles = {104, 124}, circles = {100, 136}, rows = {260, 52}, bars = {250, 70},
	chips = {64, 96}, plaques = {96, 136}}

local function goldText()
	return {hex("FFF8B8"), hex("F4C22E")}
end

-- one menu button (entry: id, label, icon, key, opens, hotkey, gold)
local function menuButton(parent, e, x, y, i)
	local form = ST.menu
	local pnt = ST.paint(T, e.key or "Primary", "menu")
	local box, content
	if form == "rings" then
		local s = 128
		box = new("ImageButton", {Name = e.id, Image = "", BackgroundTransparency = 1, AutoButtonColor = false,
			Size = UDim2.fromOffset(s, s), Position = UDim2.fromOffset(x, y), Parent = parent})
		local body = frame(box, "Body", {BackgroundTransparency = 0.22, BackgroundColor3 = hex("2B3038"), Size = UDim2.fromScale(1, 1),
			ZIndex = 1})
		corner(body, "pill")
		stroke(body, hex("14171B"), 3, 0.1)
		local rim = frame(body, "Rim", {Size = UDim2.new(1, -10, 1, -10), Position = UDim2.fromOffset(5, 5), ZIndex = 1})
		corner(rim, "pill")
		stroke(rim, hex("6A727E"), 2, 0.45)
		icon(box, e.icon, 128, {pos = UDim2.new(0.5, 0, 0.5, -10), z = 5})
		label(box, e.label, {name = "Text", size = UDim2.new(1, 70, 0, 48), pos = UDim2.new(0.5, 0, 1, -12),
			anchor = Vector2.new(0.5, 0.5), ts = 38, role = "button", stroke = INK, strokeW = 3.5, z = 6,
			gradient = e.gold and goldText() or nil})
	elseif form == "tiles" then
		local s = 104
		box, _, content = surface(parent, {name = e.id, w = s, h = s, pos = UDim2.fromOffset(x, y), key = e.key, role = "menu",
			kind = "tile", button = true, paint = pnt, tiltSign = (i % 2 == 0) and -1 or 1})
		icon(content, e.icon, 70, {pos = UDim2.fromScale(0.5, 0.44), color = pnt.text, tone2 = pnt.fill})
		label(box, e.label, {name = "Text", size = UDim2.new(1, 44, 0, 34), pos = UDim2.new(0.5, 0, 1, -6),
			anchor = Vector2.new(0.5, 0.5), ts = 27, role = "button", color = WHITE,
			stroke = pnt.textStroke or darker(pnt.fill, 0.6), strokeW = math.max(ST.textStroke, 2), z = 10})
	elseif form == "circles" then
		local s = 100
		box, _, content = surface(parent, {name = e.id, w = s, h = s, pos = UDim2.fromOffset(x, y), key = e.key, role = "menu",
			kind = "chip", button = true, paint = pnt, radius = "pill"})
		icon(box, e.icon, 92, {pos = UDim2.new(0.5, 0, 0.5, -14), z = 11, color = pnt.text, tone2 = pnt.fill})
		local tag, _, tc = surface(box, {name = "Tag", w = 112, h = 34, pos = UDim2.new(0.5, 0, 1, 4),
			anchor = Vector2.new(0.5, 0.5), key = e.key, role = "menu", kind = "pill", radius = "pill", z = 12, noDeco = true,
			shadow = "none", tilt = 0})
		label(tc, e.label, {name = "Text", ts = 22, role = "button", color = WHITE, stroke = pnt.textStroke, z = 6})
	elseif form == "rows" then
		box = new("ImageButton", {Name = e.id, Image = "", BackgroundTransparency = 1, AutoButtonColor = false,
			Size = UDim2.fromOffset(260, 44), Position = UDim2.fromOffset(x, y), Parent = parent})
		frame(box, "Accent", {BackgroundTransparency = 1, BackgroundColor3 = T.Primary, Size = UDim2.new(0, 3, 0.7, 0),
			Position = UDim2.fromScale(0, 0.15)})
		label(box, e.label, {name = "Text", size = UDim2.new(1, -60, 1, 0), pos = UDim2.fromOffset(16, 0),
			x = Enum.TextXAlignment.Left, ts = 30, role = "button", color = pnl().text, flicker = true})
		if e.hotkey then
			label(box, "[" .. e.hotkey .. "]", {name = "Key", size = UDim2.new(0, 60, 1, 0), pos = UDim2.new(1, -60, 0, 0),
				x = Enum.TextXAlignment.Right, ts = 20, color = pnl().dim, role = "number"})
		end
		box:SetAttribute("Fx", "row")
	elseif form == "bars" then
		box, _, content = surface(parent, {name = e.id, w = 250, h = 58, pos = UDim2.fromOffset(x, y), key = e.key,
			role = "menu", kind = "button", button = true, paint = pnt})
		icon(content, e.icon, 38, {pos = UDim2.new(0, 36, 0.5, 0), color = pnt.accent or WHITE, tone2 = pnt.fill})
		label(content, e.label, {name = "Text", size = UDim2.new(1, -74, 1, 0), pos = UDim2.fromOffset(64, 0),
			x = Enum.TextXAlignment.Left, ts = 28, role = "button", color = WHITE, stroke = pnt.textStroke})
	elseif form == "chips" then
		box, _, content = surface(parent, {name = e.id, w = 64, h = 64, pos = UDim2.fromOffset(x, y), key = e.key,
			role = "menu", kind = "chip", button = true, paint = pnt})
		icon(content, e.icon, 36, {color = pnt.accent or pnt.text, tone2 = pnt.fill})
		label(box, e.label, {name = "Text", size = UDim2.new(1, 50, 0, 22), pos = UDim2.new(0.5, 0, 1, 14),
			anchor = Vector2.new(0.5, 0.5), ts = 17, role = "body", color = ST.menuLabel or WHITE, z = 10,
			stroke = BLACK, strokeW = (ST.menuLabel and 0) or 1.5, strokeT = 0.4})
	elseif form == "plaques" then
		box, _, content = surface(parent, {name = e.id, w = 96, h = 96, pos = UDim2.fromOffset(x, y), key = e.key,
			role = "menu", kind = "chip", button = true, paint = pnt, radius = "pill"})
		icon(content, e.icon, 60, {color = pnt.text, tone2 = pnt.fill})
		local rib, _, rc = surface(box, {name = "Ribbon", w = 116, h = 32, pos = UDim2.new(0.5, 0, 1, 2),
			anchor = Vector2.new(0.5, 0.5), key = "Red", role = "action", kind = "small", z = 12, noDeco = true,
			shadow = "none", tilt = 0})
		label(rc, e.label, {name = "Text", ts = 19, role = "button", color = hex("FFF1C9"), stroke = hex("2A170A"), strokeW = 1.5})
	end
	if e.opens then
		box:SetAttribute("Opens", e.opens)
	end
	return hover(box)
end

local function menuColumn(root, name, entries, side, yOff)
	local sz = MENU_SIZE[ST.menu] or MENU_SIZE.tiles
	local stair = ST.menu == "bars" and 14 or 0
	local w = sz[1] + 50 + stair * #entries
	local h = #entries * sz[2]
	local right = side == "right"
	local c = cluster(root, name, Vector2.new(right and 1 or 0, 0.5),
		UDim2.new(right and 1 or 0, right and -24 or 24, 0.5, yOff or 0), w, h)
	for i, e in ipairs(entries) do
		local dx = stair * (i - 1)
		local x = right and (w - sz[1] - 25 - dx) or (25 + dx)
		menuButton(c, e, x, (i - 1) * sz[2], i)
	end
	return c
end

local function menuRow(root, name, entries, anchor, pos)
	local sz = MENU_SIZE[ST.menu] or MENU_SIZE.tiles
	local step = ({rings = 160, tiles = 124, circles = 130, rows = 200, bars = 262, chips = 92, plaques = 130})[ST.menu] or 124
	local w = #entries * step
	local h = ST.menu == "rows" and 44 or sz[2]
	local c = cluster(root, name, anchor, pos, w, h)
	for i, e in ipairs(entries) do
		menuButton(c, e, (i - 1) * step + (step - sz[1]) / 2, 0, i)
	end
	return c
end

-- a currency display (c: name, icon, key, value, cash). Returns the frame.
local function currency(parent, c, x, y, o)
	o = o or {}
	local form = ST.currency
	local big = o.big and 1.3 or 1
	local h = math.floor(60 * big)
	local w = math.floor(290 * big)
	local text = (c.cash and "$" or "") .. commas(c.value or 0)
	local numColor, numStroke, numGrad = WHITE, INK, nil
	local root
	if form == "fade" then
		h = math.floor(80 * big)
		root = frame(parent, c.name .. "Row", {Size = UDim2.fromOffset(math.floor(430 * big), h), Position = UDim2.fromOffset(x, y)})
		local bar = frame(root, "Bar", {BackgroundTransparency = 0.3, BackgroundColor3 = hex("3B414C"),
			Size = UDim2.new(1, 0, 1, -18), Position = UDim2.fromOffset(0, 9)})
		new("UIGradient", {Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0),
			NumberSequenceKeypoint.new(0.5, 0.3), NumberSequenceKeypoint.new(1, 1)}), Parent = bar})
		for _, yy in ipairs({0, 1}) do
			local ln = frame(bar, "Line", {BackgroundTransparency = yy == 0 and 0.45 or 0.6, BackgroundColor3 = yy == 0 and WHITE or BLACK,
				Size = UDim2.new(1, 0, 0, 2), Position = UDim2.new(0, 0, yy, yy == 0 and 0 or -2)})
			new("UIGradient", {Transparency = NumberSequence.new(0, 1), Parent = ln})
		end
		icon(root, c.icon, math.floor(h * 1.3), {pos = UDim2.fromOffset(math.floor(h * 0.75), math.floor(h / 2)), z = 4, rot = -6})
		if c.cash then
			numGrad = {hex("D8FF7A"), hex("3CC21E")}
		end
		label(root, text, {name = c.name, size = UDim2.new(1, -math.floor(h * 1.45), 1, 0), pos = UDim2.fromOffset(math.floor(h * 1.45), 0),
			x = Enum.TextXAlignment.Left, ts = math.floor(h * 0.74), role = "number", stroke = INK, strokeW = 3.5, z = 5,
			gradient = numGrad})
		root:FindFirstChild(c.name):SetAttribute("Currency", c.name)
		root:FindFirstChild(c.name):SetAttribute("Prefix", c.cash and "$" or "")
		return root
	end
	local paint
	local radius = "pill"
	local tilt = 0
	local iconOut = true
	if form == "pill" then
		paint = {fill = hex("1A1C26"), t = 0.25, stroke = BLACK, strokeT = 0.5, strokeW = 2, text = WHITE}
	elseif form == "bubble" then
		paint = {fill = WHITE, stroke = T.color(c.key), strokeW = 4, text = darker(T.Outline, 0.1)}
		numColor, numStroke = darker(T.Outline, 0.1), nil
	elseif form == "sticker" then
		paint = {fill = WHITE, stroke = hex("141414"), strokeW = 4, text = hex("141414")}
		radius, tilt = 8, -2
		numColor, numStroke = hex("141414"), nil
	elseif form == "slanted" then
		paint = {fill = T.Panel, t = 0.1, stroke = T.color(c.key), strokeW = 2, accent = T.color(c.key), text = WHITE}
		radius, tilt = 0, -5
		numStroke = BLACK
	elseif form == "readout" then
		paint = {fill = T.Panel2, t = 0.3, stroke = T.Primary, strokeW = 1.5, strokeT = 0.3, accent = T.Primary}
		radius, iconOut = 2, false
		numColor, numStroke = lighter(T.Primary, 0.5), nil
	elseif form == "plank" then
		paint = {fill = T.Primary, stroke = T.Accent, strokeW = 2, accent = T.Accent, frame = hex("2A170A")}
		radius = 6
		numColor, numStroke = hex("FFF1C9"), hex("2A170A")
	elseif form == "chip" then
		paint = ST.paint(T, c.key, "menu")
		numColor, numStroke = paint.text, nil
		iconOut = false
	elseif form == "box" then
		paint = {fill = T.Panel2, stroke = BLACK, strokeW = 4}
		radius = 0
		numColor, numStroke = T.Accent, nil
	else -- "text"
		root = frame(parent, c.name .. "Row", {Size = UDim2.fromOffset(w, 40), Position = UDim2.fromOffset(x, y)})
		local l = label(root, text, {name = c.name, x = Enum.TextXAlignment.Left, ts = 30, role = "number", color = pnl().text})
		l:SetAttribute("Currency", c.name)
		l:SetAttribute("Prefix", c.cash and "$" or "")
		return root
	end
	local box, _, content = surface(parent, {name = c.name .. "Row", w = w, h = h, pos = UDim2.fromOffset(x, y), paint = paint,
		kind = "pill", radius = radius, tilt = tilt, noStuds = true, noGloss = true,
		shadow = (form == "sticker" or form == "box") and "hard" or "none", surface = form == "plank" and "wood" or "flat",
		noDeco = form ~= "readout" and form ~= "plank"})
	local ip = iconOut and math.floor(h * 1.25) or math.floor(h * 0.62)
	icon(iconOut and box or content, c.icon, ip, {pos = UDim2.fromOffset(iconOut and math.floor(h * 0.3) or math.floor(h * 0.55), math.floor(h / 2)),
		z = 11, color = T.color(c.key), tone2 = paint.fill})
	local left = iconOut and math.floor(h * 0.95) or math.floor(h * 1.05)
	local l = label(content, text, {name = c.name, size = UDim2.new(1, -(left + 60), 1, 0), pos = UDim2.fromOffset(left, 0),
		x = Enum.TextXAlignment.Left, ts = math.floor(h * 0.62), role = "number", color = numColor, stroke = numStroke,
		strokeW = numStroke and math.max(ST.textStroke, 2) or 0, z = 6})
	l:SetAttribute("Currency", c.name)
	l:SetAttribute("Prefix", c.cash and "$" or "")
	if o.plus ~= false then
		button(content, "Buy" .. c.name, "+", "Green", h - 16, h - 16, UDim2.new(1, -(h - 8), 0, 8),
			{kind = "small", ts = math.floor(h * 0.55), opens = "Shop", noDeco = true, shadow = "none", tilt = 0,
				radius = radius == "pill" and "pill" or nil})
	end
	return box
end

-- progress bar: returns back, fill
local function bar(parent, name, frac, key, w, h, pos, text, o)
	o = o or {}
	local form = o.form or ST.bars
	local col = T.color(key)
	if form == "line" then
		local root = frame(parent, name, {Size = UDim2.fromOffset(w, h + 24), Position = pos, AnchorPoint = o.anchor or Vector2.new(0, 0)})
		if text then
			label(root, text, {name = "Text", size = UDim2.new(1, 0, 0, 22), x = Enum.TextXAlignment.Left, ts = 20,
				color = pnl().dim})
		end
		local back = frame(root, "Back", {BackgroundTransparency = 0.8, BackgroundColor3 = pnl().text,
			Size = UDim2.new(1, 0, 0, 4), Position = UDim2.new(0, 0, 1, -4)})
		local fill = frame(back, "Fill", {BackgroundTransparency = 0, BackgroundColor3 = col, Size = UDim2.fromScale(frac, 1)})
		return root, fill
	end
	if form == "segments" then
		local root = frame(parent, name, {Size = UDim2.fromOffset(w, h), Position = pos, AnchorPoint = o.anchor or Vector2.new(0, 0)})
		local n = 10
		local gap = 4
		local sw = (w - gap * (n - 1)) / n
		local fill
		for i = 1, n do
			local on = i <= math.floor(frac * n + 0.5)
			local seg = frame(root, on and "On" or "Off", {BackgroundTransparency = on and 0.05 or 0.75,
				BackgroundColor3 = on and col or darker(col, 0.5), Size = UDim2.fromOffset(sw, h),
				Position = UDim2.fromOffset((i - 1) * (sw + gap), 0)})
			if R.style == "Pixel" then
				stroke(seg, BLACK, 2, 0, true)
			end
			fill = fill or seg
		end
		if text then
			label(root, text, {name = "Text", size = UDim2.new(1, 0, 0, 20), pos = UDim2.fromOffset(0, -24),
				x = Enum.TextXAlignment.Left, ts = 18, role = "body", color = lighter(col, 0.4)})
		end
		return root, fill
	end
	local backPaint = {fill = hex("20242E"), t = 0.15, stroke = INK, strokeW = 2.5}
	local radius = "pill"
	local tilt = 0
	local shadow = "none"
	if form == "thick" then
		backPaint = {fill = WHITE, stroke = hex("141414"), strokeW = 4}
		shadow = "hard"
	elseif form == "framed" then
		backPaint = {fill = hex("2A170A"), stroke = T.Accent, strokeW = 2}
		radius = 4
	elseif form == "slanted" then
		backPaint = {fill = T.Panel2, t = 0.1, stroke = col, strokeW = 2}
		radius, tilt = 0, -5
	elseif form == "pill" and (R.style == "Minimal" or R.style == "Glass") then
		backPaint = {fill = R.style == "Glass" and WHITE or pnl().inner, t = R.style == "Glass" and 0.75 or 0}
	elseif form == "studded" then
		backPaint = {fill = hex("1B1E2A"), t = 0.1, stroke = BLACK, strokeW = 2, strokeT = 0.3}
	end
	local back, _, bc = surface(parent, {name = name, w = w, h = h, pos = pos, anchor = o.anchor, paint = backPaint, kind = "pill",
		radius = radius, tilt = tilt, noDeco = true, shadow = shadow, surface = "flat"})
	local fw = math.max(h, math.floor(w * frac))
	local fill = surface(bc, {name = "Fill", w = fw, h = h, size = UDim2.new(frac, 0, 1, 0), paint = {fill = col, text = WHITE},
		kind = "pill", radius = radius, tilt = 0, shadow = "none", noDeco = form ~= "studded", noGloss = false,
		surface = (R.style == "Sim" and "vivid") or "gradient"})
	if frac <= 0 then
		fill.Visible = false
	end
	if text then
		label(bc, text, {name = "Text", ts = math.floor(h * 0.62), role = "number",
			color = form == "thick" and hex("141414") or WHITE, stroke = (form ~= "thick") and INK or nil,
			strokeW = 2.5, z = 12})
	end
	return back, fill
end

-- a slot (hotbar / inventory cell)
local function slot(parent, name, w, h, pos, rim, o)
	o = o or {}
	local pp = pnl()
	local paint
	if ST.hotbar == "slate" then
		paint = {fill = hex("3C5659"), stroke = rim or INK, strokeW = 3, text = WHITE}
	else
		paint = {fill = pp.inner, t = pp.innerT, stroke = rim or pp.line, strokeW = math.max(2, ST.outlineW),
			strokeT = rim and 0 or 0.4, text = pp.text, accent = rim}
	end
	local box, body, content = surface(parent, {name = name, w = w, h = h, pos = pos, kind = "small", paint = paint,
		button = true, noStuds = true, noGloss = true, noDeco = true, tilt = 0,
		shadow = ST.shadow == "hard" and "hard" or "none", surface = ST.hotbar == "slate" and "slate" or "flat",
		radius = o.radius})
	if ST.hotbar == "slate" then
		body:FindFirstChildOfClass("UIStroke").Thickness = 3
		local face = body
		face.BackgroundColor3 = WHITE
		new("UIGradient", {Rotation = 90, Color = ColorSequence.new(hex("48676A"), hex("2F4547")), Parent = face})
	end
	return hover(box), content
end

-- the per-style colour of a card, returns paint and the key used
local CARD_KEYS = {"Blue", "Orange", "Purple", "Green", "Pink", "Gold"}
local function cardPaint(i, key)
	key = key or CARD_KEYS[(i - 1) % #CARD_KEYS + 1]
	if ST.colorful then
		local p = copy(ST.paint(T, key, "card"))
		return p, key
	end
	local pp = pnl()
	return {fill = pp.inner, t = pp.innerT, stroke = T.color(key), strokeW = math.max(1.5, ST.outlineW), strokeT = 0.2,
		text = pp.text, accent = T.color(key)}, key
end

-- a price button: Robux icon + price (Sim) or coin + price
local function priceButton(parent, name, price, key, w, h, pos, robux)
	local b, pnt, content = button(parent, name, "", key or "Green", w, h, pos, {role = "action", action = "Buy"})
	local ip = math.floor(h * 0.62)
	if robux then
		vicon(content, "robux", ip, WHITE, pnt.fill, {pos = UDim2.new(0, math.floor(h * 0.14) + ip / 2, 0.5, 0), z = 7})
	else
		icon(content, "coin", ip, {pos = UDim2.new(0, math.floor(h * 0.14) + ip / 2, 0.5, 0), z = 7, color = T.color("Gold"),
			tone2 = pnt.fill})
	end
	label(content, commas(price), {name = "Price", size = UDim2.new(1, -(ip + 22), 1, 0), pos = UDim2.fromOffset(ip + 18, -2),
		ts = math.floor(h * 0.74), role = "number", color = pnt.text, stroke = pnt.textStroke or INK,
		strokeW = math.max(ST.textStroke, 2.5), z = 7})
	return b
end

-- an item card (shop / gamepass / unit / car...). it: name, sub, icon, price, key, robux, stats, action, old
local function card(parent, it, i, w, h)
	local paint, key = cardPaint(i, it.key)
	local c = T.color(key)
	local box, body, content, face = surface(parent, {name = it.name, w = w, h = h, kind = "card", paint = paint,
		surface = ST.colorful and "card" or nil, tilt = 0, noStuds = not ST.colorful, button = false})
	box.LayoutOrder = i
	local tc, ts = paint.text, paint.textStroke
	if ST.cards == "hex" then
		local hs = math.floor(h * 0.56)
		hexagon(content, "Badge", UDim2.new(0.5, 0, 0, math.floor(h * 0.33)), hs, lighter(c, 0.05), darker(c, 0.32), 6, 2, 30)
		hexagon(content, "BadgeInner", UDim2.new(0.5, 0, 0, math.floor(h * 0.33)), math.floor(hs * 0.8), lighter(c, 0.3), nil, 0, 3, 30)
		icon(content, it.icon, math.floor(h * 0.54), {pos = UDim2.new(0.5, 0, 0, math.floor(h * 0.31)), z = 6})
		label(content, it.name, {name = "Title", size = UDim2.new(1, -12, 0, math.floor(h * 0.14)),
			pos = UDim2.new(0.5, 0, 0, math.floor(h * 0.61)), anchor = Vector2.new(0.5, 0.5), ts = math.floor(h * 0.12),
			role = "title", stroke = INK, strokeW = 3.5, z = 7})
		if it.sub then
			label(content, it.sub, {name = "Sub", size = UDim2.new(1, -12, 0, math.floor(h * 0.08)),
				pos = UDim2.new(0.5, 0, 0, math.floor(h * 0.705)), anchor = Vector2.new(0.5, 0.5), ts = math.floor(h * 0.062),
				role = "body", stroke = INK, strokeW = 2.5, z = 7})
		end
		local bh = math.floor(h * 0.2)
		priceButton(content, "Buy", it.price or 99, "Green", w - bh - 34, bh, UDim2.new(0, 12, 1, -(bh + 12)), it.robux ~= false)
		local g, gp, gc = button(content, "Gift", "", "Pink", bh, bh, UDim2.new(1, -(bh + 12), 1, -(bh + 12)), {role = "action",
			action = "Gift"})
		icon(gc, "daily", math.floor(bh * 0.8), {z = 7, color = WHITE, tone2 = gp.fill})
		if it.old then
			local o = label(content, commas(it.old), {name = "Old", size = UDim2.fromOffset(120, 26),
				pos = UDim2.new(0.5, -bh / 2, 1, -(bh + 18)), anchor = Vector2.new(0.5, 0.5), ts = 24, role = "number",
				color = hex("E8323C"), stroke = INK, strokeW = 2, z = 9})
			frame(o, "Strike", {BackgroundTransparency = 0, BackgroundColor3 = hex("E8323C"), Size = UDim2.new(1, 0, 0, 3),
				Position = UDim2.fromScale(0, 0.5), Rotation = -6, ZIndex = 4})
		end
		return box
	end
	-- the other styles: icon left/top, title, price row, stat bars, action button
	local ip = math.floor(math.min(h * 0.5, w * 0.36))
	icon(content, it.icon, ip, {pos = UDim2.new(1, -math.floor(ip * 0.62), 0, math.floor(ip * 0.62) + 4), color = paint.accent or c,
		tone2 = paint.fill, z = 6})
	label(content, it.name, {name = "Title", size = UDim2.new(1, -(ip + 20), 0, 34), pos = UDim2.fromOffset(14, 8),
		x = Enum.TextXAlignment.Left, ts = 26, role = "button", color = tc, stroke = ts, z = 7})
	if it.sub then
		label(content, it.sub, {name = "Sub", size = UDim2.new(1, -(ip + 20), 0, 22), pos = UDim2.fromOffset(14, 40),
			x = Enum.TextXAlignment.Left, ts = 18, role = "body", color = ST.colorful and WHITE or pnl().dim,
			stroke = ST.colorful and ts or nil, strokeW = 1.5, z = 7})
	end
	local y = 70
	for _, st in ipairs(it.stats or {}) do
		label(content, st[1], {size = UDim2.fromOffset(90, 18), pos = UDim2.fromOffset(14, y), x = Enum.TextXAlignment.Left,
			ts = 16, color = ST.colorful and WHITE or pnl().dim, stroke = ST.colorful and ts or nil, strokeW = 1.5, z = 7})
		bar(content, "Stat", st[2], st[3] or key, w - 130, 12, UDim2.fromOffset(104, y + 3), nil, {form = ST.bars == "line"
			and "line" or (ST.bars == "segments" and "segments" or "pill")})
		y = y + 24
	end
	local bh = math.max(38, math.floor(h * 0.24))
	if it.price then
		priceButton(content, "Buy", it.price, "Green", math.floor(w * 0.52), bh, UDim2.new(1, -(math.floor(w * 0.52) + 12), 1, -(bh + 10)),
			it.robux)
	else
		button(content, "Select", it.action or "Select", "Green", math.floor(w * 0.45), bh,
			UDim2.new(1, -(math.floor(w * 0.45) + 12), 1, -(bh + 10)), {role = "action", action = it.action or "Select"})
	end
	return box
end

-----------------------------------------------------------------------------------------------
-- windows
-----------------------------------------------------------------------------------------------
local function textWidth(s, ts)
	return #s * ts * (ST.charW or 0.52) * (ST.textScale or 1)
end

local function panelSurface(parent, name, w, h, pos)
	local pp = pnl()
	local paint = {fill = pp.fill, t = pp.t, stroke = pp.stroke, strokeW = pp.strokeW, strokeT = pp.strokeT,
		accent = pp.line, text = pp.text, frame = pp.outer}
	local surf = "flat"
	if ST.surface == "glass" then
		surf = "glass"
	elseif ST.surface == "dark" then
		surf = "dark"
	end
	local shadow = ST.shadow
	if shadow == "lip" or shadow == "colored" then
		shadow = "none"
	end
	local box, body, content, face = surface(parent, {name = name, w = w, h = h, pos = pos, kind = "panel", paint = paint,
		surface = surf, noStuds = true, noGloss = true, shadow = shadow, tilt = 0})
	if pp.tint then
		gradient(face, WHITE, WHITE, pp.tint)
	end
	return box, content, pp
end

local function scroller(parent, name, size, pos)
	local sf = new("ScrollingFrame", {Name = name or "List", Size = size or UDim2.fromScale(1, 1), Position = pos or UDim2.new(),
		BackgroundTransparency = 1, ScrollBarThickness = 8,
		ScrollBarImageColor3 = R.style == "Sim" and hex("9A9DB3") or pnl().line, ScrollBarImageTransparency = 0.15,
		CanvasSize = UDim2.new(), AutomaticCanvasSize = Enum.AutomaticSize.Y, ScrollingDirection = Enum.ScrollingDirection.Y,
		Parent = parent})
	new("UIPadding", {PaddingTop = UDim.new(0, 10), PaddingLeft = UDim.new(0, 8), PaddingRight = UDim.new(0, 16),
		PaddingBottom = UDim.new(0, 12), Parent = sf})
	return sf
end

-- def: name, title, sub, icon, w, h, header, place. Returns content, width, height.
local function window(wins, def)
	local place = def.place or R.windows
	local pp = pnl()
	local W = frame(wins, def.name, {Size = UDim2.fromScale(1, 1), Visible = false})
	W:SetAttribute("Window", true)
	W:SetAttribute("Place", place)
	if place == "fullscreen" or ST.dim then
		frame(W, "Backdrop", {BackgroundTransparency = place == "fullscreen" and 0.05 or 0.45,
			BackgroundColor3 = place == "fullscreen" and darker(pp.fill, 0.2) or BLACK, Size = UDim2.fromScale(1, 1),
			Active = true, ZIndex = 1})
	end
	local w, h = def.w, def.h
	local panel
	if place == "side" then
		panel = frame(W, "Panel", {Size = UDim2.fromOffset(w, h), Position = UDim2.new(1, -30, 0.5, 0),
			AnchorPoint = Vector2.new(1, 0.5), ZIndex = 2})
	else
		panel = frame(W, "Panel", {Size = UDim2.fromOffset(w, h), Position = UDim2.fromScale(0.5, 0.52),
			AnchorPoint = Vector2.new(0.5, 0.5), ZIndex = 2})
	end
	local as = new("UIScale", {Name = "AutoScale", Scale = R.scale, Parent = panel})
	as:SetAttribute("AutoScale", true)
	local pop = frame(panel, "Pop", {Size = UDim2.fromScale(1, 1), Position = UDim2.fromScale(0.5, 0.5),
		AnchorPoint = Vector2.new(0.5, 0.5)})
	new("UIScale", {Name = "PopScale", Parent = pop})
	local form = def.header or ST.header
	local pad = 24
	local top, ctop = 0, 90
	if form == "border" then
		top, ctop = 46, def.sub and 110 or 64
	elseif form == "strip" then
		top, ctop = 34, 150
	elseif form == "bar" or form == "tag" or form == "ribbon" then
		top, ctop = 32, 70
	elseif form == "banner" then
		top, ctop = 38, 74
	end
	panelSurface(pop, "Body", w, h - top, UDim2.fromOffset(0, top))
	local tcol = pp.text
	if form == "border" then
		local ts = def.ts or 66
		local tw = math.min(w - 280, textWidth(def.title, ts))
		label(pop, def.title, {name = "Title", size = UDim2.fromOffset(tw + 60, ts + 24), pos = UDim2.new(0.5, 40, 0, top),
			anchor = Vector2.new(0.5, 0.5), ts = ts, role = "title", stroke = INK, strokeW = 4.5, z = 20})
		icon(pop, def.icon, math.floor(ts * 1.8), {pos = UDim2.new(0.5, math.floor(40 - tw / 2 - ts * 0.8), 0, top - 8), z = 21,
			rot = -10})
		if def.sub then
			label(pop, def.sub, {name = "Sub", size = UDim2.fromOffset(w - 200, 46), pos = UDim2.new(0.5, 0, 0, top + 60),
				anchor = Vector2.new(0.5, 0.5), ts = 40, role = "title", stroke = INK, strokeW = 3.5, z = 20})
		end
		closeButton(pop, def.name, UDim2.new(1, -10, 0, top), Vector2.new(0.5, 0.5), 88)
	elseif form == "strip" then
		local strip = frame(pop, "Strip", {BackgroundTransparency = 0, BackgroundColor3 = lighter(T.color("Gold"), 0.55),
			Size = UDim2.new(1, -24, 0, 118), Position = UDim2.fromOffset(12, top + 12), ZIndex = 4})
		new("UIGradient", {Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0), NumberSequenceKeypoint.new(0.6, 0.2),
			NumberSequenceKeypoint.new(1, 0.9)}), Parent = strip})
		icon(pop, def.icon, 190, {pos = UDim2.fromOffset(62, top + 22), z = 21, rot = -10})
		label(pop, def.title, {name = "Title", size = UDim2.new(1, -330, 0, 80), pos = UDim2.fromOffset(170, top + 20),
			x = Enum.TextXAlignment.Left, ts = 70, role = "title", stroke = INK, strokeW = 4.5, z = 20})
		if def.sub then
			label(pop, def.sub, {name = "Sub", size = UDim2.new(1, -200, 0, 34), pos = UDim2.fromOffset(150, top + 92),
				x = Enum.TextXAlignment.Left, ts = 28, role = "body", color = hex("8F90A6"), z = 20})
		end
		closeButton(pop, def.name, UDim2.new(1, 0, 0, top + 10), Vector2.new(0.5, 0.5), 92)
	elseif form == "bar" then
		local hb, _, hc = surface(pop, {name = "Header", w = w - 96, h = 68, key = "Primary", role = "button", kind = "button",
			tilt = 0})
		icon(hc, def.icon, 58, {pos = UDim2.fromOffset(40, 32), color = WHITE, tone2 = T.Primary, z = 9})
		label(hc, def.title, {name = "Title", size = UDim2.new(1, -90, 1, 0), pos = UDim2.fromOffset(78, 0), x = Enum.TextXAlignment.Left,
			ts = 40, role = "title", stroke = darker(T.Primary, 0.6), z = 9})
		closeButton(pop, def.name, UDim2.new(1, -68, 0, 0), nil, 68)
	elseif form == "tag" then
		local tw = math.clamp(textWidth(def.title, 40) + 130, 240, w - 170)
		local tb, _, tc = surface(pop, {name = "Header", w = tw, h = 64, pos = UDim2.new(0.5, 0, 0, top), anchor = Vector2.new(0.5, 0.5),
			key = "Primary", role = "button", kind = "tag", tiltSign = 1})
		icon(tc, def.icon, 54, {pos = UDim2.fromOffset(38, 31), color = WHITE, tone2 = T.Primary, z = 9})
		label(tc, def.title, {name = "Title", size = UDim2.new(1, -80, 1, 0), pos = UDim2.fromOffset(66, 0), ts = 40, role = "title",
			stroke = ST.paint(T, "Primary", "button").textStroke, z = 9})
		closeButton(pop, def.name, UDim2.new(1, -12, 0, top), Vector2.new(0.5, 0.5), 62)
	elseif form == "banner" then
		local tw = math.clamp(textWidth(def.title, 50) + 110, 260, w * 0.7)
		local bb, _, bc = surface(pop, {name = "Header", w = tw, h = 78, pos = UDim2.fromOffset(-22, 0), key = "Primary",
			role = "action", kind = "button", tilt = -4, shadow = "colored"})
		label(bc, def.title, {name = "Title", size = UDim2.new(1, -40, 1, 0), pos = UDim2.fromOffset(28, 0), x = Enum.TextXAlignment.Left,
			ts = 54, role = "title", stroke = darker(T.Primary, 0.6), strokeW = 2.5, z = 9})
		closeButton(pop, def.name, UDim2.new(1, -18, 0, top + 18), Vector2.new(1, 0), 52)
	elseif form == "ribbon" then
		local tw = math.clamp(textWidth(def.title, 40) + 140, 280, w * 0.8)
		for _, sgn in ipairs({-1, 1}) do
			local tail = surface(pop, {name = "Tail", w = 70, h = 48, pos = UDim2.new(0.5, sgn * (tw / 2 - 6), 0, top + 14),
				anchor = Vector2.new(0.5, 0.5), paint = {fill = darker(T.Secondary, 0.35), stroke = T.Accent, strokeW = 2},
				kind = "small", tilt = 0, noDeco = true, shadow = "none", surface = "flat", z = 3})
		end
		local rb, _, rc = surface(pop, {name = "Header", w = tw, h = 60, pos = UDim2.new(0.5, 0, 0, top),
			anchor = Vector2.new(0.5, 0.5), paint = {fill = T.Secondary, stroke = T.Accent, strokeW = 2, frame = hex("2A170A")},
			kind = "button", tilt = 0, noDeco = true, surface = "gradient", z = 4})
		label(rc, def.title, {name = "Title", ts = 42, role = "title", color = T.Accent, stroke = hex("2A170A"), strokeW = 2, z = 9})
		closeButton(pop, def.name, UDim2.new(1, -8, 0, top + 8), Vector2.new(0.5, 0.5), 54)
	else -- "title" / "line"
		if form == "line" then
			tcol = T.Primary
		elseif R.style == "Horror" then
			tcol = T.Primary
		end
		label(pop, def.title, {name = "Title", size = UDim2.new(1, -(pad * 2 + 180), 0, 58), pos = UDim2.fromOffset(pad, 16),
			x = Enum.TextXAlignment.Left, ts = form == "line" and 32 or 48, role = "title", color = tcol, z = 20,
			flicker = R.style == "Horror"})
		if form == "line" then
			label(pop, "// " .. def.name:upper() .. "_MODULE", {name = "Sub", size = UDim2.fromOffset(400, 18),
				pos = UDim2.fromOffset(pad, 58), x = Enum.TextXAlignment.Left, ts = 14, role = "number", color = pp.dim, z = 20})
			frame(pop, "Seg", {BackgroundTransparency = 0, BackgroundColor3 = T.Primary, Size = UDim2.fromOffset(90, 4),
				Position = UDim2.fromOffset(pad, 80), ZIndex = 20})
		end
		frame(pop, "Divider", {BackgroundTransparency = 0.55, BackgroundColor3 = form == "line" and T.Primary or pp.line,
			Size = UDim2.new(1, -pad * 2, 0, 2), Position = UDim2.fromOffset(pad, 82), ZIndex = 20})
		closeButton(pop, def.name, UDim2.new(1, -pad, 0, 20), Vector2.new(1, 0), 48)
	end
	local content = frame(pop, "Content", {Size = UDim2.new(1, -pad * 2, 1, -(top + ctop + pad)),
		Position = UDim2.fromOffset(pad, top + ctop), ZIndex = 5})
	return content, w - pad * 2, h - (top + ctop + pad)
end

-- window contents ---------------------------------------------------------------------------
local W = {}

local function cardGrid(parent, items, cw, cols, cellH, name, order)
	local gap = 20
	local cellW = math.floor((cw - 26 - (cols - 1) * gap) / cols)
	local rows = math.ceil(#items / cols)
	local holder = frame(parent, name or "Cards", {Size = UDim2.new(1, 0, 0, rows * cellH + (rows - 1) * gap + 8),
		LayoutOrder = order or 1})
	new("UIGridLayout", {CellSize = UDim2.fromOffset(cellW, cellH), CellPadding = UDim2.fromOffset(gap, gap),
		SortOrder = Enum.SortOrder.LayoutOrder, HorizontalAlignment = Enum.HorizontalAlignment.Center, Parent = holder})
	for i, it in ipairs(items) do
		card(holder, it, i, cellW, cellH)
	end
	return holder
end

local function tabRow(parent, names, w, y)
	local tabs = frame(parent, "Tabs", {Size = UDim2.new(1, 0, 0, 58), Position = UDim2.new(0, 0, 1, y or -58)})
	new("UIListLayout", {FillDirection = Enum.FillDirection.Horizontal, Padding = UDim.new(0, 12),
		SortOrder = Enum.SortOrder.LayoutOrder, Parent = tabs})
	local tw = math.floor((w - 12 * (#names - 1)) / #names)
	for i, t in ipairs(names) do
		local b = button(tabs, t, t, "Green", math.min(tw, 220), 54, UDim2.new(), {role = i == 1 and "tab" or "tabOff", ts = 26,
			tilt = 0})
		b.LayoutOrder = i
		b:SetAttribute("Tab", t)
	end
	return tabs
end

-- the gamepass shop of the Sim look ("Exclusive Shop!")
function W.shopSim(c, cw, ch)
	local sf = scroller(c, "List")
	new("UIListLayout", {Padding = UDim.new(0, 26), SortOrder = Enum.SortOrder.LayoutOrder, Parent = sf})
	cardGrid(sf, {
		{name = "Fast Fishing", sub = "Fish 2x quicker", icon = "fishing", price = 299, key = "Blue"},
		{name = "Two Builders!", sub = "Build 2 steps at once", icon = "hammer", price = 399, key = "Orange"},
		{name = "x2 Materials", sub = "Earn 2x more materials", icon = "mushroom", price = 199, key = "Purple"},
		{name = "x2 Luck", sub = "Find rarer items", icon = "luck", price = 249, key = "Green"},
		{name = "VIP", sub = "+20% cash and a chat tag", icon = "crown", price = 499, key = "Gold"},
		{name = "Speed Coil", sub = "Run 50% faster", icon = "bolt", price = 149, key = "Pink"},
	}, cw, 3, 400, "Gamepasses", 1)
	local sec = label(sf, "Bonus Spins!", {name = "Heading", size = UDim2.new(1, 0, 0, 50), ts = 48, role = "title",
		stroke = INK, strokeW = 3.5})
	sec.LayoutOrder = 2
	cardGrid(sf, {
		{name = "x2 Spins!", icon = "crate", price = 99, key = "Green"},
		{name = "x5 Spins!", sub = "+1 more spin", icon = "crate", price = 500, old = 625, key = "Red"},
		{name = "x12 Spins!", sub = "+4 more spins", icon = "crate", price = 1000, old = 1500, key = "Orange"},
	}, cw, 3, 380, "Spins", 3)
	-- secret shop / codes
	local wide, _, wc = surface(sf, {name = "SecretShop", w = cw - 26, h = 250, kind = "card",
		paint = {fill = T.color("Blue"), stroke = INK, strokeW = 3.5, text = WHITE}, surface = "card", tilt = 0, button = false})
	wide.LayoutOrder = 4
	icon(wc, "dice", 250, {pos = UDim2.fromOffset(130, 135), z = 6, rot = -12})
	label(wc, "Secret Shop", {name = "Title", size = UDim2.new(1, -300, 0, 70), pos = UDim2.fromOffset(280, 18), ts = 66,
		role = "title", stroke = INK, strokeW = 4, z = 7})
	label(wc, "Codes are in the server", {name = "Sub", size = UDim2.new(1, -300, 0, 40), pos = UDim2.fromOffset(280, 86),
		ts = 34, role = "title", stroke = INK, strokeW = 3, z = 7})
	local box, _, bc = surface(wc, {name = "CodeBox", w = cw - 640, h = 76, pos = UDim2.fromOffset(290, 150),
		paint = {fill = T.color("Blue"), stroke = INK, strokeW = 3.5}, kind = "button", tilt = 0, noDeco = true, surface = "vivid"})
	new("TextBox", {Name = "Input", PlaceholderText = "Enter Code...", Text = "", FontFace = R.fonts.button, TextSize = 40,
		TextColor3 = WHITE, PlaceholderColor3 = hex("DDEBFA"), BackgroundTransparency = 1, Size = UDim2.new(1, -30, 1, 0),
		Position = UDim2.fromOffset(18, 0), TextXAlignment = Enum.TextXAlignment.Left, ClearTextOnFocus = false, ZIndex = 9,
		Parent = bc})
	button(wc, "Redeem", "Redeem", "Green", 230, 76, UDim2.new(1, -254, 0, 150), {role = "action", action = "Redeem", ts = 42})
end

-- a plain shop for the other games (cards + tabs)
function W.shopCards(items, tabs, cols)
	return function(c, cw, ch)
		local area = frame(c, "Items", {Size = UDim2.new(1, 0, 1, tabs and -72 or 0)})
		local sf = scroller(area, "List")
		new("UIListLayout", {SortOrder = Enum.SortOrder.LayoutOrder, Parent = sf})
		cardGrid(sf, items, cw, cols or 2, 170, "Cards", 1)
		if tabs then
			tabRow(c, tabs, cw)
		end
	end
end

function W.rebirth(c, cw, ch)
	local pp = pnl()
	label(c, "Reset your cash for a <b>permanent</b> boost!", {name = "Info", size = UDim2.new(1, 0, 0, 50),
		ts = 36, role = "title", color = R.style == "Sim" and WHITE or pp.text, stroke = R.style == "Sim" and INK or nil,
		strokeW = 3, wrap = true})
	for i, v in ipairs({{"Now", "x1", "Gray"}, {"After", "x2", "Green"}}) do
		local bx, _, bcn = surface(c, {name = v[1], w = 210, h = 170, pos = UDim2.new(0.5, (i == 1 and -1 or 1) * 170, 0, 70),
			anchor = Vector2.new(0.5, 0), key = v[3], role = "action", kind = "card", tilt = 0,
			paint = (not ST.colorful) and {fill = pp.inner, t = pp.innerT, stroke = T.color(v[3]), strokeW = 2, text = pp.text} or nil})
		label(bcn, v[1], {size = UDim2.new(1, 0, 0, 44), pos = UDim2.fromOffset(0, 10), ts = 32, role = "title", stroke = INK,
			strokeW = 2.5, color = ST.colorful and WHITE or pp.text})
		label(bcn, v[2] .. " Cash", {size = UDim2.new(1, 0, 0, 70), pos = UDim2.fromOffset(0, 66), ts = 50, role = "number",
			stroke = INK, strokeW = 3.5, color = ST.colorful and WHITE or T.color(v[3])})
	end
	icon(c, "upgrade", 90, {pos = UDim2.new(0.5, 0, 0, 155), rot = 90, color = T.color("Green"), tone2 = WHITE})
	bar(c, "Progress", 0.62, "Green", cw - 80, 40, UDim2.new(0.5, 0, 0, 268), "$620K / $1M", {anchor = Vector2.new(0.5, 0)})
	button(c, "RebirthButton", "Rebirth!", "Green", 320, 92, UDim2.new(0.5, 0, 1, -8), {role = "action", action = "Rebirth",
		anchor = Vector2.new(0.5, 1), ts = 50})
end

function W.index(c, cw, ch)
	local muts = {{"Normal", "Gray"}, {"Gold", "Gold"}, {"Diamond", "Cyan"}, {"Rainbow", "Pink"}, {"Shiny", "Purple"}}
	local left = frame(c, "Mutations", {Size = UDim2.new(0, 230, 1, 0)})
	for i, m in ipairs(muts) do
		local b = button(left, m[1], m[1], m[2], 220, 66, UDim2.fromOffset(0, (i - 1) * 80), {role = i == 1 and "action" or "button",
			ts = 32, tilt = 0})
		b:SetAttribute("Mutation", m[1])
	end
	local right = frame(c, "Collection", {Size = UDim2.new(1, -250, 1, -90), Position = UDim2.fromOffset(250, 0)})
	local sf = scroller(right, "Grid")
	new("UIGridLayout", {CellSize = UDim2.fromOffset(140, 140), CellPadding = UDim2.fromOffset(14, 14),
		SortOrder = Enum.SortOrder.LayoutOrder, Parent = sf})
	local found = {"taco", "fishing", "crown", "gem", "egg", "luck", "hammer", "bag", "mushroom", "trophy", "potion", "crate"}
	for i = 1, 15 do
		local key = found[i]
		local s, sc = slot(sf, "Entry" .. i, 140, 140, UDim2.new(), key and T.color(i % 3 == 0 and "Gold" or "Blue") or nil)
		s.LayoutOrder = i
		if key then
			icon(sc, key, 100, {pos = UDim2.fromScale(0.5, 0.45), z = 6, color = T.color("Blue"), tone2 = WHITE})
		else
			label(sc, "?", {ts = 80, role = "title", color = pnl().dim, stroke = INK, strokeW = 2})
		end
	end
	local foot = frame(c, "Reward", {Size = UDim2.new(1, -250, 0, 76), Position = UDim2.new(0, 250, 1, -76)})
	label(foot, "Collect 15 items for a reward!", {size = UDim2.new(1, -100, 0, 34), x = Enum.TextXAlignment.Left, ts = 30,
		role = "title", color = R.style == "Sim" and WHITE or pnl().text, stroke = R.style == "Sim" and INK or nil, strokeW = 3})
	bar(foot, "Progress", 12 / 15, "Green", cw - 360, 32, UDim2.fromOffset(0, 40), "12 / 15")
	icon(foot, "daily", 80, {pos = UDim2.new(1, -44, 0.5, 0), z = 6, color = T.color("Pink"), tone2 = WHITE})
end

function W.machine(c, cw, ch)
	for i, v in ipairs({{"settings", -1}, {"goldbars", 1}}) do
		local blob = frame(c, "Blob", {BackgroundTransparency = 0.55, BackgroundColor3 = hex("CFC2FF"),
			Size = UDim2.fromOffset(250, 230), Position = UDim2.new(0.5, v[2] * 170, 0, 150), AnchorPoint = Vector2.new(0.5, 0.5)})
		corner(blob, 110)
		icon(c, v[1], 250, {pos = UDim2.new(0.5, v[2] * 170, 0, 150), z = 6, color = T.color("Gold"), tone2 = WHITE})
	end
	button(c, "Make", "Make", "Gold", 290, 108, UDim2.new(0.5, -170, 1, -6), {role = "action", action = "Make",
		anchor = Vector2.new(0.5, 1), ts = 60})
	button(c, "View", "View", "Green", 290, 108, UDim2.new(0.5, 170, 1, -6), {role = "action", action = "View",
		anchor = Vector2.new(0.5, 1), ts = 60})
end

function W.settings(c, cw, ch)
	local pp = pnl()
	local list = frame(c, "List", {Size = UDim2.fromScale(1, 1)})
	new("UIListLayout", {Padding = UDim.new(0, 12), SortOrder = Enum.SortOrder.LayoutOrder, Parent = list})
	for i, name in ipairs({"Music", "Sound Effects", "Low Graphics", "Show Other Players", "Auto Collect"}) do
		local row = frame(list, name, {BackgroundTransparency = pp.innerT, BackgroundColor3 = pp.inner,
			Size = UDim2.new(1, 0, 0, 68), LayoutOrder = i})
		corner(row, radiusFor(68, "small"))
		if R.style == "Sim" then
			stroke(row, pp.line, 2)
		end
		label(row, name, {size = UDim2.new(1, -190, 1, 0), pos = UDim2.fromOffset(20, 0), x = Enum.TextXAlignment.Left, ts = 32,
			role = "button", color = R.style == "Sim" and WHITE or pp.text, stroke = R.style == "Sim" and INK or nil, strokeW = 3})
		local on = i ~= 3
		local t = button(row, "Toggle", on and "ON" or "OFF", on and "Green" or "Red", 130, 52, UDim2.new(1, -144, 0.5, -26),
			{role = "action", ts = 28, tilt = 0})
		t:SetAttribute("Toggle", on)
	end
end

function W.codes(c, cw, ch)
	local pp = pnl()
	label(c, "Enter a code for free rewards!", {size = UDim2.new(1, 0, 0, 50), pos = UDim2.fromOffset(0, 10), ts = 34,
		role = "title", color = R.style == "Sim" and WHITE or pp.text, stroke = R.style == "Sim" and INK or nil, strokeW = 3})
	local box, _, bc = surface(c, {name = "CodeBox", w = cw - 40, h = 76, pos = UDim2.fromOffset(20, 90),
		paint = {fill = pp.inner, t = pp.innerT, stroke = pp.stroke or pp.line, strokeW = 2, text = pp.text}, kind = "button",
		tilt = 0, noDeco = true, surface = "flat", shadow = "none"})
	new("TextBox", {Name = "Input", PlaceholderText = "Enter code...", Text = "", FontFace = R.fonts.body, TextSize = 32,
		TextColor3 = pp.text, PlaceholderColor3 = pp.dim, BackgroundTransparency = 1, Size = UDim2.new(1, -30, 1, 0),
		Position = UDim2.fromOffset(18, 0), TextXAlignment = Enum.TextXAlignment.Left, ClearTextOnFocus = false, ZIndex = 9,
		Parent = bc})
	button(c, "Redeem", "Redeem", "Green", 260, 78, UDim2.new(0.5, 0, 0, 200), {role = "action", action = "Redeem",
		anchor = Vector2.new(0.5, 0), ts = 38})
end

function W.daily(c, cw, ch)
	local g = frame(c, "Days", {Size = UDim2.fromScale(1, 1)})
	new("UIGridLayout", {CellSize = UDim2.fromOffset(math.floor((cw - 3 * 14) / 4), 180), CellPadding = UDim2.fromOffset(14, 14),
		HorizontalAlignment = Enum.HorizontalAlignment.Center, SortOrder = Enum.SortOrder.LayoutOrder, Parent = g})
	local rewards = {{"coin", "500"}, {"gem", "25"}, {"coin", "2K"}, {"luck", "x2 Luck"}, {"gem", "100"}, {"egg", "Egg"},
		{"crate", "Mega"}}
	local cwid = math.floor((cw - 3 * 14) / 4)
	for i, r in ipairs(rewards) do
		local paint = cardPaint(i, i == 7 and "Gold" or "Blue")
		local bx, _, bc = surface(g, {name = "Day" .. i, w = cwid, h = 180, kind = "card", paint = paint,
			surface = ST.colorful and "card" or nil, tilt = 0, button = true})
		bx.LayoutOrder = i
		label(bc, "Day " .. i, {size = UDim2.new(1, 0, 0, 40), pos = UDim2.fromOffset(0, 8), ts = 30, role = "title",
			color = paint.text, stroke = paint.textStroke, strokeW = 3})
		icon(bc, r[1], 86, {pos = UDim2.fromScale(0.5, 0.52), z = 6, color = paint.accent or T.color("Gold"), tone2 = paint.fill})
		label(bc, r[2], {size = UDim2.new(1, 0, 0, 36), pos = UDim2.new(0, 0, 1, -44), ts = 28, role = "number",
			color = paint.text, stroke = paint.textStroke, strokeW = 3})
		bx:SetAttribute("Day", i)
		hover(bx)
	end
end

-- rows with a title, a small line and a button (quests, upgrades, jobs, journal)
function W.rows(rows, actionName)
	return function(c, cw, ch)
		local pp = pnl()
		local sf = scroller(c, "List")
		new("UIListLayout", {Padding = UDim.new(0, 12), SortOrder = Enum.SortOrder.LayoutOrder, Parent = sf})
		for i, r in ipairs(rows) do
			local paint = cardPaint(i, r.key)
			local row, _, rc = surface(sf, {name = "Row" .. i, w = cw - 26, h = 96, kind = "card", paint = paint,
				surface = ST.colorful and "card" or nil, tilt = 0, noStuds = true})
			row.LayoutOrder = i
			icon(rc, r.icon or "star", 66, {pos = UDim2.fromOffset(52, 48), z = 6, color = paint.accent or WHITE, tone2 = paint.fill})
			label(rc, r.title, {size = UDim2.new(1, -330, 0, 40), pos = UDim2.fromOffset(98, 8), x = Enum.TextXAlignment.Left,
				ts = 30, role = "button", color = paint.text, stroke = paint.textStroke, strokeW = 3})
			if r.progress then
				bar(rc, "Progress", r.progress, "Gold", cw - 380, 26, UDim2.fromOffset(98, 56),
					math.floor(r.progress * 100) .. "%")
			elseif r.sub then
				label(rc, r.sub, {size = UDim2.new(1, -330, 0, 30), pos = UDim2.fromOffset(98, 52), x = Enum.TextXAlignment.Left,
					ts = 22, role = "body", color = ST.colorful and WHITE or pp.dim, stroke = ST.colorful and paint.textStroke or nil,
					strokeW = 2})
			end
			if r.price then
				priceButton(rc, "Buy", r.price, "Green", 190, 64, UDim2.new(1, -206, 0.5, -32), false)
			else
				local done = r.progress and r.progress >= 1
				button(rc, "Action", r.action or actionName or (done and "Claim" or "Go"), done and "Green" or "Blue", 170, 62,
					UDim2.new(1, -186, 0.5, -31), {role = "action", action = r.action or actionName or "Claim", ts = 30, tilt = 0})
			end
		end
	end
end

function W.inventory(n, withRarity)
	return function(c, cw, ch)
		local pp = pnl()
		local top = frame(c, "Top", {Size = UDim2.new(1, 0, 0, 60)})
		label(top, "Equipped 3/6", {size = UDim2.new(0.4, 0, 1, 0), x = Enum.TextXAlignment.Left, ts = 32, role = "title",
			color = R.style == "Sim" and WHITE or pp.text, stroke = R.style == "Sim" and INK or nil, strokeW = 3})
		button(top, "EquipBest", "Equip Best", "Green", 210, 56, UDim2.new(1, -420, 0, 0), {role = "action", ts = 28, tilt = 0})
		button(top, "Delete", "Delete", "Red", 190, 56, UDim2.new(1, -196, 0, 0), {role = "action", ts = 28, tilt = 0})
		local area = frame(c, "Grid", {Size = UDim2.new(1, 0, 1, -76), Position = UDim2.fromOffset(0, 76)})
		local sf = scroller(area, "Grid")
		new("UIGridLayout", {CellSize = UDim2.fromOffset(122, 122), CellPadding = UDim2.fromOffset(12, 12),
			SortOrder = Enum.SortOrder.LayoutOrder, Parent = sf})
		local keys = {"pet", "egg", "gem", "sword", "potion", "luck", "crown", "bag"}
		local rar = {{"Common", "Gray"}, {"Rare", "Blue"}, {"Epic", "Purple"}, {"Legendary", "Gold"}, {"Mythic", "Red"}}
		for i = 1, n do
			local rr = rar[(i - 1) % #rar + 1]
			local s, sc = slot(sf, "Item" .. i, 122, 122, UDim2.new(), withRarity and T.color(rr[2]) or nil)
			s.LayoutOrder = i
			icon(sc, keys[(i - 1) % #keys + 1], 78, {pos = UDim2.fromScale(0.5, 0.42), z = 6, color = T.color(rr[2]), tone2 = WHITE})
			if withRarity then
				label(sc, rr[1], {size = UDim2.new(1, 0, 0, 24), pos = UDim2.new(0, 0, 1, -28), ts = 20, role = "body",
					color = T.color(rr[2]), stroke = INK, strokeW = 2, z = 8})
			end
		end
	end
end

function W.character(c, cw, ch)
	local pp = pnl()
	local left = frame(c, "Equipment", {Size = UDim2.new(0, 300, 1, 0)})
	local slotsList = {{"Helmet", "crown"}, {"Weapon", "sword"}, {"Shield", "shield"}, {"Boots", "bolt"}}
	for i, s in ipairs(slotsList) do
		local sl, sc = slot(left, s[1], 120, 120, UDim2.fromOffset(((i - 1) % 2) * 140, math.floor((i - 1) / 2) * 150), T.color("Gold"))
		icon(sc, s[2], 76, {z = 6, color = T.color("Gold"), tone2 = WHITE})
		label(sl, s[1], {size = UDim2.new(1, 20, 0, 24), pos = UDim2.new(0.5, 0, 1, 12), anchor = Vector2.new(0.5, 0.5), ts = 20,
			color = pp.text, z = 9})
	end
	local stats = frame(c, "Stats", {Size = UDim2.new(1, -330, 1, 0), Position = UDim2.fromOffset(330, 0)})
	for i, s in ipairs({{"Strength", 0.7, "Red"}, {"Defense", 0.45, "Blue"}, {"Magic", 0.3, "Purple"}, {"Speed", 0.55, "Green"}}) do
		label(stats, s[1], {size = UDim2.fromOffset(160, 30), pos = UDim2.fromOffset(0, (i - 1) * 64), x = Enum.TextXAlignment.Left,
			ts = 28, role = "button", color = pp.text})
		bar(stats, s[1], s[2], s[3], cw - 520, 28, UDim2.fromOffset(170, (i - 1) * 64 + 2), math.floor(s[2] * 100) .. "")
	end
	button(stats, "Upgrade", "Spend Points (3)", "Green", 320, 64, UDim2.new(0, 0, 1, -64), {role = "action", ts = 28, tilt = 0})
end

function W.map(c, cw, ch)
	local pp = pnl()
	local m = frame(c, "Map", {BackgroundTransparency = 0, BackgroundColor3 = pp.inner, Size = UDim2.fromScale(1, 1)})
	corner(m, radiusFor(200, "panel"))
	for i, p in ipairs({{0.2, 0.3, "Town"}, {0.6, 0.25, "Castle"}, {0.45, 0.7, "Dungeon"}, {0.8, 0.62, "Forest"}}) do
		local b = button(m, p[3], p[3], "Red", 150, 46, UDim2.fromScale(p[1], p[2]), {role = "action", anchor = Vector2.new(0.5, 0.5),
			ts = 22, icon = "flag", tilt = 0})
		b:SetAttribute("Teleport", p[3])
	end
end

function W.phone(c, cw, ch)
	local g = frame(c, "Apps", {Size = UDim2.fromScale(1, 1)})
	new("UIGridLayout", {CellSize = UDim2.fromOffset(112, 140), CellPadding = UDim2.fromOffset(18, 18),
		HorizontalAlignment = Enum.HorizontalAlignment.Center, SortOrder = Enum.SortOrder.LayoutOrder, Parent = g})
	local apps = {{"Houses", "home", "Blue"}, {"Cars", "car", "Red"}, {"Outfits", "shirt", "Pink"}, {"Jobs", "jobs", "Orange"},
		{"Friends", "friends", "Green"}, {"Music", "music", "Purple"}, {"Map", "map", "Cyan"}, {"Settings", "settings", "Gray"}}
	for i, a in ipairs(apps) do
		local holder = frame(g, a[1], {LayoutOrder = i})
		local b, _, bc = surface(holder, {name = "App", w = 104, h = 104, pos = UDim2.fromOffset(4, 0), key = a[3], role = "menu",
			kind = "tile", button = true, tilt = 0})
		icon(bc, a[2], 66, {z = 6, color = WHITE, tone2 = T.color(a[3])})
		label(holder, a[1], {size = UDim2.new(1, 0, 0, 28), pos = UDim2.new(0, 0, 1, -28), ts = 22, role = "body",
			color = pnl().text})
		hover(b)
	end
end

-----------------------------------------------------------------------------------------------
-- HUD building blocks
-----------------------------------------------------------------------------------------------
local function simText()
	-- white text with a dark outline on the "loud" styles, the panel text colour on the calm ones
	local loud = R.style == "Sim" or R.style == "Studs" or R.style == "Bubbly" or R.style == "Cartoon" or R.style == "Anime"
	return loud and WHITE or pnl().text, loud and INK or nil
end

local function topTimer(root, title, time, sub, frac)
	local tc, sc = simText()
	local c = cluster(root, "Timer", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 8), 660, 150)
	label(c, title, {name = "Title", size = UDim2.fromOffset(600, 42), pos = UDim2.fromOffset(10, 0), ts = 36, role = "title",
		color = tc, stroke = sc, strokeW = 3, z = 5})
	icon(c, "clock", 48, {pos = UDim2.fromOffset(330 + math.floor(textWidth(title, 36) / 2) + 24, 20), z = 6, rot = 10,
		color = T.color("Red"), tone2 = WHITE})
	bar(c, "Progress", frac, "Cyan", 520, 30, UDim2.fromOffset(70, 58), nil)
	label(c, time, {name = "Time", size = UDim2.fromOffset(660, 62), pos = UDim2.fromOffset(0, 40), ts = 58, role = "number",
		color = tc, stroke = sc, strokeW = 4, z = 14})
	label(c, sub, {name = "Sub", size = UDim2.fromOffset(660, 32), pos = UDim2.fromOffset(0, 106), ts = 25, role = "title",
		color = tc, stroke = sc, strokeW = 2.5, z = 5})
	for _, sgn in ipairs({-1, 1}) do
		local ln = frame(c, "Line", {BackgroundTransparency = 0.2, BackgroundColor3 = WHITE, Size = UDim2.fromOffset(170, 2),
			Position = UDim2.new(0.5, sgn * 250, 0, 122), AnchorPoint = Vector2.new(0.5, 0.5)})
		new("UIGradient", {Rotation = sgn == 1 and 0 or 180, Transparency = NumberSequence.new(0, 1), Parent = ln})
	end
	return c
end

local function eventTimers(root, list)
	local tc, sc = simText()
	local c = cluster(root, "Events", Vector2.new(1, 0), UDim2.new(1, 0, 0, 74), 340, #list * 100)
	for i, e in ipairs(list) do
		local y = (i - 1) * 100
		local bar_ = frame(c, "Bar", {BackgroundTransparency = 0.3, BackgroundColor3 = hex("3B414C"),
			Size = UDim2.fromOffset(280, 66), Position = UDim2.fromOffset(60, y + 18)})
		new("UIGradient", {Rotation = 180, Transparency = NumberSequence.new({NumberSequenceKeypoint.new(0, 0),
			NumberSequenceKeypoint.new(0.6, 0.3), NumberSequenceKeypoint.new(1, 1)}), Parent = bar_})
		icon(c, e[1], 118, {pos = UDim2.fromOffset(70, y + 46), z = 4, rot = -8, color = T.color("Cyan"), tone2 = WHITE})
		label(c, e[2], {name = "Time", size = UDim2.fromOffset(210, 66), pos = UDim2.fromOffset(126, y + 16),
			x = Enum.TextXAlignment.Left, ts = 48, role = "number", color = tc, stroke = sc, strokeW = 3.5, z = 6})
	end
	return c
end

local function boosts(root, list)
	local tc, sc = simText()
	local c = cluster(root, "Boosts", Vector2.new(0, 1), UDim2.new(0, 16, 1, -10), #list * 124 + 20, 150)
	for i, b in ipairs(list) do
		local x = (i - 1) * 124 + 64
		local col = T.color(b[3])
		if ST.boosts == "hex" then
			hexagon(c, "Boost" .. i, UDim2.fromOffset(x, 66), 112, lighter(col, 0.12), darker(col, 0.4), 5, 1, 0)
		else
			local box = surface(c, {name = "Boost" .. i, w = 96, h = 96, pos = UDim2.fromOffset(x - 48, 18), key = b[3],
				role = "menu", kind = "tile", tilt = 0})
		end
		icon(c, b[1], ST.boosts == "hex" and 100 or 70, {pos = UDim2.fromOffset(x, 62), z = 4, color = WHITE, tone2 = col})
		label(c, b[2], {name = "Value", size = UDim2.fromOffset(120, 44), pos = UDim2.fromOffset(x, 124),
			anchor = Vector2.new(0.5, 0.5), ts = 38, role = "number", color = tc, stroke = sc or INK, strokeW = 3.5, z = 6})
	end
	return c
end

local function hotbar(root, items, keys, anchor, pos)
	local s, gap = 90, 10
	local n = #items
	local c = cluster(root, "Hotbar", anchor or Vector2.new(0.5, 1), pos or UDim2.new(0.5, 0, 1, -12), n * (s + gap) - gap, s + 8)
	for i, it in ipairs(items) do
		local b, content = slot(c, "Slot" .. i, s, s, UDim2.fromOffset((i - 1) * (s + gap), 0), nil, {radius = 8})
		icon(content, it, 72, {z = 6, color = pnl().text, tone2 = pnl().inner})
		label(content, keys and keys[i] or tostring(i), {name = "Key", size = UDim2.fromOffset(30, 26), pos = UDim2.fromOffset(6, 2),
			x = Enum.TextXAlignment.Left, ts = 26, role = "number", color = WHITE, stroke = INK, strokeW = 2.5, z = 8})
		b:SetAttribute("Slot", i)
	end
	return c
end

local function tip(root, text, iconKey)
	local c = cluster(root, "Tip", Vector2.new(1, 0), UDim2.new(1, -14, 0, 92), 560, 640)
	c.Visible = false
	c:SetAttribute("Tip", true)
	local tail = frame(c, "Tail", {BackgroundTransparency = 0, BackgroundColor3 = hex("EEF0FF"), Size = UDim2.fromOffset(40, 40),
		Position = UDim2.fromOffset(300, 212), AnchorPoint = Vector2.new(0.5, 0.5), Rotation = 45, ZIndex = 1})
	stroke(tail, INK, 3)
	local bub = frame(c, "Bubble", {BackgroundTransparency = 0, BackgroundColor3 = hex("EEF0FF"), Size = UDim2.fromOffset(560, 212),
		ZIndex = 2})
	corner(bub, 4)
	stroke(bub, INK, 3)
	DECO.dots(bub, bub, {}, hex("C9CCF2"), 560, 212, 4, "card")
	local l = label(bub, text, {name = "Text", size = UDim2.fromOffset(350, 190), pos = UDim2.fromOffset(18, 10),
		x = Enum.TextXAlignment.Left, ts = 50, role = "title", stroke = INK, strokeW = 3.5, wrap = true, z = 6,
		gradient = goldText()})
	icon(bub, iconKey or "cash", 170, {pos = UDim2.fromOffset(460, 105), z = 6, rot = 12, color = T.color("Green"), tone2 = WHITE})
	local por = frame(c, "Portrait", {BackgroundTransparency = 0, BackgroundColor3 = WHITE, Size = UDim2.fromOffset(290, 290),
		Position = UDim2.fromOffset(410, 470), AnchorPoint = Vector2.new(0.5, 0.5), ZIndex = 2})
	corner(por, "pill")
	stroke(por, hex("9FD8FF"), 8)
	gradient(por, hex("7CCBFF"), hex("3E8FE0"))
	icon(c, "pet", 300, {pos = UDim2.fromOffset(410, 440), z = 5, color = WHITE, tone2 = T.Primary})
	return c
end

local function announce(root, line1, line2)
	local c = cluster(root, "Announcement", Vector2.new(0, 0), UDim2.new(0, 0, 0.2, 0), 520, 150)
	for i, s in ipairs({line1, line2}) do
		label(c, s, {name = "Line" .. i, size = UDim2.fromOffset(520, 70), pos = UDim2.fromOffset(0, (i - 1) * 70),
			x = Enum.TextXAlignment.Left, ts = i == 1 and 70 or 58, role = "title", stroke = INK, strokeW = 4, z = 5,
			gradient = {hex("FF7A7A"), hex("E02A2A")}})
	end
	return c
end

local function currencies(root, list, anchor, pos, big)
	local fade = ST.currency == "fade"
	local step = fade and 104 or (ST.currency == "text" and 44 or 78)
	local c = cluster(root, "Currencies", anchor, pos, fade and 440 or 380, #list * step)
	for i, cur in ipairs(list) do
		currency(c, cur, fade and 0 or 20, (i - 1) * step, {big = big, plus = not fade})
	end
	return c
end

local function statusBars(root, bars_, portraitIcon)
	local c = cluster(root, "Status", Vector2.new(0, 0), UDim2.fromOffset(20, 76), 520, 40 + #bars_ * 44)
	local x = 0
	if portraitIcon then
		local p, _, pc = surface(c, {name = "Portrait", w = 110, h = 110, key = "Primary", role = "menu", kind = "chip",
			radius = R.style == "Anime" and 0 or "pill", tilt = 0})
		icon(pc, portraitIcon, 76, {z = 6, color = WHITE, tone2 = T.Primary})
		x = 126
	end
	for i, b in ipairs(bars_) do
		bar(c, b[1], b[2], b[3], b[5] or 360, b[4] or 32, UDim2.fromOffset(x, 6 + (i - 1) * 42), b[6])
	end
	return c
end

local function abilityBar(root, keys, icons_, anchor, pos, size)
	local s = size or 96
	local gap = 14
	local c = cluster(root, "Abilities", anchor, pos, #keys * (s + gap), s + 30)
	for i, k in ipairs(keys) do
		local b, _, content = surface(c, {name = "Ability" .. i, w = s, h = s, pos = UDim2.fromOffset((i - 1) * (s + gap), 0),
			key = ({"Red", "Blue", "Purple", "Gold", "Green", "Cyan", "Orange", "Pink"})[i], role = "menu", kind = "tile",
			button = true, radius = R.style == "Bubbly" and "pill" or nil, tilt = R.style == "Anime" and 45 or nil})
		local ic = icon(content, icons_[i], math.floor(s * 0.6), {z = 6, color = WHITE, tone2 = BLACK,
			rot = R.style == "Anime" and -45 or 0})
		label(b, k, {name = "Key", size = UDim2.fromOffset(40, 30), pos = UDim2.new(0.5, 0, 1, 14), anchor = Vector2.new(0.5, 0.5),
			ts = 26, role = "number", color = WHITE, stroke = INK, strokeW = 2.5, z = 10, rot = R.style == "Anime" and -45 or 0})
		if i == 2 then
			local cd = frame(content, "Cooldown", {BackgroundTransparency = 0.4, BackgroundColor3 = BLACK,
				Size = UDim2.fromScale(1, 0.55), Position = UDim2.fromScale(0, 0.45), ZIndex = 9})
			label(content, "3.2", {name = "Time", ts = 30, role = "number", color = WHITE, stroke = INK, strokeW = 2, z = 10,
				rot = R.style == "Anime" and -45 or 0})
		end
		b:SetAttribute("Ability", k)
		hover(b)
	end
	return c
end

local function feed(root, name, lines, anchor, pos)
	local tc, sc = simText()
	local c = cluster(root, name, anchor, pos, 420, #lines * 40)
	for i, s in ipairs(lines) do
		local row = frame(c, "Line" .. i, {BackgroundTransparency = 0.5, BackgroundColor3 = BLACK, Size = UDim2.fromOffset(420, 34),
			Position = UDim2.fromOffset(0, (i - 1) * 40)})
		new("UIGradient", {Rotation = anchor.X > 0.5 and 180 or 0, Transparency = NumberSequence.new(0.1, 1), Parent = row})
		label(row, s, {size = UDim2.new(1, -20, 1, 0), pos = UDim2.fromOffset(12, 0), ts = 22, role = "body",
			x = anchor.X > 0.5 and Enum.TextXAlignment.Right or Enum.TextXAlignment.Left, color = WHITE, stroke = INK, strokeW = 1.5})
	end
	return c
end

local function bigText(root, name, text, anchor, pos, ts, w, grad)
	local tc, sc = simText()
	local c = cluster(root, name, anchor, pos, w or 600, ts + 20)
	label(c, text, {name = "Text", ts = ts, role = "title", color = tc, stroke = sc or (R.style ~= "Minimal" and INK or nil),
		strokeW = math.max(ST.textStroke, 3), gradient = grad, flicker = R.style == "Horror"})
	return c
end

local function logo(root, title, y)
	if not title then
		return
	end
	local grad = {T.TitleTop, T.TitleBottom}
	local stroke_ = T.Outline
	if R.style == "Minimal" or R.style == "SciFi" or R.style == "Horror" then
		grad = nil
		stroke_ = nil
	end
	local c = cluster(root, "Logo", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, y or 16), 760, 90)
	label(c, title, {name = "Title", ts = 68, role = "title", gradient = grad,
		color = R.style == "Horror" and T.Primary or (R.style == "SciFi" and T.Primary or pnl().text), stroke = stroke_,
		strokeW = 4.5, rot = R.style == "Cartoon" and -3 or (R.style == "Anime" and -4 or 0), flicker = R.style == "Horror"})
	return c
end

local function vignette(root)
	local v = frame(root, "Vignette", {Size = UDim2.fromScale(1, 1), ZIndex = 0})
	for _, s in ipairs({{0, 0, 1, 0.3, 90}, {0, 0.7, 1, 0.3, 270}, {0, 0, 0.25, 1, 0}, {0.75, 0, 0.25, 1, 180}}) do
		local f = frame(v, "Edge", {BackgroundTransparency = 0, BackgroundColor3 = BLACK, Size = UDim2.fromScale(s[3], s[4]),
			Position = UDim2.fromScale(s[1], s[2])})
		new("UIGradient", {Rotation = s[5], Transparency = NumberSequence.new(0.05, 1), Parent = f})
	end
	v:SetAttribute("Vignette", true)
	return v
end

local function crosshair(root, dotOnly)
	local c = frame(root, "Crosshair", {Size = UDim2.fromOffset(40, 40), Position = UDim2.fromScale(0.5, 0.5),
		AnchorPoint = Vector2.new(0.5, 0.5)})
	local d = frame(c, "Dot", {BackgroundTransparency = 0.1, BackgroundColor3 = WHITE, Size = UDim2.fromOffset(6, 6),
		Position = UDim2.fromScale(0.5, 0.5), AnchorPoint = Vector2.new(0.5, 0.5)})
	corner(d, "pill")
	if not dotOnly then
		for _, s in ipairs({{0.5, 0, 2, 12}, {0.5, 1, 2, 12}, {0, 0.5, 12, 2}, {1, 0.5, 12, 2}}) do
			frame(c, "Tick", {BackgroundTransparency = 0.1, BackgroundColor3 = WHITE, Size = UDim2.fromOffset(s[3], s[4]),
				Position = UDim2.fromScale(s[1], s[2]), AnchorPoint = Vector2.new(0.5, 0.5)})
		end
	end
	return c
end

local function minimap(root, anchor, pos)
	local c = cluster(root, "Minimap", anchor, pos, 220, 220)
	local m, _, mc = surface(c, {name = "Map", w = 220, h = 220, paint = {fill = pnl().inner, t = 0.15, stroke = pnl().stroke or INK,
		strokeW = 3}, kind = "chip", radius = "pill", tilt = 0, noDeco = true, surface = "flat"})
	for i, p in ipairs({{0.3, 0.4, "Red"}, {0.62, 0.3, "Gold"}, {0.55, 0.7, "Green"}}) do
		local d = frame(mc, "Pin", {BackgroundTransparency = 0, BackgroundColor3 = T.color(p[3]), Size = UDim2.fromOffset(14, 14),
			Position = UDim2.fromScale(p[1], p[2]), AnchorPoint = Vector2.new(0.5, 0.5), ZIndex = 4})
		corner(d, "pill")
	end
	local me = frame(mc, "Me", {BackgroundTransparency = 0, BackgroundColor3 = WHITE, Size = UDim2.fromOffset(18, 18),
		Position = UDim2.fromScale(0.5, 0.5), AnchorPoint = Vector2.new(0.5, 0.5), Rotation = 45, ZIndex = 5})
	stroke(me, INK, 2)
	return c
end

-----------------------------------------------------------------------------------------------
-- games: HUD placement + windows
-----------------------------------------------------------------------------------------------
local function side(default)
	if R.seed ~= 0 and R.menuSide == "right" then
		return default == "right" and "left" or "right"
	end
	return default
end

GAMES.simulator = {
	windows = {
		{name = "Shop", title = "Exclusive Shop!", sub = "Gamepasses!", icon = "shop", w = 1200, h = 760, build = W.shopSim},
		{name = "Rebirth", title = "Rebirth", icon = "rebirth", w = 780, h = 600, build = W.rebirth},
		{name = "Index", title = "Index", icon = "index", w = 1120, h = 700, build = W.index},
		{name = "Machine", title = "Gold Machine", sub = "Make Gold items that earn 3x cash per second", icon = "goldbars",
			w = 820, h = 700, header = "strip", build = W.machine},
		{name = "Settings", title = "Settings", icon = "settings", w = 760, h = 560, build = W.settings},
		{name = "Codes", title = "Codes", icon = "codes", w = 720, h = 440, build = W.codes},
	},
	hud = function(root)
		local cside = side("left")
		local fadeX = ST.currency == "fade" and 0 or 24
		currencies(root, {{name = "Gems", icon = "gem", key = "Cyan", value = 0}, {name = "Cash", icon = "cash", key = "Green",
			value = 10100, cash = true}}, Vector2.new(cside == "left" and 0 or 1, 0.5),
			UDim2.new(cside == "left" and 0 or 1, cside == "left" and fadeX or -24, 0.5, 30))
		menuColumn(root, "Menu", {
			{id = "Shop", label = "Shop", icon = "shop", key = "Red", opens = "Shop", gold = true},
			{id = "Rebirth", label = "Rebirth", icon = "rebirth", key = "Green", opens = "Rebirth"},
			{id = "Index", label = "Index", icon = "index", key = "Blue", opens = "Index"},
		}, cside == "left" and "right" or "left", 90)
		topTimer(root, "Next update in", "6D 3H 24M", "YOUR BASE EARNS OFFLINE!", 0.08)
		if R.title then
			logo(root, R.title, 160)
		end
		eventTimers(root, {{"ufo", "In 14:07"}, {"heli", "In 24:09"}})
		boosts(root, {{"luck", "x1", "Green"}, {"cash", "x1", "Cyan"}, {"friends", "+0%", "Gold"}})
		hotbar(root, {"hammer", "bat", "bag", "crate"})
		announce(root, "Secret Market", "Arrives in 23M 29S")
		tip(root, "Shut off the lasers and RUN BACK!", "cash"):SetAttribute("HidesMenu", cside == "left")
	end,
}

GAMES.tycoon = {
	windows = {
		{name = "Shop", title = "Upgrades", icon = "upgrade", w = 900, h = 660, build = W.rows({
			{title = "Faster Droppers", sub = "Ore drops 25% faster", icon = "bolt", price = 2500, key = "Blue"},
			{title = "Better Furnace", sub = "x1.5 cash per ore", icon = "fire", price = 12000, key = "Orange"},
			{title = "Auto Collect", sub = "Cash goes straight to you", icon = "magnet", price = 45000, key = "Purple"},
			{title = "Second Floor", sub = "More room to build", icon = "home", price = 150000, key = "Green"},
			{title = "Golden Conveyor", sub = "x2 conveyor speed", icon = "star", price = 600000, key = "Gold"}})},
		{name = "Rebirth", title = "Rebirth", icon = "rebirth", w = 780, h = 600, build = W.rebirth},
		{name = "Codes", title = "Codes", icon = "codes", w = 720, h = 440, build = W.codes},
		{name = "Settings", title = "Settings", icon = "settings", w = 760, h = 560, build = W.settings},
		{name = "DailyRewards", title = "Daily Rewards", icon = "daily", w = 900, h = 560, build = W.daily},
	},
	hud = function(root)
		local c = cluster(root, "Cash", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 14), 420, 140)
		currency(c, {name = "Cash", icon = "cash", key = "Green", value = 98400, cash = true}, 0, 0, {big = true, plus = false})
		local tc, sc = simText()
		label(c, "+$125/s", {name = "Income", size = UDim2.fromOffset(420, 40), pos = UDim2.fromOffset(0, 102), ts = 34,
			role = "number", color = T.color("Green"), stroke = INK, strokeW = 3})
		menuColumn(root, "Menu", {
			{id = "Shop", label = "Upgrades", icon = "upgrade", key = "Orange", opens = "Shop", gold = true},
			{id = "Rebirth", label = "Rebirth", icon = "rebirth", key = "Green", opens = "Rebirth"},
			{id = "DailyRewards", label = "Daily", icon = "daily", key = "Pink", opens = "DailyRewards"},
			{id = "Codes", label = "Codes", icon = "codes", key = "Purple", opens = "Codes"},
		}, side("right"), 40)
		menuColumn(root, "Menu2", {{id = "Settings", label = "Settings", icon = "settings", key = "Gray", opens = "Settings"}},
			side("left"), 260)
		feed(root, "Feed", {"+$250 Dropper bought!", "+$1,200 Furnace upgraded!", "Your tycoon earned $4,500 offline"},
			Vector2.new(0, 0.5), UDim2.new(0, 16, 0.5, -40))
		local bc = cluster(root, "RebirthBar", Vector2.new(0.5, 1), UDim2.new(0.5, 0, 1, -20), 640, 80)
		label(bc, "Rebirth progress", {size = UDim2.fromOffset(640, 32), ts = 28, role = "title", color = tc, stroke = sc, strokeW = 3})
		bar(bc, "Progress", 0.62, "Gold", 640, 36, UDim2.fromOffset(0, 40), "62%")
		if R.title then
			logo(root, R.title, 150)
		end
	end,
}

GAMES.obby = {
	windows = {
		{name = "Shop", title = "Shop", icon = "shop", w = 900, h = 640, build = W.shopCards({
			{name = "Rainbow Trail", sub = "Sparkly!", icon = "star", price = 500, key = "Pink"},
			{name = "Speed Coil", sub = "+30% speed", icon = "bolt", price = 1200, key = "Blue"},
			{name = "Gravity Coil", sub = "Jump higher", icon = "upgrade", price = 1500, key = "Purple"},
			{name = "Skip Stage", sub = "One stage", icon = "flag", price = 25, key = "Green", robux = true}}, {"Trails", "Gear", "Skips"})},
		{name = "Codes", title = "Codes", icon = "codes", w = 720, h = 440, build = W.codes},
		{name = "Settings", title = "Settings", icon = "settings", w = 760, h = 560, build = W.settings},
	},
	hud = function(root)
		local tc, sc = simText()
		local top = cluster(root, "Progress", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 16), 900, 110)
		label(top, "Stage 12 / 100", {name = "Stage", size = UDim2.fromOffset(900, 56), ts = 54, role = "title", color = tc,
			stroke = sc, strokeW = 4})
		bar(top, "Stages", 0.12, "Green", 820, 30, UDim2.fromOffset(40, 64), nil)
		icon(top, "flag", 56, {pos = UDim2.fromOffset(880, 78), z = 6, color = T.color("Red"), tone2 = WHITE})
		local t = cluster(root, "Timer", Vector2.new(1, 0), UDim2.new(1, -24, 0, 20), 260, 70)
		icon(t, "clock", 60, {pos = UDim2.fromOffset(34, 35), z = 5, color = T.color("Gold"), tone2 = WHITE})
		label(t, "02:31", {name = "Time", size = UDim2.fromOffset(190, 70), pos = UDim2.fromOffset(70, 0),
			x = Enum.TextXAlignment.Left, ts = 52, role = "number", color = tc, stroke = sc, strokeW = 3.5})
		local act = cluster(root, "Actions", Vector2.new(1, 1), UDim2.new(1, -30, 1, -30), 360, 220)
		local skip = button(act, "SkipStage", "Skip Stage", "Green", 360, 110, UDim2.new(), {role = "action", icon = "flag",
			ts = 44, action = "SkipStage"})
		button(act, "Reset", "Reset", "Red", 220, 80, UDim2.fromOffset(140, 134), {role = "action", ts = 36, action = "Reset"})
		currencies(root, {{name = "Coins", icon = "coin", key = "Gold", value = 12500}}, Vector2.new(0, 1),
			UDim2.new(0, ST.currency == "fade" and 0 or 20, 1, -30))
		menuColumn(root, "Menu", {
			{id = "Shop", label = "Shop", icon = "shop", key = "Red", opens = "Shop", gold = true},
			{id = "Codes", label = "Codes", icon = "codes", key = "Purple", opens = "Codes"},
			{id = "Settings", label = "Settings", icon = "settings", key = "Gray", opens = "Settings"},
		}, side("left"), -40)
	end,
}

GAMES.fighting = {
	windows = {
		{name = "Abilities", title = "Abilities", icon = "bolt", w = 980, h = 660, build = W.shopCards({
			{name = "Flame Dash", sub = "Dash through enemies", icon = "fire", key = "Red", stats = {{"Damage", 0.7}, {"Cooldown", 0.4}}},
			{name = "Ice Wall", sub = "Block for 3s", icon = "shield", key = "Blue", stats = {{"Defense", 0.8}, {"Cooldown", 0.6}}},
			{name = "Thunder Fist", sub = "Stun on hit", icon = "bolt", key = "Gold", stats = {{"Damage", 0.9}, {"Cooldown", 0.8}}},
			{name = "Shadow Step", sub = "Teleport behind", icon = "eye", key = "Purple", stats = {{"Speed", 0.9}, {"Cooldown", 0.5}}},
		}, {"Equipped", "All", "Ultimates"})},
		{name = "Shop", title = "Shop", icon = "shop", w = 900, h = 640, build = W.shopCards({
			{name = "Katana", sub = "Fast hits", icon = "sword", price = 2500, key = "Red"},
			{name = "Aura", sub = "Red flames", icon = "fire", price = 399, key = "Orange", robux = true},
			{name = "x2 XP", sub = "1 hour", icon = "star", price = 99, key = "Purple", robux = true},
			{name = "Spin", sub = "New power", icon = "dice", price = 50, key = "Blue", robux = true}})},
		{name = "Quests", title = "Quests", icon = "quests", w = 900, h = 600, build = W.rows({
			{title = "Defeat 10 players", progress = 0.6, icon = "skull", key = "Red"},
			{title = "Win 3 ranked matches", progress = 0.33, icon = "trophy", key = "Gold"},
			{title = "Use your ultimate", progress = 1, icon = "bolt", key = "Purple"}})},
		{name = "Settings", title = "Settings", icon = "settings", w = 760, h = 560, build = W.settings},
	},
	hud = function(root)
		statusBars(root, {{"Health", 0.8, "Green", 36, 380, "100 / 125"}, {"Energy", 0.55, "Cyan", 26, 320}, {"XP", 0.3, "Gold", 18, 280}},
			"user")
		local tc, sc = simText()
		local top = cluster(root, "Round", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 12), 420, 110)
		label(top, "1:24", {name = "Time", size = UDim2.fromOffset(420, 64), ts = 60, role = "number", color = tc, stroke = sc, strokeW = 4})
		label(top, "<font color=\"#5AB4FF\">3</font>  -  <font color=\"#FF5A6A\">2</font>", {name = "Score",
			size = UDim2.fromOffset(420, 40), pos = UDim2.fromOffset(0, 66), ts = 38, role = "number", color = tc, stroke = sc, strokeW = 3})
		menuColumn(root, "Menu", {
			{id = "Shop", label = "Shop", icon = "shop", key = "Red", opens = "Shop"},
			{id = "Abilities", label = "Abilities", icon = "bolt", key = "Purple", opens = "Abilities"},
			{id = "Quests", label = "Quests", icon = "quests", key = "Gold", opens = "Quests"},
			{id = "Settings", label = "Settings", icon = "settings", key = "Gray", opens = "Settings"},
		}, side("right"), -40)
		abilityBar(root, {"Q", "E", "R", "F"}, {"fire", "shield", "bolt", "eye"}, Vector2.new(1, 1), UDim2.new(1, -40, 1, -50), 100)
		bigText(root, "Combo", "x12 COMBO!", Vector2.new(0, 0.5), UDim2.new(0, 40, 0.62, 0), 60, 460,
			{hex("FFF3A0"), hex("FF6A2A")})
		feed(root, "KillFeed", {"You defeated Noob123", "Speedy KO'd Tank", "Blaze got a 5 streak!"}, Vector2.new(1, 0),
			UDim2.new(1, -20, 0, 20))
	end,
}

GAMES.horror = {
	windows = {
		{name = "Journal", title = "Journal", icon = "journal", w = 980, h = 640, build = W.rows({
			{title = "Day 1", sub = "The lights went out again. Something is in the walls.", icon = "note", action = "Read"},
			{title = "Day 3", sub = "I found a key under the stairs. Room 204?", icon = "key", action = "Read"},
			{title = "Day 6", sub = "Don't look at it. Don't run. Just hide.", icon = "eye", action = "Read"},
			{title = "???", sub = "The page is torn.", icon = "unknown", action = "Read"}}, "Read")},
		{name = "Inventory", title = "Inventory", icon = "bag", w = 900, h = 600, build = W.inventory(12, false)},
		{name = "Settings", title = "Settings", icon = "settings", w = 760, h = 560, build = W.settings},
	},
	hud = function(root)
		if ST.vignette then
			vignette(root)
		end
		local pp = pnl()
		local ob = cluster(root, "Objective", Vector2.new(0, 0), UDim2.fromOffset(28, 84), 560, 90)
		label(ob, "objective", {name = "Head", size = UDim2.fromOffset(300, 28), x = Enum.TextXAlignment.Left, ts = 22,
			color = T.Primary, role = "body"})
		label(ob, "Find the 3 keys (1/3)", {name = "Text", size = UDim2.fromOffset(560, 44), pos = UDim2.fromOffset(0, 30),
			x = Enum.TextXAlignment.Left, ts = 34, color = pp.text, flicker = true, stroke = R.style ~= "Horror" and INK or nil, strokeW = 2.5})
		crosshair(root, true)
		local st = cluster(root, "Stamina", Vector2.new(0.5, 1), UDim2.new(0.5, 0, 1, -40), 420, 50)
		bar(st, "Stamina", 0.7, "Gray", 420, 10, UDim2.new(), "stamina")
		local b = cluster(root, "Battery", Vector2.new(1, 0), UDim2.new(1, -30, 0, 30), 220, 50)
		icon(b, "battery", 44, {pos = UDim2.fromOffset(24, 25), color = pp.text, tone2 = BLACK, mode = R.icons == "emoji" and "emoji" or "vector"})
		label(b, "78%", {name = "Value", size = UDim2.fromOffset(160, 50), pos = UDim2.fromOffset(60, 0), x = Enum.TextXAlignment.Left,
			ts = 32, color = pp.text, role = "number", stroke = R.style ~= "Horror" and INK or nil, strokeW = 2})
		hotbar(root, {"light", "key", "battery", "unknown"}, nil, Vector2.new(1, 1), UDim2.new(1, -30, 1, -30))
		menuColumn(root, "Menu", {
			{id = "Journal", label = "Journal", icon = "journal", key = "Gray", opens = "Journal", hotkey = "J"},
			{id = "Inventory", label = "Inventory", icon = "bag", key = "Gray", opens = "Inventory", hotkey = "I"},
			{id = "Settings", label = "Settings", icon = "settings", key = "Gray", opens = "Settings", hotkey = "Esc"},
		}, side("left"), 300)
	end,
}

GAMES.racing = {
	windows = {
		{name = "Garage", title = "Garage", icon = "car", w = 1000, h = 660, build = W.shopCards({
			{name = "Street Racer", sub = "Starter car", icon = "car", key = "Red", action = "Drive",
				stats = {{"Speed", 0.55}, {"Handling", 0.7}, {"Boost", 0.4}}},
			{name = "Muscle GT", sub = "Raw power", icon = "car", key = "Orange", price = 25000,
				stats = {{"Speed", 0.8}, {"Handling", 0.45}, {"Boost", 0.6}}},
			{name = "Hyper X", sub = "Top speed king", icon = "rocket", key = "Purple", price = 150000,
				stats = {{"Speed", 0.95}, {"Handling", 0.7}, {"Boost", 0.85}}},
			{name = "Drift Kart", sub = "Sideways fun", icon = "car", key = "Green", price = 8000,
				stats = {{"Speed", 0.5}, {"Handling", 0.95}, {"Boost", 0.5}}}}, {"Cars", "Paint", "Wheels"})},
		{name = "Shop", title = "Shop", icon = "shop", w = 900, h = 600, build = W.shopCards({
			{name = "Nitro Pack", sub = "x5 nitro", icon = "fire", price = 99, key = "Orange", robux = true},
			{name = "x2 Cash", sub = "Forever", icon = "cash", price = 299, key = "Green", robux = true}})},
		{name = "Settings", title = "Settings", icon = "settings", w = 760, h = 560, build = W.settings},
	},
	hud = function(root)
		local tc, sc = simText()
		local pos = cluster(root, "Position", Vector2.new(0, 0), UDim2.fromOffset(30, 80), 260, 110)
		label(pos, "1st", {name = "Place", size = UDim2.fromOffset(170, 100), x = Enum.TextXAlignment.Left,
			ts = 84, role = "number", color = tc, stroke = sc, strokeW = 4})
		label(pos, "/ 8", {size = UDim2.fromOffset(90, 60), pos = UDim2.fromOffset(176, 36), x = Enum.TextXAlignment.Left, ts = 40,
			role = "number", color = tc, stroke = sc, strokeW = 3})
		local lap = cluster(root, "Lap", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 16), 420, 110)
		label(lap, "LAP 2 / 3", {size = UDim2.fromOffset(420, 56), ts = 50, role = "title", color = tc, stroke = sc, strokeW = 3.5})
		label(lap, "01:24.33", {name = "Time", size = UDim2.fromOffset(420, 44), pos = UDim2.fromOffset(0, 58), ts = 38,
			role = "number", color = T.color("Gold"), stroke = sc, strokeW = 3})
		local sp = cluster(root, "Speedometer", Vector2.new(1, 1), UDim2.new(1, -30, 1, -30), 360, 240)
		local g, _, gc = surface(sp, {name = "Dial", w = 240, h = 240, pos = UDim2.fromOffset(120, 0), key = "Primary", role = "menu",
			kind = "chip", radius = "pill", tilt = 0, paint = {fill = pnl().fill, t = 0.2, stroke = T.Primary, strokeW = 4}})
		label(gc, "184", {name = "Speed", size = UDim2.new(1, 0, 0, 90), pos = UDim2.fromOffset(0, 58), ts = 88, role = "number",
			color = WHITE, stroke = INK, strokeW = 3})
		label(gc, "MPH", {size = UDim2.new(1, 0, 0, 30), pos = UDim2.fromOffset(0, 146), ts = 28, role = "title", color = T.Primary})
		label(gc, "4", {name = "Gear", size = UDim2.new(1, 0, 0, 30), pos = UDim2.fromOffset(0, 186), ts = 30, role = "number",
			color = WHITE})
		bar(sp, "Nitro", 0.65, "Orange", 100, 26, UDim2.fromOffset(0, 200), "NOS")
		minimap(root, Vector2.new(0, 1), UDim2.new(0, 30, 1, -30))
		menuColumn(root, "Menu", {
			{id = "Garage", label = "Garage", icon = "car", key = "Red", opens = "Garage"},
			{id = "Shop", label = "Shop", icon = "shop", key = "Orange", opens = "Shop"},
			{id = "Settings", label = "Settings", icon = "settings", key = "Gray", opens = "Settings"},
		}, side("left"), -20)
	end,
}

GAMES.rpg = {
	windows = {
		{name = "Bag", title = "Bag", icon = "bag", w = 900, h = 640, build = W.inventory(20, true)},
		{name = "Character", title = "Character", icon = "user", w = 980, h = 560, build = W.character},
		{name = "Quests", title = "Quests", icon = "quests", w = 900, h = 600, build = W.rows({
			{title = "Slay 10 Slimes", progress = 0.7, icon = "sword", key = "Green"},
			{title = "Find the Lost Crown", progress = 0.2, icon = "crown", key = "Gold"},
			{title = "Talk to the Wizard", progress = 1, icon = "star", key = "Purple"}})},
		{name = "Map", title = "World Map", icon = "map", w = 1000, h = 640, build = W.map},
		{name = "Settings", title = "Settings", icon = "settings", w = 760, h = 560, build = W.settings},
	},
	hud = function(root)
		statusBars(root, {{"Health", 0.85, "Red", 32, 360, "850 / 1000"}, {"Mana", 0.6, "Blue", 26, 320, "60 / 100"},
			{"XP", 0.4, "Gold", 16, 300}}, "user")
		currencies(root, {{name = "Gold", icon = "coin", key = "Gold", value = 720}}, Vector2.new(0, 0), UDim2.fromOffset(20, 230))
		minimap(root, Vector2.new(1, 0), UDim2.new(1, -30, 0, 20))
		local q = cluster(root, "Tracker", Vector2.new(1, 0), UDim2.new(1, -30, 0, 270), 360, 140)
		local tc, sc = simText()
		label(q, "Slay 10 Slimes", {size = UDim2.fromOffset(360, 36), x = Enum.TextXAlignment.Right, ts = 30, role = "title",
			color = T.color("Gold"), stroke = INK, strokeW = 2.5})
		label(q, "7 / 10 slimes", {size = UDim2.fromOffset(360, 30), pos = UDim2.fromOffset(0, 38), x = Enum.TextXAlignment.Right,
			ts = 24, color = WHITE, stroke = INK, strokeW = 2})
		abilityBar(root, {"1", "2", "3", "4", "5", "6"}, {"sword", "fire", "shield", "bolt", "potion", "heart"}, Vector2.new(0.5, 1),
			UDim2.new(0.5, 0, 1, -40), 86)
		menuRow(root, "Menu", {
			{id = "Bag", label = "Bag", icon = "bag", key = "Orange", opens = "Bag"},
			{id = "Character", label = "Hero", icon = "user", key = "Blue", opens = "Character"},
			{id = "Quests", label = "Quests", icon = "quests", key = "Gold", opens = "Quests"},
			{id = "Map", label = "Map", icon = "map", key = "Green", opens = "Map"},
			{id = "Settings", label = "Settings", icon = "settings", key = "Gray", opens = "Settings"},
		}, Vector2.new(1, 1), UDim2.new(1, -20, 1, -170))
	end,
}

GAMES.shooter = {
	windows = {
		{name = "Loadout", title = "Loadout", icon = "ammo", w = 1000, h = 660, build = W.shopCards({
			{name = "AR-15", sub = "Assault rifle", icon = "ammo", key = "Blue", action = "Equip",
				stats = {{"Damage", 0.6}, {"Fire rate", 0.8}, {"Range", 0.65}}},
			{name = "Sniper", sub = "One shot", icon = "target", key = "Purple", action = "Equip",
				stats = {{"Damage", 0.95}, {"Fire rate", 0.2}, {"Range", 1}}},
			{name = "Shotgun", sub = "Close range", icon = "ammo", key = "Orange", price = 5000,
				stats = {{"Damage", 0.9}, {"Fire rate", 0.35}, {"Range", 0.25}}},
			{name = "SMG", sub = "Spray", icon = "ammo", key = "Green", price = 3500,
				stats = {{"Damage", 0.4}, {"Fire rate", 1}, {"Range", 0.4}}}}, {"Primary", "Secondary", "Melee"})},
		{name = "Shop", title = "Shop", icon = "shop", w = 900, h = 600, build = W.shopCards({
			{name = "Gold Skin", sub = "All guns", icon = "star", price = 399, key = "Gold", robux = true},
			{name = "x2 XP", sub = "1 hour", icon = "upgrade", price = 99, key = "Purple", robux = true}})},
		{name = "Settings", title = "Settings", icon = "settings", w = 760, h = 560, build = W.settings},
	},
	hud = function(root)
		local tc, sc = simText()
		local hp = cluster(root, "Health", Vector2.new(0, 1), UDim2.new(0, 30, 1, -30), 460, 110)
		label(hp, "100", {name = "Value", size = UDim2.fromOffset(150, 80), x = Enum.TextXAlignment.Left, ts = 80, role = "number",
			color = tc, stroke = sc, strokeW = 3.5})
		bar(hp, "Health", 1, "Green", 300, 20, UDim2.fromOffset(150, 30), nil)
		bar(hp, "Armor", 0.5, "Blue", 300, 14, UDim2.fromOffset(150, 60), nil)
		local am = cluster(root, "Ammo", Vector2.new(1, 1), UDim2.new(1, -30, 1, -30), 420, 120)
		label(am, "30<font size=\"40\"> / 120</font>", {name = "Value", size = UDim2.fromOffset(420, 84), x = Enum.TextXAlignment.Right,
			ts = 80, role = "number", color = tc, stroke = sc, strokeW = 3.5})
		label(am, "AR-15", {size = UDim2.fromOffset(420, 32), pos = UDim2.fromOffset(0, 84), x = Enum.TextXAlignment.Right, ts = 28,
			role = "title", color = T.Primary, stroke = sc, strokeW = 2})
		crosshair(root, false)
		local sb = cluster(root, "Score", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 14), 460, 90)
		for i, t in ipairs({{"12", "Blue", -1}, {"9", "Red", 1}}) do
			local b, _, bcn = surface(sb, {name = "Team" .. i, w = 110, h = 64, pos = UDim2.new(0.5, t[3] * 150, 0, 8),
				anchor = Vector2.new(0.5, 0), key = t[2], role = "action", kind = "button", tilt = 0})
			label(bcn, t[1], {ts = 44, role = "number", color = WHITE, stroke = INK, strokeW = 2.5})
		end
		label(sb, "4:12", {name = "Time", size = UDim2.fromOffset(160, 70), pos = UDim2.new(0.5, 0, 0, 6),
			anchor = Vector2.new(0.5, 0), ts = 52, role = "number", color = tc, stroke = sc, strokeW = 3.5})
		feed(root, "KillFeed", {"You  >  Sniper  >  Bot_7", "Ace  >  SMG  >  Rookie", "Bot_2  >  AR-15  >  Max"},
			Vector2.new(1, 0), UDim2.new(1, -20, 0, 20))
		menuRow(root, "Menu", {
			{id = "Loadout", label = "Loadout", icon = "ammo", key = "Blue", opens = "Loadout"},
			{id = "Shop", label = "Shop", icon = "shop", key = "Orange", opens = "Shop"},
			{id = "Settings", label = "Settings", icon = "settings", key = "Gray", opens = "Settings"},
		}, Vector2.new(0, 0), UDim2.fromOffset(130, 16))
	end,
}

GAMES.tower = {
	windows = {
		{name = "Units", title = "Units", icon = "tower", w = 1000, h = 660, build = W.shopCards({
			{name = "Archer", sub = "Cheap and fast", icon = "bow", key = "Green", price = 250,
				stats = {{"Damage", 0.3}, {"Range", 0.7}, {"Speed", 0.8}}},
			{name = "Cannon", sub = "Splash damage", icon = "fire", key = "Orange", price = 800,
				stats = {{"Damage", 0.7}, {"Range", 0.5}, {"Speed", 0.3}}},
			{name = "Wizard", sub = "Hits flying", icon = "staff", key = "Purple", price = 1500,
				stats = {{"Damage", 0.6}, {"Range", 0.8}, {"Speed", 0.5}}},
			{name = "Freezer", sub = "Slows enemies", icon = "water", key = "Blue", price = 1200,
				stats = {{"Damage", 0.2}, {"Range", 0.6}, {"Speed", 0.6}}}}, {"All", "Owned", "Legendary"})},
		{name = "Shop", title = "Shop", icon = "shop", w = 900, h = 600, build = W.shopCards({
			{name = "Mystery Crate", sub = "Random unit", icon = "crate", price = 50, key = "Gold", robux = true},
			{name = "x2 Speed", sub = "Game speed", icon = "bolt", price = 199, key = "Blue", robux = true}})},
		{name = "Settings", title = "Settings", icon = "settings", w = 760, h = 560, build = W.settings},
	},
	hud = function(root)
		local tc, sc = simText()
		local wv = cluster(root, "Wave", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 14), 560, 120)
		label(wv, "Wave 5 / 30", {name = "Wave", size = UDim2.fromOffset(560, 60), ts = 56, role = "title", color = tc, stroke = sc,
			strokeW = 4})
		bar(wv, "BaseHealth", 0.72, "Red", 460, 30, UDim2.fromOffset(50, 70), "Base 72%")
		currencies(root, {{name = "Cash", icon = "cash", key = "Green", value = 1850, cash = true}}, Vector2.new(0, 0),
			UDim2.fromOffset(ST.currency == "fade" and 0 or 20, 80))
		local bar_ = cluster(root, "Units", Vector2.new(0.5, 1), UDim2.new(0.5, 0, 1, -20), 5 * 134, 150)
		local units = {{"bow", 250}, {"fire", 800}, {"staff", 1500}, {"water", 1200}, {"unknown", 0}}
		for i, u in ipairs(units) do
			local s, sc_ = slot(bar_, "Unit" .. i, 120, 120, UDim2.fromOffset((i - 1) * 134, 0), T.color(CARD_KEYS[i]))
			icon(sc_, u[1], 76, {pos = UDim2.fromScale(0.5, 0.44), z = 6, color = T.color(CARD_KEYS[i]), tone2 = WHITE})
			if u[2] > 0 then
				label(s, "$" .. commas(u[2]), {name = "Cost", size = UDim2.fromOffset(120, 30), pos = UDim2.new(0.5, 0, 1, 12),
					anchor = Vector2.new(0.5, 0.5), ts = 26, role = "number", color = T.color("Green"), stroke = INK, strokeW = 2.5, z = 10})
			end
		end
		local sp = cluster(root, "Speed", Vector2.new(1, 1), UDim2.new(1, -30, 1, -30), 300, 190)
		button(sp, "Speed1", "x1", "Blue", 140, 74, UDim2.new(), {role = "action", ts = 38})
		button(sp, "Speed2", "x2", "Gray", 140, 74, UDim2.fromOffset(160, 0), {role = "tabOff", ts = 38})
		button(sp, "SkipWave", "Skip Wave", "Green", 300, 86, UDim2.fromOffset(0, 96), {role = "action", ts = 40, action = "SkipWave"})
		menuColumn(root, "Menu", {
			{id = "Units", label = "Units", icon = "tower", key = "Purple", opens = "Units"},
			{id = "Shop", label = "Shop", icon = "shop", key = "Red", opens = "Shop", gold = true},
			{id = "Settings", label = "Settings", icon = "settings", key = "Gray", opens = "Settings"},
		}, side("right"), -60)
	end,
}

GAMES.roleplay = {
	windows = {
		{name = "Houses", title = "Houses", icon = "home", w = 1000, h = 640, build = W.shopCards({
			{name = "Starter Home", sub = "2 rooms", icon = "home", key = "Green", action = "Spawn"},
			{name = "Modern Villa", sub = "Pool + garage", icon = "home", key = "Blue", price = 450, robux = true},
			{name = "Mansion", sub = "12 rooms", icon = "crown", key = "Gold", price = 999, robux = true},
			{name = "Treehouse", sub = "Cozy", icon = "home", key = "Orange", action = "Spawn"}})},
		{name = "Vehicles", title = "Vehicles", icon = "car", w = 1000, h = 640, build = W.shopCards({
			{name = "Scooter", sub = "Zippy", icon = "car", key = "Pink", action = "Spawn"},
			{name = "Pickup", sub = "Seats 4", icon = "car", key = "Orange", action = "Spawn"},
			{name = "Police Car", sub = "Sirens", icon = "car", key = "Blue", action = "Spawn"},
			{name = "Limo", sub = "VIP", icon = "car", key = "Purple", price = 299, robux = true}})},
		{name = "Outfits", title = "Outfits", icon = "shirt", w = 900, h = 640, build = W.inventory(16, false)},
		{name = "Jobs", title = "Jobs", icon = "jobs", w = 900, h = 620, build = W.rows({
			{title = "Police", sub = "$120 / paycheck", icon = "shield", key = "Blue", action = "Join"},
			{title = "Doctor", sub = "$150 / paycheck", icon = "heart", key = "Red", action = "Join"},
			{title = "Chef", sub = "$90 / paycheck", icon = "fire", key = "Orange", action = "Join"},
			{title = "Firefighter", sub = "$130 / paycheck", icon = "water", key = "Red", action = "Join"}}, "Join")},
		{name = "Phone", title = "Phone", icon = "phone", w = 620, h = 620, build = W.phone},
		{name = "Settings", title = "Settings", icon = "settings", w = 760, h = 560, build = W.settings},
	},
	hud = function(root)
		currencies(root, {{name = "Cash", icon = "cash", key = "Green", value = 2500, cash = true}}, Vector2.new(1, 0),
			UDim2.new(1, -20, 0, 20))
		local tc, sc = simText()
		bigText(root, "Job", "Job: Police", Vector2.new(1, 0), UDim2.new(1, -30, 0, 110), 34, 320)
		menuRow(root, "Menu", {
			{id = "Houses", label = "Houses", icon = "home", key = "Blue", opens = "Houses"},
			{id = "Vehicles", label = "Cars", icon = "car", key = "Red", opens = "Vehicles"},
			{id = "Outfits", label = "Outfits", icon = "shirt", key = "Pink", opens = "Outfits"},
			{id = "Jobs", label = "Jobs", icon = "jobs", key = "Orange", opens = "Jobs"},
			{id = "Phone", label = "Phone", icon = "phone", key = "Green", opens = "Phone"},
			{id = "Settings", label = "Settings", icon = "settings", key = "Gray", opens = "Settings"},
		}, Vector2.new(0.5, 1), UDim2.new(0.5, 0, 1, -50))
	end,
}

-----------------------------------------------------------------------------------------------
-- the LocalScript that runs the UI in game
-----------------------------------------------------------------------------------------------
local CONTROLLER = [==[
-- SimUI controller (made by the SimUI Generator plugin).
-- Opens/closes the windows, gives the buttons their feel, scales the UI for every screen and
-- shows leaderstats values. From your own LocalScripts:
--   gui.OpenWindow:Fire("Shop")   gui.CloseWindow:Fire()   gui.ShowTip:Fire("Grab the cash!")
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")
local UserInputService = game:GetService("UserInputService")
local gui = script.Parent
local root = gui:WaitForChild("Root")
local windows = root:WaitForChild("Windows")
local motion = gui:GetAttribute("Motion") or "bouncy"
local sizeMul = gui:GetAttribute("SizeMul") or 1
local camera = workspace.CurrentCamera

local function tw(o, t, props, style, dir)
	local tween = TweenService:Create(o, TweenInfo.new(t, style or Enum.EasingStyle.Quad, dir or Enum.EasingDirection.Out), props)
	tween:Play()
	return tween
end

local function rescale()
	local v = camera.ViewportSize
	local s = math.clamp(math.min(v.X / 1920, v.Y / 1080), 0.4, 1.5) * sizeMul
	for _, d in ipairs(root:GetDescendants()) do
		if d:IsA("UIScale") and d:GetAttribute("AutoScale") then
			d.Scale = s
		end
	end
end
camera:GetPropertyChangedSignal("ViewportSize"):Connect(rescale)
rescale()

local blur
local function setBlur(on)
	-- the big logo would clash with window titles: hide it while a window is open
	local logo = root:FindFirstChild("Logo")
	if logo then
		logo.Visible = not on
	end
	if not gui:GetAttribute("Blur") then
		return
	end
	if not blur then
		blur = Instance.new("BlurEffect")
		blur.Size = 0
		blur.Parent = camera
	end
	tw(blur, 0.25, {Size = on and 16 or 0})
end

local current = nil
local function parts(w)
	local panel = w:FindFirstChild("Panel")
	local pop = panel and panel:FindFirstChild("Pop")
	return panel, pop and pop:FindFirstChild("PopScale"), w:FindFirstChild("Backdrop")
end

local function closeW(name, instant)
	local w = windows:FindFirstChild(name or current or "")
	if not w then
		return
	end
	if current == w.Name then
		current = nil
	end
	local panel, ps, bd = parts(w)
	if instant or motion == "retro" or motion == "none" then
		w.Visible = false
	else
		local home = panel:GetAttribute("Home")
		if w:GetAttribute("Place") == "side" and home then
			tw(panel, 0.2, {Position = home + UDim2.new(0, 900, 0, 0)}, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		elseif ps then
			tw(ps, 0.15, {Scale = 0.6}, Enum.EasingStyle.Quad, Enum.EasingDirection.In)
		end
		if bd then
			tw(bd, 0.15, {BackgroundTransparency = 1})
		end
		task.delay(0.17, function()
			if current ~= w.Name then
				w.Visible = false
				if home then
					panel.Position = home
				end
			end
		end)
	end
	if not current then
		setBlur(false)
	end
end

local function openW(name)
	local w = windows:FindFirstChild(name)
	if not w then
		return
	end
	if current == name then
		closeW(name)
		return
	end
	if current then
		closeW(current, true)
	end
	current = name
	local panel, ps, bd = parts(w)
	local place = w:GetAttribute("Place")
	w.Visible = true
	if bd then
		local t0 = bd:GetAttribute("T0") or bd.BackgroundTransparency
		bd:SetAttribute("T0", t0)
		bd.BackgroundTransparency = 1
		tw(bd, 0.2, {BackgroundTransparency = t0})
	end
	local home = panel:GetAttribute("Home") or panel.Position
	panel:SetAttribute("Home", home)
	if place == "side" then
		panel.Position = home + UDim2.new(0, 900, 0, 0)
		tw(panel, 0.35, {Position = home}, motion == "slide" and Enum.EasingStyle.Back or Enum.EasingStyle.Quint)
		ps.Scale = 1
	elseif motion == "retro" then
		task.spawn(function()
			for _, s in ipairs({0.34, 0.67, 1}) do
				ps.Scale = s
				task.wait(0.05)
			end
		end)
	elseif motion == "flicker" then
		ps.Scale = 1
		task.spawn(function()
			for i = 1, 4 do
				w.Visible = i % 2 == 0
				task.wait(0.05)
			end
			w.Visible = current == name
		end)
	elseif motion == "press" then
		ps.Scale = 1
		panel.Position = home - UDim2.new(0, 0, 0, 700)
		tw(panel, 0.5, {Position = home}, Enum.EasingStyle.Bounce)
	else
		local calm = motion == "smooth" or motion == "glitch" or motion == "none"
		ps.Scale = motion == "squish" and 0.4 or (calm and 0.92 or 0.6)
		tw(ps, calm and 0.2 or 0.32, {Scale = 1}, calm and Enum.EasingStyle.Quad or Enum.EasingStyle.Back)
	end
	setBlur(true)
end

local function recolor(b, c)
	local body = b:FindFirstChild("Body")
	if not body then
		return
	end
	local face = body:FindFirstChild("Face") or body
	local g = face:FindFirstChildOfClass("UIGradient")
	if g and face.BackgroundColor3 == Color3.new(1, 1, 1) then
		g.Color = ColorSequence.new({ColorSequenceKeypoint.new(0, c:Lerp(Color3.new(1, 1, 1), 0.42)),
			ColorSequenceKeypoint.new(0.5, c:Lerp(Color3.new(1, 1, 1), 0.08)), ColorSequenceKeypoint.new(1, c:Lerp(Color3.new(), 0.08))})
	else
		face.BackgroundColor3 = c
	end
end

local ON, OFF = Color3.fromRGB(79, 214, 44), Color3.fromRGB(238, 59, 59)

local function hook(b)
	local hs = b:FindFirstChild("HoverScale")
	local body = b:FindFirstChild("Body")
	local rest = body and body.Position
	local rot0 = b.Rotation
	local px, py = b:GetAttribute("PressX") or 0, b:GetAttribute("PressY") or 0
	local text = b:FindFirstChild("Text", true)
	local accent = b:FindFirstChild("Accent")
	local function state(s)
		if not hs then
			return
		end
		if motion == "bouncy" or motion == "squish" then
			local sc = s == "hover" and (motion == "squish" and 1.1 or 1.08) or (s == "down" and 0.9 or 1)
			tw(hs, s == "down" and 0.06 or 0.18, {Scale = sc}, s == "down" and Enum.EasingStyle.Quad or Enum.EasingStyle.Back)
		elseif motion == "press" then
			if body then
				tw(body, 0.06, {Position = s == "down" and (rest + UDim2.fromOffset(px, py)) or rest})
			end
			tw(b, 0.12, {Rotation = rot0 + (s == "hover" and 3 or 0)})
		elseif motion == "smooth" then
			tw(hs, 0.15, {Scale = s == "hover" and 1.04 or (s == "down" and 0.97 or 1)})
			if body then
				tw(body, 0.15, {Position = rest + UDim2.fromOffset(0, s == "hover" and -3 or 0)})
			end
		elseif motion == "slide" then
			if body then
				tw(body, 0.12, {Position = rest + UDim2.fromOffset(s == "hover" and 10 or 0, 0)})
			end
			tw(hs, 0.08, {Scale = s == "down" and 0.95 or 1})
		elseif motion == "flicker" then
			if accent then
				accent.BackgroundTransparency = s == "idle" and 1 or 0
			end
			if text and text:IsA("TextLabel") and s == "hover" then
				task.spawn(function()
					for _ = 1, 3 do
						text.TextTransparency = 0.6
						task.wait(0.04)
						text.TextTransparency = 0
						task.wait(0.05)
					end
				end)
			end
			tw(hs, 0.1, {Scale = s == "down" and 0.97 or 1})
		elseif motion == "glitch" then
			if body and s == "hover" then
				task.spawn(function()
					for _, dx in ipairs({3, -3, 2, 0}) do
						body.Position = rest + UDim2.fromOffset(dx, 0)
						task.wait(0.03)
					end
				end)
			end
			tw(hs, 0.08, {Scale = s == "down" and 0.96 or (s == "hover" and 1.03 or 1)})
		elseif motion == "retro" then
			hs.Scale = 1
			if body then
				body.Position = s == "down" and (rest + UDim2.fromOffset(3, 3)) or rest
			end
		end
	end
	b.MouseEnter:Connect(function() state("hover") end)
	b.MouseLeave:Connect(function() state("idle") end)
	b.MouseButton1Down:Connect(function() state("down") end)
	b.MouseButton1Up:Connect(function() state("hover") end)
	b.Activated:Connect(function()
		local o, c = b:GetAttribute("Opens"), b:GetAttribute("Closes")
		if o then
			openW(o)
		elseif c then
			closeW(c)
		end
		if b:GetAttribute("Toggle") ~= nil then
			local on = not b:GetAttribute("Toggle")
			b:SetAttribute("Toggle", on)
			if text and text:IsA("TextLabel") then
				text.Text = on and "ON" or "OFF"
			end
			recolor(b, on and ON or OFF)
		end
		if b:GetAttribute("Tab") then
			for _, s in ipairs(b.Parent:GetChildren()) do
				if s:IsA("GuiButton") and s:GetAttribute("Tab") then
					local hsc = s:FindFirstChild("HoverScale")
					s:SetAttribute("Active", s == b)
					if s:FindFirstChild("Body") then
						s.Body.BackgroundTransparency = 0
					end
					recolor(s, s == b and ON or Color3.fromRGB(174, 181, 194))
				end
			end
		end
	end)
end

for _, b in ipairs(root:GetDescendants()) do
	if b:IsA("GuiButton") then
		hook(b)
	end
end

-- hotbar: keys 1-9 pick a slot
local slots = {}
for _, d in ipairs(root:GetDescendants()) do
	if d:IsA("GuiButton") and d:GetAttribute("Slot") then
		slots[d:GetAttribute("Slot")] = d
	end
end
local keys = {Enum.KeyCode.One, Enum.KeyCode.Two, Enum.KeyCode.Three, Enum.KeyCode.Four, Enum.KeyCode.Five,
	Enum.KeyCode.Six, Enum.KeyCode.Seven, Enum.KeyCode.Eight, Enum.KeyCode.Nine}
UserInputService.InputBegan:Connect(function(input, processed)
	if processed then
		return
	end
	for i, k in ipairs(keys) do
		if input.KeyCode == k and slots[i] then
			for j, s in pairs(slots) do
				local st = s:FindFirstChild("Body") and s.Body:FindFirstChildOfClass("UIStroke")
				if st then
					st.Color = j == i and Color3.fromRGB(255, 214, 64) or Color3.fromRGB(27, 27, 34)
				end
			end
		end
	end
end)

-- the API events
local function ev(name)
	return gui:FindFirstChild(name)
end
if ev("OpenWindow") then
	ev("OpenWindow").Event:Connect(openW)
end
if ev("CloseWindow") then
	ev("CloseWindow").Event:Connect(function(name)
		closeW(name)
	end)
end
local tipFrame = root:FindFirstChild("Tip")
if ev("ShowTip") and tipFrame then
	ev("ShowTip").Event:Connect(function(text)
		if text then
			local l = tipFrame:FindFirstChild("Text", true)
			if l then
				l.Text = text
			end
			tipFrame.Visible = true
		else
			tipFrame.Visible = false
		end
		-- the tip sits where the side menu is, like in the big simulator games
		local menu = root:FindFirstChild("Menu")
		if menu and tipFrame:GetAttribute("HidesMenu") then
			menu.Visible = not tipFrame.Visible
		end
	end)
end

-- ambient motion: shine sweep, flicker, scan lines
task.spawn(function()
	while gui.Parent do
		for _, d in ipairs(root:GetDescendants()) do
			if d.Name == "Shine" and d:IsA("Frame") then
				local g = d:FindFirstChildOfClass("UIGradient")
				if g then
					g.Offset = Vector2.new(-1, 0)
					tw(g, 0.9, {Offset = Vector2.new(1, 0)})
				end
			elseif d:GetAttribute("Scan") then
				d.Position = UDim2.fromScale(0, 0)
				tw(d, 2.5, {Position = UDim2.fromScale(0, 1)}, Enum.EasingStyle.Linear)
			end
		end
		task.wait(3.5)
	end
end)
if motion == "flicker" then
	task.spawn(function()
		local flick = {}
		for _, d in ipairs(root:GetDescendants()) do
			if d:GetAttribute("Flicker") and d:IsA("TextLabel") then
				table.insert(flick, d)
			end
		end
		while gui.Parent and #flick > 0 do
			task.wait(1 + math.random() * 3)
			local l = flick[math.random(1, #flick)]
			for _ = 1, 2 do
				l.TextTransparency = 0.7
				task.wait(0.05)
				l.TextTransparency = 0
				task.wait(0.07)
			end
		end
	end)
end

-- leaderstats -> the currency counters
local function short(n)
	local a = math.abs(n)
	local units = {{1e12, "T"}, {1e9, "B"}, {1e6, "M"}, {1e3, "K"}}
	for _, u in ipairs(units) do
		if a >= u[1] then
			local v = n / u[1]
			local s = v >= 100 and string.format("%d", math.floor(v)) or string.format("%.1f", v):gsub("%.0$", "")
			return s .. u[2]
		end
	end
	return tostring(math.floor(n))
end
local function commas(n)
	local s = tostring(math.floor(n))
	local out = s:reverse():gsub("(%d%d%d)", "%1,"):reverse()
	return (out:gsub("^,", ""))
end
task.spawn(function()
	local player = Players.LocalPlayer
	local stats = player:WaitForChild("leaderstats", 30)
	if not stats then
		return
	end
	for _, lbl in ipairs(root:GetDescendants()) do
		local name = lbl:IsA("TextLabel") and lbl:GetAttribute("Currency")
		local v = name and stats:FindFirstChild(name)
		if v and (v:IsA("IntValue") or v:IsA("NumberValue")) then
			local function upd()
				local val = v.Value
				lbl.Text = (lbl:GetAttribute("Prefix") or "") .. (lbl:GetAttribute("Short") and short(val) or commas(val))
			end
			v.Changed:Connect(upd)
			upd()
		end
	end
end)
]==]

-----------------------------------------------------------------------------------------------
-- build
-----------------------------------------------------------------------------------------------
local function normalizeId(s)
	if type(s) ~= "string" then
		return nil
	end
	local digits = s:match("(%d+)")
	if not digits or #digits < 3 then
		return nil
	end
	return "rbxassetid://" .. digits
end

local function build(opts)
	opts = opts or {}
	for k, v in pairs(DEFAULT_OPTIONS) do
		if opts[k] == nil then
			opts[k] = v
		end
	end
	loadKit()
	R, ST, T = resolve(opts)
	R.sheet = normalizeId(opts.iconSheet)
	local rec = nil
	pcall(function()
		rec = ChangeHistoryService:TryBeginRecording("SimUI build")
	end)
	local old = StarterGui:FindFirstChild("SimUI")
	if old then
		old:Destroy()
	end
	local gui = new("ScreenGui", {Name = "SimUI", ResetOnSpawn = false, IgnoreGuiInset = true,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling})
	gui:SetAttribute("Prompt", opts.prompt or "")
	gui:SetAttribute("GameType", R.game)
	gui:SetAttribute("Style", R.style)
	gui:SetAttribute("Palette", R.palette)
	gui:SetAttribute("Motion", ST.motion)
	gui:SetAttribute("SizeMul", R.scale)
	gui:SetAttribute("Blur", ST.blur == true)
	gui:SetAttribute("Seed", R.seed)
	gui:SetAttribute("Version", VERSION)
	for _, n in ipairs({"OpenWindow", "CloseWindow", "ShowTip"}) do
		new("BindableEvent", {Name = n, Parent = gui})
	end
	local root = frame(gui, "Root", {Size = UDim2.fromScale(1, 1)})
	local g = GAMES[R.game]
	g.hud(root)
	if ST.currency == "fade" then
		for _, d in ipairs(root:GetDescendants()) do
			if d:GetAttribute("Currency") then
				d:SetAttribute("Short", true)
			end
		end
	end
	local wins = frame(root, "Windows", {Size = UDim2.fromScale(1, 1), ZIndex = 50})
	for _, def in ipairs(g.windows) do
		local content, cw, ch = window(wins, def)
		def.build(content, cw, ch)
	end
	local ctrl = new("LocalScript", {Name = "SimUIController"})
	ctrl.Source = CONTROLLER
	ctrl.Parent = gui
	gui.Parent = StarterGui
	if rec then
		pcall(function()
			ChangeHistoryService:FinishRecording(rec, Enum.FinishRecordingOperation.Commit)
		end)
	else
		pcall(function()
			ChangeHistoryService:SetWaypoint("SimUI build")
		end)
	end
	pcall(function()
		SelectionService:Set({gui})
	end)
	local summary = ("%s - %s style - %s colours%s"):format(GAME_LABELS[R.game], R.style, R.palette,
		R.title and (' - "' .. R.title .. '"') or "")
	print("SimUI: built " .. summary .. " (" .. #gui:GetDescendants() .. " instances)")
	return gui, summary
end

-----------------------------------------------------------------------------------------------
-- the plugin panel (or build straight away from the Command Bar)
-----------------------------------------------------------------------------------------------
if plugin then
	local opts = copy(DEFAULT_OPTIONS)
	local saved = plugin:GetSetting("SimUIOptions")
	if type(saved) == "table" then
		for k, v in pairs(saved) do
			opts[k] = v
		end
	end
	local toolbar = plugin:CreateToolbar("SimUI")
	local tbButton = toolbar:CreateButton("SimUI", "Generate a game UI from a prompt", "")
	local info = DockWidgetPluginGuiInfo.new(Enum.InitialDockState.Float, true, false, 420, 760, 340, 420)
	local widget = plugin:CreateDockWidgetPluginGui("SimUIGenerator2", info)
	widget.Title = "SimUI Generator " .. VERSION

	local BG, ROW, TXT, DIM = hex("26272B"), hex("34363C"), hex("EDEFF5"), hex("9CA1AD")
	local UI = Enum.Font.GothamMedium
	local root = new("ScrollingFrame", {Name = "Panel", Size = UDim2.fromScale(1, 1), BackgroundColor3 = BG,
		ScrollBarThickness = 6, CanvasSize = UDim2.new(), AutomaticCanvasSize = Enum.AutomaticSize.Y,
		ScrollingDirection = Enum.ScrollingDirection.Y, Parent = widget})
	new("UIPadding", {PaddingTop = UDim.new(0, 10), PaddingLeft = UDim.new(0, 10), PaddingRight = UDim.new(0, 14),
		PaddingBottom = UDim.new(0, 14), Parent = root})
	new("UIListLayout", {Padding = UDim.new(0, 6), SortOrder = Enum.SortOrder.LayoutOrder, Parent = root})
	local order = 0
	local function nextOrder()
		order = order + 1
		return order
	end
	local function text(t, size, color, h)
		return new("TextLabel", {Text = t, Size = UDim2.new(1, 0, 0, h or 20), BackgroundTransparency = 1, Font = UI,
			TextSize = size or 14, TextColor3 = color or TXT, TextWrapped = true, TextXAlignment = Enum.TextXAlignment.Left,
			LayoutOrder = nextOrder(), Parent = root})
	end
	local function btn(parent, name, t, color, size, pos)
		local b = new("TextButton", {Name = name, Text = t, Size = size, Position = pos or UDim2.new(), BackgroundColor3 = color,
			Font = Enum.Font.GothamBold, TextSize = 14, TextColor3 = WHITE, AutoButtonColor = true, Parent = parent})
		new("UICorner", {CornerRadius = UDim.new(0, 6), Parent = b})
		return b
	end

	text("SimUI Generator " .. VERSION, 18, WHITE, 26)
	text("Describe the game, pick anything below (auto = the style decides), then Build.", 12, DIM, 30)
	local prompt = new("TextBox", {Name = "Prompt", Text = opts.prompt or PROMPT, Size = UDim2.new(1, 0, 0, 58), BackgroundColor3 = ROW,
		TextColor3 = WHITE, Font = UI, TextSize = 14, TextWrapped = true, ClearTextOnFocus = false, MultiLine = true,
		TextXAlignment = Enum.TextXAlignment.Left, TextYAlignment = Enum.TextYAlignment.Top, LayoutOrder = nextOrder(), Parent = root})
	new("UICorner", {CornerRadius = UDim.new(0, 6), Parent = prompt})
	new("UIPadding", {PaddingLeft = UDim.new(0, 8), PaddingTop = UDim.new(0, 6), Parent = prompt})
	local summary = text("", 13, hex("7BE06A"), 34)

	local rows = {}
	local function refresh()
		opts.prompt = prompt.Text
		for key, r in pairs(rows) do
			r.value.Text = tostring(opts[key])
			r.value.TextColor3 = opts[key] == "auto" and DIM or WHITE
		end
		local ok, rr, st = pcall(resolve, opts)
		if ok then
			summary.Text = ("-> %s  |  %s style  |  %s colours  |  %s motion"):format(GAME_LABELS[rr.game], rr.style, rr.palette,
				st.motion)
		end
		plugin:SetSetting("SimUIOptions", opts)
	end
	for _, o in ipairs(OPTIONS) do
		local row = new("Frame", {Name = o.key, Size = UDim2.new(1, 0, 0, 30), BackgroundColor3 = ROW, LayoutOrder = nextOrder(),
			Parent = root})
		new("UICorner", {CornerRadius = UDim.new(0, 6), Parent = row})
		new("TextLabel", {Text = o.label, Size = UDim2.new(0.42, 0, 1, 0), Position = UDim2.fromOffset(10, 0),
			BackgroundTransparency = 1, Font = UI, TextSize = 13, TextColor3 = DIM, TextXAlignment = Enum.TextXAlignment.Left,
			Parent = row})
		local value = new("TextLabel", {Name = "Value", Size = UDim2.new(0.58, -70, 1, 0), Position = UDim2.new(0.42, 30, 0, 0),
			BackgroundTransparency = 1, Font = Enum.Font.GothamBold, TextSize = 13, TextColor3 = WHITE, Parent = row})
		local function step(d)
			local list = o.values
			local idx = 1
			for i, v in ipairs(list) do
				if v == opts[o.key] then
					idx = i
				end
			end
			opts[o.key] = list[(idx - 1 + d) % #list + 1]
			refresh()
		end
		local prev = btn(row, "Prev", "<", hex("4A4D55"), UDim2.fromOffset(26, 24), UDim2.new(0.42, 0, 0, 3))
		local nxt = btn(row, "Next", ">", hex("4A4D55"), UDim2.fromOffset(26, 24), UDim2.new(1, -30, 0, 3))
		prev.MouseButton1Click:Connect(function() step(-1) end)
		nxt.MouseButton1Click:Connect(function() step(1) end)
		value.InputBegan:Connect(function(input)
			if input.UserInputType == Enum.UserInputType.MouseButton2 then
				opts[o.key] = o.values[1]
				refresh()
			end
		end)
		rows[o.key] = {value = value}
	end
	text("Icon sheet ID (optional): upload Icons/Atlas_Icons.png from the ZIP, paste its ID here for the 3D icons.",
		12, DIM, 30)
	local sheet = new("TextBox", {Name = "IconSheet", Text = opts.iconSheet or "", PlaceholderText = "rbxassetid://...",
		Size = UDim2.new(1, 0, 0, 30), BackgroundColor3 = ROW, TextColor3 = WHITE, PlaceholderColor3 = DIM, Font = UI, TextSize = 13,
		ClearTextOnFocus = false, LayoutOrder = nextOrder(), Parent = root})
	new("UICorner", {CornerRadius = UDim.new(0, 6), Parent = sheet})
	sheet.FocusLost:Connect(function()
		opts.iconSheet = sheet.Text
		refresh()
	end)
	local bar_ = new("Frame", {Name = "Buttons", Size = UDim2.new(1, 0, 0, 44), BackgroundTransparency = 1, LayoutOrder = nextOrder(),
		Parent = root})
	local go = btn(bar_, "Build", "Build UI", hex("3FAE2A"), UDim2.new(0.5, -4, 1, 0))
	go.TextSize = 18
	local shuffle = btn(bar_, "Shuffle", "Shuffle", hex("5B6CF0"), UDim2.new(0.25, -4, 1, 0), UDim2.new(0.5, 4, 0, 0))
	local reset = btn(bar_, "Reset", "Reset", hex("6A6D75"), UDim2.new(0.25, -4, 1, 0), UDim2.new(0.75, 4, 0, 0))
	local status = text("Right-click a value to set it back to auto.", 12, DIM, 40)
	local function doBuild()
		opts.prompt = prompt.Text
		opts.iconSheet = sheet.Text
		local ok, gui, sum = pcall(build, copy(opts))
		status.Text = ok and ("Built StarterGui > SimUI: " .. sum .. ". Press Play to try it.") or ("Error: " .. tostring(gui))
		status.TextColor3 = ok and hex("7BE06A") or hex("FF6B6B")
		refresh()
	end
	go.MouseButton1Click:Connect(doBuild)
	shuffle.MouseButton1Click:Connect(function()
		opts.seed = math.random(1, 999999)
		doBuild()
	end)
	reset.MouseButton1Click:Connect(function()
		local keepPrompt, keepSheet = prompt.Text, sheet.Text
		opts = copy(DEFAULT_OPTIONS)
		opts.prompt, opts.iconSheet = keepPrompt, keepSheet
		refresh()
	end)
	prompt.FocusLost:Connect(refresh)
	tbButton.Click:Connect(function()
		widget.Enabled = not widget.Enabled
	end)
	refresh()
else
	build({prompt = PROMPT})
end
