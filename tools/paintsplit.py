"""Split a finished (hand-made) paint TGA into layers that keep its original pixels.

    ../../.venv/bin/python ../../tools/paintsplit.py <car> paint.tga --name x
    run from inside a livery folder: writes <car>/out/layers_<name>/ (one PNG per layer),
    <car>/out/layers_<name>_<car>.ora and a re-flattened _check.png (should match the input).

Layers (bottom -> top): base (white/hex, holes filled from the nearest base pixel), each navy shape
(holes inside it filled navy), each orange shape (shading kept), "on navy" (logos, text, glints, cards
that sit inside a navy shape), dark parts (banners, cards). Template trim/decals are already baked into
a finished paint, so they stay in the base and come along only as hidden GUIDE layers in the .ora.
Unlike aisplit.py nothing is repainted flat, so gradients and facets survive.
"""
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import aibrief  # noqa: E402
import aisplit  # noqa: E402
import ora  # noqa: E402
import paths  # noqa: E402
import seams  # noqa: E402

SIZE = 2048


def rgba(arr, mask):
    return Image.fromarray(np.dstack([arr, np.where(mask, 255, 0).astype(np.uint8)]), "RGBA")


def components(mask, min_px, small=4000):
    """Shapes of at least `small` px one each, the rest (>= min_px) merged into one last mask."""
    lab, n = ndimage.label(mask)
    if n == 0:
        return []
    areas = ndimage.sum(mask, lab, range(1, n + 1))
    big = [lab == i + 1 for i in np.argsort(-areas) if areas[i] >= small]
    rest = np.isin(lab, [i + 1 for i in range(n) if min_px <= areas[i] < small])
    return big + ([rest] if rest.any() else [])


def at(m):
    ys, xs = np.nonzero(m)
    return f"@{int(xs.mean())},{int(ys.mean())}"


def split(key, path, name, min_px=400):
    cfg = aibrief.load(key)
    psd = aibrief.template(key)
    unpaintable, _ = aibrief.masks(psd, cfg)
    arr = np.asarray(Image.open(path).convert("RGB").resize((SIZE, SIZE), Image.LANCZOS))
    trim = seams.psd_layer(psd, cfg["trim"].lower()) if cfg.get("trim") else None
    top = seams.psd_layer(psd, cfg["top"].lower()) if cfg.get("top") else None
    ok = ~unpaintable                       # trim is baked into a finished paint: keep its pixels

    orange, navy, black, _ = aisplit.classify(arr)
    navy = aisplit.despeckle(ndimage.binary_opening(navy & ok), 150)
    navy_full = ndimage.binary_fill_holes(ndimage.binary_closing(navy, iterations=2)) & ok
    on_navy = navy_full & ~navy                                  # letters, glints, cards inside navy
    orange = aisplit.despeckle(orange & ok & ~on_navy, 150)
    black = aisplit.despeckle(ndimage.binary_opening(black & ok & ~navy_full, iterations=2), 400)
    # blended edges belong to the shape they ring
    orange_e = ndimage.binary_dilation(orange, iterations=1) & ok & ~navy_full
    black_e = ndimage.binary_dilation(black, iterations=1) & ok & ~navy_full & ~orange_e

    layers = []
    hole = ndimage.binary_dilation(navy_full | orange_e | black_e, iterations=2)
    idx = ndimage.distance_transform_edt(hole | ~ok, return_distances=False, return_indices=True)
    base = arr[idx[0], idx[1]]
    layers.append(("base", rgba(base, ok)))

    navy_rgb = np.median(arr[navy], axis=0).astype(np.uint8)
    filled = arr.copy()
    filled[on_navy] = navy_rgb
    edge = ndimage.binary_dilation(navy_full, iterations=1) & ok & ~orange_e
    for i, m in enumerate(components(edge, min_px), 1):
        layers.append((f"navy {i} {at(m)}", rgba(filled, m)))
    for i, m in enumerate(components(orange_e, min_px), 1):
        layers.append((f"orange {i} {at(m)}", rgba(arr, m)))
    for i, m in enumerate(components(on_navy, 60), 1):
        layers.append((f"on navy {i} {at(m)}", rgba(arr, m)))
    for i, m in enumerate(components(black_e, min_px), 1):
        layers.append((f"dark {i} {at(m)}", rgba(arr, m)))

    flat = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 255))
    flat.paste(Image.fromarray(arr), mask=Image.fromarray(np.where(ok, 0, 255).astype(np.uint8)))
    for _, im in layers:
        flat.alpha_composite(im)
    diff = np.abs(np.asarray(flat.convert("RGB")).astype(int) - arr).max(-1)
    print(f"{len(layers)} layers; re-flattened vs input: {np.mean(diff[ok] > 24) * 100:.2f}% of paintable px differ")

    d = paths.out_dir(os.getcwd(), key)
    folder = os.path.join(d, f"layers_{name}")
    os.makedirs(folder, exist_ok=True)
    for f in os.listdir(folder):
        os.remove(os.path.join(folder, f))
    for i, (lname, im) in enumerate(layers):
        im.save(os.path.join(folder, f"{i:02d}_{lname.split(' @')[0].replace(' ', '_')}.png"))
    mask_l = rgba(np.full((SIZE, SIZE, 3), 255, np.uint8), unpaintable)
    stem = os.path.join(d, f"layers_{name}_{key}")
    guides = [ora.Layer("GUIDE template trim", Image.fromarray(trim), visible=False)] if trim is not None else []
    guides += [ora.Layer("GUIDE template decals", Image.fromarray(top), visible=False)] if top is not None else []
    ora.write(stem + ".ora", [ora.Layer(n, im) for n, im in layers] + guides +
              [ora.Layer("GUIDE not paintable", mask_l, visible=False)])
    flat.convert("RGB").save(stem + "_check.png")
    print("wrote", folder, stem + ".ora")
    return layers


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 2:
        sys.exit(__doc__)
    split(a[0], a[1], a[a.index("--name") + 1] if "--name" in a else "x")
