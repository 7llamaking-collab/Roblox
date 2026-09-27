--!nocheck
-- A small stand-in for the Roblox engine, so the SimUI plugin can be run and checked outside Studio.
-- It covers the datatypes, Instance classes, enums and services the plugin and its controller use,
-- and it errors like Studio does on unknown properties, unknown enum items and bad values.
-- Used by ui/sim/run.py (Luau CLI): the plugin runs for real, then the UI tree is printed as JSON.

local SHIM = {}
local rawtypeof = typeof

---------------------------------------------------------------------------------------------------
-- datatypes
---------------------------------------------------------------------------------------------------
local function dtype(name)
	local mt = {__type = name}
	mt.__index = mt
	return mt
end

local function isType(v, name)
	return typeof(v) == name
end

typeof = function(v)
	if type(v) == "table" then
		local mt = getmetatable(v)
		if type(mt) == "table" and rawget(mt, "__type") then
			return rawget(mt, "__type")
		end
	end
	return rawtypeof(v)
end

local function num(v, what)
	if type(v) ~= "number" then
		error(("%s expected a number, got %s"):format(what, typeof(v)), 3)
	end
	return v
end

-- UDim
local UDimMT = dtype("UDim")
UDim = {}
function UDim.new(s, o)
	return setmetatable({Scale = s or 0, Offset = o or 0}, UDimMT)
end
UDimMT.__add = function(a, b) return UDim.new(a.Scale + b.Scale, a.Offset + b.Offset) end
UDimMT.__sub = function(a, b) return UDim.new(a.Scale - b.Scale, a.Offset - b.Offset) end
UDimMT.__eq = function(a, b) return a.Scale == b.Scale and a.Offset == b.Offset end
UDimMT.__tostring = function(a) return ("%g, %g"):format(a.Scale, a.Offset) end

-- UDim2
local UDim2MT = dtype("UDim2")
UDim2 = {}
function UDim2.new(a, b, c, d)
	if isType(a, "UDim") then
		return setmetatable({X = a, Y = b, Width = a, Height = b}, UDim2MT)
	end
	local x, y = UDim.new(a or 0, b or 0), UDim.new(c or 0, d or 0)
	return setmetatable({X = x, Y = y, Width = x, Height = y}, UDim2MT)
end
function UDim2.fromOffset(x, y) return UDim2.new(0, x or 0, 0, y or 0) end
function UDim2.fromScale(x, y) return UDim2.new(x or 0, 0, y or 0, 0) end
UDim2MT.__add = function(a, b) return UDim2.new(a.X + b.X, a.Y + b.Y) end
UDim2MT.__sub = function(a, b) return UDim2.new(a.X - b.X, a.Y - b.Y) end
UDim2MT.__eq = function(a, b) return a.X == b.X and a.Y == b.Y end
UDim2MT.__tostring = function(a) return ("{%s}, {%s}"):format(tostring(a.X), tostring(a.Y)) end
function UDim2MT.Lerp(a, b, t)
	return UDim2.new(a.X.Scale + (b.X.Scale - a.X.Scale) * t, a.X.Offset + (b.X.Offset - a.X.Offset) * t,
		a.Y.Scale + (b.Y.Scale - a.Y.Scale) * t, a.Y.Offset + (b.Y.Offset - a.Y.Offset) * t)
end

-- Vector2
local Vector2MT = dtype("Vector2")
Vector2 = {}
function Vector2.new(x, y)
	x, y = x or 0, y or 0
	return setmetatable({X = x, Y = y, Magnitude = math.sqrt(x * x + y * y)}, Vector2MT)
end
Vector2.zero = Vector2.new(0, 0)
Vector2.one = Vector2.new(1, 1)
Vector2.xAxis = Vector2.new(1, 0)
Vector2.yAxis = Vector2.new(0, 1)
Vector2MT.__add = function(a, b) return Vector2.new(a.X + b.X, a.Y + b.Y) end
Vector2MT.__sub = function(a, b) return Vector2.new(a.X - b.X, a.Y - b.Y) end
Vector2MT.__mul = function(a, b)
	if type(a) == "number" then return Vector2.new(a * b.X, a * b.Y) end
	if type(b) == "number" then return Vector2.new(a.X * b, a.Y * b) end
	return Vector2.new(a.X * b.X, a.Y * b.Y)
end
Vector2MT.__div = function(a, b)
	if type(b) == "number" then return Vector2.new(a.X / b, a.Y / b) end
	return Vector2.new(a.X / b.X, a.Y / b.Y)
end
Vector2MT.__unm = function(a) return Vector2.new(-a.X, -a.Y) end
Vector2MT.__eq = function(a, b) return a.X == b.X and a.Y == b.Y end
Vector2MT.__tostring = function(a) return ("%g, %g"):format(a.X, a.Y) end
function Vector2MT.Lerp(a, b, t) return Vector2.new(a.X + (b.X - a.X) * t, a.Y + (b.Y - a.Y) * t) end
function Vector2MT.Dot(a, b) return a.X * b.X + a.Y * b.Y end

-- Color3
local Color3MT = dtype("Color3")
Color3 = {}
function Color3.new(r, g, b)
	return setmetatable({R = r or 0, G = g or 0, B = b or 0}, Color3MT)
end
function Color3.fromRGB(r, g, b)
	num(r, "Color3.fromRGB")
	return Color3.new(math.clamp(r, 0, 255) / 255, math.clamp(g or 0, 0, 255) / 255, math.clamp(b or 0, 0, 255) / 255)
end
function Color3.fromHex(h)
	h = h:gsub("#", "")
	if #h ~= 6 then
		error("Unable to convert characters to hex value", 2)
	end
	return Color3.fromRGB(tonumber(h:sub(1, 2), 16), tonumber(h:sub(3, 4), 16), tonumber(h:sub(5, 6), 16))
end
function Color3.fromHSV(h, s, v)
	h = (h % 1) * 6
	local i = math.floor(h)
	local f = h - i
	local p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
	local r, g, b
	if i == 0 then r, g, b = v, t, p
	elseif i == 1 then r, g, b = q, v, p
	elseif i == 2 then r, g, b = p, v, t
	elseif i == 3 then r, g, b = p, q, v
	elseif i == 4 then r, g, b = t, p, v
	else r, g, b = v, p, q end
	return Color3.new(r, g, b)
end
function Color3.toHSV(c)
	local r, g, b = c.R, c.G, c.B
	local mx, mn = math.max(r, g, b), math.min(r, g, b)
	local d = mx - mn
	local h = 0
	if d > 0 then
		if mx == r then h = ((g - b) / d) % 6
		elseif mx == g then h = (b - r) / d + 2
		else h = (r - g) / d + 4 end
		h = h / 6
	end
	return h, mx > 0 and d / mx or 0, mx
end
Color3MT.ToHSV = Color3.toHSV
function Color3MT.Lerp(a, b, t)
	if not isType(b, "Color3") then error("Color3:Lerp expects a Color3", 2) end
	return Color3.new(a.R + (b.R - a.R) * t, a.G + (b.G - a.G) * t, a.B + (b.B - a.B) * t)
end
function Color3MT.ToHex(c)
	return ("%02X%02X%02X"):format(math.floor(c.R * 255 + 0.5), math.floor(c.G * 255 + 0.5), math.floor(c.B * 255 + 0.5))
end
Color3MT.__eq = function(a, b) return a.R == b.R and a.G == b.G and a.B == b.B end
Color3MT.__tostring = function(c) return ("%g, %g, %g"):format(c.R, c.G, c.B) end

-- sequences
local CSKMT = dtype("ColorSequenceKeypoint")
ColorSequenceKeypoint = {}
function ColorSequenceKeypoint.new(t, c)
	if not isType(c, "Color3") then error("ColorSequenceKeypoint.new expects a Color3", 2) end
	return setmetatable({Time = t, Value = c}, CSKMT)
end
local CSMT = dtype("ColorSequence")
ColorSequence = {}
function ColorSequence.new(a, b)
	local kps
	if isType(a, "Color3") then
		kps = {ColorSequenceKeypoint.new(0, a), ColorSequenceKeypoint.new(1, b or a)}
	elseif type(a) == "table" then
		kps = a
		if #kps < 2 or kps[1].Time ~= 0 or kps[#kps].Time ~= 1 then
			error("ColorSequence: the first keypoint must be at time 0 and the last at time 1", 2)
		end
		for i = 2, #kps do
			if kps[i].Time < kps[i - 1].Time then error("ColorSequence: keypoints must be in order", 2) end
		end
	else
		error("ColorSequence.new: bad arguments", 2)
	end
	return setmetatable({Keypoints = kps}, CSMT)
end

local NSKMT = dtype("NumberSequenceKeypoint")
NumberSequenceKeypoint = {}
function NumberSequenceKeypoint.new(t, v, e)
	return setmetatable({Time = num(t, "NumberSequenceKeypoint.new"), Value = num(v, "NumberSequenceKeypoint.new"),
		Envelope = e or 0}, NSKMT)
end
local NSMT = dtype("NumberSequence")
NumberSequence = {}
function NumberSequence.new(a, b)
	local kps
	if type(a) == "number" then
		kps = {NumberSequenceKeypoint.new(0, a), NumberSequenceKeypoint.new(1, b or a)}
	elseif type(a) == "table" then
		kps = a
		if #kps < 2 or kps[1].Time ~= 0 or kps[#kps].Time ~= 1 then
			error("NumberSequence: the first keypoint must be at time 0 and the last at time 1", 2)
		end
		if #kps > 20 then error("NumberSequence: at most 20 keypoints", 2) end
		for i = 2, #kps do
			if kps[i].Time < kps[i - 1].Time then error("NumberSequence: keypoints must be in order", 2) end
		end
	else
		error("NumberSequence.new: bad arguments", 2)
	end
	return setmetatable({Keypoints = kps}, NSMT)
end
local NRMT = dtype("NumberRange")
NumberRange = {}
function NumberRange.new(a, b) return setmetatable({Min = a, Max = b or a}, NRMT) end

local RectMT = dtype("Rect")
Rect = {}
function Rect.new(a, b, c, d)
	local mn, mx
	if isType(a, "Vector2") then mn, mx = a, b else mn, mx = Vector2.new(a or 0, b or 0), Vector2.new(c or 0, d or 0) end
	return setmetatable({Min = mn, Max = mx, Width = mx.X - mn.X, Height = mx.Y - mn.Y}, RectMT)
end

local TweenInfoMT = dtype("TweenInfo")
TweenInfo = {}
function TweenInfo.new(time, style, dir, rep, rev, delay)
	return setmetatable({Time = time or 1, EasingStyle = style or Enum.EasingStyle.Quad,
		EasingDirection = dir or Enum.EasingDirection.Out, RepeatCount = rep or 0, Reverses = rev or false,
		DelayTime = delay or 0}, TweenInfoMT)
end

local RandomMT = dtype("Random")
Random = {}
function Random.new(seed)
	local s = math.floor(math.abs(seed or os.clock() * 1e6)) % 2147483647
	if s == 0 then s = 1 end
	return setmetatable({_s = s}, RandomMT)
end
function RandomMT:_next()
	self._s = (self._s * 16807) % 2147483647
	return self._s / 2147483647
end
function RandomMT:NextNumber(a, b)
	a, b = a or 0, b or 1
	return a + (b - a) * self:_next()
end
function RandomMT:NextInteger(a, b)
	if a > b then error("Random:NextInteger: min is larger than max", 2) end
	return a + math.floor(self:_next() * (b - a + 1))
end
function RandomMT:Clone() return setmetatable({_s = self._s}, RandomMT) end

---------------------------------------------------------------------------------------------------
-- enums
---------------------------------------------------------------------------------------------------
local ENUMS = {
	Font = {"Legacy", "Arial", "ArialBold", "SourceSans", "SourceSansBold", "SourceSansSemibold", "SourceSansLight",
		"SourceSansItalic", "Bodoni", "Garamond", "Cartoon", "Code", "Highway", "SciFi", "Arcade", "Fantasy", "Antique",
		"Gotham", "GothamMedium", "GothamBold", "GothamBlack", "AmaticSC", "Bangers", "Creepster", "DenkOne", "Fondamento",
		"FredokaOne", "GrenzeGotisch", "IndieFlower", "JosefinSans", "Jura", "Kalam", "LuckiestGuy", "Merriweather",
		"Michroma", "Nunito", "Oswald", "PatrickHand", "PermanentMarker", "Roboto", "RobotoCondensed", "RobotoMono",
		"Sarpanch", "SpecialElite", "TitilliumWeb", "Ubuntu", "BuilderSans", "BuilderSansMedium", "BuilderSansBold",
		"BuilderSansExtraBold", "Arimo", "ArimoBold", "Unknown"},
	FontWeight = {"Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Heavy"},
	FontStyle = {"Normal", "Italic"},
	TextXAlignment = {"Left", "Center", "Right"},
	TextYAlignment = {"Top", "Center", "Bottom"},
	TextTruncate = {"None", "AtEnd", "SplitWord"},
	TextDirection = {"Auto", "LeftToRight", "RightToLeft"},
	FillDirection = {"Horizontal", "Vertical"},
	HorizontalAlignment = {"Center", "Left", "Right"},
	VerticalAlignment = {"Center", "Top", "Bottom"},
	SortOrder = {"Name", "Custom", "LayoutOrder"},
	StartCorner = {"TopLeft", "TopRight", "BottomLeft", "BottomRight"},
	ScaleType = {"Stretch", "Slice", "Tile", "Fit", "Crop"},
	ResamplerMode = {"Default", "Pixelated"},
	ApplyStrokeMode = {"Contextual", "Border"},
	LineJoinMode = {"Round", "Bevel", "Miter"},
	EasingStyle = {"Linear", "Sine", "Back", "Quad", "Quart", "Quint", "Bounce", "Elastic", "Exponential",
		"Circular", "Cubic"},
	EasingDirection = {"In", "Out", "InOut"},
	PlaybackState = {"Begin", "Delayed", "Playing", "Paused", "Completed", "Cancelled"},
	ZIndexBehavior = {"Global", "Sibling"},
	AutomaticSize = {"None", "X", "Y", "XY"},
	InitialDockState = {"Top", "Bottom", "Left", "Right", "Float"},
	ScrollingDirection = {"X", "Y", "XY"},
	ScrollBarInset = {"None", "ScrollBar", "Always"},
	VerticalScrollBarPosition = {"Left", "Right"},
	ElasticBehavior = {"WhenScrollable", "Always", "Never"},
	AspectType = {"FitWithinMaxSize", "ScaleWithParentSize"},
	DominantAxis = {"Width", "Height"},
	SizeConstraint = {"RelativeXY", "RelativeXX", "RelativeYY"},
	BorderMode = {"Outline", "Middle", "Inset"},
	ButtonStyle = {"Custom", "RobloxButtonDefault", "RobloxButton", "RobloxRoundButton", "RobloxRoundDefaultButton",
		"RobloxRoundDropdownButton"},
	FinishRecordingOperation = {"Cancel", "Commit", "Append"},
	UserInputType = {"MouseButton1", "MouseButton2", "MouseButton3", "MouseWheel", "MouseMovement", "Touch", "Keyboard",
		"Focus", "Accelerometer", "Gyro", "Gamepad1", "Gamepad2", "TextInput", "InputMethod", "None"},
	UserInputState = {"Begin", "Change", "End", "Cancel", "None"},
	KeyCode = {"Unknown", "Backspace", "Tab", "Return", "Escape", "Space", "Zero", "One", "Two", "Three", "Four",
		"Five", "Six", "Seven", "Eight", "Nine", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N",
		"O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "LeftShift", "RightShift", "LeftControl",
		"RightControl", "LeftAlt", "RightAlt", "Up", "Down", "Left", "Right", "F1", "F2", "F3", "F4", "ButtonA",
		"ButtonB", "ButtonX", "ButtonY", "ButtonL1", "ButtonR1", "ButtonL2", "ButtonR2", "DPadUp", "DPadDown"},
	SelectionBehavior = {"Escape", "Stop"},
	ScreenInsets = {"None", "DeviceSafeInsets", "CoreUISafeInsets", "TopbarSafeInsets"},
	SafeAreaCompatibility = {"None", "FullscreenExtension"},
	UIFlexAlignment = {"None", "Fill", "SpaceAround", "SpaceBetween", "SpaceEvenly"},
	ItemLineAlignment = {"Automatic", "Start", "Center", "End", "Stretch"},
	UIFlexMode = {"None", "Grow", "Shrink", "Fill", "Custom"},
}

local EnumItemMT = dtype("EnumItem")
EnumItemMT.__tostring = function(e) return "Enum." .. e.EnumType .. "." .. e.Name end
local EnumMT = dtype("Enum")
Enum = {}
for ename, items in pairs(ENUMS) do
	local byName = {}
	for i, n in ipairs(items) do
		byName[n] = setmetatable({Name = n, Value = i - 1, EnumType = ename}, EnumItemMT)
	end
	local e = setmetatable({}, {
		__type = "Enum",
		__index = function(_, k)
			if k == "GetEnumItems" then
				return function()
					local out = {}
					for _, n in ipairs(items) do table.insert(out, byName[n]) end
					return out
				end
			end
			local it = byName[k]
			if not it then
				error(("%s is not a valid member of \"Enum.%s\""):format(tostring(k), ename), 2)
			end
			return it
		end,
		__newindex = function() error("Enums are read only", 2) end,
	})
	rawset(Enum, ename, e)
end
setmetatable(Enum, {__index = function(_, k) error(("%s is not a valid EnumItem"):format(tostring(k)), 2) end})

local function isEnum(v, ename)
	return typeof(v) == "EnumItem" and v.EnumType == ename
end

-- Font (FontFace)
local FontMT = dtype("Font")
Font = {}
local FONT_ENUM_FAMILY = {
	Gotham = {"GothamSSm", "Regular"}, GothamMedium = {"GothamSSm", "Medium"}, GothamBold = {"GothamSSm", "Bold"},
	GothamBlack = {"GothamSSm", "Heavy"}, SourceSans = {"SourceSansPro", "Regular"},
	SourceSansBold = {"SourceSansPro", "Bold"}, SourceSansSemibold = {"SourceSansPro", "SemiBold"},
	SourceSansLight = {"SourceSansPro", "Light"}, Arcade = {"PressStart2P", "Regular"}, Code = {"Inconsolata", "Regular"},
	BuilderSans = {"BuilderSans", "Regular"}, BuilderSansMedium = {"BuilderSans", "Medium"},
	BuilderSansBold = {"BuilderSans", "Bold"}, BuilderSansExtraBold = {"BuilderSans", "ExtraBold"},
	ArialBold = {"Arial", "Bold"}, ArimoBold = {"Arimo", "Bold"}, RobotoCondensed = {"RobotoCondensed", "Regular"},
}
function Font.new(family, weight, style)
	if type(family) ~= "string" then error("Font.new expects a family string", 2) end
	if weight ~= nil and not isEnum(weight, "FontWeight") then error("Font.new: weight must be an Enum.FontWeight", 2) end
	return setmetatable({Family = family, Weight = weight or Enum.FontWeight.Regular,
		Style = style or Enum.FontStyle.Normal}, FontMT)
end
function Font.fromEnum(e)
	if not isEnum(e, "Font") then error("Font.fromEnum expects an Enum.Font", 2) end
	local m = FONT_ENUM_FAMILY[e.Name] or {e.Name, "Regular"}
	return Font.new("rbxasset://fonts/families/" .. m[1] .. ".json", Enum.FontWeight[m[2]])
end
function Font.fromName(name, weight, style)
	return Font.new("rbxasset://fonts/families/" .. name .. ".json", weight, style)
end
FontMT.__index = function(f, k)
	if k == "Bold" then return f.Weight.Value >= Enum.FontWeight.Bold.Value end
	return rawget(FontMT, k)
end

---------------------------------------------------------------------------------------------------
-- signals and a tiny scheduler (task.*, tweens)
---------------------------------------------------------------------------------------------------
local Sched = {now = 0, queue = {}, seq = 0, errors = {}}
SHIM.Sched = Sched

local function report(err)
	table.insert(Sched.errors, tostring(err))
end

local function resume(co, ...)
	local ok, a, b = coroutine.resume(co, ...)
	if not ok then
		report(debug.traceback(co, a))
		return
	end
	if coroutine.status(co) == "suspended" then
		if a == "__wait" then
			Sched.at(Sched.now + math.max(b or 0, 1 / 60), co)
		end
		-- "__signal": parked on a signal, it resumes it
	end
end

function Sched.at(t, co, ...)
	Sched.seq = Sched.seq + 1
	table.insert(Sched.queue, {t = t, seq = Sched.seq, co = co, args = table.pack(...)})
end

function Sched.run(untilTime)
	while true do
		local best, bi = nil, nil
		for i, it in ipairs(Sched.queue) do
			if it.t <= untilTime and (not best or it.t < best.t or (it.t == best.t and it.seq < best.seq)) then
				best, bi = it, i
			end
		end
		if not best then break end
		table.remove(Sched.queue, bi)
		Sched.now = math.max(Sched.now, best.t)
		if type(best.co) == "function" then
			local ok, err = pcall(best.co, table.unpack(best.args, 1, best.args.n))
			if not ok then report(err) end
		else
			resume(best.co, table.unpack(best.args, 1, best.args.n))
		end
	end
	Sched.now = untilTime
end

local SignalMT = dtype("RBXScriptSignal")
local ConnMT = dtype("RBXScriptConnection")
local function newSignal(name)
	return setmetatable({_name = name, _conns = {}, _waiting = {}}, SignalMT)
end
function SignalMT:Connect(fn)
	if type(fn) ~= "function" then error("Attempt to connect failed: Passed value is not a function", 2) end
	local c = setmetatable({Connected = true, _fn = fn}, ConnMT)
	table.insert(self._conns, c)
	return c
end
function SignalMT:Once(fn)
	local c
	c = self:Connect(function(...)
		c:Disconnect()
		fn(...)
	end)
	return c
end
function SignalMT:Wait()
	local co = coroutine.running()
	table.insert(self._waiting, co)
	return coroutine.yield("__signal")
end
function ConnMT:Disconnect()
	self.Connected = false
end
function SignalMT:_fire(...)
	for _, c in ipairs(table.clone(self._conns)) do
		if c.Connected then
			local co = coroutine.create(c._fn)
			resume(co, ...)
		end
	end
	local w = self._waiting
	self._waiting = {}
	for _, co in ipairs(w) do
		resume(co, ...)
	end
end
SHIM.newSignal = newSignal

task = {}
function task.spawn(f, ...)
	local co = type(f) == "thread" and f or coroutine.create(f)
	resume(co, ...)
	return co
end
function task.defer(f, ...)
	local co = type(f) == "thread" and f or coroutine.create(f)
	Sched.at(Sched.now, co, ...)
	return co
end
function task.delay(t, f, ...)
	local co = type(f) == "thread" and f or coroutine.create(f)
	Sched.at(Sched.now + (t or 0), co, ...)
	return co
end
function task.wait(t)
	local co, main = coroutine.running()
	if main or not co then
		error("task.wait called outside a task (the shim runs scripts inside task.spawn)", 2)
	end
	coroutine.yield("__wait", t or 0)
	return t or 0
end
function task.cancel() end
wait = task.wait
delay = task.delay
spawn = task.spawn
tick = function() return Sched.now end
time = tick

---------------------------------------------------------------------------------------------------
-- classes
---------------------------------------------------------------------------------------------------
local function C(r, g, b) return Color3.fromRGB(r, g, b) end

local CLASSES = {}
local function class(name, super, props, extra)
	CLASSES[name] = {name = name, super = super, props = props or {}, extra = extra or {}}
end

-- property type tags: value = default. "RO" marks read-only.
local RO = {}
local NODEF = {}

class("Instance", nil, {Name = "", Archivable = true})
class("GuiBase2d", "Instance", {AutoLocalize = true, AbsolutePosition = RO, AbsoluteSize = RO, AbsoluteRotation = RO,
	SelectionBehaviorUp = Enum.SelectionBehavior.Escape, SelectionBehaviorDown = Enum.SelectionBehavior.Escape,
	SelectionBehaviorLeft = Enum.SelectionBehavior.Escape, SelectionBehaviorRight = Enum.SelectionBehavior.Escape,
	SelectionGroup = false})
class("GuiObject", "GuiBase2d", {
	Active = false, AnchorPoint = Vector2.new(0, 0), AutomaticSize = Enum.AutomaticSize.None,
	BackgroundColor3 = C(163, 162, 165), BackgroundTransparency = 0, BorderColor3 = C(27, 42, 53),
	BorderMode = Enum.BorderMode.Outline, BorderSizePixel = 1, ClipsDescendants = false, Interactable = true,
	LayoutOrder = 0, Position = UDim2.new(0, 0, 0, 0), Rotation = 0, Selectable = false, SelectionOrder = 0,
	Size = UDim2.new(0, 100, 0, 100), SizeConstraint = Enum.SizeConstraint.RelativeXY, Visible = true, ZIndex = 1,
})
class("Frame", "GuiObject", {Style = RO})
class("CanvasGroup", "GuiObject", {GroupColor3 = C(255, 255, 255), GroupTransparency = 0})
local TEXT = {Font = Enum.Font.Legacy, FontFace = NODEF, LineHeight = 1, MaxVisibleGraphemes = -1, RichText = false,
	Text = "Label", TextColor3 = C(27, 42, 53), TextDirection = Enum.TextDirection.Auto, TextScaled = false,
	TextSize = 8, TextStrokeColor3 = C(0, 0, 0), TextStrokeTransparency = 1, TextTransparency = 0,
	TextTruncate = Enum.TextTruncate.None, TextWrapped = false, TextXAlignment = Enum.TextXAlignment.Center,
	TextYAlignment = Enum.TextYAlignment.Center, ContentText = RO, TextBounds = RO, TextFits = RO, LocalizedText = RO}
local IMAGE = {Image = "", ImageColor3 = C(255, 255, 255), ImageRectOffset = Vector2.new(0, 0),
	ImageRectSize = Vector2.new(0, 0), ImageTransparency = 0, ResampleMode = Enum.ResamplerMode.Default,
	ScaleType = Enum.ScaleType.Stretch, SliceCenter = Rect.new(0, 0, 0, 0), SliceScale = 1,
	TileSize = UDim2.new(1, 0, 1, 0), IsLoaded = RO}
local BUTTON = {AutoButtonColor = true, Modal = false, Selected = false, Style = Enum.ButtonStyle.Custom}
local function merge(...)
	local out = {}
	for _, t in ipairs({...}) do for k, v in pairs(t) do out[k] = v end end
	return out
end
class("TextLabel", "GuiObject", TEXT)
class("ImageLabel", "GuiObject", IMAGE)
class("GuiButton", "GuiObject", BUTTON)
class("TextButton", "GuiButton", merge(TEXT, {Text = "Button"}))
class("ImageButton", "GuiButton", merge(IMAGE, {HoverImage = "", PressedImage = ""}))
class("TextBox", "GuiObject", merge(TEXT, {Text = "TextBox", ClearTextOnFocus = true, CursorPosition = 1,
	MultiLine = false, PlaceholderColor3 = C(178, 178, 178), PlaceholderText = "", SelectionStart = -1,
	ShowNativeInput = true, TextEditable = true}))
class("ScrollingFrame", "GuiObject", {AutomaticCanvasSize = Enum.AutomaticSize.None, BottomImage = "",
	CanvasPosition = Vector2.new(0, 0), CanvasSize = UDim2.new(0, 0, 2, 0),
	ElasticBehavior = Enum.ElasticBehavior.WhenScrollable, HorizontalScrollBarInset = Enum.ScrollBarInset.None,
	MidImage = "", ScrollBarImageColor3 = C(255, 255, 255), ScrollBarImageTransparency = 0, ScrollBarThickness = 12,
	ScrollingDirection = Enum.ScrollingDirection.XY, ScrollingEnabled = true, TopImage = "",
	VerticalScrollBarInset = Enum.ScrollBarInset.None, VerticalScrollBarPosition = Enum.VerticalScrollBarPosition.Right,
	AbsoluteCanvasSize = RO, AbsoluteWindowSize = RO})
class("LayerCollector", "GuiBase2d", {Enabled = true, ResetOnSpawn = true, ZIndexBehavior = Enum.ZIndexBehavior.Global})
class("ScreenGui", "LayerCollector", {DisplayOrder = 0, IgnoreGuiInset = false,
	ScreenInsets = Enum.ScreenInsets.CoreUISafeInsets, ClipToDeviceSafeArea = true,
	SafeAreaCompatibility = Enum.SafeAreaCompatibility.FullscreenExtension})
class("PluginGui", "LayerCollector", {Title = ""})
class("DockWidgetPluginGui", "PluginGui", {HostWidgetWasRestored = RO})
class("UIComponent", "Instance", {})
class("UIBase", "UIComponent", {})
class("UICorner", "UIComponent", {CornerRadius = UDim.new(0, 8)})
class("UIStroke", "UIComponent", {ApplyStrokeMode = Enum.ApplyStrokeMode.Contextual, Color = C(0, 0, 0), Enabled = true,
	LineJoinMode = Enum.LineJoinMode.Round, Thickness = 1, Transparency = 0})
class("UIGradient", "UIComponent", {Color = ColorSequence.new(C(255, 255, 255)), Enabled = true,
	Offset = Vector2.new(0, 0), Rotation = 0, Transparency = NumberSequence.new(0)})
class("UIPadding", "UIComponent", {PaddingBottom = UDim.new(0, 0), PaddingLeft = UDim.new(0, 0),
	PaddingRight = UDim.new(0, 0), PaddingTop = UDim.new(0, 0)})
class("UIScale", "UIComponent", {Scale = 1})
class("UIConstraint", "UIComponent", {})
class("UIAspectRatioConstraint", "UIConstraint", {AspectRatio = 1, AspectType = Enum.AspectType.FitWithinMaxSize,
	DominantAxis = Enum.DominantAxis.Width})
class("UISizeConstraint", "UIConstraint", {MaxSize = Vector2.new(math.huge, math.huge), MinSize = Vector2.new(0, 0)})
class("UITextSizeConstraint", "UIConstraint", {MaxTextSize = 100, MinTextSize = 1})
class("UIGridStyleLayout", "UIComponent", {FillDirection = Enum.FillDirection.Horizontal,
	HorizontalAlignment = Enum.HorizontalAlignment.Left, VerticalAlignment = Enum.VerticalAlignment.Top,
	SortOrder = Enum.SortOrder.LayoutOrder, AbsoluteContentSize = RO})
class("UIListLayout", "UIGridStyleLayout", {FillDirection = Enum.FillDirection.Vertical, Padding = UDim.new(0, 0),
	Wraps = false, HorizontalFlex = Enum.UIFlexAlignment.None, VerticalFlex = Enum.UIFlexAlignment.None,
	ItemLineAlignment = Enum.ItemLineAlignment.Automatic})
class("UIGridLayout", "UIGridStyleLayout", {CellPadding = UDim2.new(0, 5, 0, 5), CellSize = UDim2.new(0, 100, 0, 100),
	FillDirectionMaxCells = 0, StartCorner = Enum.StartCorner.TopLeft, AbsoluteCellCount = RO, AbsoluteCellSize = RO})
class("LuaSourceContainer", "Instance", {})
class("BaseScript", "LuaSourceContainer", {Disabled = false, Enabled = true, LinkedSource = ""})
class("Script", "BaseScript", {Source = ""})
class("LocalScript", "Script", {})
class("ModuleScript", "LuaSourceContainer", {Source = "", LinkedSource = ""})
class("Folder", "Instance", {})
class("BindableEvent", "Instance", {})
class("Configuration", "Instance", {})
class("ValueBase", "Instance", {})
class("IntValue", "ValueBase", {Value = 0})
class("NumberValue", "ValueBase", {Value = 0})
class("StringValue", "ValueBase", {Value = ""})
class("BoolValue", "ValueBase", {Value = false})
class("PostEffect", "Instance", {Enabled = true})
class("BlurEffect", "PostEffect", {Size = 24})
class("Sound", "Instance", {SoundId = "", Volume = 0.5, PlaybackSpeed = 1, Looped = false, Playing = false,
	TimePosition = 0})
class("Camera", "Instance", {ViewportSize = Vector2.new(1920, 1080), FieldOfView = 70})
class("Player", "Instance", {DisplayName = "Player", UserId = 1})
class("PlayerGui", "Instance", {})
class("ServiceProvider", "Instance", {})
class("Service", "Instance", {})
class("Workspace", "Instance", {CurrentCamera = NODEF})
class("Lighting", "Instance", {})

local ABSTRACT = {Instance = true, GuiBase2d = true, GuiObject = true, GuiButton = true, LayerCollector = true,
	UIComponent = true, UIBase = true, UIConstraint = true, UIGridStyleLayout = true, LuaSourceContainer = true,
	BaseScript = true, ValueBase = true, PostEffect = true, Service = true, ServiceProvider = true, PluginGui = true,
	DockWidgetPluginGui = true, Player = true, PlayerGui = true, Workspace = true, Lighting = true, Camera = false}

local function classChain(name)
	local out = {}
	local c = CLASSES[name]
	while c do
		table.insert(out, c)
		c = c.super and CLASSES[c.super]
	end
	return out
end

local function propInfo(cname, prop)
	for _, c in ipairs(classChain(cname)) do
		local v = c.props[prop]
		if v ~= nil then
			return true, v
		end
	end
	return false
end

-- expected datatype for a property, taken from its default
local function expectedType(default)
	if default == RO or default == NODEF then return nil end
	local t = typeof(default)
	if t == "EnumItem" then return "EnumItem", default.EnumType end
	return t
end

local InstanceMT = {__type = "Instance"}
local ALL = {}
SHIM.ALL = ALL

local EVENTS = {
	GuiObject = {"InputBegan", "InputEnded", "InputChanged", "MouseEnter", "MouseLeave", "MouseMoved",
		"SelectionGained", "SelectionLost"},
	GuiButton = {"Activated", "MouseButton1Click", "MouseButton1Down", "MouseButton1Up", "MouseButton2Click"},
	TextBox = {"FocusLost", "Focused", "ReturnPressedFromOnScreenKeyboard"},
	Instance = {"Changed", "ChildAdded", "ChildRemoved", "DescendantAdded", "DescendantRemoving", "AncestryChanged",
		"Destroying", "AttributeChanged"},
	ValueBase = {"Changed"},
	PluginGui = {"WindowFocused", "WindowFocusReleased"},
	BindableEvent = {"Event"},
}

local function isA(cname, other)
	for _, c in ipairs(classChain(cname)) do
		if c.name == other then return true end
	end
	return false
end

local methods = {}

local function newInstance(cname, raw)
	local cls = CLASSES[cname]
	if not cls or (ABSTRACT[cname] and not raw) then
		error(("Unable to create an Instance of type \"%s\""):format(tostring(cname)), 3)
	end
	local self = {_class = cname, _props = {Name = cname}, _children = {}, _parent = nil, _attrs = {}, _events = {},
		_propSignals = {}}
	for _, c in ipairs(classChain(cname)) do
		for k, v in pairs(c.props) do
			if self._props[k] == nil and v ~= RO and v ~= NODEF then
				self._props[k] = v
			end
		end
	end
	self._props.Name = cname
	for base, list in pairs(EVENTS) do
		if isA(cname, base) then
			for _, e in ipairs(list) do self._events[e] = newSignal(e) end
		end
	end
	setmetatable(self, InstanceMT)
	table.insert(ALL, self)
	return self
end
SHIM.newInstance = newInstance

local function descendants(inst, out)
	for _, c in ipairs(inst._children) do
		table.insert(out, c)
		descendants(c, out)
	end
	return out
end

local function fullName(inst)
	local parts = {}
	local p = inst
	while p do
		table.insert(parts, 1, p._props.Name)
		p = p._parent
	end
	return table.concat(parts, ".")
end

function methods:IsA(n) return isA(self._class, n) end
function methods:GetChildren() return table.clone(self._children) end
function methods:GetDescendants() return descendants(self, {}) end
function methods:FindFirstChild(name, recursive)
	for _, c in ipairs(self._children) do
		if c._props.Name == name then return c end
	end
	if recursive then
		for _, c in ipairs(self._children) do
			local f = c:FindFirstChild(name, true)
			if f then return f end
		end
	end
	return nil
end
function methods:FindFirstChildOfClass(cn)
	for _, c in ipairs(self._children) do
		if c._class == cn then return c end
	end
	return nil
end
function methods:FindFirstChildWhichIsA(cn, recursive)
	for _, c in ipairs(self._children) do
		if isA(c._class, cn) then return c end
	end
	if recursive then
		for _, c in ipairs(self._children) do
			local f = c:FindFirstChildWhichIsA(cn, true)
			if f then return f end
		end
	end
	return nil
end
function methods:FindFirstAncestor(name)
	local p = self._parent
	while p do
		if p._props.Name == name then return p end
		p = p._parent
	end
	return nil
end
function methods:FindFirstAncestorWhichIsA(cn)
	local p = self._parent
	while p do
		if isA(p._class, cn) then return p end
		p = p._parent
	end
	return nil
end
function methods:IsDescendantOf(other)
	local p = self._parent
	while p do
		if p == other then return true end
		p = p._parent
	end
	return false
end
function methods:WaitForChild(name, timeout)
	local c = self:FindFirstChild(name)
	if c then return c end
	if timeout then return nil end
	error(("Infinite yield: %s is missing %s"):format(fullName(self), name), 2)
end
function methods:GetFullName() return fullName(self) end
function methods:ClearAllChildren()
	for _, c in ipairs(table.clone(self._children)) do c:Destroy() end
end
function methods:Destroy()
	self.Parent = nil
	rawset(self, "_destroyed", true)
	for _, c in ipairs(table.clone(self._children)) do c:Destroy() end
end
function methods:Clone()
	local c = newInstance(self._class, true)
	for k, v in pairs(self._props) do c._props[k] = v end
	for k, v in pairs(self._attrs) do c._attrs[k] = v end
	for _, ch in ipairs(self._children) do
		local cc = ch:Clone()
		cc.Parent = c
	end
	return c
end
local ATTR_OK = {string = true, boolean = true, number = true, UDim = true, UDim2 = true, Color3 = true, Vector2 = true,
	Vector3 = true, NumberSequence = true, ColorSequence = true, NumberRange = true, Rect = true, BrickColor = true,
	EnumItem = true, Font = true, CFrame = true}
function methods:SetAttribute(k, v)
	if type(k) ~= "string" or #k == 0 or #k > 100 or k:match("[^%w_]") or k:sub(1, 3) == "RBX" then
		error(("Attribute name \"%s\" is not valid"):format(tostring(k)), 2)
	end
	if v ~= nil and not ATTR_OK[typeof(v)] then
		error(("%s is not a supported attribute type"):format(typeof(v)), 2)
	end
	self._attrs[k] = v
	self._events.AttributeChanged:_fire(k)
end
function methods:GetAttribute(k) return self._attrs[k] end
function methods:GetAttributes() return table.clone(self._attrs) end
function methods:GetPropertyChangedSignal(p)
	local ok = propInfo(self._class, p) or p == "Parent" or p == "Name"
	if not ok then
		error(("%s is not a valid property name."):format(tostring(p)), 2)
	end
	self._propSignals[p] = self._propSignals[p] or newSignal(p)
	return self._propSignals[p]
end
function methods:GetAttributeChangedSignal(k)
	rawset(self, "_attrSignals", rawget(self, "_attrSignals") or {})
	self._attrSignals[k] = self._attrSignals[k] or newSignal(k)
	return self._attrSignals[k]
end
-- classes with their own methods
local CLASS_METHODS = {}

InstanceMT.__index = function(self, k)
	if type(k) == "string" and k:sub(1, 1) == "_" then return nil end
	if k == "Parent" then return self._parent end
	if k == "ClassName" then return self._class end
	local m = methods[k]
	if m then return m end
	for _, c in ipairs(classChain(self._class)) do
		local cm = CLASS_METHODS[c.name]
		if cm and cm[k] ~= nil then
			local v = cm[k]
			return v
		end
	end
	local ev = self._events[k]
	if ev then return ev end
	local v = self._props[k]
	if v ~= nil then return v end
	local ok, def = propInfo(self._class, k)
	if ok then
		if def == RO then
			if k == "AbsoluteSize" or k == "AbsolutePosition" then return Vector2.new(0, 0) end
			if k == "TextBounds" then return Vector2.new(0, 0) end
			if k == "AbsoluteContentSize" then return Vector2.new(0, 0) end
			return nil
		end
		return nil
	end
	for _, c in ipairs(self._children) do
		if c._props.Name == k then return c end
	end
	error(("%s is not a valid member of %s \"%s\""):format(tostring(k), self._class, fullName(self)), 2)
end

InstanceMT.__newindex = function(self, k, v)
	if type(k) == "string" and k:sub(1, 1) == "_" then
		rawset(self, k, v)
		return
	end
	if k == "Parent" then
		if v ~= nil and typeof(v) ~= "Instance" then
			error("Parent must be an Instance or nil", 2)
		end
		local p = v
		while p do
			if p == self then error("Attempt to set parent of " .. fullName(self) .. " to itself or a descendant", 2) end
			p = p._parent
		end
		local old = self._parent
		if old then
			for i, c in ipairs(old._children) do
				if c == self then table.remove(old._children, i) break end
			end
			old._events.ChildRemoved:_fire(self)
		end
		self._parent = v
		if v then
			table.insert(v._children, self)
			v._events.ChildAdded:_fire(self)
			local a = v
			while a do
				a._events.DescendantAdded:_fire(self)
				a = a._parent
			end
		end
		self._events.AncestryChanged:_fire(self, v)
		return
	end
	if k == "ClassName" then error("ClassName is read only", 2) end
	local ok, def = propInfo(self._class, k)
	if not ok then
		error(("%s is not a valid member of %s \"%s\""):format(tostring(k), self._class, fullName(self)), 2)
	end
	if def == RO then
		error(("Unable to assign property %s. Property is read only"):format(k), 2)
	end
	local et, ename = expectedType(def)
	if k == "FontFace" then et = "Font" end
	if k == "CurrentCamera" then et = nil end
	if et and v ~= nil then
		local vt = typeof(v)
		if et == "EnumItem" then
			if vt == "EnumItem" then
				if v.EnumType ~= ename then
					error(("Unable to assign property %s. Enum.%s expected, got Enum.%s"):format(k, ename, v.EnumType), 2)
				end
			elseif vt == "string" or vt == "number" then
				local found = nil
				for _, it in ipairs(Enum[ename]:GetEnumItems()) do
					if it.Name == v or it.Value == v then found = it end
				end
				if not found then error(("Unable to assign property %s. Invalid value \"%s\""):format(k, tostring(v)), 2) end
				v = found
			else
				error(("Unable to assign property %s. EnumItem expected, got %s"):format(k, vt), 2)
			end
		elseif et == "number" then
			if vt ~= "number" then
				error(("Unable to assign property %s. number expected, got %s"):format(k, vt), 2)
			end
			if v ~= v then error(("Unable to assign property %s: NaN"):format(k), 2) end
		elseif et == "string" then
			if vt == "number" then v = tostring(v)
			elseif vt ~= "string" then
				error(("Unable to assign property %s. string expected, got %s"):format(k, vt), 2)
			end
		elseif vt ~= et then
			error(("Unable to assign property %s. %s expected, got %s"):format(k, et, vt), 2)
		end
	end
	if k == "Font" and v then
		self._props.FontFace = Font.fromEnum(v)
	elseif k == "FontFace" and v then
		self._props.Font = Enum.Font.Unknown
	end
	self._props[k] = v
	local s = self._propSignals[k]
	if s then s:_fire() end
	self._events.Changed:_fire(k)
end

InstanceMT.__tostring = function(self) return self._props.Name end

Instance = {}
function Instance.new(cname, parent)
	local i = newInstance(cname)
	if parent then i.Parent = parent end
	return i
end

---------------------------------------------------------------------------------------------------
-- game, services, player
---------------------------------------------------------------------------------------------------
local function service(name, cls)
	CLASSES[name] = CLASSES[name] or {name = name, super = cls or "Service", props = {}, extra = {}}
	local s = newInstance(name, true)
	s._props.Name = name
	return s
end

local game_ = newInstance("ServiceProvider", true)
game_._props.Name = "Game"
game = game_
local services = {}
local function addService(name, cls)
	local s = service(name, cls)
	s.Parent = game_
	services[name] = s
	return s
end
local Workspace = addService("Workspace", "Workspace")
local cam = newInstance("Camera")
cam.Name = "Camera"
cam.Parent = Workspace
Workspace._props.CurrentCamera = cam
workspace = Workspace
for _, n in ipairs({"ReplicatedStorage", "StarterGui", "StarterPlayer", "ServerStorage", "SoundService",
	"ChangeHistoryService", "Selection", "HttpService", "RunService", "UserInputService", "TweenService", "Players",
	"CollectionService", "GuiService", "ContentProvider", "TextService", "CoreGui", "MarketplaceService"}) do
	addService(n)
end
addService("Lighting", "Lighting")
CLASSES.StarterGui.props = {ShowDevelopmentGui = true}

function methods:GetService(name)
	if self ~= game_ then error("GetService is not a valid member", 2) end
	local s = services[name]
	if not s then error(("'%s' is not a valid Service name"):format(tostring(name)), 2) end
	return s
end

-- ChangeHistoryService
SHIM.waypoints = {}
CLASS_METHODS.ChangeHistoryService = {
	SetWaypoint = function(_, name) table.insert(SHIM.waypoints, name) end,
	TryBeginRecording = function(_, name) table.insert(SHIM.waypoints, "begin:" .. tostring(name)) return "rec1" end,
	FinishRecording = function(_, id, op)
		if not isEnum(op, "FinishRecordingOperation") then error("FinishRecording expects an operation", 2) end
		table.insert(SHIM.waypoints, "finish:" .. op.Name)
	end,
}
SHIM.selection = {}
CLASS_METHODS.Selection = {
	Set = function(_, list)
		if type(list) ~= "table" then error("Selection:Set expects a table", 2) end
		SHIM.selection = list
	end,
	Get = function() return SHIM.selection end,
}
CLASS_METHODS.HttpService = {
	GenerateGUID = function() return "00000000-0000-0000-0000-000000000000" end,
}
CLASS_METHODS.RunService = {
	IsStudio = function() return true end,
	IsRunning = function() return SHIM.running == true end,
	IsEdit = function() return SHIM.running ~= true end,
}
services.RunService._events.Heartbeat = newSignal("Heartbeat")
services.RunService._events.RenderStepped = newSignal("RenderStepped")
services.RunService._events.Stepped = newSignal("Stepped")
CLASS_METHODS.UserInputService = {TouchEnabled = false, KeyboardEnabled = true, MouseEnabled = true,
	GamepadEnabled = false, GetMouseLocation = function() return Vector2.new(0, 0) end}
services.UserInputService._events.InputBegan = newSignal("InputBegan")
services.UserInputService._events.InputEnded = newSignal("InputEnded")
services.UserInputService._events.LastInputTypeChanged = newSignal("LastInputTypeChanged")
CLASS_METHODS.GuiService = {GetGuiInset = function() return Vector2.new(0, 58), Vector2.new(0, 0) end}
CLASS_METHODS.CollectionService = {
	AddTag = function(_, inst, tag) rawset(inst, "_tags", rawget(inst, "_tags") or {}) inst._tags[tag] = true end,
	HasTag = function(_, inst, tag) return inst._tags ~= nil and inst._tags[tag] == true end,
	GetTagged = function(_, tag)
		local out = {}
		for _, i in ipairs(ALL) do if i._tags and i._tags[tag] and not i._destroyed then table.insert(out, i) end end
		return out
	end,
}
CLASS_METHODS.BindableEvent = {Fire = function(self, ...) self._events.Event:_fire(...) end}
CLASS_METHODS.Sound = {Play = function(s) s._props.Playing = true end, Stop = function(s) s._props.Playing = false end}

-- TweenService
local TweenMT = {__type = "Instance"}
local function easing(style, dir, t)
	local s = style.Name
	local function ein(x)
		if s == "Linear" then return x
		elseif s == "Quad" then return x * x
		elseif s == "Cubic" then return x * x * x
		elseif s == "Quart" then return x ^ 4
		elseif s == "Quint" then return x ^ 5
		elseif s == "Sine" then return 1 - math.cos(x * math.pi / 2)
		elseif s == "Exponential" then return x == 0 and 0 or 2 ^ (10 * x - 10)
		elseif s == "Circular" then return 1 - math.sqrt(1 - x * x)
		elseif s == "Back" then return 2.70158 * x ^ 3 - 1.70158 * x * x
		elseif s == "Elastic" then return x == 0 and 0 or x == 1 and 1 or -(2 ^ (10 * x - 10)) * math.sin((x * 10 - 10.75) * (2 * math.pi) / 3)
		elseif s == "Bounce" then
			local y = 1 - x
			local r
			if y < 1 / 2.75 then r = 7.5625 * y * y
			elseif y < 2 / 2.75 then y = y - 1.5 / 2.75 r = 7.5625 * y * y + 0.75
			elseif y < 2.5 / 2.75 then y = y - 2.25 / 2.75 r = 7.5625 * y * y + 0.9375
			else y = y - 2.625 / 2.75 r = 7.5625 * y * y + 0.984375 end
			return 1 - r
		end
		return x
	end
	if dir.Name == "In" then return ein(t)
	elseif dir.Name == "Out" then return 1 - ein(1 - t)
	else return t < 0.5 and ein(t * 2) / 2 or 1 - ein((1 - t) * 2) / 2 end
end
SHIM.easing = easing

local TWEENABLE = {number = true, UDim2 = true, UDim = true, Color3 = true, Vector2 = true}
SHIM.tweens = {}
CLASS_METHODS.TweenService = {
	Create = function(_, inst, info, goals)
		if typeof(inst) ~= "Instance" then error("TweenService:Create: first argument must be an Instance", 2) end
		if typeof(info) ~= "TweenInfo" then error("TweenService:Create: second argument must be a TweenInfo", 2) end
		for k, v in pairs(goals) do
			local ok, def = propInfo(inst._class, k)
			if not ok then error(("TweenService:Create property named '%s' cannot be tweened due to type mismatch (property is a 'nil', but given type is '%s')"):format(k, typeof(v)), 2) end
			if not TWEENABLE[typeof(v)] and typeof(v) ~= "boolean" then
				error(("TweenService:Create: property '%s' of type %s cannot be tweened"):format(k, typeof(v)), 2)
			end
			local et = expectedType(def)
			if et and et ~= typeof(v) then
				error(("TweenService:Create property named '%s' cannot be tweened due to type mismatch (property is a '%s', but given type is '%s')"):format(k, et, typeof(v)), 2)
			end
		end
		local tw = {Instance = inst, TweenInfo = info, _goals = goals, PlaybackState = Enum.PlaybackState.Begin,
			Completed = newSignal("Completed"), _id = 0}
		table.insert(SHIM.tweens, tw)
		return setmetatable(tw, {__type = "Instance", __index = {
			Play = function(self)
				self._id = self._id + 1
				local id = self._id
				self.PlaybackState = Enum.PlaybackState.Playing
				local start = {}
				for k in pairs(self._goals) do start[k] = self.Instance[k] end
				local T = math.max(self.TweenInfo.Time, 0)
				local t0 = Sched.now + self.TweenInfo.DelayTime
				local steps = math.max(1, math.floor(T * 30))
				for s = 1, steps do
					Sched.at(t0 + T * s / steps, function()
						if self._id ~= id or self.Instance._destroyed then return end
						local a = easing(self.TweenInfo.EasingStyle, self.TweenInfo.EasingDirection, s / steps)
						for k, g in pairs(self._goals) do
							local s0 = start[k]
							local v
							if type(g) == "number" then v = s0 + (g - s0) * a
							elseif type(g) == "boolean" then v = a >= 1 and g or s0
							elseif typeof(g) == "Color3" or typeof(g) == "Vector2" or typeof(g) == "UDim2" then v = s0:Lerp(g, a)
							elseif typeof(g) == "UDim" then v = UDim.new(s0.Scale + (g.Scale - s0.Scale) * a, s0.Offset + (g.Offset - s0.Offset) * a)
							end
							self.Instance[k] = v
						end
						if s == steps then
							self.PlaybackState = Enum.PlaybackState.Completed
							self.Completed:_fire(Enum.PlaybackState.Completed)
						end
					end)
				end
			end,
			Cancel = function(self)
				self._id = self._id + 1
				self.PlaybackState = Enum.PlaybackState.Cancelled
			end,
			Pause = function(self)
				self._id = self._id + 1
				self.PlaybackState = Enum.PlaybackState.Paused
			end,
			Destroy = function() end,
		}})
	end,
}

-- a player with leaderstats (used when the controller runs)
local Players = services.Players
local player = newInstance("Player", true)
player.Name = "Player1"
player.Parent = Players
local pgui = newInstance("PlayerGui", true)
pgui.Name = "PlayerGui"
pgui.Parent = player
local ls = newInstance("Folder")
ls.Name = "leaderstats"
ls.Parent = player
for n, v in pairs({Coins = 12500, Gems = 340, Cash = 98400, Gold = 720}) do
	local iv = newInstance("IntValue")
	iv.Name = n
	iv.Value = v
	iv.Parent = ls
end
CLASS_METHODS.Players = {LocalPlayer = player}
CLASS_METHODS.Player = {GetMouse = function() return {X = 0, Y = 0} end}
SHIM.player = player

---------------------------------------------------------------------------------------------------
-- plugin API (only when a test asks for it)
---------------------------------------------------------------------------------------------------
local DWInfoMT = dtype("DockWidgetPluginGuiInfo")
DockWidgetPluginGuiInfo = {}
function DockWidgetPluginGuiInfo.new(state, enabled, override, fw, fh, mw, mh)
	if not isEnum(state, "InitialDockState") then error("DockWidgetPluginGuiInfo.new expects an InitialDockState", 2) end
	return setmetatable({InitialDockState = state, InitialEnabled = enabled, FloatingXSize = fw or 0,
		FloatingYSize = fh or 0, MinWidth = mw or 0, MinHeight = mh or 0}, DWInfoMT)
end

function SHIM.makePlugin(settings)
	local p = {_settings = settings or {}, toolbars = {}, widgets = {}}
	local PluginMT = {__type = "Instance"}
	PluginMT.__index = {
		CreateToolbar = function(self, name)
			local tb = {name = name, buttons = {}}
			tb.CreateButton = function(_, id, tip, icon, text)
				local b = {Click = newSignal("Click"), Enabled = true, ClickableWhenViewportHidden = false}
				b.SetActive = function() end
				table.insert(tb.buttons, b)
				return b
			end
			table.insert(self.toolbars, tb)
			return tb
		end,
		CreateDockWidgetPluginGui = function(self, id, info)
			if typeof(info) ~= "DockWidgetPluginGuiInfo" then error("CreateDockWidgetPluginGui expects DockWidgetPluginGuiInfo", 2) end
			local w = newInstance("DockWidgetPluginGui", true)
			w._props.Name = id
			w._props.Enabled = info.InitialEnabled
			rawset(w, "_size", Vector2.new(info.FloatingXSize, info.FloatingYSize))
			table.insert(self.widgets, w)
			return w
		end,
		GetSetting = function(self, k) return self._settings[k] end,
		SetSetting = function(self, k, v)
			if type(v) == "table" then
				for kk, vv in pairs(v) do
					if type(vv) ~= "string" and type(vv) ~= "number" and type(vv) ~= "boolean" and type(vv) ~= "table" then
						error("SetSetting: value is not serializable", 2)
					end
				end
			end
			self._settings[k] = v
		end,
		GetMouse = function() return {} end,
		Unloading = newSignal("Unloading"),
	}
	return setmetatable(p, PluginMT)
end

---------------------------------------------------------------------------------------------------
-- running a LocalScript's source (the generated controller)
---------------------------------------------------------------------------------------------------
function SHIM.runScript(scriptInst)
	local src = scriptInst.Source
	local fn, err = loadstring(src, "=" .. scriptInst:GetFullName())
	if not fn then error("controller does not compile: " .. tostring(err)) end
	local env = setmetatable({script = scriptInst}, {__index = getfenv(0)})
	setfenv(fn, env)
	task.spawn(fn)
end

---------------------------------------------------------------------------------------------------
-- JSON dump of an instance tree (read by ui/sim/render.py)
---------------------------------------------------------------------------------------------------
local function jstr(s)
	return '"' .. s:gsub('[%c"\\]', function(c)
		if c == '"' then return '\\"' elseif c == "\\" then return "\\\\" elseif c == "\n" then return "\\n"
		elseif c == "\t" then return "\\t" else return ("\\u%04x"):format(c:byte()) end
	end) .. '"'
end
local function jnum(n)
	if n ~= n then return "0" end
	if n == math.huge then return "1e30" end
	if n == -math.huge then return "-1e30" end
	return ("%.6g"):format(n)
end
local function jval(v)
	local t = typeof(v)
	if t == "number" then return jnum(v)
	elseif t == "string" then return jstr(v)
	elseif t == "boolean" then return v and "true" or "false"
	elseif t == "UDim" then return ('{"t":"UDim","v":[%s,%s]}'):format(jnum(v.Scale), jnum(v.Offset))
	elseif t == "UDim2" then
		return ('{"t":"UDim2","v":[%s,%s,%s,%s]}'):format(jnum(v.X.Scale), jnum(v.X.Offset), jnum(v.Y.Scale), jnum(v.Y.Offset))
	elseif t == "Vector2" then return ('{"t":"Vector2","v":[%s,%s]}'):format(jnum(v.X), jnum(v.Y))
	elseif t == "Color3" then return ('{"t":"Color3","v":[%s,%s,%s]}'):format(jnum(v.R), jnum(v.G), jnum(v.B))
	elseif t == "ColorSequence" then
		local kp = {}
		for _, k in ipairs(v.Keypoints) do
			table.insert(kp, ("[%s,%s,%s,%s]"):format(jnum(k.Time), jnum(k.Value.R), jnum(k.Value.G), jnum(k.Value.B)))
		end
		return '{"t":"ColorSequence","v":[' .. table.concat(kp, ",") .. "]}"
	elseif t == "NumberSequence" then
		local kp = {}
		for _, k in ipairs(v.Keypoints) do table.insert(kp, ("[%s,%s]"):format(jnum(k.Time), jnum(k.Value))) end
		return '{"t":"NumberSequence","v":[' .. table.concat(kp, ",") .. "]}"
	elseif t == "Rect" then
		return ('{"t":"Rect","v":[%s,%s,%s,%s]}'):format(jnum(v.Min.X), jnum(v.Min.Y), jnum(v.Max.X), jnum(v.Max.Y))
	elseif t == "EnumItem" then return ('{"t":"Enum","v":%s}'):format(jstr(v.EnumType .. "." .. v.Name))
	elseif t == "Font" then
		return ('{"t":"Font","family":%s,"weight":%s,"style":%s}'):format(jstr(v.Family), jstr(v.Weight.Name), jstr(v.Style.Name))
	end
	return "null"
end

function SHIM.dump(inst)
	local parts = {}
	table.insert(parts, '{"c":' .. jstr(inst._class) .. ',"n":' .. jstr(inst._props.Name) .. ',"p":{')
	local first = true
	local keys = {}
	for k in pairs(inst._props) do table.insert(keys, k) end
	table.sort(keys)
	for _, k in ipairs(keys) do
		local v = inst._props[k]
		if k ~= "Name" and typeof(v) ~= "Instance" and k ~= "Source" then
			table.insert(parts, (first and "" or ",") .. jstr(k) .. ":" .. jval(v))
			first = false
		end
	end
	table.insert(parts, '},"a":{')
	first = true
	for k, v in pairs(inst._attrs) do
		table.insert(parts, (first and "" or ",") .. jstr(k) .. ":" .. jval(v))
		first = false
	end
	table.insert(parts, '},"k":[')
	for i, c in ipairs(inst._children) do
		table.insert(parts, (i > 1 and "," or "") .. SHIM.dump(c))
	end
	table.insert(parts, "]}")
	return table.concat(parts)
end

function SHIM.count(inst)
	return #inst:GetDescendants()
end

-- (the driver is appended to this chunk and uses SHIM directly)
