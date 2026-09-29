"""Project a reference image (e.g. a livery mockup render) onto the paint sheet.

For each view we have:
  - a UV-coded in-sim screenshot (see uvcode.py) -> sheet (x, y) per screenshot pixel
  - the same view in the reference image
  - landmark pairs (screenshot px, reference px): roundel, kidney corners, headlight tips...
A thin-plate spline through the landmarks maps every screenshot pixel into the reference,
so every visible sheet pixel gets the reference's colour. Views are blended per sheet pixel,
favouring views that see the surface head-on (more screenshot pixels per sheet pixel).
"""
import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.interpolate import RBFInterpolator

from uvcode import SIZE, decode


def load_uv(path, flip=False, mirror_y=None):
    """Decode a UV screenshot. flip=True mirrors it left-right; with mirror_y the decoded sheet y
    is mirrored too, turning a right-side shot into a virtual left-side shot."""
    im = Image.open(path).convert("RGB")
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    x, y, ok = decode(im)
    if mirror_y is not None:
        y = 2 * mirror_y - y
    # Smooth the decoded coords a little (webp noise), then drop pixels that don't behave like a
    # painted surface: floor shadows decode to near-constant coords (tiny gradient).
    xs = ndimage.median_filter(x, 5)
    ys = ndimage.median_filter(y, 5)
    gx = np.hypot(*np.gradient(xs))
    gy = np.hypot(*np.gradient(ys))
    grad = ndimage.uniform_filter(gx + gy, 9)
    ok = ok & (grad > 0.35) & (grad < 40)
    ok = ndimage.binary_opening(ok, iterations=2)
    # Jacobian area: sheet px per screen px. Small = head-on, high resolution.
    area = ndimage.uniform_filter(np.abs(np.gradient(xs)[1] * np.gradient(ys)[0] -
                                         np.gradient(xs)[0] * np.gradient(ys)[1]), 7)
    return xs, ys, ok, area


def warp_field(shape, uv_pts, ref_pts):
    """Reference-image coords for every screenshot pixel, via a thin-plate spline."""
    h, w = shape
    rbf = RBFInterpolator(np.asarray(uv_pts, float), np.asarray(ref_pts, float),
                          kernel="thin_plate_spline", smoothing=1.0)
    step = 8                                                   # evaluate coarse, then upsample
    gy, gx = np.mgrid[0:h:step, 0:w:step]
    coarse = rbf(np.stack([gx.ravel(), gy.ravel()], 1)).reshape(gy.shape + (2,))
    zoom = (h / coarse.shape[0], w / coarse.shape[1])
    rx = ndimage.zoom(coarse[..., 0], zoom, order=1)[:h, :w]
    ry = ndimage.zoom(coarse[..., 1], zoom, order=1)[:h, :w]
    return rx, ry


def project(views, ref, weight_power=1.0):
    """views: list of dict(uv=(xs, ys, ok, area), uv_pts, ref_pts, crop=(x0,y0,x1,y1), rot, weight).
    ref: reference PIL image. Returns (sheet RGB float, sheet weight)."""
    acc = np.zeros((SIZE, SIZE, 3), np.float64)
    wsum = np.zeros((SIZE, SIZE), np.float64)
    refa = np.asarray(ref.convert("RGB")).astype(np.float32)
    for v in views:
        xs, ys, ok, area = v["uv"]
        rx, ry = warp_field(ok.shape, v["uv_pts"], v["ref_pts"])
        rx, ry = rx + v.get("offset", (0, 0))[0], ry + v.get("offset", (0, 0))[1]
        inside = ok & (rx >= 0) & (ry >= 0) & (rx < refa.shape[1] - 1) & (ry < refa.shape[0] - 1)
        if "ref_mask" in v:                                    # only take reference pixels on the car
            inside &= v["ref_mask"][np.clip(ry.astype(int), 0, refa.shape[0] - 1),
                                    np.clip(rx.astype(int), 0, refa.shape[1] - 1)]
        cols = np.stack([ndimage.map_coordinates(refa[..., c], [ry[inside], rx[inside]], order=1)
                         for c in range(3)], 1)
        w = v.get("weight", 1.0) / np.maximum(area[inside], 0.05) ** weight_power
        sx = np.clip(xs[inside].round().astype(int), 0, SIZE - 1)
        sy = np.clip(ys[inside].round().astype(int), 0, SIZE - 1)
        np.add.at(acc, (sy, sx), cols * w[:, None])
        np.add.at(wsum, (sy, sx), w)
    return acc, wsum


def finish(acc, wsum, min_w=1e-6, blur=2.0):
    """Splat -> filled sheet image. Each screenshot pixel lands on one sheet pixel, so spread
    them with a gaussian (normalised), then fill remaining holes from the nearest known pixel."""
    a = np.stack([ndimage.gaussian_filter(acc[..., c], blur) for c in range(3)], -1)
    w = ndimage.gaussian_filter(wsum, blur)
    known = w > min_w * max(w.max(), 1e-9)
    img = np.zeros_like(a)
    img[known] = a[known] / w[known, None]
    idx = ndimage.distance_transform_edt(~known, return_distances=False, return_indices=True)
    img = img[idx[0], idx[1]]
    return np.clip(img, 0, 255).astype(np.uint8), known
