"""Simulator upgrade tiers. Tools and weapons are built once and painted per tier.

The gem tiers match the tints used on the animal bundle (Gold, Diamond, Emerald,
Ruby, Rainbow) so upgrades read the same everywhere in a game.
"""
from .geo import RAINBOW, rainbow

RB = "RAINBOW"

TIERS = {
    "Wood": dict(main="wood_light", dark="wood_mid", light="wood_pale", handle="wood_dark",
                 grip="leather", grip2="leather_dark", accent="wood_mid", gem="wood_pale"),
    "Stone": dict(main="stone", dark="stone_dark", light="stone_light", handle="wood",
                  grip="leather", grip2="leather_dark", accent="stone_dark", gem="stone_light"),
    "Iron": dict(main="iron", dark="iron_dark", light="silver", handle="wood_mid",
                 grip="leather_dark", grip2="charcoal", accent="iron_dark", gem="silver"),
    "Gold": dict(main="gold", dark="gold_dark", light="gold_light", handle="wood_dark",
                 grip="fabric_red", grip2="rug_red", accent="gold_dark", gem="ruby"),
    "Diamond": dict(main="diamond", dark="diamond_dark", light="diamond_light", handle="iron_dark",
                    grip="fabric_navy", grip2="charcoal", accent="silver", gem="diamond_light"),
    "Emerald": dict(main="emerald", dark="emerald_dark", light="emerald_light", handle="charcoal",
                    grip="fabric_green", grip2="leaf_deep", accent="gold", gem="emerald_light"),
    "Ruby": dict(main="ruby", dark="ruby_dark", light="ruby_light", handle="charcoal",
                 grip="black", grip2="ruby_dark", accent="gold", gem="ruby_light"),
    "Rainbow": dict(main=RB, dark="rb_purple", light="white", handle="charcoal",
                    grip="fabric_purple", grip2="rb_pink", accent="gold", gem=RB),
}
ORDER = list(TIERS.keys())


def paint(T, role, axis="z", lo=0.0, hi=1.0, **extra):
    """Keyword args for a primitive: ``color`` (and plane ``cuts`` for rainbow bands)."""
    c = T[role]
    if c != RB:
        return dict(color=c, **extra)
    n = len(RAINBOW)
    step = (hi - lo) / n
    cuts = {axis: [lo + step * k for k in range(1, n)]}
    return dict(color=rainbow(axis, lo, hi), cuts=cuts, **extra)


def solid(T, role, fallback="rb_cyan"):
    """A single colour for small parts (rainbow gets a bright stand-in)."""
    c = T[role]
    return fallback if c == RB else c
