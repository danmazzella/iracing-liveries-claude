"""Turn an AI model's image into a paint layer for a car.

    ../../.venv/bin/python ../../tools/aiingest.py bmw-m4-gt3 model_output.png --name mydesign [--mirror] [--base "#F4F4F0"]
       [--layer logo=file.png[~#1E2744,#hex] ...] [--key "#FF00FF"] [--split] [--dodge text,mascot]   element passes over the art (key colour -> transparent);
       --dodge: those split layers slide rearward off the number plates (logos, not body graphics)
       --split puts every separate shape/logo of a layer on its own layer ("logo 1 @x,y", ...)
    run from inside a livery folder: writes <car>/out/ai_<name>_<car>.{tga,png,ora} + _preview.png

What it does to the model's picture:
  1. resize to 2048x2048 (the model's output size rarely matches)
  2. blend out the red centre line the models copy from the guide
  3. --mirror: copy the lower half (car's left) onto the upper half (car's right) about the
     centre line, wherever the flipped source row exists (the wing and the top strip are left
     as drawn). Text in the art comes out mirrored on the right side: use it for textures.
  4. clip to the paintable area (template Mask), fill the rest of the sheet with --base
  5. composite the template's trim over it (regions.json 'over_trim' panels, e.g. the wing,
     get the art back on top of the trim), then the top decal layer (regions.json names them)
Outputs: the paint TGA, the art alone as an alpha PNG layer, a layered .ora (art / trim /
guides) for finishing by hand, and a preview with the not-paintable mask drawn over it.
"""
import os
import sys

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import aibrief  # noqa: E402
import ora  # noqa: E402
import paths  # noqa: E402
import seams  # noqa: E402

SIZE = 2048


def mirror_lower_to_upper(arr, mid):
    out = arr.copy()
    for y in range(SIZE):
        src = round(2 * mid - y)
        if y < mid and 0 <= src < SIZE:
            out[y] = arr[src]
    return out


def remove_centre_line(arr, mid, half=5):
    """The brief draws a red dashed centre line; models copy it. Blend it out from the rows either side."""
    out = arr.astype(np.float32)
    y0, y1 = int(mid) - half, int(mid) + half
    for y in range(y0, y1 + 1):
        t = (y - y0) / (y1 - y0)
        out[y] = out[y0 - 1] * (1 - t) + out[y1 + 1] * t
    return out.round().astype(np.uint8)


def load_layer(path, key_colour=None, tol=60, drop=()):
    """Sheet-sized element layer -> RGBA. Key colour (e.g. #FF00FF) becomes transparent, edge defringed."""
    from scipy import ndimage
    im = Image.open(path).convert("RGBA")
    if im.size != (SIZE, SIZE):
        im = im.resize((SIZE, SIZE), Image.LANCZOS)
    a = np.asarray(im).copy()
    if key_colour:
        k = np.array([int(key_colour.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)])
        keyed = np.abs(a[..., :3].astype(int) - k).sum(-1) < tol * 3
        if k[0] > 200 and k[2] > 200 and k[1] < 60:      # magenta key: models also paint darker purple/pink variants
            r, g, b = (a[..., i].astype(int) for i in range(3))
            keyed |= (r > 90) & (b > 90) & (g < 0.8 * np.minimum(r, b)) & (np.abs(r - b) < 0.45 * np.maximum(r, b))
        for d in drop:                                              # colours that belong to another pass (e.g. navy in the orange pass)
            dc = np.array([int(d.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)])
            near_dc = np.abs(a[..., :3].astype(int) - dc).sum(-1) < 90
            keyed |= ndimage.binary_dilation(near_dc, iterations=4)     # also the blended edge pixels
        if k[0] > 200 and k[2] > 200 and k[1] < 60:      # neutral dark grey = the models' fill for not-paintable areas
            r, g, b = (a[..., i].astype(int) for i in range(3))
            keyed |= (np.maximum(np.maximum(r, g), b) < 150) & (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b) < 18)
        keyed = ndimage.binary_dilation(keyed, iterations=1)       # eat the pink fringe
        a[..., 3] = np.where(keyed, 0, a[..., 3])
        # bleed edge colour inward so semi-pink pixels do not tint
        near = ndimage.binary_dilation(keyed, iterations=3) & ~keyed
        a[near, 3] = (a[near, 3] * 0.6).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def split_layer(lname, lim, grow=18, min_area=3000, max_parts=14):
    """One transparent layer -> one layer per separate shape/logo (nearby pieces, e.g. letters, stay together)."""
    from scipy import ndimage
    a = np.asarray(lim)
    solid = a[..., 3] > 20
    lab, n = ndimage.label(ndimage.binary_dilation(solid, iterations=grow))
    if n <= 1:
        return [ora.Layer(lname, lim)]
    areas = ndimage.sum(solid, lab, range(1, n + 1))
    order = [i + 1 for i in np.argsort(-areas) if areas[i] >= min_area][:max_parts]
    out, used = [], np.zeros(solid.shape, bool)
    for rank, i in enumerate(order, 1):
        sel = lab == i
        used |= sel
        ys, xs = np.nonzero(sel & solid)
        part = a.copy()
        part[~sel, 3] = 0
        out.append(ora.Layer(f"{lname} {rank} @{int(xs.mean())},{int(ys.mean())}", Image.fromarray(part, "RGBA")))
    rest = a.copy()
    rest[used, 3] = 0
    if (rest[..., 3] > 0).any():
        out.append(ora.Layer(f"{lname} small bits", Image.fromarray(rest, "RGBA")))
    return out


def clip_alpha(im, clip):
    a = np.asarray(im).copy()
    a[..., 3] = np.minimum(a[..., 3], clip)
    return Image.fromarray(a, "RGBA")


def dodge_numbers(layer, nb, step=10, limit=400):
    """A split shape that overlaps a number plate slides toward the rear (+x) until clear."""
    a = np.asarray(layer.image)
    solid = a[..., 3] > 20
    if not (solid & nb).any():
        return layer
    for dx in range(step, limit + 1, step):
        moved = np.roll(solid, dx, axis=1)
        if not (moved & nb).any():
            out = np.roll(a, dx, axis=1)
            print(f"moved '{layer.name}' {dx}px rearward off the number plate")
            return ora.Layer(layer.name, Image.fromarray(out, "RGBA"))
    return layer


def ingest(key, image_path, name, mirror=False, base="#F4F4F0", out_dir=None, layers=(), split=False, dodge=()):
    """layers: [(name, png_path, key_colour_or_None)] element passes composited over the art."""
    cfg = aibrief.load(key)
    psd = aibrief.template(key)
    unpaintable, _ = aibrief.masks(psd, cfg)
    art = Image.open(image_path).convert("RGB")
    if art.size != (SIZE, SIZE):
        print(f"resizing {art.size} -> {SIZE}x{SIZE}" + ("" if art.width == art.height else " (not square: stretched!)"))
        art = art.resize((SIZE, SIZE), Image.LANCZOS)
    arr = remove_centre_line(np.asarray(art), cfg["mirror_y"])
    if mirror:
        arr = mirror_lower_to_upper(arr, cfg["mirror_y"])

    nb = aibrief.number_blocks(psd, cfg)       # models copy/decorate these boxes: wipe to the base colour
    arr = arr.copy()
    arr[nb] = [int(base.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)]

    layer = np.dstack([arr, np.where(unpaintable, 0, 255).astype(np.uint8)])
    art_layer = Image.fromarray(layer, "RGBA")
    trim = seams.psd_layer(psd, cfg["trim"].lower()) if cfg.get("trim") else None
    top = seams.psd_layer(psd, cfg["top"].lower()) if cfg.get("top") else None
    blank = Image.new("RGBA", (SIZE, SIZE))
    trim_l = Image.fromarray(trim) if trim is not None else blank
    top_l = Image.fromarray(top) if top is not None else blank

    over = Image.new("RGBA", (SIZE, SIZE))
    if cfg.get("over_trim"):          # panels whose trim is only a base (BMW wing): art goes over it
        car = seams.Car(key)
        sel = np.zeros((SIZE, SIZE), bool)
        for code in cfg["over_trim"]:
            sel |= car.mask(code, grow=2)
        over = Image.fromarray(np.dstack([arr, np.where(sel & ~unpaintable, 255, 0).astype(np.uint8)]), "RGBA")

    nb_core = aibrief.number_blocks(psd, cfg, grow=1)
    clip = np.where(unpaintable | nb, 0, 255).astype(np.uint8)
    extra = []
    for lname, lpath, lkey in layers:
        lpath, _, drops = lpath.partition("~")
        lim = load_layer(lpath, lkey, drop=[d for d in drops.split(",") if d])
        la = np.asarray(lim).copy()
        la[..., 3] = np.where(unpaintable, 0, la[..., 3])
        white = (la[..., :3].min(-1) > 235) & nb_core                  # white squares the model draws on the number blocks
        la[white, 3] = 0
        lim = Image.fromarray(la, "RGBA")
        parts = split_layer(lname, lim) if split else [ora.Layer(lname, lim)]
        if split and lname in dodge:
            parts = [dodge_numbers(pt, nb) for pt in parts]
        parts = [ora.Layer(pt.name, clip_alpha(pt.image, clip)) for pt in parts]
        extra.extend(parts)
    if cfg.get("over_trim"):          # element shapes on those panels go back over the trim too
        for e in extra:
            ea = np.asarray(e.image).copy()
            ea[..., 3] = np.where(sel, ea[..., 3], 0)
            over.alpha_composite(Image.fromarray(ea, "RGBA"))
    flat = Image.new("RGBA", (SIZE, SIZE), base)
    flat.alpha_composite(art_layer)
    for e in extra:
        flat.alpha_composite(e.image)
    for l in (trim_l, over, top_l):
        flat.alpha_composite(l)
    mask_l = Image.fromarray(np.dstack([np.full((SIZE, SIZE, 3), 255, np.uint8),
                                        np.where(unpaintable, 150, 0).astype(np.uint8)]), "RGBA")
    preview = flat.copy()
    preview.alpha_composite(mask_l)

    d = out_dir or paths.out_dir(os.getcwd(), key)
    stem = os.path.join(d, f"ai_{name}_{key}")
    flat.convert("RGB").save(stem + ".tga")
    art_layer.save(stem + "_layer.png")
    preview.convert("RGB").save(stem + "_preview.png")
    ora.write(stem + ".ora", [ora.Layer("base", Image.new("RGBA", (SIZE, SIZE), base)),
                              ora.Layer("AI art", art_layer),
                              *extra,
                              ora.Layer("trim (template)", trim_l),
                              ora.Layer("AI art over trim", over),
                              ora.Layer("decals (template)", top_l),
                              ora.Layer("GUIDE not paintable", mask_l, visible=False)])
    return stem


def main():
    args = sys.argv[1:]
    if len(args) < 2 or "--name" not in args:
        sys.exit(__doc__)
    key, image = args[0], args[1]
    name = args[args.index("--name") + 1]
    base = args[args.index("--base") + 1] if "--base" in args else "#F4F4F0"
    layers = []
    for i, a in enumerate(args):
        if a == "--layer":
            lname, lpath = args[i + 1].split("=", 1)
            layers.append((lname, lpath, args[args.index("--key") + 1] if "--key" in args else None))
    stem = ingest(key, image, name, mirror="--mirror" in args, base=base, layers=layers, split="--split" in args,
                  dodge=args[args.index("--dodge") + 1].split(",") if "--dodge" in args else ())
    print("wrote", stem + ".tga (+ _layer.png, _preview.png, .ora)")


if __name__ == "__main__":
    main()
