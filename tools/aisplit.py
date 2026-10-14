"""Split a flat AI-made paint sheet into editable layers by colour.

    ../../.venv/bin/python ../../tools/aisplit.py bmw-m4-gt3 sheet.png --name x [--navy "#1E2744"] [--orange "#FF7300"] [--erase x0,y0,x1,y1:navy|base|black ...]
    run from inside a livery folder: writes <car>/out/split_<name>_<car>.{tga,ora} + _preview.png

Layers (bottom -> top): base (everything that is not navy/orange: white, grey hex tiles, holes
filled from the nearest base pixel), then every separate navy shape and orange shape as its own
flat-colour layer ("navy 3 @x,y"), then the template trim/decals like aiingest.
Letters and small marks stay with the shape they touch (grow 18 px).
"""
import os
import sys

import numpy as np
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import aibrief  # noqa: E402
import aiingest  # noqa: E402
import ora  # noqa: E402
import paths  # noqa: E402
import seams  # noqa: E402

SIZE = 2048


def hexrgb(h):
    return tuple(int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4))


def hsv(a):
    return np.asarray(Image.fromarray(a.astype(np.uint8), "RGB").convert("HSV")).astype(np.float32) / 255


def classify(arr):
    h, s, v = (x for x in np.moveaxis(hsv(arr), -1, 0))
    h = h * 360
    orange = (h > 10) & (h < 45) & (s > 0.55) & (v > 0.6)
    navy = (h > 195) & (h < 260) & (s > 0.25) & (v < 0.5) & (v > 0.08)
    black = (v < 0.2) & (s < 0.35) & ~navy
    grey = (s < 0.12) & (v > 0.3) & (v < 0.78)
    return orange, navy, black, grey


def despeckle(mask, min_px=150):
    from scipy import ndimage
    lab, n = ndimage.label(mask)
    if n == 0:
        return mask
    keep = np.nonzero(ndimage.sum(mask, lab, range(1, n + 1)) >= min_px)[0] + 1
    return np.isin(lab, keep)


def shapes(mask, colour, name, grow=18, min_area=1200, max_parts=40):
    from scipy import ndimage
    soft = ndimage.gaussian_filter(mask.astype(np.float32), 0.8)
    alpha = np.clip((soft - 0.3) / 0.4, 0, 1)
    lab, n = ndimage.label(ndimage.binary_dilation(mask, iterations=grow))
    if n == 0:
        return []
    areas = ndimage.sum(mask, lab, range(1, n + 1))
    order = [i + 1 for i in np.argsort(-areas) if areas[i] >= min_area][:max_parts]
    out, used = [], np.zeros(mask.shape, bool)
    rgb = np.zeros((SIZE, SIZE, 3), np.uint8)
    rgb[:] = colour
    for rank, i in enumerate(order, 1):
        sel = lab == i
        used |= sel
        ys, xs = np.nonzero(sel & mask)
        a = np.where(sel, alpha, 0)
        out.append(ora.Layer(f"{name} {rank} @{int(xs.mean())},{int(ys.mean())}",
                             Image.fromarray(np.dstack([rgb, (a * 255).astype(np.uint8)]), "RGBA")))
    rest = np.where(used, 0, alpha)
    if rest.max() > 0.05:
        out.append(ora.Layer(f"{name} small bits", Image.fromarray(np.dstack([rgb, (rest * 255).astype(np.uint8)]), "RGBA")))
    return out


def split(key, image, name, navy="#1E2744", orange="#FF7300", base="#F4F4F0", out_dir=None, erase=()):
    from scipy import ndimage
    cfg = aibrief.load(key)
    psd = aibrief.template(key)
    unpaintable, _ = aibrief.masks(psd, cfg)
    art = Image.open(image).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS)
    arr = aiingest.remove_centre_line(np.asarray(art), cfg["mirror_y"])
    nb = aibrief.number_blocks(psd, cfg)
    arr = arr.copy()
    arr[nb] = hexrgb(base)
    fills = {"navy": hexrgb(navy), "base": hexrgb(base), "black": (17, 17, 17), "orange": hexrgb(orange)}
    for box in erase:                       # "x0,y0,x1,y1:navy" paints a logo/text box out with a flat colour
        coords, _, mode = box.partition(":")
        x0, y0, x1, y1 = (int(v) for v in coords.split(","))
        arr[y0:y1, x0:x1] = fills[mode or "base"]

    o_mask, n_mask, k_mask, g_mask = classify(arr)
    ok = ~unpaintable & ~nb
    o_mask, n_mask, k_mask = o_mask & ok, n_mask & ok, k_mask & ok
    o_mask = despeckle(ndimage.binary_opening(o_mask, iterations=1))
    n_mask = despeckle(ndimage.binary_opening(n_mask, iterations=1))
    k_mask = despeckle(ndimage.binary_opening(k_mask, iterations=2), 400)
    g_mask = ndimage.binary_dilation(g_mask & ok, iterations=1)       # the model's grey panel outlines

    # base: orange/navy (and a 3 px rim, the blended edge) replaced by the nearest base pixel
    hole = ndimage.binary_dilation(o_mask | n_mask | k_mask, iterations=3) | g_mask
    idx = ndimage.distance_transform_edt(hole, return_distances=False, return_indices=True)
    bimg = arr[idx[0], idx[1]]
    base_layer = Image.fromarray(np.dstack([bimg, np.where(unpaintable, 0, 255).astype(np.uint8)]), "RGBA")

    layers = shapes(n_mask, hexrgb(navy), "navy") + shapes(o_mask, hexrgb(orange), "orange") + shapes(k_mask, (17, 17, 17), "black")
    clip = np.where(unpaintable | nb, 0, 255).astype(np.uint8)
    layers = [ora.Layer(l.name, aiingest.clip_alpha(l.image, clip)) for l in layers]

    trim = seams.psd_layer(psd, cfg["trim"].lower()) if cfg.get("trim") else None
    top = seams.psd_layer(psd, cfg["top"].lower()) if cfg.get("top") else None
    blank = Image.new("RGBA", (SIZE, SIZE))
    trim_l = Image.fromarray(trim) if trim is not None else blank
    top_l = Image.fromarray(top) if top is not None else blank
    over = Image.new("RGBA", (SIZE, SIZE))
    if cfg.get("over_trim"):
        car = seams.Car(key)
        sel = np.zeros((SIZE, SIZE), bool)
        for code in cfg["over_trim"]:
            sel |= car.mask(code, grow=2)
        over = Image.fromarray(np.dstack([arr, np.where(sel & ~unpaintable, 255, 0).astype(np.uint8)]), "RGBA")

    flat = Image.new("RGBA", (SIZE, SIZE), base)
    flat.alpha_composite(base_layer)
    for l in layers:
        flat.alpha_composite(l.image)
    for l in (trim_l, over, top_l):
        flat.alpha_composite(l)
    mask_l = Image.fromarray(np.dstack([np.full((SIZE, SIZE, 3), 255, np.uint8),
                                        np.where(unpaintable, 150, 0).astype(np.uint8)]), "RGBA")
    preview = flat.copy()
    preview.alpha_composite(mask_l)

    d = out_dir or paths.out_dir(os.getcwd(), key)
    stem = os.path.join(d, f"split_{name}_{key}")
    flat.convert("RGB").save(stem + ".tga")
    preview.convert("RGB").save(stem + "_preview.png")
    ora.write(stem + ".ora", [ora.Layer("base (white + grey tiles)", base_layer), *layers,
                              ora.Layer("trim (template)", trim_l), ora.Layer("art over trim", over),
                              ora.Layer("decals (template)", top_l),
                              ora.Layer("GUIDE not paintable", mask_l, visible=False)])
    print(f"{len(layers)} shape layers")
    return stem


def main():
    a = sys.argv[1:]
    if len(a) < 2 or "--name" not in a:
        sys.exit(__doc__)
    g = lambda f, d: a[a.index(f) + 1] if f in a else d
    erase = [a[i + 1] for i, v in enumerate(a) if v == "--erase"]
    stem = split(a[0], a[1], g("--name", "x"), g("--navy", "#1E2744"), g("--orange", "#FF7300"), erase=erase)
    print("wrote", stem + ".tga (+ .ora, _preview.png)")


if __name__ == "__main__":
    main()
