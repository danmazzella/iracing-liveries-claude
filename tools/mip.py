"""Decode an iRacing spec `.mip` (the file iRacing builds next to a custom spec TGA) back into an image.

    ../../.venv/bin/python ../../tools/mip.py "My_spec.mip" out.png     (or out.tga)

Format (reverse-engineered 2026-10-07, see LIVERY_GUIDE section 13):
  36-byte file header, then one `BMAP` chunk per mip level, smallest (1x1) to largest (2048).
  Each chunk: tag, 4 bytes 0, u32 length, then `BMHD` (14 bytes: u8 flag, u32 w, u32 h, u32 ?, u8 format)
  and `DATA`. The 2048 level's DATA is: u32 chunk count (32), then per chunk [u32 raw size 0x20000,
  u32 0, u32 compressed size, zstd frame]. Raw payload = DXT5/BC3, 2048*2048 bytes, so R/G/B are the
  spec's metallic/roughness/clearcoat (lossy: DXT5 blocks, values land in steps of ~8) and A is the
  spec mask.
  Only the zstd layout (BMHD format byte 0x17) is decoded. A second layout (format byte 0x13: a table
  of chunk sizes first, no zstd magic) exists in some files and is NOT decoded yet.
"""
import io
import re
import struct
import sys

import numpy as np
from PIL import Image

MAGIC = b"\x28\xb5\x2f\xfd"


def top_level_payload(data):
    """DATA payload of the largest (2048 px) mip level, or None."""
    pos, best = 36, None
    while pos < len(data) - 12:
        length = struct.unpack("<I", data[pos + 8:pos + 12])[0]
        body = data[pos + 12:pos + 12 + length]
        pos += 12 + length
        width = struct.unpack("<I", body[13:17])[0]
        if width == 2048:
            best = body[body.find(b"ATAD") + 12:]
    return best


def decode(path):
    """Return the 2048x2048 RGBA array stored in a .mip."""
    import zstandard
    pay = top_level_payload(open(path, "rb").read())
    starts = [m.start() for m in re.finditer(re.escape(MAGIC), pay or b"")]
    if not starts:
        raise ValueError("no zstd frames: this .mip uses the other (undecoded) layout")
    raw = b""
    for a, b in zip(starts, starts[1:] + [len(pay)]):
        raw += zstandard.ZstdDecompressor().decompressobj().decompress(pay[a:b])
    size = 2048
    dds = (b"DDS " + struct.pack("<7I", 124, 0x81007, size, size, size * size, 0, 0) + b"\0" * 44
           + struct.pack("<2I4s5I", 32, 4, b"DXT5", 0, 0, 0, 0, 0) + struct.pack("<5I", 0x1000, 0, 0, 0, 0))
    return np.array(Image.open(io.BytesIO(dds + raw)).convert("RGBA"))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    arr = decode(sys.argv[1])
    Image.fromarray(arr[..., :3]).save(sys.argv[2])
    print("wrote", sys.argv[2], "mean RGBA", arr.reshape(-1, 4).mean(0).round(1))
