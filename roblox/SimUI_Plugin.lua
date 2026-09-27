--[[
	SimUI Generator - studs-style game UI from a prompt (no AI, keyword matching)

	INSTALL AS A PLUGIN
	  Studio > Plugins tab > Plugins Folder, drop this file in (keep the .lua ending) and restart
	  Studio. A "SimUI" button appears in the Plugins tab: type a prompt, click Build.

	OR RUN ONCE FROM THE COMMAND BAR
	  Change PROMPT below, paste the whole file into View > Command Bar, press Enter.

	PROMPT EXAMPLES
	  '"Pet Legends" candy simulator'     theme Candy, simulator layout, logo "Pet Legends"
	  'lava fighting'                      Lava theme, fighting layout (health/xp bars, abilities)
	  'galaxy tycoon', 'spooky horror', 'ocean fishing simulator', 'neon obby', 'royal rpg'
	  Themes: classic candy ocean lava forest galaxy neon winter spooky holiday royal desert toxic pastel
	          military midnight sunset (plus colour words: red, blue, pink...)
	  Game types: simulator tycoon obby fighting horror racing rpg

	IMAGES (optional)
	  Out of the box everything is native Roblox UI (UICorner, UIStroke, UIGradient, shine) with
	  emoji icons. For the full studs look: run ui/generate.py with the same prompt (or pick a kit
	  in ui/kits/), upload its Atlas_*.png + ui/icons/Atlas_Icons.png + Stud_Tile.png, paste the
	  ids into SimUIKit.lua and put it in ReplicatedStorage as a ModuleScript named SimUIKit.
	  The generator then uses the sprite sheets (9-slice buttons, panels, cards, icons, titles).

	Everything is built into StarterGui > SimUI with a LocalScript that opens/closes the windows,
	animates buttons and the shine, scales the UI for any screen and shows leaderstats values.
]]

local PROMPT = '"My Simulator" classic simulator'

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local StarterGui = game:GetService("StarterGui")
local ChangeHistoryService = game:GetService("ChangeHistoryService")

-----------------------------------------------------------------------------------------------
-- themes (same presets as ui/themes.py)
-----------------------------------------------------------------------------------------------
local THEMES = {
	Classic = {kw = "classic default bright simulator sim blue cartoon", Primary = "2FA4FF", Secondary = "43D162", Accent = "FFC933", Panel = "3E8EF7", Panel2 = "2361D6", Inner = "9FD2FF", Outline = "10275C", TitleTop = "FFFFFF", TitleBottom = "FFE25A"},
	Candy = {kw = "candy sweet pink pastel cute kawaii bubblegum sugar", Primary = "FF6FB5", Secondary = "B57BFF", Accent = "6FE3FF", Panel = "FF9ACB", Panel2 = "E75CA8", Inner = "FFE0F0", Outline = "6A1B4D", TitleTop = "FFFFFF", TitleBottom = "FFB3E0"},
	Ocean = {kw = "ocean sea water aqua beach fish fishing island teal summer", Primary = "1FC8E8", Secondary = "2BD9A4", Accent = "FFD85A", Panel = "1AA7D9", Panel2 = "0B6FB0", Inner = "A9ECFF", Outline = "06304F", TitleTop = "FFFFFF", TitleBottom = "8FF3FF"},
	Lava = {kw = "lava fire volcano hell inferno red flame magma dragon", Primary = "FF5A2A", Secondary = "FFB02E", Accent = "FFE14D", Panel = "D8431E", Panel2 = "8E1D0E", Inner = "FFC0A0", Outline = "3A0A04", TitleTop = "FFF3B0", TitleBottom = "FF7A1A"},
	Forest = {kw = "forest nature jungle green farm garden wood tree plant", Primary = "4CC94F", Secondary = "A9D13C", Accent = "FFC94A", Panel = "5BAA3C", Panel2 = "357A26", Inner = "D6F5B8", Outline = "173A10", TitleTop = "FFFFFF", TitleBottom = "C8FF6A"},
	Galaxy = {kw = "galaxy space cosmic star alien planet universe purple moon", Primary = "8A5CFF", Secondary = "3FD2FF", Accent = "FF6BE6", Panel = "3A2A8C", Panel2 = "1B1248", Inner = "8C7BE0", Outline = "0A0620", TitleTop = "FFFFFF", TitleBottom = "C9A6FF"},
	Neon = {kw = "neon cyber cyberpunk arcade retro synth glow techno future", Primary = "FF2FD0", Secondary = "28F0FF", Accent = "F7FF3C", Panel = "26214A", Panel2 = "110E26", Inner = "4B3F8E", Outline = "05030F", TitleTop = "FFFFFF", TitleBottom = "28F0FF"},
	Winter = {kw = "winter ice snow frost frozen cold arctic white", Primary = "5CC8FF", Secondary = "A6E6FF", Accent = "FFFFFF", Panel = "E6F6FF", Panel2 = "A8D8F5", Inner = "FFFFFF", Outline = "1B4A73", TitleTop = "FFFFFF", TitleBottom = "9FE3FF"},
	Spooky = {kw = "spooky halloween horror scary ghost haunted pumpkin creepy zombie", Primary = "FF8A1F", Secondary = "9B4DFF", Accent = "7CFF4D", Panel = "3A2450", Panel2 = "1C1028", Inner = "6B4A8C", Outline = "0C0612", TitleTop = "FFE7B0", TitleBottom = "FF8A1F"},
	Holiday = {kw = "christmas xmas holiday festive santa noel gift", Primary = "E8323C", Secondary = "2DB34A", Accent = "FFD24A", Panel = "C9252E", Panel2 = "7E1219", Inner = "FFE3C4", Outline = "3B0507", TitleTop = "FFFFFF", TitleBottom = "FFD24A"},
	Royal = {kw = "royal gold golden luxury rich king vip premium money bank", Primary = "FFC21A", Secondary = "B884FF", Accent = "FFFFFF", Panel = "2B2440", Panel2 = "141022", Inner = "4E4466", Outline = "1A1200", TitleTop = "FFF6C0", TitleBottom = "FFB300"},
	Desert = {kw = "desert sand egypt pyramid western cowboy canyon sun", Primary = "F2A53A", Secondary = "E3683B", Accent = "56C7D9", Panel = "E3B878", Panel2 = "B77D3E", Inner = "FFE9C2", Outline = "4A2A0E", TitleTop = "FFF6D8", TitleBottom = "FFB54A"},
	Toxic = {kw = "toxic slime radioactive acid lime mutant poison", Primary = "8CFF2E", Secondary = "C04DFF", Accent = "FFE93A", Panel = "2E3A1E", Panel2 = "141A0C", Inner = "4D6630", Outline = "060A02", TitleTop = "F3FFB0", TitleBottom = "8CFF2E"},
	Pastel = {kw = "pastel soft cozy light cafe cottage bunny spring easter", Primary = "8FD3FF", Secondary = "FFB3C7", Accent = "FFE38A", Panel = "FFF4E8", Panel2 = "F2D9C4", Inner = "FFFFFF", Outline = "6B4E5E", TitleTop = "FFFFFF", TitleBottom = "FFC9D9"},
	Military = {kw = "military army war soldier tank battle shooter fps gun", Primary = "7A8F3C", Secondary = "C9A55A", Accent = "E8D27A", Panel = "4A5530", Panel2 = "2A3119", Inner = "7A8757", Outline = "121608", TitleTop = "F2F0D0", TitleBottom = "C9D17A"},
	Midnight = {kw = "dark midnight night black shadow ninja minimal sleek mono", Primary = "4F7CFF", Secondary = "3DDC97", Accent = "FFD166", Panel = "2A2E3A", Panel2 = "171A22", Inner = "3C4252", Outline = "07080C", TitleTop = "FFFFFF", TitleBottom = "A9B8FF"},
	Sunset = {kw = "sunset tropical orange summer vibes paradise evening", Primary = "FF7A45", Secondary = "FF4F8B", Accent = "FFD24A", Panel = "FF9A5A", Panel2 = "E0507A", Inner = "FFE3C9", Outline = "4A1024", TitleTop = "FFFFFF", TitleBottom = "FFD24A"},
}
local THEME_ORDER = {"Classic", "Candy", "Ocean", "Lava", "Forest", "Galaxy", "Neon", "Winter", "Spooky", "Holiday",
	"Royal", "Desert", "Toxic", "Pastel", "Military", "Midnight", "Sunset"}
local STD = {Green = "56D63B", Blue = "2FA4FF", Orange = "FF9A1F", Red = "F0443A", Yellow = "FFD21F", Purple = "A35CFF",
	Pink = "FF5FAE", Cyan = "27D8E8", Gray = "9AA3B2", Gold = "FFC21A"}
local COLOR_WORDS = {red = "E8323C", orange = "FF8A1F", yellow = "FFD21F", green = "43D162", lime = "8CFF2E",
	teal = "1FC8C0", cyan = "28F0FF", blue = "2F7BFF", navy = "1F3F9E", purple = "8A5CFF", violet = "A35CFF",
	pink = "FF6FB5", magenta = "FF2FD0", white = "F4F7FF", black = "23252E", gray = "8A93A6", grey = "8A93A6",
	brown = "9A6A3A", gold = "FFC21A"}
local GAME_TYPES = {
	{"simulator", "simulator sim clicker pet pets egg collect mining farm"},
	{"tycoon", "tycoon factory business restaurant store shop empire money"},
	{"obby", "obby parkour tower jump platformer stage"},
	{"fighting", "fighting fight pvp battle combat sword anime boss arena"},
	{"horror", "horror scary survival escape creepy backrooms"},
	{"racing", "racing race car cars drift kart driving"},
	{"rpg", "rpg adventure quest dungeon fantasy mmo"},
}

-- what each game type gets: top tabs, side buttons (name, colour, emoji, window), currencies, extras
local LAYOUTS = {
	simulator = {
		top = {{"Sell", "Green"}, {"Base", "Blue"}, {"Upgrades", "Orange"}},
		left = {{"Shop", "Red", "🛒"}, {"Pets", "Primary", "🐾"}, {"Rebirth", "Green", "🔁"}, {"Settings", "Gray", "⚙️"}},
		right = {{"Index", "Blue", "📘"}, {"Codes", "Purple", "🎟️"}, {"DailyRewards", "Yellow", "🎁"}},
		currencies = {{"Gems", "💎", "Cyan"}, {"Coins", "🪙", "Gold"}},
		hotbar = 9, boosts = true, quests = true, level = true, luck = true,
	},
	tycoon = {
		top = {{"Build", "Green"}, {"Shop", "Blue"}, {"Rebirth", "Orange"}},
		left = {{"Shop", "Red", "🛒"}, {"Rebirth", "Green", "🔁"}, {"Settings", "Gray", "⚙️"}},
		right = {{"Codes", "Purple", "🎟️"}, {"DailyRewards", "Yellow", "🎁"}},
		currencies = {{"Cash", "💵", "Green"}},
		hotbar = 0, boosts = true, quests = true, level = false, luck = false,
	},
	obby = {
		top = {{"Skip Stage", "Orange"}, {"Checkpoint", "Blue"}},
		left = {{"Shop", "Red", "🛒"}, {"Settings", "Gray", "⚙️"}},
		right = {{"Codes", "Purple", "🎟️"}},
		currencies = {{"Coins", "🪙", "Gold"}},
		hotbar = 0, boosts = false, quests = false, level = true, luck = false, stage = true,
	},
	fighting = {
		top = {{"Play", "Green"}, {"Arena", "Red"}, {"Ranked", "Purple"}},
		left = {{"Shop", "Red", "🛒"}, {"Pets", "Primary", "⚔️"}, {"Quests", "Yellow", "📜"}, {"Settings", "Gray", "⚙️"}},
		right = {{"Index", "Blue", "📘"}, {"Codes", "Purple", "🎟️"}},
		currencies = {{"Gems", "💎", "Cyan"}, {"Coins", "🪙", "Gold"}},
		hotbar = 5, boosts = true, quests = false, level = true, luck = false, health = true,
	},
	horror = {
		top = {},
		left = {{"Settings", "Gray", "⚙️"}},
		right = {},
		currencies = {},
		hotbar = 4, boosts = false, quests = false, level = false, luck = false, health = true,
	},
	racing = {
		top = {{"Race", "Green"}, {"Garage", "Blue"}, {"Upgrades", "Orange"}},
		left = {{"Shop", "Red", "🛒"}, {"Settings", "Gray", "⚙️"}},
		right = {{"Codes", "Purple", "🎟️"}, {"DailyRewards", "Yellow", "🎁"}},
		currencies = {{"Cash", "💵", "Green"}},
		hotbar = 0, boosts = true, quests = true, level = true, luck = false,
	},
	rpg = {
		top = {},
		left = {{"Pets", "Primary", "🎒"}, {"Quests", "Yellow", "📜"}, {"Shop", "Red", "🛒"}, {"Settings", "Gray", "⚙️"}},
		right = {{"Index", "Blue", "🗺️"}},
		currencies = {{"Gold", "🪙", "Gold"}},
		hotbar = 6, boosts = false, quests = true, level = true, luck = false, health = true,
	},
}
local WINDOW_TITLES = {Shop = "Shop", Pets = "Pets", Rebirth = "Rebirth", Settings = "Settings", Codes = "Codes",
	Index = "Index", DailyRewards = "Daily Rewards", Quests = "Quests"}
local KIT_ICON = {Shop = "Shop", Pets = "Paw", Rebirth = "Rebirth", Settings = "Settings", Codes = "Codes",
	Index = "Index", DailyRewards = "Gift", Quests = "Quests", Gems = "Gem", Coins = "Coin", Cash = "Cash",
	Gold = "Coin"}

-----------------------------------------------------------------------------------------------
-- helpers
-----------------------------------------------------------------------------------------------
local function hex(h)
	h = h:gsub("#", "")
	return Color3.fromRGB(tonumber(h:sub(1, 2), 16), tonumber(h:sub(3, 4), 16), tonumber(h:sub(5, 6), 16))
end

local function darker(c, t)
	return c:Lerp(Color3.new(0, 0, 0), t)
end

local function lighter(c, t)
	return c:Lerp(Color3.new(1, 1, 1), t)
end

local function new(class, props, children)
	local o = Instance.new(class)
	local parent = nil
	for k, v in pairs(props or {}) do
		if k == "Parent" then
			parent = v
		else
			o[k] = v
		end
	end
	for _, c in ipairs(children or {}) do
		c.Parent = o
	end
	if parent then
		o.Parent = parent
	end
	return o
end

local function hasWord(list, word)
	for w in list:gmatch("%S+") do
		if w == word then
			return true
		end
	end
	return false
end

local function parsePrompt(prompt)
	local title = prompt:match('"([^"]+)"') or prompt:match("'([^']+)'")
	local rest = prompt:gsub('"[^"]*"', " "):gsub("'[^']*'", " "):lower()
	local words = {}
	for w in rest:gmatch("[%a%d]+") do
		table.insert(words, w)
	end
	local best, score = "Classic", 0
	for _, name in ipairs(THEME_ORDER) do
		local s = 0
		for _, w in ipairs(words) do
			if w == name:lower() then
				s = s + 2
			elseif hasWord(THEMES[name].kw, w) then
				s = s + 1
			end
		end
		if s > score then
			best, score = name, s
		end
	end
	local theme = {}
	for k, v in pairs(THEMES[best]) do
		theme[k] = v
	end
	theme.Name = best
	for _, w in ipairs(words) do
		if COLOR_WORDS[w] then
			if not hasWord(THEMES[best].kw, w) then
				theme.Primary = COLOR_WORDS[w]
			end
			break
		end
	end
	local game = "simulator"
	for _, g in ipairs(GAME_TYPES) do
		local found = false
		for _, w in ipairs(words) do
			if hasWord(g[2], w) then
				found = true
			end
		end
		if found then
			game = g[1]
			break
		end
	end
	local font = Enum.Font.FredokaOne
	for _, w in ipairs(words) do
		if w == "cartoon" or w == "comic" or w == "luckiest" then
			font = Enum.Font.LuckiestGuy
		end
	end
	local C = {}
	for k, v in pairs(theme) do
		if type(v) == "string" and #v == 6 and k ~= "kw" and k ~= "Name" then
			C[k] = hex(v)
		end
	end
	for k, v in pairs(STD) do
		C[k] = hex(v)
	end
	return {Name = best, C = C, Title = title, Game = game, Font = font}
end

-----------------------------------------------------------------------------------------------
-- the kit (optional sprite sheets)
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
-- building blocks
-----------------------------------------------------------------------------------------------
local S -- current style (theme colours, font)

local function corner(parent, r)
	return new("UICorner", {CornerRadius = UDim.new(0, r or 10), Parent = parent})
end

local function stroke(parent, color, thick)
	return new("UIStroke", {Color = color, Thickness = thick or 3, ApplyStrokeMode = Enum.ApplyStrokeMode.Border,
		LineJoinMode = Enum.LineJoinMode.Round, Parent = parent})
end

local function label(parent, text, size, pos, textSize, props)
	props = props or {}
	local l = new("TextLabel", {
		Name = props.Name or "Label", Text = text, Size = size, Position = pos or UDim2.new(),
		AnchorPoint = props.AnchorPoint or Vector2.new(0, 0), BackgroundTransparency = 1, Font = S.Font,
		TextSize = textSize or 28, TextColor3 = props.Color or Color3.new(1, 1, 1),
		TextXAlignment = props.XAlign or Enum.TextXAlignment.Center, TextYAlignment = Enum.TextYAlignment.Center,
		ZIndex = props.ZIndex or 5, RichText = true, Parent = parent,
	})
	new("UIStroke", {Color = props.Stroke or Color3.fromRGB(15, 15, 25), Thickness = props.StrokeThickness or 2.5,
		LineJoinMode = Enum.LineJoinMode.Round, Parent = l})
	if props.Gradient then
		new("UIGradient", {Rotation = 90, Color = ColorSequence.new(props.Gradient[1], props.Gradient[2]), Parent = l})
	end
	return l
end

local function icon(parent, name, emoji, size, pos, anchor)
	local img, s = kitSprite("Icons", KIT_ICON[name] or name)
	if img then
		return new("ImageLabel", {Name = "Icon", Image = img, ImageRectOffset = Vector2.new(s[2], s[3]),
			ImageRectSize = Vector2.new(s[4], s[5]), Size = size, Position = pos, AnchorPoint = anchor or Vector2.new(0.5, 0.5),
			BackgroundTransparency = 1, ZIndex = 4, Parent = parent})
	end
	local l = new("TextLabel", {Name = "Icon", Text = emoji or "⭐", TextScaled = true, Font = Enum.Font.GothamBold,
		Size = size, Position = pos, AnchorPoint = anchor or Vector2.new(0.5, 0.5), BackgroundTransparency = 1,
		ZIndex = 4, Parent = parent})
	return l
end

-- a studded, glossy box: ImageButton (clickable) or Frame. sprite = kit sprite name for image mode
local function studBox(parent, name, color, size, pos, opts)
	opts = opts or {}
	local class = opts.Button and "ImageButton" or "Frame"
	local img, s = nil, nil
	if opts.Sprite then
		img, s = kitSprite("UI", opts.Sprite)
	end
	local o
	if img then
		o = new(opts.Button and "ImageButton" or "ImageLabel", {
			Name = name, Size = size, Position = pos, AnchorPoint = opts.AnchorPoint or Vector2.new(0, 0),
			BackgroundTransparency = 1, Image = img, ImageRectOffset = Vector2.new(s[2], s[3]),
			ImageRectSize = Vector2.new(s[4], s[5]), ScaleType = Enum.ScaleType.Slice,
			SliceCenter = Rect.new(s[6] or 12, s[7] or 12, s[4] - (s[8] or 12), s[5] - (s[9] or 12)),
			SliceScale = opts.SliceScale or 1, ZIndex = opts.ZIndex or 2, Parent = parent,
		})
		if opts.Button then
			o.AutoButtonColor = false
		end
		o:SetAttribute("Shine", opts.Shine ~= false)
		return o
	end
	o = new(class, {
		Name = name, Size = size, Position = pos, AnchorPoint = opts.AnchorPoint or Vector2.new(0, 0),
		BackgroundColor3 = color, BackgroundTransparency = opts.Transparency or 0, BorderSizePixel = 0,
		ZIndex = opts.ZIndex or 2, Parent = parent,
	})
	if opts.Button then
		o.Image = ""
		o.AutoButtonColor = false
	end
	corner(o, opts.Radius or 10)
	stroke(o, opts.Outline or darker(color, 0.6), opts.StrokeThickness or 3)
	new("UIGradient", {Rotation = 90, Color = ColorSequence.new({
		ColorSequenceKeypoint.new(0, lighter(color, opts.Light or 0.18)),
		ColorSequenceKeypoint.new(0.55, color),
		ColorSequenceKeypoint.new(1, darker(color, 0.12)),
	}), Parent = o})
	if opts.Lip ~= false then
		local lip = new("Frame", {Name = "Lip", Size = UDim2.new(1, 0, 0, 6), Position = UDim2.new(0, 0, 1, -6),
			BackgroundColor3 = darker(color, 0.35), BorderSizePixel = 0, ZIndex = (opts.ZIndex or 2), Parent = o})
		corner(lip, opts.Radius or 10)
	end
	local stud = kitImage("Stud")
	if stud and opts.Studs ~= false then
		local st = new("ImageLabel", {Name = "Studs", Image = stud, ScaleType = Enum.ScaleType.Tile,
			TileSize = UDim2.fromOffset(opts.StudSize or 22, opts.StudSize or 22), Size = UDim2.fromScale(1, 1),
			BackgroundTransparency = 1, ImageTransparency = opts.StudFade or 0.15, ZIndex = (opts.ZIndex or 2) + 1,
			Parent = o})
		corner(st, opts.Radius or 10)
	end
	if opts.Gloss ~= false then
		local g = new("Frame", {Name = "Gloss", Size = UDim2.new(1, -8, 0.46, 0), Position = UDim2.fromOffset(4, 3),
			BackgroundColor3 = Color3.new(1, 1, 1), BackgroundTransparency = 0.55, BorderSizePixel = 0,
			ZIndex = (opts.ZIndex or 2) + 1, Parent = o})
		corner(g, math.max(2, (opts.Radius or 10) - 3))
		new("UIGradient", {Rotation = 90, Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 0.35), NumberSequenceKeypoint.new(1, 1)}), Parent = g})
	end
	if opts.Shine ~= false then
		local sh = new("Frame", {Name = "Shine", Size = UDim2.fromScale(1, 1), BackgroundColor3 = Color3.new(1, 1, 1),
			BackgroundTransparency = 0, BorderSizePixel = 0, ZIndex = (opts.ZIndex or 2) + 2, Parent = o})
		corner(sh, opts.Radius or 10)
		new("UIGradient", {Rotation = 20, Offset = Vector2.new(-1, 0), Transparency = NumberSequence.new({
			NumberSequenceKeypoint.new(0, 1), NumberSequenceKeypoint.new(0.45, 1), NumberSequenceKeypoint.new(0.5, 0.55),
			NumberSequenceKeypoint.new(0.55, 1), NumberSequenceKeypoint.new(1, 1)}), Parent = sh})
		o:SetAttribute("Shine", true)
	end
	return o
end

local function button(parent, name, text, colorName, size, pos, opts)
	opts = opts or {}
	local c = S.C[colorName] or S.C.Green
	local spriteName = opts.Sprite or ("Button_" .. colorName)
	local b = studBox(parent, name, c, size, pos, {Button = true, Sprite = spriteName, AnchorPoint = opts.AnchorPoint,
		Radius = opts.Radius, ZIndex = opts.ZIndex})
	if text and text ~= "" then
		label(b, text, UDim2.new(1, -10, 1, -8), UDim2.fromOffset(5, 1), opts.TextSize or 30,
			{ZIndex = (opts.ZIndex or 2) + 4, Stroke = darker(c, 0.7)})
	end
	new("UIScale", {Name = "HoverScale", Parent = b})
	return b
end

local function bar(parent, name, frac, colorName, size, pos, text)
	local back = studBox(parent, name, Color3.fromRGB(30, 34, 48), size, pos, {Sprite = "Bar_Back", Radius = 99,
		Lip = false, Gloss = false, Shine = false, Studs = false, Outline = Color3.fromRGB(10, 12, 20)})
	local fill = studBox(back, "Fill", S.C[colorName] or S.C.Green, UDim2.fromScale(frac, 1), UDim2.new(),
		{Sprite = "Bar_Fill_" .. colorName, Radius = 99, Lip = false, ZIndex = 3, StudSize = 14})
	if text then
		label(back, text, UDim2.fromScale(1, 1), UDim2.new(), 20, {Name = "Text", ZIndex = 9})
	end
	return back, fill
end

local function slot(parent, name, rimColor, size, pos, order)
	local sprite = "Slot"
	local o = studBox(parent, name, Color3.fromRGB(34, 38, 52), size, pos, {Sprite = sprite, Radius = 10, Lip = false,
		Gloss = false, Shine = false, Studs = false, Outline = rimColor or Color3.fromRGB(70, 76, 96), StrokeThickness = 3,
		Button = true})
	if order then
		o.LayoutOrder = order
	end
	return o
end

-----------------------------------------------------------------------------------------------
-- windows
-----------------------------------------------------------------------------------------------
local RARITY = {{"Common", "B8C0CC"}, {"Uncommon", "56D63B"}, {"Rare", "2FA4FF"}, {"Epic", "A35CFF"},
	{"Legendary", "FFC21A"}, {"Mythic", "FF3B5C"}, {"Secret", "1C1C24"}}

local function window(parent, name, w, h)
	local win = new("Frame", {Name = name, Size = UDim2.fromOffset(w, h), Position = UDim2.fromScale(0.5, 0.5),
		AnchorPoint = Vector2.new(0.5, 0.5), BackgroundTransparency = 1, Visible = false, Parent = parent})
	new("UIScale", {Name = "PopScale", Parent = win})
	local body = studBox(win, "Body", darker(S.C.Panel2, 0.35), UDim2.new(1, 0, 1, -60), UDim2.fromOffset(0, 60),
		{Sprite = "Panel", Transparency = 0.12, Radius = 12, Lip = false, Gloss = false, Shine = false, StudFade = 0.7,
			Outline = S.C.Outline, ZIndex = 1})
	local header = studBox(win, "Header", S.C.Primary, UDim2.new(1, -76, 0, 68), UDim2.new(),
		{Sprite = "Header_Primary", Radius = 10, ZIndex = 3})
	icon(header, name, "✨", UDim2.fromOffset(56, 56), UDim2.fromOffset(38, 32))
	label(header, WINDOW_TITLES[name] or name, UDim2.new(1, -90, 1, -6), UDim2.fromOffset(74, 0), 38,
		{XAlign = Enum.TextXAlignment.Left, ZIndex = 8, Stroke = darker(S.C.Primary, 0.7)})
	local close = button(win, "Close", "X", "Red", UDim2.fromOffset(68, 68), UDim2.new(1, -68, 0, 0),
		{Sprite = "Close", TextSize = 40})
	close:SetAttribute("Closes", name)
	local content = new("Frame", {Name = "Content", Size = UDim2.new(1, -28, 1, -88), Position = UDim2.fromOffset(14, 74),
		BackgroundTransparency = 1, ZIndex = 3, Parent = win})
	return win, content
end

local function grid(parent, cell, pad, cols)
	local sf = new("ScrollingFrame", {Name = "List", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1,
		BorderSizePixel = 0, ScrollBarThickness = 8, ScrollBarImageColor3 = S.C.Inner,
		AutomaticCanvasSize = Enum.AutomaticSize.Y, CanvasSize = UDim2.new(), ZIndex = 3, Parent = parent})
	new("UIGridLayout", {CellSize = cell, CellPadding = UDim2.fromOffset(pad, pad), SortOrder = Enum.SortOrder.LayoutOrder,
		FillDirectionMaxCells = cols or 0, Parent = sf})
	new("UIPadding", {PaddingTop = UDim.new(0, 6), PaddingLeft = UDim.new(0, 6), PaddingRight = UDim.new(0, 12),
		Parent = sf})
	return sf
end

local CARD_COLORS = {{"Pink", "FF4FA0", "FF3B5C"}, {"Orange", "FF9A1F", "FFD21F"}, {"Purple", "A35CFF", "E04FD8"},
	{"Blue", "2F8BFF", "27D8E8"}, {"Green", "3FBF3A", "A6E23A"}, {"Gold", "FFB300", "FFE14D"}}
local SHOP_ITEMS = {{"Apple", "🍎", "Heart"}, {"Bananas", "🍌", "Energy"}, {"Cookie", "🍪", "Chest"},
	{"Blueberries", "🫐", "Gem"}, {"Speed Potion", "🧪", "PotionYellow"}, {"Luck Potion", "🍀", "PotionGreen"}}

local function buildShop(content)
	local list = new("Frame", {Name = "Items", Size = UDim2.new(1, 0, 1, -64), BackgroundTransparency = 1,
		Parent = content})
	local g = grid(list, UDim2.fromOffset(292, 150), 12, 2)
	for i, it in ipairs(SHOP_ITEMS) do
		local cc = CARD_COLORS[(i - 1) % #CARD_COLORS + 1]
		local card = studBox(g, it[1], hex(cc[2]), UDim2.fromOffset(292, 150), UDim2.new(),
			{Sprite = "Card_" .. cc[1], Radius = 12, ZIndex = 3})
		card.LayoutOrder = i
		local grad = card:FindFirstChildOfClass("UIGradient")
		if grad then
			grad.Rotation = 0
			grad.Color = ColorSequence.new(hex(cc[2]), hex(cc[3]))
		end
		label(card, it[1], UDim2.fromOffset(170, 34), UDim2.fromOffset(12, 8), 28,
			{XAlign = Enum.TextXAlignment.Left, ZIndex = 9})
		icon(card, it[3], it[2], UDim2.fromOffset(88, 88), UDim2.new(1, -56, 0, 56))
		icon(card, "Coin", "🪙", UDim2.fromOffset(30, 30), UDim2.fromOffset(28, 68))
		label(card, "3,412", UDim2.fromOffset(110, 30), UDim2.fromOffset(46, 53), 24,
			{XAlign = Enum.TextXAlignment.Left, ZIndex = 9, Name = "Price"})
		label(card, "+500 HP", UDim2.fromOffset(110, 24), UDim2.fromOffset(12, 112), 18,
			{XAlign = Enum.TextXAlignment.Left, ZIndex = 9})
		local buy = button(card, "Buy", "Buy", "Green", UDim2.fromOffset(120, 46), UDim2.new(1, -130, 1, -56),
			{TextSize = 26, ZIndex = 6})
		buy:SetAttribute("Action", "Buy")
	end
	local tabs = new("Frame", {Name = "Tabs", Size = UDim2.new(1, 0, 0, 52), Position = UDim2.new(0, 0, 1, -52),
		BackgroundTransparency = 1, Parent = content})
	new("UIListLayout", {FillDirection = Enum.FillDirection.Horizontal, Padding = UDim.new(0, 10), Parent = tabs})
	for i, t in ipairs({"Food", "Swords", "Boosts"}) do
		local tb = button(tabs, t, t, i == 1 and "Green" or "Gray", UDim2.fromOffset(190, 50), UDim2.new(),
			{Sprite = i == 1 and "Tab_Active" or "Tab_Inactive", TextSize = 24})
		tb.LayoutOrder = i
		tb:SetAttribute("Tab", t)
	end
end

local function buildPets(content)
	local top = new("Frame", {Name = "Top", Size = UDim2.new(1, 0, 0, 54), BackgroundTransparency = 1, Parent = content})
	label(top, "Equipped 3/5", UDim2.fromOffset(240, 50), UDim2.new(), 28, {XAlign = Enum.TextXAlignment.Left})
	button(top, "EquipBest", "Equip Best", "Green", UDim2.fromOffset(190, 50), UDim2.new(1, -390, 0, 0), {TextSize = 24})
	button(top, "Delete", "Delete", "Red", UDim2.fromOffset(180, 50), UDim2.new(1, -190, 0, 0), {TextSize = 24})
	local area = new("Frame", {Name = "Grid", Size = UDim2.new(1, 0, 1, -64), Position = UDim2.fromOffset(0, 64),
		BackgroundTransparency = 1, Parent = content})
	local g = grid(area, UDim2.fromOffset(110, 110), 10)
	for i = 1, 24 do
		local r = RARITY[(i - 1) % #RARITY + 1]
		local s = slot(g, "Pet" .. i, hex(r[2]), UDim2.fromOffset(110, 110), UDim2.new(), i)
		icon(s, "Pet", "🐶", UDim2.fromOffset(74, 74), UDim2.fromScale(0.5, 0.45))
		label(s, r[1], UDim2.new(1, 0, 0, 22), UDim2.new(0, 0, 1, -26), 16, {Color = hex(r[2]), ZIndex = 9})
	end
end

local function buildRebirth(content)
	label(content, "Rebirth to get <font color=\"#FFE14D\">x2 Coins</font> forever!", UDim2.new(1, 0, 0, 60),
		UDim2.fromOffset(0, 20), 34)
	icon(content, "Rebirth", "🔁", UDim2.fromOffset(150, 150), UDim2.new(0.5, 0, 0, 170))
	bar(content, "Progress", 0.62, "Gold", UDim2.new(1, -80, 0, 40), UDim2.new(0, 40, 0, 270), "62% (620K / 1M Coins)")
	local b = button(content, "RebirthButton", "Rebirth!", "Green", UDim2.fromOffset(300, 84), UDim2.new(0.5, -150, 1, -100),
		{TextSize = 40})
	b:SetAttribute("Action", "Rebirth")
end

local function buildSettings(content)
	local list = new("Frame", {Name = "List", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, Parent = content})
	new("UIListLayout", {Padding = UDim.new(0, 10), SortOrder = Enum.SortOrder.LayoutOrder, Parent = list})
	for i, name in ipairs({"Music", "Sound Effects", "Low Graphics", "Show Other Pets", "Auto Sell"}) do
		local row = studBox(list, name, darker(S.C.Panel2, 0.15), UDim2.new(1, 0, 0, 64), UDim2.new(),
			{Sprite = "PanelInner", Radius = 10, Lip = false, Gloss = false, Shine = false, Studs = false})
		row.LayoutOrder = i
		label(row, name, UDim2.new(1, -170, 1, 0), UDim2.fromOffset(18, 0), 28, {XAlign = Enum.TextXAlignment.Left})
		local on = i ~= 3
		local t = button(row, "Toggle", on and "ON" or "OFF", on and "Green" or "Gray", UDim2.fromOffset(120, 48),
			UDim2.new(1, -134, 0.5, -24), {Sprite = on and "Toggle_On" or "Toggle_Off", TextSize = 22})
		t:SetAttribute("Toggle", on)
	end
end

local function buildCodes(content)
	label(content, "Enter a code for free rewards!", UDim2.new(1, 0, 0, 50), UDim2.fromOffset(0, 20), 30)
	local box = studBox(content, "CodeBox", Color3.fromRGB(20, 22, 34), UDim2.new(1, -60, 0, 70), UDim2.new(0, 30, 0, 100),
		{Sprite = "Pill", Radius = 35, Lip = false, Gloss = false, Shine = false, Studs = false})
	new("TextBox", {Name = "Input", PlaceholderText = "Enter code...", Text = "", Font = S.Font, TextSize = 30,
		TextColor3 = Color3.new(1, 1, 1), PlaceholderColor3 = Color3.fromRGB(150, 156, 172), BackgroundTransparency = 1,
		Size = UDim2.new(1, -40, 1, 0), Position = UDim2.fromOffset(20, 0), ZIndex = 8, ClearTextOnFocus = false,
		Parent = box})
	local b = button(content, "Redeem", "Redeem", "Green", UDim2.fromOffset(260, 76), UDim2.new(0.5, -130, 0, 200),
		{TextSize = 34})
	b:SetAttribute("Action", "Redeem")
	label(content, "Follow the game for new codes!", UDim2.new(1, 0, 0, 40), UDim2.new(0, 0, 1, -50), 22,
		{Color = S.C.Inner})
end

local MUTATIONS = {{"None", "E1E4EB", "9AA0AC"}, {"Shocked", "FFE64A", "F0B814"}, {"Radioactive", "3CAA28", "1F6E14"},
	{"Molten", "FF7A2A", "C0280E"}, {"Icy", "BFEFFF", "7CC8F2"}, {"Golden", "FFE06A", "E0A010"}}

local function buildIndex(content)
	local left = new("Frame", {Name = "Mutations", Size = UDim2.new(0, 220, 1, -90), BackgroundTransparency = 1,
		Parent = content})
	label(left, "Mutation:", UDim2.new(1, 0, 0, 36), UDim2.new(), 26, {XAlign = Enum.TextXAlignment.Left})
	for i, m in ipairs(MUTATIONS) do
		local b = studBox(left, m[1], hex(m[2]), UDim2.new(1, -10, 0, 52), UDim2.fromOffset(0, 44 + (i - 1) * 60),
			{Button = true, Sprite = "Mutation_" .. m[1], Radius = 8})
		local grad = b:FindFirstChildOfClass("UIGradient")
		if grad then
			grad.Color = ColorSequence.new(hex(m[2]), hex(m[3]))
		end
		label(b, m[1], UDim2.fromScale(1, 1), UDim2.new(), 26, {ZIndex = 9})
		b:SetAttribute("Mutation", m[1])
	end
	local right = new("Frame", {Name = "Collection", Size = UDim2.new(1, -236, 1, -90), Position = UDim2.fromOffset(236, 0),
		BackgroundTransparency = 1, Parent = content})
	local g = grid(right, UDim2.fromOffset(128, 128), 10)
	for i = 1, 16 do
		local s = slot(g, "Entry" .. i, Color3.fromRGB(70, 76, 96), UDim2.fromOffset(128, 128), UDim2.new(), i)
		local known = i % 3 ~= 0
		icon(s, "Pet", known and "🐡" or "❔", UDim2.fromOffset(78, 78), UDim2.fromScale(0.5, 0.48))
		label(s, known and "Puffer" or "???", UDim2.new(1, 0, 0, 24), UDim2.new(0, 0, 1, -28), 20, {ZIndex = 9})
		label(s, i == 16 and "0.1%" or "50%", UDim2.fromOffset(60, 22), UDim2.new(1, -64, 0, 4), 18,
			{Color = hex(({"FFE14D", "56D63B", "2FA4FF", "A35CFF"})[i % 4 + 1]), ZIndex = 9})
		label(s, "M", UDim2.fromOffset(24, 22), UDim2.fromOffset(6, 4), 18, {Color = hex("F0443A"), ZIndex = 9})
	end
	local foot = studBox(content, "Reward", darker(S.C.Panel2, 0.2), UDim2.new(1, 0, 0, 78), UDim2.new(0, 0, 1, -78),
		{Sprite = "PanelInner", Radius = 10, Lip = false, Gloss = false, Shine = false, Studs = false})
	label(foot, "Catch every <font color=\"#FF7A2A\">Molten</font> variant for a Final Prize!", UDim2.new(1, -110, 0, 32),
		UDim2.fromOffset(14, 4), 24, {XAlign = Enum.TextXAlignment.Left})
	bar(foot, "Progress", 0.65, "Green", UDim2.new(1, -120, 0, 26), UDim2.fromOffset(14, 42), "65%")
	icon(foot, "Gift", "🎁", UDim2.fromOffset(64, 64), UDim2.new(1, -48, 0.5, 0))
end

local function buildDaily(content)
	local g = grid(content, UDim2.fromOffset(140, 170), 12, 4)
	local rewards = {{"Coin", "🪙", "500"}, {"Gem", "💎", "25"}, {"Coin", "🪙", "2K"}, {"PotionGreen", "🍀", "x2 Luck"},
		{"Gem", "💎", "100"}, {"Egg", "🥚", "Egg"}, {"Chest", "🎁", "Mega"}}
	for i, r in ipairs(rewards) do
		local c = studBox(g, "Day" .. i, i == 7 and S.C.Gold or S.C.Primary, UDim2.fromOffset(140, 170), UDim2.new(),
			{Button = true, Sprite = i == 7 and "Card_Gold" or "Card_Blue", Radius = 12})
		c.LayoutOrder = i
		label(c, "Day " .. i, UDim2.new(1, 0, 0, 34), UDim2.fromOffset(0, 6), 26, {ZIndex = 9})
		icon(c, r[1], r[2], UDim2.fromOffset(78, 78), UDim2.fromScale(0.5, 0.5))
		label(c, r[3], UDim2.new(1, 0, 0, 30), UDim2.new(0, 0, 1, -38), 24, {ZIndex = 9})
		c:SetAttribute("Day", i)
	end
end

local function buildQuests(content)
	local list = new("Frame", {Name = "List", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, Parent = content})
	new("UIListLayout", {Padding = UDim.new(0, 12), Parent = list})
	for i, q in ipairs({{"Collect 1,000 Coins", 0.7}, {"Hatch 5 Eggs", 0.4}, {"Rebirth once", 1.0}}) do
		local row = studBox(list, "Quest" .. i, darker(S.C.Panel2, 0.15), UDim2.new(1, 0, 0, 96), UDim2.new(),
			{Sprite = "PanelInner", Radius = 10, Lip = false, Gloss = false, Shine = false, Studs = false})
		row.LayoutOrder = i
		label(row, q[1], UDim2.new(1, -200, 0, 40), UDim2.fromOffset(16, 6), 28, {XAlign = Enum.TextXAlignment.Left})
		bar(row, "Progress", q[2], "Gold", UDim2.new(1, -220, 0, 30), UDim2.fromOffset(16, 52),
			math.floor(q[2] * 100) .. "%")
		local b = button(row, "Claim", q[2] >= 1 and "Claim" or "Go", q[2] >= 1 and "Green" or "Blue",
			UDim2.fromOffset(160, 64), UDim2.new(1, -176, 0.5, -34), {TextSize = 28})
		b:SetAttribute("Action", "ClaimQuest")
	end
end

local WINDOW_BUILDERS = {Shop = buildShop, Pets = buildPets, Rebirth = buildRebirth, Settings = buildSettings,
	Codes = buildCodes, Index = buildIndex, DailyRewards = buildDaily, Quests = buildQuests}
local WINDOW_SIZES = {Shop = {640, 560}, Pets = {680, 560}, Rebirth = {560, 480}, Settings = {560, 470},
	Codes = {560, 400}, Index = {860, 600}, DailyRewards = {640, 520}, Quests = {640, 460}}

-----------------------------------------------------------------------------------------------
-- HUD
-----------------------------------------------------------------------------------------------
local function cluster(root, name, anchor, pos, size)
	local f = new("Frame", {Name = name, AnchorPoint = anchor, Position = pos, Size = UDim2.fromOffset(size[1], size[2]),
		BackgroundTransparency = 1, Parent = root})
	local sc = new("UIScale", {Name = "AutoScale", Parent = f})
	sc:SetAttribute("AutoScale", true)
	return f
end

local function sideButton(parent, entry, y, order)
	local name, colorName, emoji = entry[1], entry[2], entry[3]
	local b = studBox(parent, name, S.C[colorName] or S.C.Primary, UDim2.fromOffset(104, 104), UDim2.fromOffset(0, y),
		{Button = true, Sprite = "Square_" .. colorName, Radius = 14})
	icon(b, name, emoji, UDim2.fromOffset(84, 84), UDim2.fromScale(0.5, 0.44))
	label(b, WINDOW_TITLES[name] or name, UDim2.new(1, 30, 0, 34), UDim2.new(0, -15, 1, -30), 28, {ZIndex = 9})
	new("UIScale", {Name = "HoverScale", Parent = b})
	if WINDOW_BUILDERS[name] then
		b:SetAttribute("Opens", name)
	end
	return b
end

local function buildHUD(root, L)
	-- top tabs
	if #L.top > 0 then
		local top = cluster(root, "Top", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 16), {#L.top * 250, 96})
		for i, t in ipairs(L.top) do
			local b = button(top, t[1]:gsub(" ", ""), t[1], t[2], UDim2.fromOffset(236, 84), UDim2.fromOffset((i - 1) * 250, 0),
				{TextSize = 40})
			if WINDOW_BUILDERS[t[1]] then
				b:SetAttribute("Opens", t[1])
			end
		end
	end
	if S.Title then
		local tf = cluster(root, "Logo", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, #L.top > 0 and 108 or 16), {700, 70})
		local img, s = kitSprite("Titles", "LOGO")
		if img then
			new("ImageLabel", {Name = "Logo", Image = img, ImageRectOffset = Vector2.new(s[2], s[3]),
				ImageRectSize = Vector2.new(s[4], s[5]), Size = UDim2.fromOffset(s[4] * 70 / s[5], 70),
				Position = UDim2.fromScale(0.5, 0), AnchorPoint = Vector2.new(0.5, 0), BackgroundTransparency = 1, Parent = tf})
		else
			label(tf, S.Title, UDim2.fromScale(1, 1), UDim2.new(), 52, {Gradient = {S.C.TitleTop, S.C.TitleBottom},
				Stroke = S.C.Outline, StrokeThickness = 4})
		end
	end
	-- left menu
	if #L.left > 0 then
		local left = cluster(root, "Left", Vector2.new(0, 0.5), UDim2.new(0, 24, 0.5, 0), {104, #L.left * 128})
		for i, e in ipairs(L.left) do
			sideButton(left, e, (i - 1) * 128, i)
		end
	end
	-- right column: menu buttons, starter pack, quests, luck
	local rightH = #L.right * 128 + (L.quests and 200 or 0) + (L.luck and 130 or 0) + 150
	local right = cluster(root, "Right", Vector2.new(1, 0.5), UDim2.new(1, -24, 0.5, 0), {260, rightH})
	local y = 0
	for i, e in ipairs(L.right) do
		local b = sideButton(right, e, y, i)
		b.Position = UDim2.new(1, -104, 0, y)
		y = y + 128
	end
	local pack = new("ImageButton", {Name = "StarterPack", Image = "", BackgroundTransparency = 1,
		Size = UDim2.fromOffset(150, 140), Position = UDim2.new(1, -150, 0, y), Parent = right})
	icon(pack, "Gift", "🎁", UDim2.fromOffset(100, 100), UDim2.fromScale(0.5, 0.45))
	label(pack, "Starter Pack", UDim2.new(1, 20, 0, 30), UDim2.new(0, -10, 1, -30), 24, {Color = hex("78DCFF")})
	label(pack, "R$ 99", UDim2.new(1, 0, 0, 30), UDim2.new(), 26, {Color = hex("56D63B")})
	pack:SetAttribute("Action", "StarterPack")
	y = y + 150
	if L.quests then
		label(right, "Daily Quests!", UDim2.new(1, 0, 0, 40), UDim2.fromOffset(0, y), 34,
			{Gradient = {hex("FFF3A0"), hex("FFB300")}, Stroke = hex("462800")})
		for i = 1, 2 do
			label(right, "Quest description", UDim2.new(1, 0, 0, 26), UDim2.fromOffset(0, y + 38 + (i - 1) * 76), 22)
			bar(right, "Quest" .. i, i == 1 and 0.6 or 1, "Gold", UDim2.new(1, 0, 0, 26),
				UDim2.fromOffset(0, y + 66 + (i - 1) * 76), i == 2 and "CLAIM" or nil)
		end
		y = y + 200
	end
	if L.luck then
		icon(right, "Luck", "🍀", UDim2.fromOffset(80, 80), UDim2.new(1, -75, 0, y + 70))
		label(right, "x2 Luck", UDim2.fromOffset(150, 34), UDim2.new(1, -150, 0, y), 30, {Color = hex("A6FF5A")})
		label(right, "00:00", UDim2.fromOffset(150, 28), UDim2.new(1, -150, 0, y + 106), 24,
			{Color = hex("FF5A5A"), Name = "LuckTimer"})
	end
	-- currencies (bottom left)
	if #L.currencies > 0 then
		local bl = cluster(root, "Currencies", Vector2.new(0, 1), UDim2.new(0, 24, 1, -24), {420, #L.currencies * 64})
		for i, c in ipairs(L.currencies) do
			local yy = (i - 1) * 64
			icon(bl, c[1], c[2], UDim2.fromOffset(58, 58), UDim2.fromOffset(30, yy + 30))
			local col = c[1] == "Cash" and hex("6EE650") or Color3.new(1, 1, 1)
			label(bl, (c[1] == "Cash" and "$" or "") .. "0", UDim2.fromOffset(280, 56), UDim2.fromOffset(66, yy + 2), 44,
				{XAlign = Enum.TextXAlignment.Left, Color = col, Name = c[1], ZIndex = 6})
			local plus = button(bl, "Buy" .. c[1], "+", "Green", UDim2.fromOffset(44, 44), UDim2.fromOffset(360, yy + 8),
				{Sprite = "Plus", TextSize = 36})
			plus:SetAttribute("Opens", "Shop")
		end
	end
	-- hotbar + level bar (bottom centre)
	if L.hotbar > 0 or L.level then
		local n = math.max(L.hotbar, 1)
		local bc = cluster(root, "Hotbar", Vector2.new(0.5, 1), UDim2.new(0.5, 0, 1, -16), {math.max(n * 84, 640), 150})
		if L.hotbar > 0 then
			label(bc, "(F) Open Inventory", UDim2.new(1, 0, 0, 30), UDim2.new(), 26)
			for i = 1, L.hotbar do
				local s = slot(bc, "Slot" .. i, Color3.fromRGB(70, 76, 96), UDim2.fromOffset(76, 76),
					UDim2.new(0.5, (i - 1 - L.hotbar / 2) * 84 + 4, 0, 36), i)
				label(s, tostring(i), UDim2.fromOffset(20, 20), UDim2.fromOffset(4, 2), 20, {ZIndex = 9})
				label(s, "Name", UDim2.new(1, 0, 0, 20), UDim2.new(0, 0, 1, -24), 18, {ZIndex = 9})
				s:SetAttribute("Slot", i)
			end
		end
		if L.level then
			bar(bc, "Level", 0.56, "Green", UDim2.new(1, 0, 0, 26), UDim2.new(0, 0, 1, -28), "Lv. 25  56%")
		end
	end
	-- health / xp (fighting, horror, rpg)
	if L.health then
		local hp = cluster(root, "Health", Vector2.new(0, 0), UDim2.fromOffset(24, 24), {420, 90})
		bar(hp, "Health", 0.8, "Red", UDim2.fromOffset(420, 38), UDim2.new(), "100 / 100")
		if L.level then
			bar(hp, "XP", 0.35, "Blue", UDim2.fromOffset(420, 28), UDim2.fromOffset(0, 50), "XP 350 / 1000")
		end
	end
	if L.stage then
		local st = cluster(root, "Stage", Vector2.new(0.5, 0), UDim2.new(0.5, 0, 0, 110), {400, 70})
		label(st, "Stage 1", UDim2.fromScale(1, 1), UDim2.new(), 56, {Gradient = {S.C.TitleTop, S.C.TitleBottom},
			Stroke = S.C.Outline, StrokeThickness = 4, Name = "StageLabel"})
	end
	-- boosts (bottom right)
	if L.boosts then
		local br = cluster(root, "Boosts", Vector2.new(1, 1), UDim2.new(1, -24, 1, -24), {5 * 86, 90})
		local boosts = {{"Yellow", "PotionYellow", "⚡"}, {"Green", "PotionGreen", "🍀"}, {"Cyan", "PotionBlue", "💧"},
			{"Purple", "PotionRed", "❤️"}, {"Red", "Boost", "🔥"}}
		for i, bst in ipairs(boosts) do
			local t = studBox(br, "Boost" .. i, S.C[bst[1]], UDim2.fromOffset(78, 78), UDim2.fromOffset((i - 1) * 86, 0),
				{Sprite = "Square_" .. (bst[1] == "Cyan" and "Blue" or bst[1] == "Red" and "Primary" or bst[1]), Radius = 10})
			icon(t, bst[2], bst[3], UDim2.fromOffset(58, 58), UDim2.fromScale(0.5, 0.42))
			label(t, "59m", UDim2.new(1, 0, 0, 24), UDim2.new(0, 0, 1, -26), 22, {ZIndex = 9, Name = "Timer"})
		end
	end
end

-----------------------------------------------------------------------------------------------
-- the LocalScript that makes it all work in game
-----------------------------------------------------------------------------------------------
local CONTROLLER = [==[
-- SimUI controller (generated). Opens/closes windows, animates buttons, scales the UI,
-- sweeps the shine and shows leaderstats (Coins / Gems / Cash / Gold) in the counters.
local TweenService = game:GetService("TweenService")
local Players = game:GetService("Players")
local gui = script.Parent
local root = gui:WaitForChild("Root")
local windows = root:WaitForChild("Windows")
local camera = workspace.CurrentCamera

local function rescale()
	local v = camera.ViewportSize
	local s = math.clamp(math.min(v.X / 1920, v.Y / 1080), 0.42, 1.4)
	for _, d in ipairs(root:GetDescendants()) do
		if d:IsA("UIScale") and d:GetAttribute("AutoScale") then
			d.Scale = s
		end
	end
end
camera:GetPropertyChangedSignal("ViewportSize"):Connect(rescale)
rescale()

local current = nil
local function close(name)
	local w = windows:FindFirstChild(name)
	if not w then return end
	local sc = w:FindFirstChild("PopScale")
	local t = TweenService:Create(sc, TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {Scale = 0.6})
	t:Play()
	t.Completed:Wait()
	w.Visible = false
	if current == name then current = nil end
end
local function open(name)
	if current == name then close(name) return end
	if current then close(current) end
	local w = windows:FindFirstChild(name)
	if not w then return end
	local sc = w:FindFirstChild("PopScale")
	sc.Scale = 0.6
	w.Visible = true
	current = name
	TweenService:Create(sc, TweenInfo.new(0.25, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {Scale = 1}):Play()
end

for _, b in ipairs(root:GetDescendants()) do
	if b:IsA("GuiButton") then
		local hover = b:FindFirstChild("HoverScale")
		if hover then
			b.MouseEnter:Connect(function()
				TweenService:Create(hover, TweenInfo.new(0.12), {Scale = 1.08}):Play()
			end)
			b.MouseLeave:Connect(function()
				TweenService:Create(hover, TweenInfo.new(0.12), {Scale = 1}):Play()
			end)
			b.MouseButton1Down:Connect(function()
				TweenService:Create(hover, TweenInfo.new(0.06), {Scale = 0.92}):Play()
			end)
			b.MouseButton1Up:Connect(function()
				TweenService:Create(hover, TweenInfo.new(0.1), {Scale = 1.08}):Play()
			end)
		end
		b.Activated:Connect(function()
			local o = b:GetAttribute("Opens")
			local c = b:GetAttribute("Closes")
			if o then open(o) elseif c then close(c) end
		end)
	end
end

-- shine sweep across buttons every few seconds
task.spawn(function()
	while gui.Parent do
		for _, d in ipairs(root:GetDescendants()) do
			if d.Name == "Shine" and d:IsA("Frame") and d.Visible then
				local g = d:FindFirstChildOfClass("UIGradient")
				if g then
					g.Offset = Vector2.new(-1, 0)
					TweenService:Create(g, TweenInfo.new(0.9, Enum.EasingStyle.Quad), {Offset = Vector2.new(1, 0)}):Play()
				end
			end
		end
		task.wait(3.5)
	end
end)

-- currencies from leaderstats
local function short(n)
	local s = tostring(math.floor(n))
	local out = s:reverse():gsub("(%d%d%d)", "%1,"):reverse()
	return out:gsub("^,", "")
end
local player = Players.LocalPlayer
task.spawn(function()
	local stats = player:WaitForChild("leaderstats", 30)
	if not stats then return end
	local cur = root:FindFirstChild("Currencies")
	if not cur then return end
	for _, v in ipairs(stats:GetChildren()) do
		local lbl = cur:FindFirstChild(v.Name)
		if lbl and lbl:IsA("TextLabel") and (v:IsA("IntValue") or v:IsA("NumberValue")) then
			local prefix = v.Name == "Cash" and "$" or ""
			local function upd() lbl.Text = prefix .. short(v.Value) end
			v.Changed:Connect(upd)
			upd()
		end
	end
end)
]==]

-----------------------------------------------------------------------------------------------
-- build
-----------------------------------------------------------------------------------------------
local function build(prompt)
	loadKit()
	local p = parsePrompt(prompt)
	S = {C = p.C, Font = p.Font, Title = p.Title}
	if Kit and Kit.Theme and kitImage("UI") then
		-- a generated kit carries its own colours: use them so images and native bits match
		for k, v in pairs(Kit.Theme) do
			if typeof(v) == "Color3" then
				S.C[k] = v
			end
		end
	end
	local L = LAYOUTS[p.Game] or LAYOUTS.simulator
	local old = StarterGui:FindFirstChild("SimUI")
	if old then
		old:Destroy()
	end
	local gui = new("ScreenGui", {Name = "SimUI", ResetOnSpawn = false, IgnoreGuiInset = true,
		ZIndexBehavior = Enum.ZIndexBehavior.Sibling})
	gui:SetAttribute("Prompt", prompt)
	gui:SetAttribute("Theme", p.Name)
	gui:SetAttribute("GameType", p.Game)
	local root = new("Frame", {Name = "Root", Size = UDim2.fromScale(1, 1), BackgroundTransparency = 1, Parent = gui})
	buildHUD(root, L)
	local wins = cluster(root, "Windows", Vector2.new(0.5, 0.5), UDim2.fromScale(0.5, 0.5), {1, 1})
	local wanted = {}
	for _, e in ipairs(L.left) do wanted[e[1]] = true end
	for _, e in ipairs(L.right) do wanted[e[1]] = true end
	for _, e in ipairs(L.top) do wanted[e[1]] = true end
	if #L.currencies > 0 then wanted.Shop = true end
	for name, fn in pairs(WINDOW_BUILDERS) do
		if wanted[name] then
			local sz = WINDOW_SIZES[name]
			local w, content = window(wins, name, sz[1], sz[2])
			fn(content)
		end
	end
	local ctrl = new("LocalScript", {Name = "SimUIController"})
	ctrl.Source = CONTROLLER
	ctrl.Parent = gui
	gui.Parent = StarterGui
	ChangeHistoryService:SetWaypoint("SimUI build")
	print(("SimUI: built %s UI with the %s theme%s%s"):format(p.Game, p.Name, p.Title and (' - "' .. p.Title .. '"') or "",
		Kit and kitImage("UI") and " (kit images)" or " (native)"))
	return gui
end

-----------------------------------------------------------------------------------------------
-- plugin UI (or run straight away from the Command Bar)
-----------------------------------------------------------------------------------------------
if plugin then
	local toolbar = plugin:CreateToolbar("SimUI")
	local tbButton = toolbar:CreateButton("SimUI", "Generate a studs-style game UI from a prompt", "")
	local info = DockWidgetPluginGuiInfo.new(Enum.InitialDockState.Float, false, false, 380, 470, 320, 380)
	local widget = plugin:CreateDockWidgetPluginGui("SimUIGenerator", info)
	widget.Title = "SimUI Generator"
	local bg = new("Frame", {Size = UDim2.fromScale(1, 1), BackgroundColor3 = Color3.fromRGB(28, 31, 44), Parent = widget})
	new("UIPadding", {PaddingTop = UDim.new(0, 10), PaddingLeft = UDim.new(0, 10), PaddingRight = UDim.new(0, 10),
		Parent = bg})
	new("UIListLayout", {Padding = UDim.new(0, 8), SortOrder = Enum.SortOrder.LayoutOrder, Parent = bg})
	local function t(text, order, size)
		return new("TextLabel", {Text = text, Size = UDim2.new(1, 0, 0, size or 22), BackgroundTransparency = 1,
			Font = Enum.Font.GothamBold, TextSize = 14, TextColor3 = Color3.fromRGB(230, 234, 245), TextWrapped = true,
			TextXAlignment = Enum.TextXAlignment.Left, LayoutOrder = order, Parent = bg})
	end
	t("Describe your game (theme words, game type, \"title in quotes\"):", 1, 34)
	local box = new("TextBox", {Text = PROMPT, Size = UDim2.new(1, 0, 0, 60), BackgroundColor3 = Color3.fromRGB(16, 18, 28),
		TextColor3 = Color3.new(1, 1, 1), Font = Enum.Font.Gotham, TextSize = 15, TextWrapped = true, ClearTextOnFocus = false,
		TextXAlignment = Enum.TextXAlignment.Left, LayoutOrder = 2, Parent = bg})
	corner(box, 8)
	new("UIPadding", {PaddingLeft = UDim.new(0, 8), PaddingRight = UDim.new(0, 8), Parent = box})
	t("Quick themes:", 3)
	local chips = new("Frame", {Size = UDim2.new(1, 0, 0, 150), BackgroundTransparency = 1, LayoutOrder = 4, Parent = bg})
	new("UIGridLayout", {CellSize = UDim2.fromOffset(84, 26), CellPadding = UDim2.fromOffset(6, 6), Parent = chips})
	for _, name in ipairs(THEME_ORDER) do
		local th = THEMES[name]
		local c = new("TextButton", {Text = name, Font = Enum.Font.GothamBold, TextSize = 13, TextColor3 = Color3.new(1, 1, 1),
			BackgroundColor3 = hex(th.Primary), Parent = chips})
		corner(c, 6)
		new("UIStroke", {Color = hex(th.Outline), Thickness = 1.5, ApplyStrokeMode = Enum.ApplyStrokeMode.Border, Parent = c})
		c.MouseButton1Click:Connect(function()
			local title = box.Text:match('"[^"]+"') or ""
			local g = "simulator"
			for _, gt in ipairs(GAME_TYPES) do
				if box.Text:lower():find(gt[1]) then g = gt[1] end
			end
			box.Text = (title ~= "" and (title .. " ") or "") .. name:lower() .. " " .. g
		end)
	end
	local go = new("TextButton", {Text = "Build UI", Size = UDim2.new(1, 0, 0, 44), BackgroundColor3 = hex("56D63B"),
		Font = Enum.Font.FredokaOne, TextSize = 24, TextColor3 = Color3.new(1, 1, 1), LayoutOrder = 5, Parent = bg})
	corner(go, 10)
	new("UIStroke", {Color = hex("1F5A12"), Thickness = 2, ApplyStrokeMode = Enum.ApplyStrokeMode.Border, Parent = go})
	local status = t("Game types: simulator, tycoon, obby, fighting, horror, racing, rpg", 6, 40)
	go.MouseButton1Click:Connect(function()
		local ok, err = pcall(build, box.Text)
		status.Text = ok and "Built StarterGui > SimUI. Press Play to try it!" or ("Error: " .. tostring(err))
	end)
	tbButton.Click:Connect(function()
		widget.Enabled = not widget.Enabled
	end)
else
	build(PROMPT)
end
