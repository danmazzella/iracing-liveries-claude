"""Labelled mapping grid for any iRacing car template, plus a layer lister.

The grid is a 32x32 board of 64px coloured cells labelled 'column,row' (cell c,r covers sheet
x c*64..c*64+63, y r*64..r*64+63), with the template's wireframe on top. Install it as the
car's paint, screenshot the car in-sim, and you can read which sheet area paints which part.

    ../.venv/bin/python ../tools/grid.py "My Car.psd"                 list the PSD's layers
    ../.venv/bin/python ../tools/grid.py "My Car.psd" wire mycar     write out/mycar_grid.tga
                                                                      (+ _grid_preview.png)
Run from inside a livery folder (output goes to ./out). The PSD path is relative to the repo
root if it isn't found as given. Layer names differ per template ('wire', 'Wire', ...):
list them first.
"""
import colorsys
import os
import sys

from PIL import Image, ImageDraw, ImageFont
from psd_tools import PSDImage

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZE, CELL = 2048, 64
FONTS = [   # first one that exists wins
    "/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf",   # macOS
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",                                 # Windows
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",         # Linux
]


def open_psd(path):
    if not os.path.exists(path):
        path = os.path.join(REPO, path)
    return PSDImage.open(path)


def list_layers(psd):
    def walk(group, depth):
        for lyr in group:
            print("  " * depth + f"{lyr.name!r}  ({lyr.kind}{'' if lyr.visible else ', hidden'})")
            if lyr.is_group():
                walk(lyr, depth + 1)
    walk(psd, 0)


def layer(psd, name):
    # topil + paste, not composite(): composite() comes back empty for hidden layers (the wire
    # layer usually is)
    lyr = next(l for l in psd.descendants() if l.name == name and l.kind == "pixel")
    full = Image.new("RGBA", (SIZE, SIZE))
    full.paste(lyr.topil().convert("RGBA"), (lyr.left, lyr.top))
    return full


def font(size):
    for f in FONTS:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default(size)


def grid(wire=None, mask=None):
    t = Image.new("RGBA", (SIZE, SIZE))
    d = ImageDraw.Draw(t)
    fnt = font(22)
    for gy in range(SIZE // CELL):
        for gx in range(SIZE // CELL):
            h = (gx * 5 + gy * 3) % 32 / 32
            v = 1.0 if (gx + gy) % 2 else 0.75
            col = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(h, 0.6, v)) + (255,)
            d.rectangle((gx * CELL, gy * CELL, (gx + 1) * CELL - 1, (gy + 1) * CELL - 1), fill=col)
            d.text((gx * CELL + 4, gy * CELL + 20), f"{gx},{gy}", font=fnt, fill=(0, 0, 0, 255))
    for i in range(0, SIZE, 256):   # heavy lines every 256px (4 cells)
        d.line((i, 0, i, SIZE), fill=(0, 0, 0, 255), width=4)
        d.line((0, i, SIZE, i), fill=(0, 0, 0, 255), width=4)
    if wire is not None:
        t.alpha_composite(wire)
    prev = t.copy()
    if mask is not None:
        prev.alpha_composite(mask)
    return t.convert("RGB"), prev.convert("RGB")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    psd = open_psd(args[0])
    if len(args) == 1:
        list_layers(psd)
        sys.exit()
    wire_name, key = args[1], (args[2] if len(args) > 2 else "car")
    mask_name = args[3] if len(args) > 3 else "Mask"
    try:
        mask = layer(psd, mask_name)
    except StopIteration:
        mask = None
        print(f"no layer {mask_name!r}: preview has no mask")
    tga, prev = grid(layer(psd, wire_name), mask)
    out = os.path.join(os.getcwd(), "out")
    os.makedirs(out, exist_ok=True)
    tga.save(os.path.join(out, f"{key}_grid.tga"))
    prev.save(os.path.join(out, f"{key}_grid_preview.png"))
    print("wrote", os.path.join(out, f"{key}_grid.tga"))
