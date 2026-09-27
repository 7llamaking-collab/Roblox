--[[
	Stud Style helper (optional) — run once in Roblox Studio's Command Bar.

	1. Import the FBX files (File > Import 3D) and select the imported models/MeshParts.
	2. Paste this whole file into View > Command Bar and press Enter.

	It gives every selected MeshPart the stud overlay used by AnimalBundle
	(six Texture objects, one per face) so the Blender assets match your animals.
	Nothing else in the library needs scripts — all models are made in Blender.
]]

-- Same stud texture/settings as the animals in AnimalBundle_1.rbxl.
-- To use this library's own stud tile instead, upload textures/Stud.png and set
-- STUD_TEXTURE to its id and STUDS_PER_TILE to 0.5.
local STUD_TEXTURE = "rbxassetid://9527811247"
local STUDS_PER_TILE = 9
local TRANSPARENCY = 0.4

-- Optional shiny metals & gems: upload textures/StudPalette.png,
-- StudPalette_Metalness.png and StudPalette_Roughness.png and paste the ids here.
local PALETTE_COLOR = "" -- e.g. "rbxassetid://123"
local PALETTE_METAL = ""
local PALETTE_ROUGH = ""

local Selection = game:GetService("Selection")
local ChangeHistoryService = game:GetService("ChangeHistoryService")

local function hasStuds(part)
	for _, child in ipairs(part:GetChildren()) do
		if child:IsA("Texture") and child.Texture == STUD_TEXTURE then
			return true
		end
	end
	return false
end

local function style(part)
	if not part:IsA("MeshPart") then
		return
	end
	if not hasStuds(part) then
		for _, face in ipairs(Enum.NormalId:GetEnumItems()) do
			local t = Instance.new("Texture")
			t.Name = "Studs"
			t.Texture = STUD_TEXTURE
			t.Face = face
			t.StudsPerTileU = STUDS_PER_TILE
			t.StudsPerTileV = STUDS_PER_TILE
			t.Transparency = TRANSPARENCY
			t.Parent = part
		end
	end
	if PALETTE_COLOR ~= "" and not part:FindFirstChildOfClass("SurfaceAppearance") then
		local sa = Instance.new("SurfaceAppearance")
		sa.ColorMap = PALETTE_COLOR
		sa.MetalnessMap = PALETTE_METAL
		sa.RoughnessMap = PALETTE_ROUGH
		sa.Parent = part
	end
end

local count = 0
for _, obj in ipairs(Selection:Get()) do
	style(obj)
	for _, d in ipairs(obj:GetDescendants()) do
		style(d)
	end
	count += 1
end
ChangeHistoryService:SetWaypoint("Stud Style")
print(("Stud Style applied to %d selected object(s)"):format(count))
