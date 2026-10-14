# AI brief: bmw-m4-gt3

Attach: `guide_atlas.png` (layout to paint on, no text on it), `guide_legend.png` (colour -> panel names) and `guide_wire.png` (panel outlines).

## Prompt

This image is a flat 2048x2048 UV paint sheet for a race car (bmw-m4-gt3), not a picture of a car.
Every coloured region is a body panel (image 2 names each colour). Dark grey areas are not paintable
(leave them dark grey). Redraw the sheet as the finished livery artwork:

DESIGN: GoFAST Racing BMW M4 GT3, "Updated livery concept v2: same identity, more detail, more impact". Palette: navy #1E2744, vivid orange #FF7300 (league orange #E36400), white / light grey. Flat vector vinyl style, bold shapes, no gradients, no glow.

Overall: a white and light-grey hexagon (honeycomb) mosaic covers the body, slightly greyer toward the rear. Near the graphics some hex tiles break off in orange or navy. Large navy panels with sharp orange and white slashes/shards that sweep rearward give speed. Orange swoops wrap the front fenders and headlight area. Carbon trim (template) sits on top, never painted.

Rules:
- Same size, same layout: every panel stays exactly where it is, edges do not move.
- Paint inside each coloured region only; fill it edge to edge with artwork, no labels, no outlines.
- Flat 2D artwork as it would print on vinyl: no 3D rendering, no lighting, shadows or reflections.
- Solid flat colours with crisp edges. No gradients, glows, blurs, soft shading or smudged blends,
  and no colour bleeding across panel edges. Navy and orange stay saturated; whites stay clean white.
- The sheet is mirrored about the horizontal centre of the sheet (front of the car at the LEFT). The lower
  half is the car's left side, the upper half its right side (upside down). Make the upper half
  a vertical mirror image of the lower half, except text/logos (those must read correctly).
- Plain white rectangles with a thin grey outline are where the car number plate goes: leave them
  plain white, no outline, and keep every logo, text and mascot completely outside them (at least
  a box-width away). Put wide logos on the long open stretch of the side panel, well behind or in
  front of the number plate, never starting next to it.
- The wing (E) is a normal panel: paint it with bold flat colour or stripes, never grey.
- The output must contain NO text from this brief: no panel names, no "NUMBER", no title line, no
  dashed centre line, no legend.
- No car numbers, no sponsor boxes, no small text.
- If a fourth image is attached it is a 3D concept render of the finished car: copy its colours, shapes and
  style only, never its perspective, and never draw anything but the flat sheet layout.
- Keep graphics bold and simple: they are seen from a distance on a curved car.

Regions:
- **A**: LEFT SIDE: door, fender, rear quarter (upright)
- **B**: RIGHT SIDE: door, fender, rear quarter (upside down, mirror of A)
- **C**: HOOD (nose at left edge)
- **D**: ROOF
- **E**: REAR WING top surface
- **F**: FRONT BUMPER (x = height, y = across the car)
- **K**: WINDSHIELD BANNER strip
- **J**: REAR WINDOW / TRUNK
- **M**: right front fender top (mirror of N)
- **N**: left front fender top (mirror of M)
- **L**: rear bumper part (unverified)
- **R**: rear bumper part (unverified)
- **W**: rear bumper / trunk part (unverified)

Keep clear of (3D parts cover paint here):
- kidney grille: dark rounded rects at x 955-1215, y 1580-1690 (NOT windows)
- front fender louvers x 1195-1500, y 1558-1700 (left), y 951-1035 (right)
- tail light about x 1730-1850, y 1540-1700 (left): covers paint
- hood vents x 380-530, y 1400-1520
- car number blocks: leave plain, iRacing draws the number

## Base pass (the pattern layer, opaque)

Same images. Use the Prompt above but replace the whole DESIGN paragraph with:

DESIGN: PATTERN ONLY. GoFAST Racing BMW M4 GT3, "Updated livery concept v2: same identity, more detail, more impact". Palette: navy #1E2744, vivid orange #FF7300 (league orange #E36400), white / light grey. Flat vector vinyl style, bold shapes, no gradients, no glow. Cover every coloured panel with a white and light-grey hexagon (honeycomb)
mosaic, tiles slightly greyer toward the rear. NO slashes, NO logos, NO mascots, NO orange or navy. Keep the dark grey
areas dark grey and the number rectangles plain white.

## Element pass (one layer, for models without transparency)

Same images. Paste this instead of the Prompt above, once per layer:

This image is a flat 2048x2048 UV paint sheet for a race car, not a picture of a car (image 2 names each
colour). Keep the exact same layout. Draw ONLY this element: <ELEMENT>. Draw nothing else.
Style: GoFAST Racing BMW M4 GT3, "Updated livery concept v2: same identity, more detail, more impact". Palette: navy #1E2744, vivid orange #FF7300 (league orange #E36400), white / light grey. Flat vector vinyl style, bold shapes, no gradients, no glow.
- Fill EVERYTHING else, every panel, the background and the dark areas, with one flat solid magenta #FF00FF.
  No base colour, no pattern, no shadows, no outlines, no gradients, no glow, no anti-aliasing halo.
- The element itself is flat 2D vinyl art with crisp edges. Never use magenta, pink or purple in the element.
- The element sits inside the coloured panels, clear of the dark grey areas and of the plain white number
  rectangles. No text from this brief copied into the image, no car numbers.
- Mirror rule: the lower half is the car's left side, the upper half its right side (upside down). Draw the
  element on both halves, mirrored, with text/logos reading correctly.

## Bring it back

    ../../.venv/bin/python ../../tools/aiingest.py bmw-m4-gt3 <model_output.png> --name mydesign [--mirror]

Element passes: base image first (the pattern/colour pass), then
    ... --layer navy=navy.png --layer text=text.png --key "#FF00FF" --split
