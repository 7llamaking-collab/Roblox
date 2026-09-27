"""UI themes + a keyword "prompt" parser (no AI: plain keyword matching).

    theme_from_prompt('"Pet Legends" candy pink simulator')
    -> (theme dict, title "Pet Legends", game type "simulator")
"""
import re

# Every theme: button colours, panel colours, outline, title gradient and style knobs.
THEMES = {
    "Classic": dict(keywords=["classic", "default", "bright", "simulator", "sim", "blue", "cartoon"],
                    primary="#2FA4FF", secondary="#43D162", accent="#FFC933", panel="#3E8EF7", panel2="#2361D6",
                    inner="#9FD2FF", outline="#10275C", title=("#FFFFFF", "#FFE25A"), bg=("#7FD3FF", "#3E9BF0")),
    "Candy": dict(keywords=["candy", "sweet", "pink", "pastel", "cute", "kawaii", "bubblegum", "sugar"],
                  primary="#FF6FB5", secondary="#B57BFF", accent="#6FE3FF", panel="#FF9ACB", panel2="#E75CA8",
                  inner="#FFE0F0", outline="#6A1B4D", title=("#FFFFFF", "#FFB3E0"), bg=("#FFD1EC", "#C9A5FF")),
    "Ocean": dict(keywords=["ocean", "sea", "water", "aqua", "beach", "fish", "fishing", "island", "teal", "summer"],
                  primary="#1FC8E8", secondary="#2BD9A4", accent="#FFD85A", panel="#1AA7D9", panel2="#0B6FB0",
                  inner="#A9ECFF", outline="#06304F", title=("#FFFFFF", "#8FF3FF"), bg=("#7AE7FF", "#1C8FD6")),
    "Lava": dict(keywords=["lava", "fire", "volcano", "hell", "inferno", "red", "flame", "magma", "dragon"],
                 primary="#FF5A2A", secondary="#FFB02E", accent="#FFE14D", panel="#D8431E", panel2="#8E1D0E",
                 inner="#FFC0A0", outline="#3A0A04", title=("#FFF3B0", "#FF7A1A"), bg=("#FF9B55", "#7A1408")),
    "Forest": dict(keywords=["forest", "nature", "jungle", "green", "farm", "garden", "wood", "tree", "plant"],
                   primary="#4CC94F", secondary="#A9D13C", accent="#FFC94A", panel="#5BAA3C", panel2="#357A26",
                   inner="#D6F5B8", outline="#173A10", title=("#FFFFFF", "#C8FF6A"), bg=("#B5F07A", "#3D9C3A")),
    "Galaxy": dict(keywords=["galaxy", "space", "cosmic", "star", "alien", "planet", "universe", "purple", "moon"],
                   primary="#8A5CFF", secondary="#3FD2FF", accent="#FF6BE6", panel="#3A2A8C", panel2="#1B1248",
                   inner="#8C7BE0", outline="#0A0620", title=("#FFFFFF", "#C9A6FF"), bg=("#4A2F9E", "#0D0A2E")),
    "Neon": dict(keywords=["neon", "cyber", "cyberpunk", "arcade", "retro", "synth", "glow", "techno", "future"],
                 primary="#FF2FD0", secondary="#28F0FF", accent="#F7FF3C", panel="#26214A", panel2="#110E26",
                 inner="#4B3F8E", outline="#05030F", title=("#FFFFFF", "#28F0FF"), bg=("#2A1B5C", "#07051A")),
    "Winter": dict(keywords=["winter", "ice", "snow", "frost", "frozen", "cold", "arctic", "white"],
                   primary="#5CC8FF", secondary="#A6E6FF", accent="#FFFFFF", panel="#E6F6FF", panel2="#A8D8F5",
                   inner="#FFFFFF", outline="#1B4A73", title=("#FFFFFF", "#9FE3FF"), bg=("#E8F8FF", "#8CCBF2")),
    "Spooky": dict(keywords=["spooky", "halloween", "horror", "scary", "ghost", "haunted", "pumpkin", "creepy", "zombie"],
                   primary="#FF8A1F", secondary="#9B4DFF", accent="#7CFF4D", panel="#3A2450", panel2="#1C1028",
                   inner="#6B4A8C", outline="#0C0612", title=("#FFE7B0", "#FF8A1F"), bg=("#4B2A6A", "#120A1C")),
    "Holiday": dict(keywords=["christmas", "xmas", "holiday", "festive", "santa", "noel", "gift"],
                    primary="#E8323C", secondary="#2DB34A", accent="#FFD24A", panel="#C9252E", panel2="#7E1219",
                    inner="#FFE3C4", outline="#3B0507", title=("#FFFFFF", "#FFD24A"), bg=("#FFE9D1", "#2DB34A")),
    "Royal": dict(keywords=["royal", "gold", "golden", "luxury", "rich", "king", "vip", "premium", "money", "bank"],
                  primary="#FFC21A", secondary="#B884FF", accent="#FFFFFF", panel="#2B2440", panel2="#141022",
                  inner="#4E4466", outline="#1A1200", title=("#FFF6C0", "#FFB300"), bg=("#3B3159", "#120E1F")),
    "Desert": dict(keywords=["desert", "sand", "egypt", "pyramid", "western", "cowboy", "canyon", "sun"],
                   primary="#F2A53A", secondary="#E3683B", accent="#56C7D9", panel="#E3B878", panel2="#B77D3E",
                   inner="#FFE9C2", outline="#4A2A0E", title=("#FFF6D8", "#FFB54A"), bg=("#FFE0A3", "#D98E3E")),
    "Toxic": dict(keywords=["toxic", "slime", "radioactive", "acid", "lime", "mutant", "poison"],
                  primary="#8CFF2E", secondary="#C04DFF", accent="#FFE93A", panel="#2E3A1E", panel2="#141A0C",
                  inner="#4D6630", outline="#060A02", title=("#F3FFB0", "#8CFF2E"), bg=("#3B5A1A", "#0C1406")),
    "Pastel": dict(keywords=["pastel", "soft", "cozy", "light", "cafe", "cottage", "bunny", "spring", "easter"],
                   primary="#8FD3FF", secondary="#FFB3C7", accent="#FFE38A", panel="#FFF4E8", panel2="#F2D9C4",
                   inner="#FFFFFF", outline="#6B4E5E", title=("#FFFFFF", "#FFC9D9"), bg=("#FFF1F6", "#D4ECFF")),
    "Military": dict(keywords=["military", "army", "war", "soldier", "tank", "battle", "shooter", "fps", "gun"],
                     primary="#7A8F3C", secondary="#C9A55A", accent="#E8D27A", panel="#4A5530", panel2="#2A3119",
                     inner="#7A8757", outline="#121608", title=("#F2F0D0", "#C9D17A"), bg=("#8C9A63", "#3A4424")),
    "Midnight": dict(keywords=["dark", "midnight", "night", "black", "shadow", "ninja", "minimal", "sleek", "mono"],
                     primary="#4F7CFF", secondary="#3DDC97", accent="#FFD166", panel="#2A2E3A", panel2="#171A22",
                     inner="#3C4252", outline="#07080C", title=("#FFFFFF", "#A9B8FF"), bg=("#2E3446", "#0E1016")),
    "Sunset": dict(keywords=["sunset", "tropical", "orange", "summer", "vibes", "paradise", "evening"],
                   primary="#FF7A45", secondary="#FF4F8B", accent="#FFD24A", panel="#FF9A5A", panel2="#E0507A",
                   inner="#FFE3C9", outline="#4A1024", title=("#FFFFFF", "#FFD24A"), bg=("#FFB36B", "#B44C9E")),
}

COLOR_WORDS = {
    "red": "#E8323C", "orange": "#FF8A1F", "yellow": "#FFD21F", "gold": "#FFC21A", "green": "#43D162",
    "lime": "#8CFF2E", "teal": "#1FC8C0", "cyan": "#28F0FF", "blue": "#2F7BFF", "navy": "#1F3F9E",
    "purple": "#8A5CFF", "violet": "#A35CFF", "pink": "#FF6FB5", "magenta": "#FF2FD0", "white": "#F4F7FF",
    "black": "#23252E", "gray": "#8A93A6", "grey": "#8A93A6", "brown": "#9A6A3A",
}

GAME_TYPES = {
    "simulator": ["simulator", "sim", "clicker", "pet", "pets", "egg", "collect", "mining", "farm"],
    "tycoon": ["tycoon", "factory", "business", "restaurant", "store", "shop", "empire", "money"],
    "obby": ["obby", "parkour", "tower", "jump", "platformer", "stage"],
    "fighting": ["fighting", "fight", "pvp", "battle", "combat", "sword", "anime", "boss", "arena"],
    "horror": ["horror", "scary", "survival", "escape", "creepy", "backrooms"],
    "racing": ["racing", "race", "car", "cars", "drift", "kart", "driving"],
    "rpg": ["rpg", "adventure", "quest", "dungeon", "fantasy", "rpg", "mmo"],
}


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def theme_from_prompt(prompt):
    """Pick a theme, a game type and an optional "quoted title" from free text."""
    title = None
    m = re.search(r'"([^"]+)"|\'([^\']+)\'', prompt)
    if m:
        title = (m.group(1) or m.group(2)).strip()
        prompt = prompt.replace(m.group(0), " ")
    words = re.findall(r"[a-z0-9]+", prompt.lower())
    best, score = "Classic", 0
    for name, t in THEMES.items():
        s = sum(2 if w == name.lower() else 1 for w in words if w in t["keywords"] or w == name.lower())
        if s > score:
            best, score = name, s
    theme = dict(THEMES[best], name=best)
    # a colour word overrides the main button colour ("candy blue" -> blue buttons, candy panels)
    colours = [w for w in words if w in COLOR_WORDS]
    if colours and colours[0] not in THEMES[best]["keywords"]:
        theme["primary"] = COLOR_WORDS[colours[0]]
        theme["name"] = f"{best}{colours[0].title()}"
    game = "simulator"
    for g, kws in GAME_TYPES.items():
        if any(w in kws for w in words):
            game = g
            break
    theme["studs"] = not any(w in ("smooth", "clean", "flat", "nostud", "nostuds") for w in words)
    theme["font"] = ("LuckiestGuy" if any(w in ("cartoon", "comic", "luckiest") for w in words) else
                     "LilitaOne" if any(w in ("lilita", "chunky") for w in words) else "FredokaBold")
    return theme, title, game
