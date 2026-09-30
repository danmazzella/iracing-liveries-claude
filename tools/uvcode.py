"""UV-coded paint: every pixel's colour encodes its own sheet position.

Install it, take in-sim screenshots, and `decode()` turns each screenshot pixel back into
the sheet (x, y) that paints it. That lets us project a design reference (mockup render)
straight onto the sheet instead of hand-placing shapes.

Encoding: B is a constant 255 and R, G carry x, y in [LO, HI]. Lighting and gamma scale all
three channels together, so the ratios R/B and G/B survive shading. Neutral pixels
(background, tyres, glass, iRacing's number) have ratios near 1, above HI/255, so decode()
rejects them.

    ../../.venv/bin/python ../../tools/uvcode.py              writes uvcode.tga + uvcode_spec.tga into ./out
"""
import os
import sys

import numpy as np
from PIL import Image

SIZE = 2048
LO, HI = 30, 215


def encode():
    x = np.linspace(0, 1, SIZE, dtype=np.float32)
    r = np.broadcast_to(LO + (HI - LO) * x[None, :], (SIZE, SIZE))
    g = np.broadcast_to(LO + (HI - LO) * x[:, None], (SIZE, SIZE))
    b = np.full((SIZE, SIZE), 255, np.float32)
    return Image.fromarray(np.stack([r, g, b], -1).round().astype(np.uint8))


def spec():
    """Matte, non-metallic, so reflections don't wash the code out.
    B (clearcoat) 255: assumed to mean no clearcoat; check the screenshot for glare."""
    return Image.fromarray(np.stack([np.zeros((SIZE, SIZE)), np.full((SIZE, SIZE), 255),
                                     np.full((SIZE, SIZE), 255)], -1).astype(np.uint8))


def decode(img, min_blue=40):
    """Screenshot (PIL) -> (sheet_x, sheet_y, valid) arrays in screenshot pixel space."""
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    bs = np.maximum(b, 1)
    rr, gr = r / bs * 255, g / bs * 255
    u = (rr - LO) / (HI - LO)
    v = (gr - LO) / (HI - LO)
    valid = (b >= min_blue) & (b > r + 25) & (b > g + 25) & (u > -0.02) & (u < 1.02) & (v > -0.02) & (v < 1.02)
    return np.clip(u, 0, 1) * (SIZE - 1), np.clip(v, 0, 1) * (SIZE - 1), valid


if __name__ == "__main__":
    out = os.path.join(os.getcwd(), "out")
    os.makedirs(out, exist_ok=True)
    encode().save(os.path.join(out, "uvcode.tga"))
    spec().save(os.path.join(out, "uvcode_spec.tga"))
    print("wrote", out)
