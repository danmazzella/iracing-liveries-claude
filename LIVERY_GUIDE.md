# iRacing livery guide: everything we learned

Distilled from the liveries built in this repo with Claude Code (a vector team
livery with hex tiles, an art-car collage, a CFD "wind tunnel" livery, and a retro JPS-style
F1 livery), across three cars (BMW M4 GT3, McLaren 720S GT3 EVO, Lotus 79) and ~40 in-sim test rounds. Every fact here was checked
in the sim unless it says otherwise.

Read this first, then `cars/<car>/README.md` for the car you're painting.

---

## 1. How it works

Liveries are **Python scripts** that draw straight onto iRacing's 2048x2048 paint sheet
(Pillow + numpy). Each livery lives in its own folder and writes into `<livery>/out/`, named
`<livery>_<car>_<build>` so the installer can find it (`<car>` = the folder name in `cars/`):

| File | What it is |
|---|---|
| `<livery>_<car>_<build>.tga` | the paint: 24-bit RGB, 2048x2048 |
| `..._spec.tga` | the spec map (finish: metallic / roughness / clearcoat). Optional extra finishes: `_spec_metal.tga`, `_spec_chrome.tga` |
| `..._preview.png` | the paint with the template's not-paintable mask drawn over it, for checking |

You copy the TGAs into iRacing's paint folder, press **Ctrl+R** in the sim, look, screenshot,
and repeat. Code (not Photoshop) makes it cheap to change one number and rebuild, to mirror
the design onto both sides automatically, and to write several finishes at once.

Minimal working example: `example/livery.py`. Grid/mapping tool: `tools/grid.py`.
Installer: `tools/install_paint.ps1 -Project <livery> -Car <car> [-Build N] [-Finish metal]`
(run it with no options for help). It maps car keys to iRacing folders from the
`iRacing paint folder: \`...\`` line in `cars/<car>/README.md`, so keep that line in every car README.

---

## 2. iRacing facts

- Paint file: `Documents\iRacing\paint\<carfolder>\car_<customerID>.tga`.
  Spec file: `car_spec_<customerID>.tga` in the same folder.
- iRacing builds a `.mip` from the spec itself. **Delete the old `car_spec_<id>.mip`** when you
  replace the spec, or it can go stale. (`tools/install_paint.ps1` does this.)
- **Ctrl+R** in the sim reloads paints. No restart needed.
- **One custom paint per car per account.** Installing a livery replaces whatever was on that
  car. Different cars are independent.
- **iRacing draws the car number** on the template's number blocks. Never paint numbers.
  Leave the number block areas plain (or put a clean card behind them).
- Wheel colour and tyre sidewall colour are set in iRacing's paint screen, not in our files.
- Car folders found so far: BMW M4 GT3 = `bmwm4gt3`, McLaren 720S GT3 EVO = `mclaren720sgt3`, Lotus 79 = `lotus79`, Formula IR04 (F4) = `formulair04`.
  For another car, look in `Documents\iRacing\paint\` (the folder appears once you've
  driven the car).
- Your customer ID is on your iRacing account page.

---

## 3. Templates (the PSD)

iRacing publishes a paint template (`.psd`) for every car. It's not included in this repo:
download it and put it in the repo root (e.g. `BMW M4 GT3.psd`). Scripts read the layers
directly with `psd-tools`. List a template's layers with `tools/grid.py "<file>.psd"`.

Conventions that held on both templates:

- **Front of the car is on the left** of the sheet.
- **The sheet is mirrored about a horizontal line** (BMW y = 1311.5, McLaren y = 1206.5).
  Larger y = the car's **left** side; smaller y = right side. **The right-side panel is upside
  down.** Hood, roof and trunk sit across the mirror line (the line is the car's centre line).
  - Design body graphics once in lower-half (car's left) coords and mirror them:
    `y_top = 2*mid - y`.
  - Text and logos can't just be mirrored (they'd read backwards). Paste them separately on
    the right side, **rotated 180°**.
  - If a side panel is tilted on the sheet (McLaren: ~5°), the mirrored copy of a rotated logo
    needs rotation `180 - rot`, not `rot + 180`.
  - Parts outside the mirrored band (McLaren rear bumper at the sheet top, y < ~366) are not
    mirrored copies: draw both corners explicitly.
- Useful layers (names differ per car, so list them):
  - `Mask`: alpha = **not** paintable. Draw it over previews.
  - `wire` / `Wire`: UV wireframe. Used by the grid.
  - `Carbon Fiber` (BMW) / `Car_decal` (McLaren): black/carbon trim, splitter, diffuser.
    Composite it **over** your paint.
  - `Car_decal` (BMW): manufacturer decals + the windshield banner shape. Keep on top.
  - `Number Blocks`, `Sponsor`: where iRacing's number and sponsor boxes go.
  - A hidden custom-spec group (`Custom Spec/rough`, `Custom Spec Map/Green Channel Roughness`)
    with the trim's roughness. Reuse it for the trim in your spec map.
  - Drop series-specific decal layers you don't want (the McLaren's IMSA layer), but you can
    still use their shapes (e.g. as the windshield banner outline).
  - Don't use the template's example metallic spec layer: it chromes some paintable parts.

---

## 4. Map the car before designing (the grid)

**Panels are not where they look on the sheet.** Examples we hit:
- On the BMW, the two dark rounded rectangles that look like side windows are the **kidney
  grille**. Stripes drawn over the "door top" band ended up on the front of the car.
- The BMW front fender louvers sit next to the grille frame on the sheet, nowhere near the fender.
- The McLaren front wheel-arch vent is an island on the sheet's **right edge**.

So map every new car first:

1. `tools/grid.py "<car>.psd" <wire layer> <key>` writes a 32x32 grid of 64px coloured cells
   labelled `col,row` (cell c,r covers sheet x `c*64..c*64+63`, y `r*64..r*64+63`) with the
   wireframe on top. Copy `out/<key>_grid.tga` to `cars/<key>/grid.tga` and start
   `cars/<key>/README.md` with the line ``iRacing paint folder: `<folder>` `` (the installer reads it).
2. Install it: `tools/install_paint.ps1 -Car <key> -Grid`. In the sim take screenshots: front, front 3/4, both
   sides, rear, rear 3/4, top. Save them in `cars/<car>/` as `grid_<view>.webp`.
   **If a part's labels aren't readable (hidden, too small, edge-on), Claude asks for more
   angles** instead of guessing: close-ups (halo, mirrors, cockpit rim), low front/rear (wing
   undersides, diffuser), straight-on of the other side. List what's still unmapped in the README.
   The paint-screen camera is limited (no low or underside views): ask only for what it can
   reach (zoomed top-down, close-ups from above, the preset side/front/rear views).
3. Read the labels in each screenshot and write a **part → columns/rows table** in
   `cars/<car>/README.md` (see the BMW and McLaren ones). Note the mirror line, the
   orientation of the bumpers (the BMW front bumper's x runs bottom→top), and what 3D parts
   sit over paint.
4. Keep a "Proven placements" and a "Gotchas" section in that README and add to it after
   every in-sim round.

Already mapped here: **BMW M4 GT3** (`cars/bmw/`), **McLaren 720S GT3 EVO** (`cars/mclaren/`), **Lotus 79** (`cars/lotus79/`), **Formula IR04 / F4** (`cars/ir04/`).

Some templates' `Mask` covers almost nothing. The panel (UV island) outlines are then drawn in the
wireframe layer (Lotus 79: pure green lines in `Wire`): label the regions enclosed by them to get
each panel as a mask, and pick panels with a seed point. Check that a seed didn't land on the
background (it silently grabs the whole sheet).

Failed alternative: a colour-coded paint where each pixel's colour encodes its own sheet
position (`tools/uvcode.py`). Garage lighting shifts colours enough to throw the decode off
by 200-400 px. Use the labelled grid.

---

## 5. Spec map (finish)

Channels: **R = metallic, G = roughness** (lower = shinier), **B = clearcoat**. The templates
leave B at 0 everywhere (= full clearcoat); we do the same and don't touch it.

What we measured in the sim (values 0-255):

| Finish | Metallic | Roughness | Result |
|---|---|---|---|
| Satin | any | 16-26 | reads as satin in the garage |
| "Shiny like a render" | any | ≤ 8 | glossy |
| White/silver pearl | 35 | 6 | good; greys up to ~160 metallic read as silver |
| Navy, deep metallic | 150 | 8 | good |
| Vinyl stickers/logos/cards | 0 | 18 | good |
| Orange, metallic 215 | 215 | - | looked **bronze** |
| Orange, metallic 120 | 110-120 | - | metallic orange, but dull/muddy in garage light |
| Orange, vivid | **0** | 4 | most vivid: any metallic greys orange out in garage light |
| Orange under "metal"/"chrome" finish | up to ~170 | 2-6 | OK on a bright base (`#FF7300`); 235 went too dark |
| Chrome | 160-245 | 2 | strong reflections; colours get darker off-angle |
| Orange pinstripes as "gold leaf" (on navy) | 150 | 4 | darker bronze-gold orange: a retro JPS gold look (Lotus 79) |

Rules of thumb:
- **Metallic darkens coloured paint** (reflections replace the base colour). Bright, saturated
  colours want low metallic; whites, greys and dark blues take metallic well.
- Write several finishes per build (e.g. `_spec.tga` gloss, `_spec_metal.tga`,
  `_spec_chrome.tga`) and let the user swap them in-sim without touching the paint.
- Give each area its finish from what's under it: body colour, graphic, sticker, and the
  template's own roughness for trim.

---

## 6. Colour

- **Sample colours from the reference** (median over a patch), don't pick them by eye.
- Pale gradient highlights and white sheen turn orange into tan/amber in the sim.
- For a vivid colour: fully saturated, no white sheen, metallic 0.
- **Per-shape gradients mismatch where shapes on different panels meet** (bumper vs hood:
  adjacent shapes met at opposite ends of their gradients). Use flat colour for graphics that
  cross panel seams.
- Single-colour line art disappears on the same colour (an orange mascot on an orange stripe).
- The flat preview lies about colour: garage lighting and the spec change it a lot. Only
  in-sim screenshots count.

---

## 7. Placement and design lessons

**Scale of changes**
- Moves under **~60 sheet px** are barely visible in the sim at normal camera distance. Make
  decisive moves. (A 40 px nudge got "I see no change".)
- Always compare before/after screenshots side by side with the reference, **panel by panel**
  (side, front, rear, top). "Close in the flat preview" was wrong several times.

**3D parts cover paint**
- Check each decal against the `Mask` **and** the 3D parts: tail lights, LED position lights,
  mirrors and vents sit on top of paint and cut decals off. (A BMW rear mascot was cut by the
  tail light; the McLaren door strip had to end ~75 px early for the IMSA LED light.)
- Door decals can't always grow lengthwise: number card in front, lights behind.

**Seams between panels**
- The same sheet y does **not** line up across the hood/bumper seam. On the BMW, an edge at
  bumper (x 255, y 1490) continues on the hood at y ≈ 1462 near the headlight. Match the edge's
  **angle** across the seam too, not just its position.
- The shift varies across the seam: near the centre line it's small (scale 1.04 about the
  mirror line), by the headlight it's larger (1.186). A single scale for the whole seam put
  stripes 20-35 px off. Continuous stripes across a seam: copy the hood's seam column onto the
  bumper with a measured scale and verify in-sim.

**Shapes**
- Reference designs are usually **curved** (they follow body lines). Use Bezier edges, not
  straight polygons. Check which way a curve bulges in-sim: on the BMW bumper (x = height), a
  control point toward higher x / lower y bulges toward the grille; low and outward gives a
  concave edge.
- Stretched lettering reads wrong at car scale (a G stretched 1.6x read as a "U").
- Busy texture (random tiles, speed bars) looks messy on small panels like bumpers. Keep them calm.
- Thin lines can read as plain grey from distance; check line art in-sim.
- Render at 2x and downsample for anti-aliasing.
- **Pinstripes/coachlines that follow panel edges**: take the panel mask (see section 4), then
  either the distance transform inside it (a band at distance d..d+w = an inset frame) or, for
  one edge only, the per-column top/bottom edge smoothed and offset. They follow the real panel
  shape for free. Leave out UV seam edges that aren't real panel edges (limit the frame by x).
  Stacked offset stripes in shades of one colour ("sunset stripes") gave a 70s car its pizazz.
- Tilted text: fit the text to its box first, then rotate. Fitting the rotated bounding box
  shrinks long lettering badly (a 4-degree tilt on a 470 px line cost half the letter height).
- `Image.thumbnail` never upscales. Use a resize-to-fit helper that rotates first, then scales
  (up or down) to the box, so the box is given in sheet axes:
  ```python
  def fit(im, box, rot=0):
      im = im.rotate(rot, expand=True, resample=Image.BICUBIC)
      k = min(box[0] / im.width, box[1] / im.height)
      return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)
  ```
- Logo orientation: work out the rotation per spot (a hood mascot at rot 90 looked upside
  down; rot −90 was right). Put rotation in the per-car config and confirm in-sim.

---

## 8. Matching a reference image

We tried to reproduce an AI-rendered mockup exactly.

- **Hand-placing polygons by eye drifted badly** (8 rounds, no convergence).
- **Projecting the mockup's pixels onto the sheet** works geometrically (`tools/labelproj.py`):
  read `(screen px) → (col,row)` from the grid screenshots for visible labels in each view
  (`cars/bmw/projection/*_bmw.py` holds those for the BMW: front, side, rear, top), add ~10
  landmarks between the screenshot and the mockup (wheel hubs, lights, roundel), and
  thin-plate splines compose to sheet → mockup. The side view is mirrored for the other side.
- **But the projected paint was rejected** as a livery: an AI render is too low-res and has
  lighting baked in, so it looked smeared.
- What worked: use the projection as a **placement guide**, then build clean vector shapes +
  flat colours on top of it. Clean shapes beat copied pixels.
- The `LABELS` in the BMW projection files are reusable for any design on the BMW; the
  `LANDMARKS` are specific to our mockup, so you'd redo those for yours.

---

## 9. Techniques from the three liveries

Ideas that worked, to reuse or remix:

- **Vector team livery** (hex tiles + slashes): white/silver hex tile base that gets greyer
  toward the rear; tiles next to a graphic "break off" in its colour with a probability that
  falls with distance (keep it light on bumpers). Graphics are `(colour, polygon)` lists in
  lower-half coords, mirrored. Sharp thin triangles ("shards") sweeping rearward for speed.
  Painting small awkward islands (louvers, arch vents) the graphic colour instead of base
  made the car look finished.
- **Art-car collage**: Voronoi shards filled with patterns (stripes, dots, checks) plus big
  "mega dots", revealed through a halftone dot mask that grows from nose to tail. A cartoon
  comic-burst side decal read far better than straight borders or torn paper.
- **CFD flow ("aero lab")**: stream function `psi = y` (flow runs nose→tail along sheet x),
  plus potential-flow cylinders at the wheels/mascots, noise turbulence toward the tail and
  point vortices in the wake. Streamlines = contour lines of psi, drawn analytically so line
  width stays even; coloured by airspeed `|grad psi|`. "Smoke ribbons" = filled psi bands.
  Because it's a field, the whole design follows the body and wraps around features for free.

---

## 10. Working loop with Claude

1. New car? Map it (section 4). Existing car? Read `cars/<car>/README.md`.
2. Describe the design (or give a reference image). Claude writes the livery script in its own
   folder (`<livery>/livery.py`, `<livery>/out/`), builds, and checks the preview (crop and zoom
   on problem areas; draw the mask over it).
3. Install (`tools/install_paint.ps1 -Project <livery> -Car <car>`), Ctrl+R, take screenshots from the same angles each time.
4. **Save screenshots as files in the repo** (`<livery>/reference/`) and give Claude the path.
   Screenshots pasted into chat aren't always saved as files, and `/tmp` gets wiped.
5. Claude fixes and **writes down what it learned**: version notes in `<livery>/CLAUDE.md`
   (what changed, what the in-sim result was), placement facts in `cars/<car>/README.md`,
   general lessons here.
6. Number every build (v1, v2, ...). Copy approved builds to `<livery>/final/` together with a
   copy of the script that made them.

Feedback that helped: say what's wrong **and where** ("orange too high above the headlight on
the front", "the hood edge bows the wrong way"), and whether something is good and must be kept.
