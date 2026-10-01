"""Write a layered OpenRaster (.ora) file so a livery can be finished by hand in GIMP or Krita.

A livery script normally flattens everything into one TGA. To get an editable file, draw each
part onto its own transparent RGBA layer and hand the list to `write`:

    sys.path.insert(0, os.path.join(REPO, "tools")); import ora
    ora.write("bmw-m4-gt3/out/mylivery_bmw-m4-gt3_1.ora", [            # bottom -> top, like the Layers panel read upward
        ora.Layer("base", base),
        ora.Layer("stripe", stripe),
        ora.Layer("trim (template)", trim),
        ora.Layer("mask (not paintable)", mask, visible=False, opacity=0.6),
    ])

GIMP opens .ora with all layers (File > Save As... .xcf keeps a GIMP file). To export the paint:
Image > Flatten Image (drops the hidden GUIDE layers and the alpha: 24-bit), File > Export As...
<name>.tga with "RLE compression" unticked (like the scripts' TGAs), then Edit > Undo the
flatten. Tested with GIMP 3.2: same pixels as the script's TGA except anti-aliased edges (GIMP
blends soft edges slightly differently, invisible on the car).

    python ora.py <file.ora>        list the layers of an .ora (a quick check)
"""
import io
import os
import sys
import zipfile
from dataclasses import dataclass
from xml.sax.saxutils import quoteattr

from PIL import Image


@dataclass
class Layer:
    name: str
    image: Image.Image           # RGBA, same size as the canvas (2048x2048 for iRacing)
    visible: bool = True
    opacity: float = 1.0


def _png(im):
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=False, compress_level=6)
    return buf.getvalue()


def write(path, layers, size=None):
    """Write `layers` (bottom -> top) to `path` as OpenRaster. Hidden layers stay out of the
    merged preview but are kept in the file."""
    layers = [Layer(l.name, l.image.convert("RGBA"), l.visible, l.opacity) for l in layers]
    w, h = size or layers[0].image.size
    merged = Image.new("RGBA", (w, h))
    for l in layers:
        if l.visible:
            im = l.image
            if l.opacity < 1:
                im = im.copy()
                im.putalpha(im.getchannel("A").point(lambda a: round(a * l.opacity)))
            merged.alpha_composite(im)

    # stack.xml lists the topmost layer first
    rows = []
    for i, l in reversed(list(enumerate(layers))):
        rows.append(f'  <layer name={quoteattr(l.name)} src="data/layer{i:02d}.png" x="0" y="0" '
                    f'opacity="{l.opacity:.3f}" visibility="{"visible" if l.visible else "hidden"}"/>')
    stack = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             f'<image version="0.0.5" w="{w}" h="{h}">\n<stack>\n' + "\n".join(rows) + "\n</stack>\n</image>\n")

    thumb = merged.copy()
    thumb.thumbnail((256, 256))
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        # the spec wants "mimetype" first and uncompressed
        z.writestr(zipfile.ZipInfo("mimetype"), "image/openraster", compress_type=zipfile.ZIP_STORED)
        z.writestr("stack.xml", stack)
        for i, l in enumerate(layers):
            z.writestr(f"data/layer{i:02d}.png", _png(l.image), compress_type=zipfile.ZIP_STORED)
        z.writestr("mergedimage.png", _png(merged), compress_type=zipfile.ZIP_STORED)
        z.writestr("Thumbnails/thumbnail.png", _png(thumb), compress_type=zipfile.ZIP_STORED)
    return merged


def paint_layer(color, shape, size=None):
    """A transparent layer filled with `color` where the L-mode `shape` is set (anti-aliased)."""
    im = Image.new("RGBA", size or shape.size, color)
    im.putalpha(shape)
    return im


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    with zipfile.ZipFile(sys.argv[1]) as z:
        print(z.read("stack.xml").decode())
