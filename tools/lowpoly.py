"""Low-poly ("faceted") shading texture, the way the GFR V2 paint shades its orange (LIVERY_GUIDE 14).

    import lowpoly
    tex = lowpoly.texture((2048, 2048), dark="#CE4C00", light="#FF7E18", cell=260, seed=1)   # RGB array
    layer = lowpoly.overlay(tex, shape_alpha, feather=60, keep=0.7)                          # RGBA array

His recipe: flat colour shape underneath, the faceted texture laid over it, cut to the shape with soft
(feathered) edges so the facets fade into the flat colour. `overlay` does the cut + fade.

    python lowpoly.py [out.png]      writes a 2048 sample
"""
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.spatial import Delaunay


def _rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def texture(size, dark="#CE4C00", light="#FF7E18", cell=220, stretch=1.8, jitter=0.45, tilt=0.35, seed=0):
    """Big flat triangles, each one shade between `dark` and `light` (random, plus a gentle slope so
    neighbours relate). `cell` = rough triangle height in px; `stretch` makes them longer along x (the car's
    flow on most sheets), like his facets."""
    w, h = size
    rng = np.random.default_rng(seed)
    cx = cell * stretch
    gx, gy = np.meshgrid(np.arange(-cx, w + 2 * cx, cx), np.arange(-cell, h + 2 * cell, cell * 0.8))
    pts = np.stack([gx.ravel(), gy.ravel()], 1).astype(float)
    pts += rng.uniform(-jitter, jitter, pts.shape) * np.array([cx, cell])
    tri = Delaunay(pts)
    d, l = _rgb(dark), _rgb(light)
    im = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(im)
    ang = rng.uniform(0, np.pi)
    for simplex in tri.simplices:
        p = pts[simplex]
        c = p.mean(0)
        slope = (np.cos(ang) * c[0] + np.sin(ang) * c[1]) / max(w, h)
        t = np.clip(rng.uniform(0, 1) * (1 - tilt) + tilt * (slope % 1), 0, 1)
        draw.polygon([tuple(q) for q in p], fill=tuple(int(v) for v in d + (l - d) * t))
    return np.asarray(im)


def overlay(tex, shape_alpha, feather=60, keep=0.7, seed=0):
    """Cut `tex` to `shape_alpha` (0-255, HxW) with soft edges: alpha fades to 0 over `feather` px inside
    the shape edge, and about (1 - keep) of the shape fades out along a random direction, like his
    hand-erased copies (facets in some places, flat colour showing through in others)."""
    inside = shape_alpha > 127
    dist = ndimage.distance_transform_edt(inside)
    a = np.clip(dist / max(feather, 1), 0, 1)
    rng = np.random.default_rng(seed)
    h, w = inside.shape
    ang = rng.uniform(0, 2 * np.pi)
    yy, xx = np.mgrid[0:h, 0:w]
    ramp = np.cos(ang) * xx + np.sin(ang) * yy
    if inside.any():
        lo, hi = np.percentile(ramp[inside], [100 * (1 - keep) - 15, 100 * (1 - keep) + 15])
        a *= np.clip((ramp - lo) / max(hi - lo, 1), 0, 1)
    a *= shape_alpha / 255
    return np.dstack([tex, (a * 255).astype(np.uint8)])


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "lowpoly_sample.png"
    t = texture((2048, 2048))
    shape = Image.new("L", (2048, 2048))
    ImageDraw.Draw(shape).polygon([(150, 600), (1900, 900), (1700, 1300), (300, 1500)], fill=255)
    base = Image.new("RGBA", (2048, 2048), (240, 240, 240, 255))
    flat = Image.new("RGBA", (2048, 2048), (255, 126, 0, 0))
    flat.putalpha(shape)
    base.alpha_composite(flat)
    base.alpha_composite(Image.fromarray(overlay(t, np.asarray(shape))))
    base.convert("RGB").save(out)
    print("wrote", out)
