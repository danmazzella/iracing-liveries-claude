"""Project a reference image onto the sheet using grid-label correspondences.

A view = labels [(screen px, (col,row))] read off a grid screenshot + landmarks
[(screen px, reference px)] between that screenshot and the reference image. Screen->reference
is a thin-plate spline through the landmarks; composing gives sheet->reference, which is
evaluated only near the labels (where that view actually sees the surface).
"""
import numpy as np
from scipy import ndimage
from scipy.interpolate import RBFInterpolator

SIZE, CELL = 2048, 64


def label_sheet_pt(col, row):
    return col * CELL + 26, row * CELL + 31          # centre of the label text in grid.tga


def view_map(labels, landmarks, flip_w=None, mirror_y=None, smooth=30):
    scr = np.array([p for p, _ in labels], float)
    if flip_w:
        scr[:, 0] = flip_w - scr[:, 0]
    sheet = np.array([label_sheet_pt(*cr) for _, cr in labels], float)
    if mirror_y is not None:
        sheet[:, 1] = 2 * mirror_y - sheet[:, 1]
    s2r = RBFInterpolator(np.array([p for p, _ in landmarks], float),
                          np.array([q for _, q in landmarks], float), kernel="thin_plate_spline", smoothing=5)
    return sheet, RBFInterpolator(sheet, s2r(scr), kernel="thin_plate_spline", smoothing=smooth)


def render(ref, sheet_pts, sheet2ref, reach=70):
    """Returns (rgb float sheet, weight) — weight falls off with distance from the nearest label."""
    known = np.zeros((SIZE, SIZE), bool)
    ij = np.clip(np.round(sheet_pts).astype(int), 0, SIZE - 1)
    known[ij[:, 1], ij[:, 0]] = True
    dist = ndimage.distance_transform_edt(~known)
    wmask = dist < reach
    ys, xs = np.nonzero(wmask)
    q = sheet2ref(np.stack([xs, ys], 1).astype(float))
    out = np.zeros((SIZE, SIZE, 3), np.float32)
    for c in range(3):
        out[ys, xs, c] = ndimage.map_coordinates(ref[..., c], [q[:, 1], q[:, 0]], order=1, mode="nearest")
    w = np.clip(1 - dist / reach, 0, 1) ** 2
    return out, w
