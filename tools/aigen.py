"""Generate artwork for a car's paint sheet with OpenAI gpt-image-1 (image edit), using the brief kit.

    export OPENAI_API_KEY=sk-...
    ../../.venv/bin/python ../../tools/aigen.py bmw-m4-gt3 "design text" --name x [--quality high] [--transparent] [--ingest]
    ... --only "navy slashes" --ref concept.webp   one ELEMENT pass on a transparent background

--only "<element>": layer pass. The model draws just that element (everything else transparent) on the
  sheet layout; --ref adds a style reference image (a concept render), repeatable. Stack the passes
  with aiingest --layer name=file.png (no --key needed: the PNGs have real alpha).

Sends cars/<car>/ai/guide_atlas.png + guide_legend.png + guide_wire.png with the prompt from
aibrief.py (rebuilt with your design text). Run from inside a livery folder: the raw output goes to
<car>/reference/ai_<name>_raw.png; --ingest then runs aiingest on it.
--transparent asks for a transparent background (element passes: logo, mascot; see aiingest --layer).
"""
import base64
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))
import aibrief  # noqa: E402
import paths  # noqa: E402


def opt(args, flag, default=None):
    return args[args.index(flag) + 1] if flag in args else default


def main():
    args = sys.argv[1:]
    if len(args) < 2 or "--name" not in args:
        sys.exit(__doc__)
    key = args[0]
    flags = {"--name", "--quality", "--size", "--only", "--ref"}
    design = " ".join(a for i, a in enumerate(args[1:], 1)
                      if not a.startswith("--") and args[i - 1] not in flags)
    name = opt(args, "--name")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("set OPENAI_API_KEY first (export OPENAI_API_KEY=sk-...)")
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("pip install openai  (use ../../.venv/bin/pip install openai)")

    cfg = aibrief.load(key)
    text = aibrief.prompt(key, cfg, design)
    text = text.split("## Prompt", 1)[1].split("## Bring it back", 1)[0].strip()
    only = opt(args, "--only")
    refs = [args[i + 1] for i, a in enumerate(args) if a == "--ref"]
    if only:
        text = text.replace("Redraw the sheet as the finished livery artwork:",
                            "Draw ONE LAYER of the livery on this sheet layout. Draw ONLY this element, and leave "
                            "everything else fully transparent (no base colour, no background, no other graphics):")
        text = text.replace(f"DESIGN: {design}", f"ELEMENT: {only}\nOverall livery style: {design}")
        text += ("\n- This is a transparent overlay layer: only the element's own pixels may be opaque. "
                 "Do not fill panels with a base colour.")
        args = args + ["--transparent"]
    if refs:
        text += ("\n- The last image(s) are a concept render of the finished car: match its colours, shapes and style, "
                 "but lay everything out on the sheet using the panel colours, never the render's perspective.")
    ai = os.path.join(REPO, "cars", key, "ai")
    files = [os.path.join(ai, f) for f in ("guide_atlas.png", "guide_legend.png", "guide_wire.png")]
    for f in files:
        if not os.path.exists(f):
            sys.exit(f"{f} missing: run aibrief.py {key} first")

    files += refs
    kw = {}
    if "--transparent" in args:
        kw["background"] = "transparent"
        kw["output_format"] = "png"
    print("calling gpt-image-1 ... (can take a minute)")
    handles = [open(f, "rb") for f in files]
    try:
        res = OpenAI().images.edit(model="gpt-image-1", image=handles, prompt=text,
                                   size=opt(args, "--size", "1024x1024"),
                                   quality=opt(args, "--quality", "high"), **kw)
    finally:
        for h in handles:
            h.close()
    out_dir = os.path.join(os.path.dirname(paths.out_dir(os.getcwd(), key)), "reference")
    os.makedirs(out_dir, exist_ok=True)
    raw = os.path.join(out_dir, f"ai_{name}_raw.png")
    open(raw, "wb").write(base64.b64decode(res.data[0].b64_json))
    print("wrote", raw)
    if "--ingest" in args:
        import aiingest
        stem = aiingest.ingest(key, raw, name)
        print("wrote", stem + ".tga (+ _layer.png, _preview.png, .ora)")
    else:
        print(f"next: ../../.venv/bin/python ../../tools/aiingest.py {key} {raw} --name {name}")


if __name__ == "__main__":
    main()
