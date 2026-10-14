"""Example livery: the starting point for new liveries, built the way LIVERY_GUIDE section 0 says.

A light base, one bold side sweep with an accent shard tucked under it, a centre stripe, and the depth
passes (shadow, facets, glint) that make flat shapes look finished. It shows the moving parts every
livery needs: load the template layers, derive a palette with shades, draw the car's LEFT side once and
mirror it onto the upside-down right side, keep template trim above the art, write the paint, a spec
map, a preview, and a layered file organised like a hand-made one:

    Turn Off Before Exporting TGA (hidden)   mask, wireframe, number + sponsor blocks
    Paintable Area
      trim / decals (template)               above all the art
      Top/                                   hood-roof-trunk centre stripe
      Right side/                            = Left side flipped about the centre line
      Left side/                             sweep, shadow, facets, glint, accent shard
      base

    cd liveries/example
    ../../.venv/bin/python livery.py bmw-m4-gt3 -> bmw-m4-gt3/out/example_bmw-m4-gt3.tga, _spec.tga, _preview.png, .ora, .xcf, _spec.ora
    ../../.venv/bin/python livery.py mclaren-720s-gt3

Read ../../LIVERY_GUIDE.md (section 0 first) and ../../cars/<car>/README.md before placing anything.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from psd_tools import PSDImage

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import depth  # noqa: E402
import lowpoly  # noqa: E402
import ora  # noqa: E402
import ora2xcf  # noqa: E402
import paths  # noqa: E402
import seams  # noqa: E402

SIZE = 2048

# Per-car template facts (see ../../cars/<car>/README.md). Put your PSDs in psd/.
CARS = {
    "bmw-m4-gt3": dict(psd="BMW M4 GT3.psd", mask="Mask", trim="Carbon Fiber", top="Car_decal",
                rough=("Custom Spec", "rough"), mirror_y=1311.5,
                guides=dict(wire="wire", numbers="Number Blocks", sponsors="Sponsor"),
                # left side, door/sill band (upright panel, larger y = car's left)
                stripe=dict(x0=560, x1=1800, y_top=1760, y_bot=1900)),
    "mclaren-720s-gt3": dict(psd="McLaren 720s EVO GT3.psd", mask="Mask", trim="Car_decal", top=None,
                    rough=("Custom Spec Map", "Green Channel Roughness"), mirror_y=1206.5,
                    guides=dict(wire="Wire", numbers="Number Blocks", sponsors="Sponsor Blocks"),
                    stripe=dict(x0=330, x1=1700, y_top=1760, y_bot=1880)),
}
# A tiny palette: light base, one main colour, one accent. Shades come from depth.shades().
BASE, MAIN, ACCENT = "#F4F4F0", "#1E6FD9", "#FFB300"
# (metallic, roughness) 0-255, one value per paint colour; material contrast reads best (LIVERY_GUIDE 5, 13b)
SPEC = {"base": (74, 77), "main": (107, 101), "accent": (0, 60)}


def layer(psd, name):
    if name is None:
        return Image.new("RGBA", (SIZE, SIZE))
    lyr = next(l for l in psd.descendants() if l.name == name and l.kind == "pixel")
    # layer_filter: also render the hidden guide layers (Wire, Number Blocks...)
    return lyr.composite(viewport=(0, 0, SIZE, SIZE), layer_filter=lambda l: True).convert("RGBA")


def spec_group(psd, group, sub):
    """The template's own trim roughness lives in a hidden group; flatten it."""
    grp = next(g for g in next(l for l in psd if l.name == group) if g.name == sub)
    out = Image.new("RGBA", (SIZE, SIZE))
    for lyr in grp:
        if lyr.kind == "pixel":
            out.alpha_composite(lyr.topil().convert("RGBA"), lyr.offset)
    return out


def curve(p0, ctrl, p1, n=24):
    """Points along a quadratic Bezier (excluding p1): body graphics usually curve."""
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * ctrl[0] + t * t * p1[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * ctrl[1] + t * t * p1[1])
            for t in (i / n for i in range(n))]


def shape(*polys):
    m = Image.new("L", (SIZE, SIZE))
    d = ImageDraw.Draw(m)
    for p in polys:
        d.polygon(p, fill=255)
    return np.asarray(m)


_cars = {}


def flip(rgba, mid, key=None):
    """A whole layer reflected about the centre line y = mid (the car's right side is upside down).
    With a seam-mapped car, panels whose twin sits off the exact reflection (BMW right front fender:
    27 px) are resampled from their twin (seams.Car.flip, LIVERY_GUIDE 4b)."""
    if key and os.path.exists(os.path.join(REPO, "cars", key, "islands.npz")):
        car = _cars.setdefault(key, seams.Car(key))
        if car.mirror_y == mid:
            return car.flip(rgba)
    src = np.round(2 * mid - np.arange(SIZE)).astype(int)
    out = np.zeros_like(rgba)
    ok = (src >= 0) & (src < SIZE)
    out[ok] = rgba[src[ok]]
    return out


def build(key):
    car = CARS[key]
    psd = PSDImage.open(os.path.join(REPO, "psd", car["psd"]))
    mask, trim, top = layer(psd, car["mask"]), layer(psd, car["trim"]), layer(psd, car["top"])
    s, mid = car["stripe"], car["mirror_y"]
    main, accent = depth.shades(MAIN), depth.shades(ACCENT)

    # LEFT side, designed once. Shapes run past the panel edges: the template clips them (section 0).
    # The sweep is thin at the nose and swells rearward, ending in a rear-pointing tip.
    tip = (s["x1"] + 160, s["y_top"] + 40)
    sweep = shape(curve((s["x0"] - 120, s["y_bot"] - 20), (s["x0"] + 500, s["y_top"] + 40), (s["x1"], s["y_top"]))
                  + [tip, (s["x1"] - 60, s["y_bot"] + 30), (s["x0"] - 120, s["y_bot"] + 30)])
    # accent shard tucked under the sweep's top edge (it starts from the sweep, never floats alone)
    shard = shape([(s["x0"] + 300, s["y_top"] + 70), (s["x1"] + 60, s["y_top"] - 40), (s["x1"] - 200, s["y_top"] + 10)])
    # glint: a light sliver inside the sweep, fading out toward the nose
    glint = shape([(s["x0"] + 500, s["y_bot"] - 15), (s["x1"] - 100, s["y_top"] + 50), (s["x1"] - 140, s["y_top"] + 70),
                   (s["x0"] + 520, s["y_bot"] - 5)])
    tex = lowpoly.texture((SIZE, SIZE), main["dark"], main["light"], seed=3)
    left = [
        ("accent shard", depth.flat(accent["base"], shard)),
        ("sweep", depth.flat(main["base"], sweep)),
        ("sweep shadow", depth.shadow(sweep, (s["x0"], s["y_top"]), (s["x0"] + 700, s["y_top"]), strength=0.4)),
        ("sweep facets", lowpoly.overlay(tex, sweep, feather=50, keep=0.65, seed=3)),
        ("sweep glint", depth.fade(depth.flat("#FFFFFF", glint), (s["x1"], s["y_top"]), (s["x0"] + 500, s["y_bot"]), 0.55, 0)),
    ]
    # Top: centre stripe over hood, roof and trunk (symmetric about the centre line already)
    centre = shape([(0, mid - 45), (SIZE, mid - 45), (SIZE, mid + 45), (0, mid + 45)])
    topl = [("centre stripe", depth.flat(main["base"], centre)),
            ("centre stripe facets", lowpoly.overlay(tex, centre, feather=20, keep=0.8, seed=5))]

    P, G = ("Paintable Area",), ("Turn Off Before Exporting TGA",)
    g = car["guides"]
    layers = [ora.Layer("base", Image.new("RGBA", (SIZE, SIZE), BASE), group=P)]
    layers += [ora.Layer(n, Image.fromarray(a), group=P + ("Left side",)) for n, a in left]
    layers += [ora.Layer(n, Image.fromarray(flip(a, mid, key)), group=P + ("Right side",)) for n, a in left]
    layers += [ora.Layer(n, Image.fromarray(a), group=P + ("Top",)) for n, a in topl]
    layers += [ora.Layer("trim (template)", trim, group=P),      # template trim stays above the art
               ora.Layer("decals (template)", top, group=P)]
    layers += [ora.Layer(n, layer(psd, l), group=G) for n, l in (
        ("number blocks", g["numbers"]), ("sponsor blocks", g["sponsors"]), ("wireframe", g["wire"]),
        ("mask (not paintable)", car["mask"]))]
    layers = [l for l in layers if l.image.getbbox()]  # skip empty ones (McLaren has no decal layer)
    OUT = paths.out_dir(os.path.dirname(os.path.abspath(__file__)), key)
    img = ora.write(os.path.join(OUT, f"example_{key}.ora"), layers, hidden_groups=[G])
    img.convert("RGB").save(os.path.join(OUT, f"example_{key}.tga"))   # 24-bit, no alpha
    ora2xcf.convert(os.path.join(OUT, f"example_{key}.ora"))          # GIMP file, if GIMP 3 is installed

    # Spec: R = metallic, G = roughness, B = clearcoat (0 = full clearcoat, like the templates).
    # One flat value per paint colour; trim keeps the template's own roughness. One layer per finish.
    rough = np.array(spec_group(psd, *car["rough"]))[..., 1].astype(np.uint8)
    body = np.array(trim)[..., 3] < 128
    on_main = (sweep > 127) | (flip(np.dstack([sweep] * 4), mid, key)[..., 0] > 127) | (centre > 127)
    on_accent = ((shard > 127) | (flip(np.dstack([shard] * 4), mid, key)[..., 0] > 127)) & ~on_main

    def finish(where, mv, rv):
        rgba = np.zeros((SIZE, SIZE, 4), np.uint8)
        rgba[..., 0], rgba[..., 1], rgba[..., 3] = mv, rv, where * 255
        return Image.fromarray(rgba)

    spec_layers = [
        ora.Layer("trim roughness (template)", Image.fromarray(
            np.stack([np.zeros_like(rough), rough, np.zeros_like(rough), np.full_like(rough, 255)], -1))),
        ora.Layer("base finish", finish(body & ~on_main & ~on_accent, *SPEC["base"])),
        ora.Layer("main colour finish", finish(body & on_main, *SPEC["main"])),
        ora.Layer("accent finish", finish(body & on_accent, *SPEC["accent"])),
        ora.Layer("GUIDE paint (for reference)", img, visible=False, opacity=0.5),
    ]
    spec = ora.write(os.path.join(OUT, f"example_{key}_spec.ora"), spec_layers)
    spec.convert("RGB").save(os.path.join(OUT, f"example_{key}_spec.tga"))

    prev = img.copy()
    prev.alpha_composite(mask)                         # mask alpha = NOT paintable
    prev.convert("RGB").save(os.path.join(OUT, f"example_{key}_preview.png"))
    print("wrote", os.path.join(OUT, f"example_{key}.tga"))


if __name__ == "__main__":
    args = sys.argv[1:]
    build(paths.pick_car(args, CARS, "bmw-m4-gt3"))
