"""Brief kit for an AI image model: a labelled panel atlas of a car's paint sheet plus a prompt.

    ../../.venv/bin/python ../../tools/aibrief.py bmw-m4-gt3 ["design description"]

Writes cars/<car>/ai/:
  guide_atlas.png  every named panel filled with its own colour + its name, unpaintable area
                   dark, centre line dashed, front arrow. Feed this to the image model as the
                   layout to paint on.
  guide_wire.png   white sheet with the template wireframe + unpaintable mask only
  prompt.md        the rules and region table to paste with the images

Needs cars/<car>/regions.json (panel code -> name, see the BMW one) and the seam ruler
(cars/<car>/islands.npz from tools/seams.py ruler). Bring the model's answer back with
tools/aiingest.py.
"""
import colorsys
import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import grid  # noqa: E402
import seams  # noqa: E402

SIZE = 2048


def load(key):
    p = os.path.join(REPO, "cars", key, "regions.json")
    if not os.path.exists(p):
        sys.exit(f"cars/{key}/regions.json missing: map panel codes to names first (see cars/bmw-m4-gt3/regions.json)")
    return json.load(open(p, encoding="utf-8"))


def template(key):
    return grid.open_psd(seams.template_path(key))


def masks(psd, cfg):
    """(unpaintable bool array, wire RGBA array or None)."""
    m = seams.psd_layer(psd, cfg["mask"].lower())
    unpaintable = m[..., 3] > 127 if m is not None else np.zeros((SIZE, SIZE), bool)
    return unpaintable, seams.psd_layer(psd, "wire")


def covered(psd, cfg, car):
    """Pixels the template's trim/decal layers draw over the paint (carbon pieces, logos, number card)."""
    cov = np.zeros((SIZE, SIZE), bool)
    for k in ("trim", "top"):
        l = seams.psd_layer(psd, cfg[k].lower()) if cfg.get(k) else None
        if l is not None:
            cov |= l[..., 3] > 127
    for code in cfg.get("over_trim", []):
        cov &= ~car.mask(code, grow=2)
    return cov


def number_blocks(psd, cfg, grow=45):
    """Where iRacing draws the number plate (bigger than the block itself), as a bool array."""
    n = seams.psd_layer(psd, cfg["numbers"].lower()) if cfg.get("numbers") else None
    if n is None:
        return np.zeros((SIZE, SIZE), bool)
    from scipy import ndimage
    return ndimage.binary_dilation(n[..., 3] > 127, iterations=grow)


def colour(i):
    import colorsys as cs
    return tuple(int(c * 255) for c in cs.hsv_to_rgb((i * 0.618) % 1, 0.35, 0.97))


def legend(cfg):
    """Separate image: swatch + name per panel (the atlas itself carries no text, models copy text)."""
    names = cfg["regions"]
    im = Image.new("RGB", (1100, 70 * len(names) + 140), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((20, 15), "LEGEND (reference only, do not draw this)", font=grid.font(36), fill=(0, 0, 0))
    for i, (code, name) in enumerate(names.items()):
        y = 80 + i * 70
        d.rectangle((20, y, 100, y + 52), fill=colour(i), outline=(0, 0, 0))
        d.text((120, y + 26), f"{code}: {name}", font=grid.font(30), fill=(0, 0, 0), anchor="lm")
    y = 80 + len(names) * 70
    d.rectangle((20, y, 100, y + 52), fill=(70, 70, 70), outline=(0, 0, 0))
    d.text((120, y + 26), "dark grey: not paintable", font=grid.font(30), fill=(0, 0, 0), anchor="lm")
    return im


def atlas(car, cfg, unpaintable, wire, numbers=None, labels=False):
    names = cfg["regions"]
    img = np.full((SIZE, SIZE, 3), 235, np.uint8)
    img[car.labels > 0] = (246, 246, 246)               # unnamed panels
    for i, code in enumerate(names):
        h = (i * 0.618) % 1
        img[car.mask(code, grow=3)] = [int(c * 255) for c in colorsys.hsv_to_rgb(h, 0.35, 0.97)]
    img[unpaintable] = (70, 70, 70)
    im = Image.fromarray(img)
    if wire is not None:
        w = Image.fromarray(wire)
        a = w.getchannel("A").point(lambda v: int(v * 0.35))
        w.putalpha(a)
        im = Image.alpha_composite(im.convert("RGBA"), w).convert("RGB")
    d = ImageDraw.Draw(im)
    if numbers is not None and numbers.any():
        from scipy import ndimage
        lab, n = ndimage.label(numbers)
        for i in range(1, n + 1):
            ys, xs = np.nonzero(lab == i)
            box = (xs.min(), ys.min(), xs.max(), ys.max())
            d.rectangle(box, fill=(255, 255, 255), outline=(150, 150, 150), width=3)
    mid = cfg["mirror_y"]
    if not labels:
        return im
    for x in range(0, SIZE, 40):
        d.line((x, mid, x + 20, mid), fill=(220, 0, 0), width=3)
    for i, (code, name) in enumerate(names.items()):
        cx, cy = car.panels[code]["centre"]
        big = car.panels[code]["area"] > 100000
        short = name.split(":")[0].split("(")[0].strip()
        if not big:                                   # narrow panels: code only, staggered off the centre line
            cy += (-50 if i % 2 else 50) if abs(cy - mid) < 80 else 0
        cx = min(max(cx, 130 if big else 40), SIZE - (130 if big else 40))
        d.text((cx, cy), f"{code} {short}" if big else code, font=grid.font(44 if big else 40),
               fill=(0, 0, 0), anchor="mm")
    d.text((60, 20), "FRONT OF CAR at the LEFT edge  (red dashes = car centre line)",
           font=grid.font(34), fill=(200, 0, 0))
    return im


def prompt(key, cfg, design):
    style = (design or "<describe the style>").split("\n\n", 1)[0].strip().rstrip(".")
    rows = "\n".join(f"- **{c}**: {n}" for c, n in cfg["regions"].items())
    avoid = "\n".join(f"- {a}" for a in cfg.get("avoid", []))
    return f"""# AI brief: {key}

Attach: `guide_atlas.png` (layout to paint on, no text on it), `guide_legend.png` (colour -> panel names) and `guide_wire.png` (panel outlines).

## Prompt

This image is a flat 2048x2048 UV paint sheet for a race car ({key}), not a picture of a car.
Every coloured region is a body panel (image 2 names each colour). Dark grey areas are not paintable
(leave them dark grey). Redraw the sheet as the finished livery artwork:

DESIGN: {design or "<describe the livery here: colours, style, graphics>"}

Rules:
- Same size, same layout: every panel stays exactly where it is, edges do not move.
- Paint inside each coloured region only; fill it edge to edge with artwork, no labels, no outlines.
- Flat 2D artwork as it would print on vinyl: no 3D rendering, no lighting, shadows or reflections.
- Solid flat colours with crisp edges. No gradients, glows, blurs, soft shading or smudged blends,
  and no colour bleeding across panel edges. Navy and orange stay saturated; whites stay clean white.
- The sheet is mirrored about the horizontal centre of the sheet (front of the car at the LEFT). The lower
  half is the car's left side, the upper half its right side (upside down). Make the upper half
  a vertical mirror image of the lower half, except text/logos (those must read correctly).
- Plain white rectangles with a thin grey outline are where the car number plate goes: leave them
  plain white, no outline, and keep every logo, text and mascot completely outside them (at least
  a box-width away). Put wide logos on the long open stretch of the side panel, well behind or in
  front of the number plate, never starting next to it.
- The wing (E) is a normal panel: paint it with bold flat colour or stripes, never grey.
- The output must contain NO text from this brief: no panel names, no "NUMBER", no title line, no
  dashed centre line, no legend.
- No car numbers, no sponsor boxes, no small text.
- If a fourth image is attached it is a 3D concept render of the finished car: copy its colours, shapes and
  style only, never its perspective, and never draw anything but the flat sheet layout.
- Keep graphics bold and simple: they are seen from a distance on a curved car.

Regions:
{rows}

Keep clear of (3D parts cover paint here):
{avoid}

## Base pass (the pattern layer, opaque)

Same images. Use the Prompt above but replace the whole DESIGN paragraph with:

DESIGN: PATTERN ONLY. {style}. Cover every coloured panel with a white and light-grey hexagon (honeycomb)
mosaic, tiles slightly greyer toward the rear. NO slashes, NO logos, NO mascots, NO orange or navy. Keep the dark grey
areas dark grey and the number rectangles plain white.

## Element pass (one layer, for models without transparency)

Same images. Paste this instead of the Prompt above, once per layer:

This image is a flat 2048x2048 UV paint sheet for a race car, not a picture of a car (image 2 names each
colour). Keep the exact same layout. Draw ONLY this element: <ELEMENT>. Draw nothing else.
Style: {style}.
- Fill EVERYTHING else, every panel, the background and the dark areas, with one flat solid magenta #FF00FF.
  No base colour, no pattern, no shadows, no outlines, no gradients, no glow, no anti-aliasing halo.
- The element itself is flat 2D vinyl art with crisp edges. Never use magenta, pink or purple in the element.
- The element sits inside the coloured panels, clear of the dark grey areas and of the plain white number
  rectangles. No text from this brief copied into the image, no car numbers.
- Mirror rule: the lower half is the car's left side, the upper half its right side (upside down). Draw the
  element on both halves, mirrored, with text/logos reading correctly.

## Bring it back

    ../../.venv/bin/python ../../tools/aiingest.py {key} <model_output.png> --name mydesign [--mirror]

Element passes: base image first (the pattern/colour pass), then
    ... --layer navy=navy.png --layer text=text.png --key "#FF00FF" --split
"""


def messages(key, cfg, design, out):
    """One ready-to-paste text file per Gemini message: 1 base, then one per element in the design file."""
    import re
    md = os.environ.get("AI_DESIGN_FILE")
    full = prompt(key, cfg, design)
    main_p = full.split("## Prompt", 1)[1].split("## Base pass", 1)[0].strip()
    base_design = full.split("## Base pass", 1)[1].split("DESIGN:", 1)[1].split("## Element pass", 1)[0].strip()
    base_msg = re.sub(r"DESIGN:.*?\n\nRules:", "DESIGN: " + base_design + "\n\nRules:", main_p, flags=re.S)
    tmpl = full.split("## Element pass", 1)[1].split("## Bring it back", 1)[0].split("\n\n", 2)[2].strip()
    d = os.path.join(out, "messages")
    os.makedirs(d, exist_ok=True)
    note = ("Attach these 4 images first: guide_atlas.png, guide_legend.png, guide_wire.png, concept_gofast.webp\n"
            "(new Gemini chat for every message). Then paste everything below the line.\n------------------------------\n")
    open(os.path.join(d, "1_base.txt"), "w", encoding="utf-8").write(note + base_msg + "\n")
    if not md:
        return
    text = open(md, encoding="utf-8").read().split("\n---", 1)[1]
    names = {"NAVY": "2_navy", "ORANGE": "3_orange", "TEXT": "4_text", "MASCOT": "5_mascot", "WING": "6_wing"}
    for m in re.finditer(r"^\d\. ([A-Z]+)(?: \(base\))?: (.*)$", text, re.M):
        if m.group(1) in names:
            el = m.group(2).strip().rstrip(".")
            open(os.path.join(d, names[m.group(1)] + ".txt"), "w", encoding="utf-8").write(
                note + tmpl.replace("<ELEMENT>", el) + "\n")


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    key, design = args[0], " ".join(args[1:])
    if design.startswith("@"):                       # design text from a file: @liveries/gofast/ai_concept.md (text above "---")
        design = open(design[1:], encoding="utf-8").read().split("\n---", 1)[0].strip()
    cfg = load(key)
    car = seams.Car(key)
    psd = template(key)
    unpaintable, wire = masks(psd, cfg)
    cov = covered(psd, cfg, car)
    print(f"template trim/decals cover {cov[~unpaintable].mean():.1%} of the paintable area: shown dark in the atlas")
    unpaintable = unpaintable | cov
    out = os.path.join(REPO, "cars", key, "ai")
    os.makedirs(out, exist_ok=True)
    nb = number_blocks(psd, cfg)
    atlas(car, cfg, unpaintable, wire, nb).save(os.path.join(out, "guide_atlas.png"))
    atlas(car, cfg, unpaintable, wire, nb, labels=True).save(os.path.join(out, "guide_atlas_labelled.png"))
    legend(cfg).save(os.path.join(out, "guide_legend.png"))
    wp = np.full((SIZE, SIZE, 3), 255, np.uint8)
    wp[unpaintable] = (170, 170, 170)
    wim = Image.fromarray(wp).convert("RGBA")
    if wire is not None:
        wim.alpha_composite(Image.fromarray(wire))
    wim.convert("RGB").save(os.path.join(out, "guide_wire.png"))
    open(os.path.join(out, "prompt.md"), "w", encoding="utf-8").write(prompt(key, cfg, design))
    if args[1:2] and args[1].startswith("@"):
        os.environ["AI_DESIGN_FILE"] = args[1][1:]
    messages(key, cfg, design, out)
    print("wrote", out)


if __name__ == "__main__":
    main()
