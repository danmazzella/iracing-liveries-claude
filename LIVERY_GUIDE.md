# iRacing livery guide: everything we learned

Distilled from the liveries built in this repo with Claude Code (a vector team
livery with hex tiles, an art-car collage, a CFD "wind tunnel" livery, and a retro JPS-style
F1 livery), across three cars (BMW M4 GT3, McLaren 720S GT3 EVO, Lotus 79) and ~40 in-sim test rounds. Every fact here was checked
in the sim unless it says otherwise.

Read this first, then `cars/<car>/README.md` for the car you're painting.

---

## 1. How it works

Liveries are **Python scripts** that draw straight onto iRacing's 2048x2048 paint sheet
(Pillow + numpy). Each livery lives in its own folder under `liveries/` and writes into `liveries/<livery>/<car-key>/out/`, named
`<livery>_<car-key>_<build>` so the installer can find it (`<car-key>` = the folder name in `cars/`):

| File | What it is |
|---|---|
| `<livery>_<car-key>_<build>.tga` | the paint: 24-bit RGB, 2048x2048 |
| `..._spec.tga` | the spec map (finish: metallic / roughness / clearcoat). Optional extra finishes: `_spec_metal.tga`, `_spec_chrome.tga` |
| `..._preview.png` | the paint with the template's not-paintable mask drawn over it, for checking |

You copy the TGAs into iRacing's paint folder, press **Ctrl+R** in the sim, look, screenshot,
and repeat. Code (not Photoshop) makes it cheap to change one number and rebuild, to mirror
the design onto both sides automatically, and to write several finishes at once.

Minimal working example: `liveries/example/livery.py`. Grid/mapping tool: `tools/grid.py`.
Installer: `tools/install_paint.ps1 -Project <livery> -Car <car-key> [-Build N | -Final] [-Finish metal]`
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
  It draws a plate (white on the Valkyrie) over the whole block: a team number card must be bigger
  than the block (BMW: x1.47 along the number, x1.78 across) for its header/footer to show.
  Leave the number block areas plain (or put a clean card behind them).
- Wheel colour and tyre sidewall colour are set in iRacing's paint screen, not in our files.
- Car folders found so far: BMW M4 GT3 = `bmwm4gt3`, McLaren 720S GT3 EVO = `mclaren720sgt3`, Lotus 79 = `lotus79`, Formula IR04 (F4) = `formulair04`, Aston Martin Valkyrie GTP = `amvalkyriegtp`.
  For another car, look in `Documents\iRacing\paint\` (the folder appears once you've
  driven the car).
- Your customer ID is on your iRacing account page.

### Car keys (naming rule)

A car key names `cars/<key>/`, the livery output files (`<livery>_<key>_<build>`) and the installer's `-Car`.
**New cars: `<make>-<model>-<class>`, lowercase, hyphens, specific enough that a sibling car can't
share it** (several makes have a GT3 and a GT4, a Cup car and a GT3 R...). The iRacing paint folder is
separate and always recorded in the car README (`iRacing paint folder: \`...\``).

| Key | Car | iRacing folder |
|---|---|---|
| `bmw-m4-gt3` | BMW M4 GT3 | `bmwm4gt3` |
| `mclaren-720s-gt3` | McLaren 720S GT3 EVO | `mclaren720sgt3` |
| `ferrari-296-gt3` | Ferrari 296 GT3 | `ferrari296gt3` |
| `lotus-79` | Lotus 79 | `lotus79` |
| `formula-ir04` | Formula IR04 (F4) | `formulair04` |
| `aston-martin-valkyrie-gtp` | Aston Martin Valkyrie GTP | `amvalkyriegtp` |
| `porsche-992-cup` | Porsche 911 GT3 Cup (992.2) | `porsche9922cup` (`porsche992cup` is the older 992 Cup) |

The old short keys (`bmw`, `mclaren`, `ferrari`, `lotus79`, `ir04`, `valkyrie`) are retired: scripts refuse
them with a pointer to the new key. Never reuse a key for a different car (a BMW GT4 is `bmw-m4-gt4`).

### Livery folder layout

One folder per livery; inside it one folder per car (named by the car key). Scripts stay at the livery
level because one script usually serves several cars.

```
liveries/<livery>/
  CLAUDE.md, livery.py ...      design notes + version log, the scripts
  <car-key>/
    out/                        every build: <livery>_<car-key>_<build>.tga, _spec.tga, _spec_<finish>.tga, _preview.png
    reference/                  in-sim screenshots for this car
    final/                      THE approved set (see below)
    archive/                    superseded finals
  _misc/                      things that don't belong to one car (concept builds, old scripts)
```

**`final/` is what you install** (`install_paint.ps1 -Project <livery> -Car <car-key> -Final`):

| File | Meaning |
|---|---|
| `paint.tga` | the approved paint |
| `spec.tga` | **the spec to use** (the approved finish; `NOTES.md` names which finish it is) |
| `spec_<finish>.tga` | optional alternates (`metal`, `chrome`, `gold`, `shimmer`, `bold`, `shiny`, `standard`...) |
| `livery_vN.py` etc. | the script(s) that made it |
| `NOTES.md` | what the finish names mean, build number, install command |

A car with several colourways has `final/<variant>/` folders with the same files (`-Variant <name>`).
When you approve a build, copy it to `final/` under these names and make `spec.tga` the finish you
actually chose, never just whichever file happens to have no suffix.

Finish names: the plain `spec.tga` / `_spec.tga` is the default (`-Finish gloss` in the installer, "default" in the GUI), so never name an
alternate `gloss`. Keep only the newest build per car in `out/`; older ones are replaceable from the script (approved ones live in `final/`).

---

## 3. Templates (the PSD)

iRacing publishes a paint template (`.psd`) for every car. It's not included in this repo:
download it and put it in `psd/` (e.g. `psd/BMW M4 GT3.psd`). Scripts read the layers
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

1. `tools/grid.py "<car>.psd" <wire layer> <key>` (finds the PSD in `psd/`) writes a 32x32 grid of 64px coloured cells
   labelled `col,row` (cell c,r covers sheet x `c*64..c*64+63`, y `r*64..r*64+63`) with the
   wireframe on top. Copy `out/<key>_grid.tga` (in the folder you ran it from) to `cars/<key>/grid.tga` and start
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
5. **Map the seams** (section 4b) for any panels a design will cross (hood/bumper,
   fender/door, roof/pillars...).

Already mapped here: **BMW M4 GT3** (`cars/bmw-m4-gt3/`), **McLaren 720S GT3 EVO** (`cars/mclaren-720s-gt3/`), **Lotus 79** (`cars/lotus-79/`), **Formula IR04 / F4** (`cars/formula-ir04/`), **Ferrari 296 GT3** (`cars/ferrari-296-gt3/`), **Aston Martin Valkyrie GTP** (`cars/aston-martin-valkyrie-gtp/`); **Porsche 992.2 Cup** (`cars/porsche-992-cup/`, part table done 2026-10-01, seams not read).

Some templates' `Mask` covers almost nothing. The panel (UV island) outlines are then drawn in the
wireframe layer (Lotus 79: pure green lines in `Wire`): label the regions enclosed by them to get
each panel as a mask, and pick panels with a seed point. Check that a seed didn't land on the
background (it silently grabs the whole sheet).

Failed alternative: a colour-coded paint where each pixel's colour encodes its own sheet
position (`tools/uvcode.py`). Garage lighting shifts colours enough to throw the decode off
by 200-400 px. Use the labelled grid.

### 4b. Seam map (lines that cross panels line up the first time)

The grid says where a cell lands. It doesn't say **which panel edges touch in 3D**, and that's
where stripes broke and needed 3-8 rounds of nudging (section 7, "Seams between panels").
`tools/seams.py` maps the seams once per car:

1. `tools/seams.py ruler <car>` finds every panel from the template's Wire layer (the mesh
   lines enclose small cells inside a panel; holes are cells ringed only by the green outline;
   touching panels split along the green outline), gives it a code letter (biggest = A) and
   paints a numbered ruler along all its edges: 64 px segments `C0 C1 C2 ...`, a red tick at
   each segment start, codes underlined so a rotated 6/9 reads right. Writes
   `cars/<car>/seams.tga`, `seams_sheet.png` (flat, with the mask) and `islands.npz` (panels +
   edges; regenerate only together with the ruler, readings refer to it).
2. Install it (`install_paint.ps1 -Car <car> -Seams`), zoom on each seam and screenshot it
   (`cars/<car>/seam_<where>.webp`). Read where the two rulers meet and write the pairs to
   `cars/<car>/seams.json`: `["C12", "F48.5"]` = C12's start tick is opposite the middle of
   F48. Two readings per seam at least (its ends), one every ~150 px on long or curved seams.
   `mirror_y` in that file copies each reading to the mirrored panels, but only where the
   reflected points really fall on panel edges.
3. `tools/seams.py check <car>` unfolds the seamed panels and paints straight stripes across
   them (`seamcheck.tga`, install with `-SeamCheck`). Stripes running on across a seam
   without a step or kink = that seam's readings are right.
4. In a livery, draw on the **unfolded canvas**: `u = seams.Car("<car>").unfold("C")` roots
   it at panel C (its own sheet coords stay as they are) and warps every panel seamed to it
   so it sits against C. `X, Y, on = u.field()` gives design coords for every sheet pixel (for
   field designs: flow, noise, stripes as functions of X, Y); `u.pull(img)` samples a drawn
   design image onto the sheet. The warp is a thin-plate spline pinned to the seam
   readings, similarity transform away from the seam, so it matches position **and** angle,
   including shifts that vary along the seam (the BMW hood/bumper 1.04 → 1.186).
   Only seams on the unfold's tree are continuous (a panel follows the first one it was
   reached by); `u.skipped` lists the others.
- `tools/seams.py codes <car> x,y` (or `F@x,y` for panel F only) gives the ruler code at a
  sheet point: handy for turning a known in-sim match into a reading.
- Test run (BMW hood/bumper from the in-sim facts in section 7): seam points land within
  ~1 px on average (5 px worst) after unfolding.
- First in-sim round (BMW): whole-car shots at normal zoom were enough to read seams whose
  labels face the camera (hood/bumper centre, roof/windshield banner): zoom into the
  screenshot, find the tick pairs, estimate the offset as a fraction of a segment. Seams seen
  at a grazing angle need close-ups.
- **Don't let a reading pair span a spot where the edges don't touch** (the BMW bumper edge
  detours round the roundel on the centre line; the pair across it bent the stripes). Read up
  to it on one side and let `mirror_y` add the other half.
- Thin strips (roof rails, pillars): the rulers of both edges meet in the middle. The ruler
  clips each label to its own edge's band and shrinks it to fit.
- Stripe test v1 (BMW): stripes joined at every seam but **kinked**, and bent into arcs on
  the bumper. Two causes, both fixed in the tool:
  - Only positions were pinned at the seam, so the spline sheared the child panel there
    (4:1 stretch). Now the direction straight into the child is pinned to continue the
    direction straight out of the parent, at the seam's scale (UV unwraps are close to
    angle-preserving). Stretch at the seam went from 4.2 to 1.1.
  - A small notch in one edge (bumper next to the roundel) made that stretch of edge twice as
    long as the matching hood edge, and matching by arc length squeezed it. Readings are now
    matched by progress along the straight line between them, so notches collapse.
- Some kink is real: where a seam is a body crease (hood edge → bumper face, roof → windshield
  banner), a straight line on the surface looks bent in a screenshot. Judge steps, and whether
  the stripe width and spacing carry on, not the angle in the picture.
- Root the unfold at the best-connected panel (the roof), not the biggest: a big side panel
  hanging off one thin seam made a poor root, and everything chained through it came out garbled.
- **Read ticks where they touch the seam**, not along their length: ticks lean in perspective.
- A step in the stripe test isn't always a misread. The BMW roof/banner step came from a tool
  bug: those readings already crossed the centre line, and the mirror copy added a second,
  slightly different match a pixel away, which made the spline zig-zag (v3 tore the stripes
  once I "fixed" the readings the wrong way). Now mirror copies only fill what wasn't read.
  Before changing a reading, look at the flat `seamcheck.tga`: tears or wobbles there are
  tool problems, not readings.
- **Check the sheet for touching edges first**: some UV islands are laid out edge to edge
  (BMW roof ↔ rails, hood ↔ fender tops, 1-2 px apart). `codes <car> F@x,y` near one panel's
  edge then gives the other panel's matching code directly, which helps when the in-sim labels
  are too small. Still confirm with the stripe test.
- Stop a seam where an edge turns a corner (a reading past it made a 13:1 warp spike); the
  stretch/gap numbers from the Jacobian check find these before the sim does.
- Not every panel edge is a seam: the BMW door front edge and the front fender are separated
  by a 3D vent/gill, so graphics break there whatever you do.
- Seams can be read in pieces (left half, right corner): readings of the same two panels are
  merged into one seam.
- Stripe test v2 (BMW): hood → bumper and roof → rails → sides carried the stripes through
  cleanly, so designs crossing those seams line up with no tweaking.
- Reading precision: the same seam read on the other side of the car (BMW left roof rail)
  landed 5-9 px (~0.1 segment) from the mirrored prediction. Well under the ~60 px that shows
  in the sim, so one side + `mirror_y` is enough.
- Mirrored panels are paired by overlapping their reflected shapes, not by the panel under the
  mirrored seam points: the BMW roof edge and the rail edge sit 1-10 px apart on the sheet.

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
- Shimmering pattern (untested in-sim yet): vary metallic/roughness **per pattern cell** (each hex
  tile its own random value) instead of one value per colour, so neighbouring cells catch the light
  differently as the camera moves (white-gofast `_spec_shimmer`).

---

## 6. Colour

- **Sample colours from the reference** (median over a patch), don't pick them by eye.
- Pale gradient highlights and white sheen turn orange into tan/amber in the sim.
- For a vivid colour: fully saturated, no white sheen, metallic 0.
- **Per-shape gradients mismatch where shapes on different panels meet** (bumper vs hood:
  adjacent shapes met at opposite ends of their gradients). Use flat colour for graphics that
  cross panel seams.
- Single-colour line art disappears on the same colour (an orange mascot on an orange stripe).
- Every stripe/shard should visibly start from something (another graphic, a panel edge, a
  number board). A blunt base floating in plain white reads as "coming out of nowhere": tuck the
  base under the graphic it springs from (draw it first, then the block over it).
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
- **Seam ruler** for the last few px: when nudging an edge back and forth doesn't converge, paint 8 px
  bands of distinct colours (constant y) across both panels at the seam (`liveries/white-gofast/ruler.py`),
  take one in-sim close-up and read which band meets which. The 64 px grid is too coarse for this.
- The shift varies across the seam: near the centre line it's small (scale 1.04 about the
  mirror line), by the headlight it's larger (1.186). A single scale for the whole seam put
  stripes 20-35 px off. Continuous stripes across a seam: copy the hood's seam column onto the
  bumper with a measured scale and verify in-sim. **Now: map the seam (section 4b) and draw on
  the unfolded canvas instead.**

- **UV cuts inside one body surface** (F4 sidepod: top and side strips touch only at the front,
  a wedge gap opens behind). Anything computed from sheet coords (noise, flow fields, stripes)
  jumps there in 3D. Fix it in coordinates: per sheet column, measure the gap and shift one
  strip against the other before evaluating the field (smooth the gap lightly, or you get
  ragged edges). **Measure the true edges from the Wire outlines, not the Mask**: the mask
  bleeds ~10 px past each panel edge and can even join strips that are still cut in 3D (the
  mask-based fix left a visible step; the outline-based one closed it to 1-2 px).

- **Islands that touch in 3D but sit far apart on the sheet** (Valkyrie roof/engine cover, spine, fin):
  a sheet-coordinate pattern (collage, noise) breaks up across them. Cheapest fix: fill those islands
  with a regular small pattern that doesn't need to line up (polka dots), picked by seed point
  inside the Wire outlines (`calm` in `liveries/polkadot`). Otherwise map the seams (4b).

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
- **Rear wing and roof decals read from the FRONT of the car.** The user wants
  wing text upright when viewed **from the front of the car** (looking back over the car at the wing),
  not from a chase camera behind it. On the Ferrari 296 that's rot 0 (rot 180 read from behind and was
  rejected). Applies to **every car and livery**; set it this way from the first build. Values in use:
  BMW rot 0 (box 1385-2040 x 312-598), McLaren rot 0 (0-640 x 170-290), Ferrari rot 0, Lotus 79 rot -90,
  IR04 rot 0. **Roof logos too**: letter tops toward the rear (sheet +x when the front is on the left),
  e.g. rot -90 for text across the BMW/McLaren roof (rot 90 = top toward the nose, rejected). Roof
  mascots too: the polkadot roof hornet was flipped the same way (rot 90 -> -90, head toward the rear).
**Crayon / hand-drawn look (elmers-glue, Porsche)**
- Crayon reads as crayon when it is **mostly solid wax with a few broad stroke bands in one direction** plus waxy grain gaps. Regular crossing hatching reads as a picnic blanket (plaid).
- Raster logo art (user drawings) on a dark base needs a **cream paper label or a paper-cutout edge** behind it (flood-fill the background, dilate ~20 px, fill holes): the unfilled interior otherwise shows the base colour.
- Composite logo stamps **after** glitter/sparkle layers, or the sparkles draw over them.
- Before placing a large logo, check the car README for 3D parts (hood vents, deck cut-outs): the flat preview hides how much they cover. Roof is usually the safest big canvas.
- Paper whites read beige in the sim; keep label paper bright (#FBF8F1 or lighter).

- Logo orientation: work out the rotation per spot (a hood mascot at rot 90 looked upside
  down; rot −90 was right). Put rotation in the per-car config and confirm in-sim.

---

## 8. Matching a reference image

We tried to reproduce an AI-rendered mockup exactly.

- **Hand-placing polygons by eye drifted badly** (8 rounds, no convergence).
- **Projecting the mockup's pixels onto the sheet** works geometrically (`tools/labelproj.py`):
  read `(screen px) → (col,row)` from the grid screenshots for visible labels in each view
  (`cars/bmw-m4-gt3/projection/*_bmw.py` holds those for the BMW: front, side, rear, top), add ~10
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
   folder (`liveries/<livery>/livery.py`, builds in `.../<car-key>/out/`), builds, and checks the preview (crop and zoom
   on problem areas; draw the mask over it).
3. Install (`tools/install_paint.ps1 -Project <livery> -Car <car>`), Ctrl+R, take screenshots from the same angles each time.
4. **Save screenshots as files in the repo** (`liveries/<livery>/<car-key>/reference/`) and give Claude the path.
   Screenshots pasted into chat aren't always saved as files, and `/tmp` gets wiped.
5. Claude fixes and **writes down what it learned**: version notes in `liveries/<livery>/CLAUDE.md`
   (what changed, what the in-sim result was), placement facts in `cars/<car>/README.md`,
   general lessons here.
6. Number every build (v1, v2, ...). Copy approved builds to `liveries/<livery>/<car-key>/final/` (`paint.tga`, `spec.tga`, ...: section 2) together with a
   copy of the script that made them.

Feedback that helped: say what's wrong **and where** ("orange too high above the headlight on
the front", "the hood edge bows the wrong way"), and whether something is good and must be kept.

---

## 11. Finishing a livery by hand (GIMP / Krita)

The scripts can also save **layered OpenRaster files** (`.ora`, via `tools/ora.py`) next to the
TGAs. GIMP and Krita open them with every layer kept apart; in GIMP, Save As `.xcf` to keep a
GIMP file. `liveries/example/livery.py` shows the pattern: draw each part on its own transparent layer
(`ora.paint_layer(colour, shape)`), list them bottom → top, and flatten the same list for the
TGA, so the `.ora` and the TGA always match:

- `<name>.ora`: base, graphics, template trim and decals, plus hidden `GUIDE` layers (number
  blocks, sponsor blocks, wireframe, not-paintable mask) to turn on while editing.
- `<name>_spec.ora`: one layer per finish, R = metallic, G = roughness (section 5), plus the
  paint as a hidden guide. Paint a finish with the exact colour `(metallic, roughness, 0)`.

Things to know:
- **Hand edits don't go back into the script.** Rebuilding overwrites the `.ora`, so do the
  code work first and the hand touches last (and save the `.xcf` under another name).
- **Mirroring isn't automatic by hand.** The right side is upside down on the sheet (section 3):
  copy an edit to the other side with a vertical flip about the mirror line; text and logos
  need a 180° rotation instead.
- Export: Image > Flatten Image, Export As `.tga` with RLE unticked, then undo the flatten.
  Flattening drops the hidden guides and the alpha (24-bit). Then install it like any build.
- GIMP 3.2 exports the same pixels as the script's TGA except on anti-aliased edges (it blends
  soft edges slightly differently). Nothing visible on the car.
