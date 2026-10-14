"""iRacing's own paint patterns as alignment data (LIVERY_GUIDE 4c).

Every template has a hidden `Car Patterns` group: car_pattern_000..024, the patterns of the
in-sim paint screen (R/G/B = paint colours 1/2/3). iRacing's artists drew them on the 3D car,
so their stripes already line up across the seams. car_pattern_010 is a smooth red -> green ->
blue gradient from nose to tail: its hue tells how far along the car a sheet pixel is
("length", 0 = nose end, 1 = tail end). The very nose and tail are flat red / blue (no reading).

    ../../.venv/bin/python ../../tools/patterns.py sheet <car>            all patterns on one image
    ../../.venv/bin/python ../../tools/patterns.py length <car>           decode the gradient
    ../../.venv/bin/python ../../tools/patterns.py match <car> D23-D28 B60-B72
                                                   suggest seams.json pairs from equal length

`sheet`  -> cars/<car>/patterns_sheet.png: the 25 patterns, labelled (which shapes iRacing treats
            as continuous over the car).
`length` -> cars/<car>/length.npz (float16 length per sheet px, NaN where unknown) and
            length_sheet.png (contour lines every 5 %, numbered, over the mask).
`match`  -> for each ruler code in the first range (seams.py ruler), the point in the second
            range with the same length. Works for seams that run along the car (roof rails,
            hood/fender tops, sills): a seam across the car has one length all along, so the
            match there only says "same row", not where along the seam. Flags such points.
            Give both ranges roughly (from the grid or the ruler screenshot); check the result
            with seams.py check like any reading.

    import patterns; L = patterns.length("bmw-m4-gt3")   # 2048x2048, NaN off the gradient
"""
import os
import re
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grid import SIZE, font, layer, open_psd  # noqa: E402
import seams  # noqa: E402

GRADIENT = "car_pattern_010.tga"


def _psd(key):
    return open_psd(seams.template_path(key))


def decode(rgb):
    """Gradient RGB (HxWx3 uint8) -> length 0..1, NaN where it isn't the gradient (black parts,
    greys, the flat red/blue ends)."""
    hsv = np.asarray(Image.fromarray(rgb).convert("HSV")).astype(np.float32) / 255
    r, g, b = (rgb[..., i].astype(np.float32) for i in range(3))
    # red 0 -> green 0.5 -> blue 1, from channel ratios (finer than the 8-bit hue)
    t = np.where(b <= r, 0.5 * g / np.maximum(r + g, 1), 0.5 + 0.5 * b / np.maximum(g + b, 1))
    hue = hsv[..., 0] * 360
    ok = (hsv[..., 1] > 0.5) & (hsv[..., 2] > 0.3) & (hue < 245) & (t > 0.01) & (t < 0.99)
    return np.where(ok, t, np.nan)


def build_length(key):
    psd = _psd(key)
    if not any(l.name == GRADIENT for l in psd.descendants()):
        sys.exit(f"{seams.template_path(key)} has no {GRADIENT}")
    t = decode(np.asarray(layer(psd, GRADIENT).convert("RGB")))
    out = seams.car_dir(key)
    np.savez_compressed(os.path.join(out, "length.npz"), t=t.astype(np.float16))

    # preview: grey where known, contour every 5 %, numbers every 10 %
    img = Image.new("RGB", (SIZE, SIZE), (40, 40, 40))
    known = ~np.isnan(t)
    arr = np.asarray(img).copy()
    arr[known] = (200, 200, 200)
    band = np.floor(np.nan_to_num(t, nan=-1) * 20)
    edge = known & ((band != np.roll(band, 1, 0)) | (band != np.roll(band, 1, 1)))
    edge = ndimage.binary_dilation(edge, iterations=1) & known
    arr[edge] = (220, 30, 30)
    img = Image.fromarray(arr)
    try:
        img.alpha_composite  # noqa: B018
        mask = layer(psd, "Mask")
        img = img.convert("RGBA")
        m = np.asarray(mask).copy()
        m[..., 3] = m[..., 3] // 2
        img.alpha_composite(Image.fromarray(m))
        img = img.convert("RGB")
    except StopIteration:
        pass
    d = ImageDraw.Draw(img)
    fnt = font(26)
    lab, n = ndimage.label(known & (band % 2 == 0))
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        if sl is None:
            continue
        ys, xs = np.nonzero(lab[sl] == i)
        if len(ys) < 1500:
            continue
        cy, cx = int(np.median(ys)) + sl[0].start, int(np.median(xs)) + sl[1].start
        if lab[cy, cx] != i:
            continue
        d.text((cx, cy), f"{int(band[cy, cx]) * 5}", font=fnt, fill=(0, 0, 0), anchor="mm")
    img.save(os.path.join(out, "length_sheet.png"))
    print(f"{known.mean():.0%} of the sheet has a length. wrote cars/{key}/length.npz, length_sheet.png")


def length(key):
    p = os.path.join(seams.car_dir(key), "length.npz")
    if not os.path.exists(p):
        build_length(key)
    return np.load(p)["t"].astype(np.float32)


def build_sheet(key):
    psd = _psd(key)
    grp = next((l for l in psd.descendants() if l.name == "Car Patterns"), None)
    if grp is None:
        sys.exit("no Car Patterns group in this template")
    tiles = []
    for lyr in sorted(grp, key=lambda l: l.name):
        im = lyr.topil()
        if im is None:
            continue
        full = Image.new("RGBA", (SIZE, SIZE), (128, 128, 128, 255))
        full.alpha_composite(im.convert("RGBA"), (lyr.left, lyr.top))
        t = full.convert("RGB").resize((400, 400), Image.LANCZOS)
        ImageDraw.Draw(t).text((6, 4), lyr.name.replace("car_pattern_", "").replace(".tga", ""),
                               font=font(28), fill=(255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0))
        tiles.append(t)
    cols = 6
    sheet = Image.new("RGB", (cols * 400, -(-len(tiles) // cols) * 400), "white")
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * 400, (i // cols) * 400))
    sheet.save(os.path.join(seams.car_dir(key), "patterns_sheet.png"))
    print(f"wrote cars/{key}/patterns_sheet.png ({len(tiles)} patterns)")


def _range(spec):
    """'D23-D28' or 'D23-28' -> ('D', 23.0, 28.0)"""
    m = re.fullmatch(r"([A-Z]+)(\d+(?:\.\d+)?)-(?:[A-Z]+)?(\d+(?:\.\d+)?)", spec.strip())
    if not m:
        sys.exit(f"bad range {spec!r} (want e.g. D23-D28)")
    return m.group(1), float(m.group(2)), float(m.group(3))


def _inside(car, code, t):
    """Length at each pixel, taken from the nearest pixel 6 px inside the panel (edges blend
    into the background)."""
    m = ndimage.binary_erosion(car.mask(code), iterations=6) & ~np.isnan(t)
    _, idx = ndimage.distance_transform_edt(~m, return_indices=True)
    return lambda x, y: t[tuple(idx[:, int(round(y)), int(round(x))])]


def match(key, ra, rb):
    car, t = seams.Car(key), length(key)
    (ca, a0, a1), (cb, b0, b1) = _range(ra), _range(rb)
    la, lb = _inside(car, ca, t), _inside(car, cb, t)
    sb = np.arange(min(b0, b1), max(b0, b1) + 1e-6, 0.02)
    tb = np.array([lb(*car.point(f"{cb}{s:.2f}")) for s in sb])
    pairs, prev = [], None
    for s in np.arange(min(a0, a1), max(a0, a1) + 1e-6, 1.0):
        ta = la(*car.point(f"{ca}{s:g}"))
        d = np.abs(tb - ta)
        cand = np.nonzero(d <= d.min() + 0.002)[0]
        j = cand[np.argmin(np.abs(sb[cand] - prev))] if prev is not None else cand[0]
        prev = sb[j]
        # many equally good points = the length hardly changes along B here (seam across the car)
        spread = np.ptp(sb[d <= max(0.004, d.min() + 0.002)])
        flag = "" if spread < 0.5 else f"   <- {spread:.1f} segments match: position along the seam unreliable"
        pairs.append([f"{ca}{s:g}", f"{cb}{sb[j]:.2f}"])
        print(f'["{ca}{s:g}", "{cb}{sb[j]:.2f}"]   length {ta:.3f} / {tb[j]:.3f}{flag}')
    return pairs


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    cmd, key = args[0], args[1]
    if cmd == "sheet":
        build_sheet(key)
    elif cmd == "length":
        build_length(key)
    elif cmd == "match" and len(args) == 4:
        match(key, args[2], args[3])
    else:
        sys.exit(__doc__)
