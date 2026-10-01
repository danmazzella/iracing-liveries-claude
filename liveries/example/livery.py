"""Minimal example livery: two-tone body, a curved side stripe, a centre stripe, gloss spec.

A starting point to copy into your own livery folder. It shows the moving parts every livery
needs: load the template layers, draw in sheet coordinates, mirror side graphics onto the
upside-down right-side panel, composite the template trim on top, write the paint, a spec map
and a preview with the not-paintable mask drawn over it.

Each part is drawn on its own layer and also saved as layered OpenRaster files (.ora) that GIMP
and Krita open: out/example_<car>.ora (paint) and _spec.ora (finish). Use them to finish a design
by hand (LIVERY_GUIDE section 11).

    cd example
    ../../.venv/bin/python livery.py bmw-m4-gt3 -> bmw-m4-gt3/out/example_bmw-m4-gt3.tga, _spec.tga, _preview.png, .ora, _spec.ora
    ../../.venv/bin/python livery.py mclaren-720s-gt3

Read ../../LIVERY_GUIDE.md and ../../cars/<car>/README.md before placing anything.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from psd_tools import PSDImage

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))
import ora  # noqa: E402
import paths  # noqa: E402

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
BASE, STRIPE = "#F4F4F0", "#1E6FD9"      # body colour, graphic colour
SPEC = {"base": (0, 10), "stripe": (120, 6)}   # (metallic, roughness) 0-255; lower rough = shinier


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


def mirrored(poly, mid):
    """Same shape on the car's right side: the sheet is mirrored about y = mid."""
    return [(x, 2 * mid - y) for x, y in poly]


def build(key):
    car = CARS[key]
    psd = PSDImage.open(os.path.join(REPO, "psd", car["psd"]))
    mask, trim, top = layer(psd, car["mask"]), layer(psd, car["trim"]), layer(psd, car["top"])

    shape = Image.new("L", (SIZE, SIZE))              # where the stripe is, for the spec map
    d = ImageDraw.Draw(shape)

    # Side stripe, designed once for the car's left side: thin at the nose, swelling rearward,
    # with a curved top edge. Then mirrored onto the right side.
    s, mid = car["stripe"], car["mirror_y"]
    poly = (curve((s["x0"], s["y_bot"] - 30), (s["x0"] + 500, s["y_top"] + 40), (s["x1"], s["y_top"]))
            + [(s["x1"], s["y_bot"]), (s["x0"], s["y_bot"])])
    d.polygon(poly, fill=255)
    d.polygon(mirrored(poly, mid), fill=255)
    # Centre stripe over hood, roof and trunk: symmetric about the mirror line already
    d.rectangle((0, mid - 45, SIZE, mid + 45), fill=255)

    # One layer per part, bottom -> top. The TGA is the flattened visible layers, the .ora keeps
    # them apart (plus hidden template guides) for hand editing.
    g = car["guides"]
    layers = [
        ora.Layer("base", Image.new("RGBA", (SIZE, SIZE), BASE)),
        ora.Layer("stripe", ora.paint_layer(STRIPE, shape)),
        ora.Layer("trim (template)", trim),              # carbon/black trim over the paint
        ora.Layer("decals (template)", top),             # template decals that must stay on top
        ora.Layer("GUIDE number blocks", layer(psd, g["numbers"]), visible=False),
        ora.Layer("GUIDE sponsor blocks", layer(psd, g["sponsors"]), visible=False),
        ora.Layer("GUIDE wireframe", layer(psd, g["wire"]), visible=False),
        ora.Layer("GUIDE mask (not paintable)", mask, visible=False),
    ]
    layers = [l for l in layers if l.image.getbbox()]  # skip empty ones (McLaren has no decal layer)
    OUT = paths.out_dir(os.path.dirname(os.path.abspath(__file__)), key)
    img = ora.write(os.path.join(OUT, f"example_{key}.ora"), layers)
    img.convert("RGB").save(os.path.join(OUT, f"example_{key}.tga"))   # 24-bit, no alpha

    # Spec: R = metallic, G = roughness, B = clearcoat (0 = full clearcoat, like the templates).
    # Trim keeps the template's own roughness.
    # Trim keeps the template's own roughness. One layer per finish, like the paint.
    rough = np.array(spec_group(psd, *car["rough"]))[..., 1].astype(np.uint8)
    body = np.array(trim)[..., 3] < 128
    on_stripe = np.array(shape) > 127

    def finish(where, mv, rv):
        rgba = np.zeros((SIZE, SIZE, 4), np.uint8)
        rgba[..., 0], rgba[..., 1], rgba[..., 3] = mv, rv, where * 255
        return Image.fromarray(rgba)

    spec_layers = [
        ora.Layer("trim roughness (template)", Image.fromarray(
            np.stack([np.zeros_like(rough), rough, np.zeros_like(rough), np.full_like(rough, 255)], -1))),
        ora.Layer("base finish", finish(body & ~on_stripe, *SPEC["base"])),
        ora.Layer("stripe finish", finish(body & on_stripe, *SPEC["stripe"])),
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
