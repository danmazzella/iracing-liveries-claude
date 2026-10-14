"""Turn a layered .ora into a GIMP .xcf (groups kept), with every layer composited in perceptual RGB
like a hand-made GIMP file, so GIMP's flatten matches the script's TGA exactly.

    python ora2xcf.py file.ora [out.xcf]

Needs GIMP 3 (gimp-console). Found at the usual Mac/Windows install paths or via $GIMP_CONSOLE.
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

SCRIPT = r'''
import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp, Gio
img = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, Gio.File.new_for_path({src!r}))
def persp(ls):
    for l in ls:
        l.set_composite_space(Gimp.LayerColorSpace.RGB_PERCEPTUAL)
        if l.is_group():
            persp(l.get_children())
persp(img.get_layers())
Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, img, Gio.File.new_for_path({dst!r}), None)
'''


def gimp_console():
    cands = [os.environ.get("GIMP_CONSOLE"), "/Applications/GIMP.app/Contents/MacOS/gimp-console",
             shutil.which("gimp-console"), shutil.which("gimp-console-3.0")]
    cands += sorted(glob.glob(r"C:\Program Files\GIMP 3*\bin\gimp-console*.exe"), reverse=True)
    return next((c for c in cands if c and os.path.exists(c)), None)


def convert(src, dst=None):
    exe = gimp_console()
    if not exe:
        print("GIMP 3 not found: skipped the .xcf (the .ora opens in GIMP directly)")
        return None
    src = os.path.abspath(src)
    dst = os.path.abspath(dst or os.path.splitext(src)[0] + ".xcf")
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(SCRIPT.format(src=src, dst=dst))
    try:
        subprocess.run([exe, "-i", "--quit", "--batch-interpreter=python-fu-eval",
                        "-b", f"exec(open({f.name!r}).read())"], check=True, capture_output=True, timeout=900)
    finally:
        os.remove(f.name)
    return dst if os.path.exists(dst) else None


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    print("wrote", convert(*sys.argv[1:3]))
