"""Asset registry: category modules register builder functions here."""

ASSETS = []


def asset(name, category, sub="", origin="bottom", rig=None, tags=()):
    """Decorator: register ``fn(builder)`` as an asset."""
    def deco(fn):
        ASSETS.append(dict(name=name, category=category, sub=sub, fn=fn, origin=origin,
                           rig=rig, tags=list(tags)))
        return fn
    return deco


def add(name, category, fn, sub="", origin="bottom", rig=None, tags=()):
    ASSETS.append(dict(name=name, category=category, sub=sub, fn=fn, origin=origin,
                       rig=rig, tags=list(tags)))
