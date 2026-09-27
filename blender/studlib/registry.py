"""Asset registry: category modules register builder functions here."""

ASSETS = []


def asset(name, category, sub="", origin="bottom", rig=None, tags=(), split=False):
    """Decorator: register ``fn(builder)`` as an asset. ``split``: groups become separate parts."""
    def deco(fn):
        ASSETS.append(dict(name=name, category=category, sub=sub, fn=fn, origin=origin,
                           rig=rig, tags=list(tags), split=split))
        return fn
    return deco


def add(name, category, fn, sub="", origin="bottom", rig=None, tags=(), split=False):
    ASSETS.append(dict(name=name, category=category, sub=sub, fn=fn, origin=origin,
                       rig=rig, tags=list(tags), split=split))
