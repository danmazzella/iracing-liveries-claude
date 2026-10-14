"""Depth passes over flat shapes: the shading recipe from LIVERY_GUIDE 0 and 14b, for any colour.

    import depth, lowpoly
    pal = depth.shades("#1E6FD9")                         # {"base", "dark", "light", "deep"} hex strings
    shadow = depth.shadow(shape, (x0, y0), (x1, y1))      # black ~60% at (x0,y0) fading to 0 at (x1,y1)
    sliver = depth.fade(colour_layer_rgba, (x0, y0), (x1, y1))   # any layer, alpha ramped along a line
    facets = lowpoly.overlay(lowpoly.texture(size, pal["dark"], pal["light"]), shape)

Stack per shape, bottom -> top: flat colour, shadow, facets, then streak/glint slivers (LIVERY_GUIDE 0).
`shape` is an L-mode image or uint8 array (255 = inside). All functions return RGBA uint8 arrays.
"""
import colorsys

import numpy as np


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _hex(rgb):
    return "#" + "".join(f"{int(round(max(0, min(255, c)))):02X}" for c in rgb)


def shades(colour, dark=0.80, light=1.06, deep=0.70):
    """A colour's working shades by value (brightness): `dark`/`light` bound facet shading,
    `deep` is for streaks. Measured on the GFR orange: #FF7E00 -> facets #CE4C00..#FF7E18 (dark ~0.8),
    navy #2C395B -> streaks #1E273F (deep ~0.7)."""
    r, g, b = (c / 255 for c in _rgb(colour))
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    # shadows lean toward red (warm colours) or deep blue (cool ones), like his orange: hue 30 -> 22 deg
    toward = 0.0 if h <= 1 / 3 else (2 / 3 if h <= 2 / 3 else 1.0)
    shift = float(np.clip((toward - h) * 0.25, -0.025, 0.025))

    def at(k, sat=1.0, hs=0.0):
        return _hex(np.array(colorsys.hsv_to_rgb((h + hs) % 1, min(1, s * sat), min(1, v * k))) * 255)
    return {"base": colour, "dark": at(dark, 1.05, shift), "light": at(light, 0.95),
            "deep": at(deep, 1.05, shift)}


def _ramp(size, start, end):
    """0 at `start`, 1 at `end`, linear along that line, clipped."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.array(end, np.float32) - np.array(start, np.float32)
    t = ((xx - start[0]) * d[0] + (yy - start[1]) * d[1]) / max(float(d @ d), 1.0)
    return np.clip(t, 0, 1)


def fade(rgba, start, end, a0=1.0, a1=0.0):
    """Ramp an RGBA layer's alpha from `a0` at `start` to `a1` at `end`."""
    out = np.array(rgba, np.uint8).copy()
    t = _ramp(out.shape[1::-1], start, end)
    out[..., 3] = (out[..., 3] * (a0 + (a1 - a0) * t)).astype(np.uint8)
    return out


def shadow(shape, start, end, strength=0.62, colour=(0, 0, 0)):
    """Black (or `colour`) at `strength` opacity over `shape`, fading to nothing toward `end`.
    His door shadow: black at ~62% (alpha 158), fading toward the rear."""
    a = np.asarray(shape, np.float32) / 255
    rgba = np.zeros(a.shape + (4,), np.uint8)
    rgba[..., :3] = colour
    rgba[..., 3] = (a * 255).astype(np.uint8)
    return fade(rgba, start, end, strength, 0.0)


def flat(colour, shape):
    """Flat colour where `shape` is set (anti-aliased by the shape's grey levels)."""
    a = np.asarray(shape, np.uint8)
    rgba = np.zeros(a.shape + (4,), np.uint8)
    rgba[..., :3] = _rgb(colour)
    rgba[..., 3] = a
    return rgba
