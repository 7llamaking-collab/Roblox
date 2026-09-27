--[[
	Building setup helper (optional) - run once in Roblox Studio's Command Bar
	after importing a Commercial or Tycoon model.

	1. Import the FBX (File > Import 3D) and select the imported model(s).
	2. Paste this whole file into View > Command Bar and press Enter.

	What it does, by part name:
	  *_Glass                     see-through glass (Transparency 0.45), no shadows, no collision
	  *_Laser, *_Lasers, *_Barrier  glowing Neon, half transparent (they are still solid, like a
	                              locked laser door - set CanCollide off in your script to open them)
	  *_Roof                      kept as is (hide it or set Transparency 1 for a top-down view)
	  everything else             Anchored, and CollisionFidelity = PreciseConvexDecomposition so
	                              players can walk through doorways and around the furniture
	If Studio refuses to change CollisionFidelity from the Command Bar, select the wall part
	(the one named after the building) and set it by hand in the Properties window.
]]

local Selection = game:GetService("Selection")
local ChangeHistoryService = game:GetService("ChangeHistoryService")

local function endsWith(s, suffix)
	return s:sub(-#suffix) == suffix
end

local counts = { glass = 0, laser = 0, fidelity = 0, fidelityFailed = 0 }

local function setup(part)
	if not part:IsA("BasePart") then
		return
	end
	part.Anchored = true
	local name = part.Name
	if endsWith(name, "_Glass") then
		part.Transparency = 0.45
		part.Reflectance = 0.1
		part.CastShadow = false
		part.CanCollide = false
		counts.glass += 1
	elseif endsWith(name, "_Laser") or endsWith(name, "_Lasers") or endsWith(name, "_Barrier") then
		part.Material = Enum.Material.Neon
		part.Transparency = 0.35
		part.CastShadow = false
		counts.laser += 1
	elseif part:IsA("MeshPart") then
		local ok = pcall(function()
			part.CollisionFidelity = Enum.CollisionFidelity.PreciseConvexDecomposition
		end)
		if ok then
			counts.fidelity += 1
		else
			counts.fidelityFailed += 1
		end
	end
end

for _, obj in ipairs(Selection:Get()) do
	setup(obj)
	for _, d in ipairs(obj:GetDescendants()) do
		setup(d)
	end
end
ChangeHistoryService:SetWaypoint("Building Setup")
print(("Building setup: %d glass, %d laser/barrier, %d precise collision (%d need setting by hand)"):format(
	counts.glass, counts.laser, counts.fidelity, counts.fidelityFailed))
