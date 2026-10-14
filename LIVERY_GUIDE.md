# iRacing livery guide: everything we learned

Distilled from the liveries built in this repo with Claude Code (a vector team
livery with hex tiles, an art-car collage, a CFD "wind tunnel" livery, and a retro JPS-style
F1 livery), across three cars (BMW M4 GT3, McLaren 720S GT3 EVO, Lotus 79) and ~40 in-sim test rounds. Every fact here was checked
in the sim unless it says otherwise.

Read this first, then `cars/<car>/README.md` for the car you're painting.

---

## 0. Principles for every livery (read first)

Distilled from a professional hand-made livery (the GFR BMW V2 GIMP file, sections 13f and 14) and our ~40 in-sim rounds.
They are colour- and theme-neutral. `liveries/example/livery.py` follows all of them: start new liveries from it.

**Design**
1. **Tiny palette.** A base, one main colour, one accent. Every other tone is a *shade* of those (`depth.shades(colour)` gives
   dark / light / deep, with shadows leaning toward red for warm colours and deep blue for cool ones). New hues read as noise.
2. **Flat shapes + depth passes.** Draw each shape in flat colour, then add depth over it:
   a shadow (black ~40-60%, fading out: `depth.shadow`), a faceted texture cut to the shape with feathered edges
   (`lowpoly.overlay`), and a few light/dark slivers (`depth.fade`). Everything fades; only the shape outlines are hard.
   Smooth gradients still break at panel seams (section 6); random facets and fades don't, because they have no direction to break.
3. **Overlap tells the order.** Base -> big sweep -> contrast shape -> accent shards -> logos. Each colour starts from the one
   under it (section 6: nothing floats alone).
4. **Motion.** Shapes swell toward the rear and end in rear-pointing tips; thin ends taper, never stop square.
5. **No empty base.** A light base gets a low-contrast pattern (tones within ~10% brightness, like the hex greys) or texture,
   so plain panels read as finished. Keep bumpers and small panels calm (section 7).
6. **Hierarchy of marks.** One big wordmark per side, inside a contrasting shape, right behind the number card; one mascot on
   a plain area of the rear quarter; small marks on small panels (mirrors, lower arch, wing endplate); class badge near the
   number. Sides and top carry the big graphics. Check the car README for panel edges and notches before sizing text.
7. **Finish by material.** One spec value per paint colour, mid roughness, contrast through metallic (sections 5, 13b).

**Construction**
1. **Draw past the panel edges** and let the template's mask and trim clip. Hand-trimmed shapes break at seams and can't be
   reused on another car; overshooting shapes port cleanly (13g). Never leave filler right at a panel edge: template masks
   are a little tight in places, and dark filler 1-20 px outside the mask showed in-sim (Ford rear quarter). Bleed the paint
   ~40 px past every paintable edge (nearest-pixel fill) if a layer stops at the outline.
2. **Design the car's left side once, mirror it** about the centre line for the right; rotate text, don't mirror it (section 3).
3. **Logos are separate files on their own layers**, placed last and never painted into shapes. Keep source assets (logos,
   pattern tiles, textures) as files.
4. **Template trim and decals sit above the art.**
5. **Layered file like a hand-made one** (`ora.Layer(..., group=...)`, `tools/ora2xcf.py` for GIMP):
   `Turn Off Before Exporting TGA` (hidden guides: mask, wire, number/sponsor blocks) and `Paintable Area` holding
   `Left side/`, `Right side/`, `Top/`, loose logo/card layers and the template trim. A hand-finisher finds his way around.
6. **Add layers instead of repainting** (`... V2`, `... on top`); keep variants (driver names, sponsors) as hidden layers.

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
| `ford-mustang-gt3` | Ford Mustang GT3 | `fordmustanggt3` (`fordmustanggt4` is the GT4) |
| `ford-mustang-nextgen` | Ford Mustang NASCAR Next Gen | `stockcars fordmustang2022` (has a space) |
| `lotus-79` | Lotus 79 | `lotus79` |
| `formula-ir04` | Formula IR04 (F4) | `formulair04` |
| `aston-martin-valkyrie-gtp` | Aston Martin Valkyrie GTP | `amvalkyriegtp` |
| `porsche-992-cup` | Porsche 911 GT3 Cup (992.2) | `porsche9922cup` (`porsche992cup` is the older 992 Cup) |
| `mercedes-amg-gt3` | Mercedes-AMG GT3 2020 (Evo) | `mercedesamgevogt3` |
| `porsche-992-gt3r` | Porsche 911 GT3 R (992) | `porsche992rgt3` (not the Cup car) |

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
    Some panels' twins sit off the exact reflection (BMW right front fender: 27 px): mirror with
    `seams.Car(key).flip(layer)` (section 4b).
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

So map every new car first (and **measure the mirror line** by flipping the `Mask` about candidate y values, best overlap wins: the Mercedes grid reading said 1312, the true line is 1327, and every centred graphic sat ~20 px off in-sim):

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
   The user maps in the paint screen only (loading a session for a replay camera takes too long).
   The installer puts a flat matte spec under mapping paints so lighting doesn't wash labels out (4c).
   Seams that run along the car can be read off iRacing's gradient pattern first (4c), so screenshots go to the rest.
3. Read the labels in each screenshot and write a **part → columns/rows table** in
   `cars/<car>/README.md` (see the BMW and McLaren ones). Note the mirror line, the
   orientation of the bumpers (the BMW front bumper's x runs bottom→top), and what 3D parts
   sit over paint.
4. Keep a "Proven placements" and a "Gotchas" section in that README and add to it after
   every in-sim round.
5. **Map the seams** (section 4b) for any panels a design will cross (hood/bumper,
   fender/door, roof/pillars...).

Already mapped here: **BMW M4 GT3** (`cars/bmw-m4-gt3/`), **McLaren 720S GT3 EVO** (`cars/mclaren-720s-gt3/`), **Lotus 79** (`cars/lotus-79/`), **Formula IR04 / F4** (`cars/formula-ir04/`), **Ferrari 296 GT3** (`cars/ferrari-296-gt3/`), **Aston Martin Valkyrie GTP** (`cars/aston-martin-valkyrie-gtp/`); **Porsche 992.2 Cup** (`cars/porsche-992-cup/`, part table done 2026-10-01, seams not read); **Ford Mustang GT3** (`cars/ford-mustang-gt3/`, first-pass part table 2026-10-01, bumpers approximate, seams not read); **Mercedes-AMG GT3 2020** (`cars/mercedes-amg-gt3/`, first-pass part table 2026-10-05; nose at low x, centre line y = 1327, left side = high rows, wing = cols 0-10 rows 0-4; seams not read); **Porsche 911 GT3 R (992)** (`cars/porsche-992-gt3r/`, part table + front/roof seams 2026-10-13; centre line y = 1299.5, nose at low x, left side = high rows; rear seams not read); **Ford Mustang NASCAR Next Gen** (`cars/ford-mustang-nextgen/`, first-pass part table 2026-10-01; nose at HIGH x, centre line y ~ 1280, left side = low rows; bumpers/spoiler approximate, seams not read).

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
  by a 3D vent/gill. Graphics still carry over it if you read the two rulers across the vent at equal height and
  add that as a seam (done on the Porsche GT3 R, see below).
- Seams can be read in pieces (left half, right corner): readings of the same two panels are
  merged into one seam.
- Stripe test v2 (BMW): hood → bumper and roof → rails → sides carried the stripes through
  cleanly, so designs crossing those seams line up with no tweaking.
- Reading precision: the same seam read on the other side of the car (BMW left roof rail)
  landed 5-9 px (~0.1 segment) from the mirrored prediction. Well under the ~60 px that shows
  in the sim, so one side + `mirror_y` is enough.
- **A panel between three others** (Porsche GT3 R lower bumper: nose above, a fender at each corner) used to follow only the
  panel it was reached by: the corners under the headlights ignored the fender seams and their stripes ran nearly vertical
  (73-110 px off). `Unfold` now warps every panel straight into design coords, fitted to **all** placed neighbours it has
  readings with (when first reached, then once more after the tree is built; never to the panels hanging off it). Two more
  fixes from the same round:
  - Away from the seams a panel follows the *nearest* seams' similarity (distance-weighted, blended with the whole-panel fit),
    not one fit for the whole panel: a strip seamed at different angles otherwise bends into an S between the seams.
  - No angle pin within 150 px of another seam (where two seams meet their directions disagree and fold the warp).
  Check every build with the Jacobian (folds = det < 0, stretch = singular value ratio) before the sim. Other cars moved < 1 px.
- **Join panels across a 3D vent** when graphics should carry over it (GT3 R fender gill -> door): read the two rulers at equal
  height across the vent and add them as a seam. The grid shows whether the rows really line up there (on the GT3 R the fender
  sits ~0.8 row lower than the door). Such short readings can't set a big panel's rotation alone: the side panel is placed from
  both fender readings together, and the stripe test is rooted at the panel with the most seam length read (it used to pick by
  neighbour count, chose the side panel, and the whole front came out garbled).
  **Read a vent crossing from the grid, not the ruler**: grid labels on both sides at the same height give the offset directly
  (GT3 R: door 48 px lower than the fender, scale 1); the ruler readings were 20-30 px off and showed as steps in-sim.
  Optionally mark such a seam `"gap": true` in `seams.json`: positions are joined but the stripe angle is not forced across the gap (with it
  forced, the GT3 R door stripes bulged next to the vent), and it doesn't set the neighbours' rotation.
- **Check the sign of a vent offset from two in-sim rounds, not from reasoning about sheet orientation**: on the BMW upper
  fender a larger offset moved the stripes down, the opposite of what the panel's sheet layout suggested; three rounds went
  the wrong way before comparing 106 / 111 / 116 side by side showed it.
  Below ~5 px, stop measuring close-ups by eye (the camera moves every shot, a curved lip distorts): bisect on the user's
  better / worse verdicts (BMW: 116 worse, 101 almost, 97 worse -> 104).
- **A height-varying vent offset also scales the graphic**: an offset sloping 111 -> 88 px over 90 px of fender drew the
  BMW fender stripes 1.35x wider than the door's in-sim. Keep the offset flat across stripes/bands and put any change in
  a zone without sharp horizontal lines (the wave).
- **The offset across a vent can change with height** (GT3 R fender -> door: ~60 px at the top of the shut line, ~35 px at
  the vent). One grid reading gave a constant 48 (still visibly off at the top), and the seam-map unfold added a tilt that
  looked worse. Fastest fix: a **numbered band ruler** (`liveries/socal/vent_ruler.py`: 16 px bands of constant sheet y,
  same number on both panels, right side rotated 180) over the livery; one close-up gives "fender 6 meets door 10" at
  every height. Then shift the panel by a height-dependent offset.
- Mirrored panels are paired by overlapping their reflected shapes, not by the panel under the
  mirrored seam points: the BMW roof edge and the rail edge sit 1-10 px apart on the sheet.
- **A vent offset measured with a ruler goes in `seams.json` "shifts"**, not as a gap seam:
  `{"panels": ["X", "N"], "onto": "A", "dy": [[1600, 106], [1712, 78], [1721, 74], [1900, 74]]}` = pixel (x, y) on X/N shows
  the door's design at (x, y + dy(y)). Tried as gap seams first (BMW fender -> door): three short pairs along a slanted fender
  edge squashed the fender to half scale and pulled the hood in through it (14:1 stretch). A shift applies only to panels no
  seam placed in that unfold, and its mirror is built from the panels' measured twin offsets.
- **Not every right-side panel is the plain mirror of its left twin.** `seams.Car(key).twin(code)` finds the twin and its
  offset from the exact reflection (best overlap). BMW: right front fender side Y is 27 px off (others <= 4 px); McLaren two small
  panels (BU/BX, CA/CB) ~39 px; Ferrari a few small ones 7-12 px; Ford, IR04, Lotus, GT3 R none. Mirror design layers with
  `seams.Car(key).flip(layer)` (plain flip, plus those panels resampled from their twin), not a plain flip.

### 4c. iRacing's own patterns: free alignment data (2026-10-14)

Every template has a hidden **`Car Patterns`** group (`car_pattern_000` .. `024`): the patterns of the in-sim paint screen
(red / green / blue = paint colours 1 / 2 / 3). iRacing's artists drew them on the 3D car, so **their stripes already line up
across every seam**. `tools/patterns.py sheet <car>` puts them all on one image (`cars/<car>/patterns_sheet.png`).

**`car_pattern_010` is a smooth red -> green -> blue gradient from nose to tail** (all 11 templates we have). Its colour says
how far along the car a sheet pixel is: a front-to-rear position map, without screenshots. It covers 25-58 % of the paintable
area; the very nose and tail are flat red / blue (no reading there).
- `tools/patterns.py length <car>` decodes it to `cars/<car>/length.npz` (0 = nose end, 1 = tail end, NaN where unknown) and
  `length_sheet.png` (contour lines every 5 %, numbered). Decode from the red/green and green/blue ratios, not the 8-bit hue
  (the hue steps were too coarse: BMW rail matches went from 0.14 to 0.08 segment).
- **Checked against our in-sim seam readings (BMW)**: equal length across the roof / rail seam lands within **0.08 segment
  (~5 px)** of every ruler reading. Hood / fender tops: C1 13.00 vs 12.92, C2 11.08 vs 11.09 (those readings were from sheet
  adjacency and unverified, so this backs them).
- `tools/patterns.py match <car> D23-D28 B60-B74` suggests `seams.json` pairs: for each ruler code in the first range, the
  point in the second range with the same length. **Only seams that run along the car** (roof rails, hood / fender tops, sills,
  door / quarter tops). A seam across the car (roof / windshield, hood / bumper, trunk / bumper) has one length all along it:
  the tool flags those ("N segments match"); read them in the sim as before. Near the nose / tail the gradient flattens and
  gets flagged too.
- Use: fill in lengthwise seams before a ruler round, and in liveries draw anything that changes front-to-rear (fades, colour
  splits "at the B-pillar", bands across the car) as a function of `patterns.length(key)`: it lines up on every panel the
  gradient covers, with no seam map at all.
- Porsche GT3 R (2026-10-14): gradient covers 35 % (hood, fenders, sides + roof, banner; not the bumpers, deck or wing). Hood /
  fender readings confirmed within 0.05 segment. Coverage and usefulness differ per car: run `length` and look before planning.
- **Stripe edges across a 3D vent** (`tools/patterns.py vent <car> <fender> <door> y0-y1`): the other patterns' stripe edges
  where they meet the fender's rear edge and the door's front edge give an offset per height. Tested against two vents tuned
  in-sim: Porsche GT3 R mid/lower vent +37..+42 vs in-sim ~35-45 (good); **BMW lower fender X +40..+50 vs in-sim 74 (26 px off)**,
  with the patterns agreeing among themselves. Likely cause: the pattern stripes slope, and over the vent's real 3D width (which
  the sheet leaves out) a sloped stripe drops further than a level band. So it is only right for graphics with the patterns'
  slope. **Use it as a first guess; confirm level bands with the vent ruler** (section 4b). Near the top of a shut line the
  patterns often disagree (Porsche: 20-80): ignore those rows.
- Not used yet: stripe edges for seams across the car (hood / bumper, deck / bumper), where the gradient gives no position.
  Same slope caveat doesn't apply there (panels touch, no gap).

**Mapping paints install with a flat matte spec** (`install_paint.ps1 -Grid / -Seams / -SeamCheck`, from 2026-10-14):
metallic 0, roughness 255, alpha 0, so garage lighting doesn't put glare and reflections over the labels. Before, they went in
with no spec (iRacing's glossy default).

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

**Spec calibration test (2026-10-01, `liveries/spec-test`, BMW, flat red `#C8102E`, garage, front 3/4)**.
iRacing's own page (iracing.com/custom-paint-textures) says: R = metallic ("typically a yes or no question"),
G = roughness (0 smooth/reflective, 255 rough), B = clearcoat ("left white typically"), **A = specular mask**
(switches environment reflections off; 32-bit TGA when used). Metallic paint must be much lighter than normal.
Banded grids in the sim agree, with caveats:

| Channel | Measured |
|---|---|
| R metallic | solid 255 (with G 0) turned the red deep and dark with strong reflections. Grids at 60-240 (G 0-64) looked identical to the no-spec baseline. So on this red, metallic is close to a switch near 255; the older bronze/muddy readings at 110-215 above were on orange, so intermediate values may show on other colours. Don't count on a smooth ramp |
| G roughness | solid 255 (R 0) = flat chalky matte, clearly different from the glossy baseline. A non-metal grid 96 -> 255 along the car fades gloss to matte (front bumper still glossy at 96-128, rear flat at 240-255). 0-64 looked the same as 8: clearcoat gloss hides base roughness there |
| B clearcoat | 0-255 sweeps (R 120-240, G 8) showed no visible change |
| A alpha | **works**: chrome (255/0, B 255) with alpha 255 -> 0 darkens smoothly; at 0 the metal has no reflections left (dark, flat). Use it to dull metal without going matte |
| No spec file | glossy clearcoat look, similar to G 8-16 |

**Applied spec (GoFAST BMW, `liveries/gofast/spec_pro.py`, 2026-10-01)**: the practical recipe is *material contrast*, not mid values:
matte navy (0/190) next to gloss orange (0/4) is the biggest visible gain; a few white hex tiles as chrome (255/0, alpha 150, ~2% of the sheet) and some matte tiles (0/200) add variation.
Chrome on text or flat near-vertical panels (windshield banner, wing) reflects the dark cockpit/sky gradient and goes **dark and muddy**: keep lettering gloss.
Chrome tiles in the flat garage sky read dull blue-grey; keep them few. User verdict on v2: "looks better", but the difference was small.
**Bold version wins**: big areas of real contrast (dark navy as chrome 255/0, white mosaic matte 0/200, orange gloss 0/4) - user: "I like that a lot". Go for large chrome-vs-matte regions, not subtle tile variation.

**Community source (r/iRacing "proper specmap instructions for GIMP", pasted by the user 2026-10-07; reddit is blocked from here)**:
R = metalness, G = roughness, B = clearcoat/gloss (the post says "Blue is Gloss"; our sweeps saw no B effect). GIMP values are percentages of 255
(90% = 230). https://gabirmotors.com/tools/specmapping previews finishes (Gloss, Flat, Matte, Satin, Chrome, Metallic, Candy, Pearl, Velvet) with sliders.
Its **Metallic preset = 90% metallic, 40% roughness, 0% clearcoat = spec colour #e66600 (230/102/0)**: metallic with a *mid* roughness, not the
near-0 roughness we used on orange (0-8). Untested in-sim; `liveries/gofast/orange_metal.py` writes it as `spec_om230r102.tga`.
GIMP method in the post: channel groups in Addition mode, a Multiply layer filled with the pure channel colour, then a greyscale Normal layer per channel.

**Finished team paints (section 13) use mid values**: orange metallic ~206 with roughness ~100, white 74/77, navy 0/125 (decoded from their `.mip` files; `tools/mip.py`). Our "orange goes bronze" rows above all had roughness 2-8; the mid-roughness combination is untested by us.

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

---

## 12. Using an AI image model for artwork (untested with a real model, 2026-10-06)

The model doesn't know our UV maps, so give it a flat labelled layout and take back only artwork.
`cars/<car>/regions.json` names the panels (panel code from the seam ruler -> name, trim/decal layers,
no-paint zones; BMW done).

1. `tools/aibrief.py <car> "design text"` -> `cars/<car>/ai/guide_atlas.png` (named, colour-coded panels,
   unpaintable area dark, centre line, front arrow), `guide_wire.png`, `prompt.md` (rules + region table).
2. Give the model the images + prompt (image-edit model, "redraw this sheet as artwork, same layout").
3. `tools/aiingest.py <car> output.png --name x [--mirror]` (run in a livery folder) -> resize to 2048,
   optional mirror of the car's left half onto the right, clip to the paintable mask, template trim and
   decals on top; writes TGA, alpha layer PNG, layered `.ora`, preview.

Expect the model to drift: panel edges move, text garbles. Use it for textures/patterns/backgrounds and
keep placement, logos and numbers in code. Open question: does it respect panel layout well enough?
Not done yet: drawing on the seam-unfolded canvas (4b) so art is continuous across panel edges.

First real round (2026-10-06, BMW, "gold and copper" prompt, 1024x1024 output): the model kept every
panel in place and made the right half a clean mirror of the left, so the atlas approach works.
Defects: it copied the red dashed centre line into the art (ingest now blends it out) and drew some
pale outlines along panel edges. Output was 1024 px, upscaled 2x (soft edges: fine for flat shapes, ask
for 2048 if the tool allows). In-sim result not recorded yet.
Round 2 (GoFAST-style prompt with logos, mascot, hex tiles): the model placed logos/mascots on the right
panels and drew readable text on both halves (do NOT use --mirror then). The BMW wing's trim layer covers the
whole wing, so `regions.json` `over_trim: ["E"]` makes ingest put the art back on top of it there. The
model ignores number-card positions: the right-door "GOFAST RACING" was half under the number card. Tell it
where the number blocks are, or move the logo afterwards.
In-sim (BMW, GoFAST-style round 2): "some issues but decent". Panel placement held: hood mascot, quarter mascots,
hex tiles, hood/door/bumper graphics all landed where drawn. Issues: right-door GOFAST RACING cut by the
number card ("GOFAS RACIN"; left door was fine); the wing shows only a thin band of its top face, so the big
wing logo reads as stray stripes; whites/greys read warmer and darker in the sim than on the flat sheet.
Fix applied: `aibrief.py` now draws the template's Number Blocks (grown 45 px, the plate is bigger than the
block) into the atlas as white NUMBER boxes and the prompt says to keep art clear of them.

---

## 13. Reference: finished team paints from other makers (2026-10-07, analysed, not built from)

The user supplied five finished GFR (GoFAST) paints, each with the `.mip` iRacing built from its spec: BMW M4 GT3,
Aston Martin Vantage GT3 EVO (Nürburgring 24h), Ford Mustang GT3 (IMSA), Lamborghini Huracán GT3 EVO (Sebring 12h)
and McLaren 720S GT3 (older, different design). Nothing here was tested by us in-sim; it is measured from their files.
Previews + decoded specs: `liveries/gfr-examples/previews/` (private). Decoder: `tools/mip.py` (needs `zstandard`).

### 13a. Reading a spec back out of a `.mip`
iRacing writes `car_spec_<id>.mip` next to the spec TGA. It holds the **full 2048 spec** as DXT5 inside zstd chunks, so any
finished car's finish can be inspected: `tools/mip.py "x_spec.mip" out.png` (format notes in the script). Lossy: values land
in steps of ~8, so read medians, not exact numbers. 4 of 5 decoded; the McLaren one uses a second layout (chunk-size table
first, no zstd magic, codec unknown) and is not decoded. Paints were 32-bit TGAs with alpha all 255 (no alpha tricks).

### 13b. Spec values the finished paints use (metallic R / roughness G, B = 0, median under each paint colour)
| Paint colour | BMW | Aston | Ford | Lambo |
|---|---|---|---|---|
| Orange `#FF7E00` | 206 / 101 | 206 / 101 | 206 / 101 | 156 / 77 |
| White and all hex-tile greys | 74 / 77 | 74 / 77 | 74 / 77 | 74 / 77 |
| Navy `#2C395B` | 0 / 130 | 0 / 125 | **74 / 207** (fully matte) | 0 / 125 |
| Black trim/decal patches | 0 / 75 | 0 / 73 | 0 / 74 | 0 / 66 |

- **One flat spec value per paint colour, no per-tile noise** (std ~3 on the tiles). The "shimmer" idea in section 5 is not what they did.
- **Orange is metallic ~206 with roughness ~100 (about half the metallic), NOT roughness ~4.** Our guide says orange metallic 215 went
  bronze/muddy, but those tests used roughness 2-8. Mid roughness is what these keep vivid. Lambo uses 156 / 77: same ~0.5 ratio.
  Also matches the community "Metallic" preset (230 / 102). **Untested by us: try orange 206/101 on `#FF7E00`.**
- White/tiles are a pearl (74/77), navy is satin-to-matte (0/125) so the two read very differently next to gloss-ish metallic orange.
  This is the "material contrast" recipe (section 5) with mid values.
- Template trim (carbon bumpers, vents, wing parts) keeps its own spec: roughly metallic 240, roughness 64-112 (BMW red-orange
  240/80, Aston pink 240/112 with B ~80-88 on those regions). Logos/badges on the Aston use chrome-like 248/0. **B is non-zero only on
  the Aston's template-trim regions**, so B probably comes from the template's own spec group, not from the artist.
- Spec areas outside the paintable sheet (the brown fill) hold junk; ignore.

### 13c. Palette (sampled medians)
Navy **`#2C395B`** (44,57,91) and orange **`#FF7E00`** (255,126,0) in all four GT3 paints; the McLaren uses orange ~`#FF9018`, white
`#FCFCFC` and SickKids blue `#3C88CC`. These are **lighter/brighter than our league colours** (navy `#1E2744`, orange `#E36400`/`#FF7300`),
so check which the league actually wants. Tile base: three light greys `#F3F3F5`, `#ECECEE`, `#E1E2E4` (cool, slightly blue)
over pure white `#F4F4F4`; the brown `(83,71,65)` = `#534741` is the template's unpaintable fill colour.

### 13d. Design anatomy shared by BMW / Aston / Ford / Lambo
One design adapted to each car's sheet, not four new designs:
- White hex-tile base (tiles ~90-110 sheet px across, 3-4 grey shades, no gradient toward the rear).
- Door/quarter: a **navy wedge** with a rear-pointing **jagged orange lightning shard** above and below it, an orange underline under
  the banner, and the **GOFAST RACING banner** (orange GO, white FAST, small RACING) inside the wedge. The wedge points rearward.
  Banner goes on the door beside the number block (sponsor stickers sit between block and banner).
- Hornet mascot as **orange outline line-art** on the white rear quarter (both sides, rotated 180 on the far side).
- Roof: one big navy shape (BMW: triangle widening rearward; Lambo: long wedge; Ford: double navy stripes with a thin white line,
  running hood -> roof -> deck). Roof/hood carry the boldest graphic.
- Windshield banner: dark/navy with GOFAST RACING (BMW) or a sponsor block (Aston "GRAN TURISMO", Lambo "SQUADRA CORSE" green).
- Orange fills the small awkward islands (louvers, arch vents, mirror backs); orange sweeps on the hood/fender fronts.
- Realism layer on top: sponsor stickers (WeatherTech, Michelin, Motul, Falken, H&R, Sport Auto, VP), class badges (PRO / GTD / GTD PRO),
  event badge on the roof or sill (Sebring 12hr, Nürburgring 24h), tiny **driver-name strip with flags** above the rear quarter
  (`C.GRIFFITH`, `B.BLACKLOCK`...), manufacturer wordmark on the sill (FORD PERFORMANCE) and rear bumper, "TEAM GFR" on the wing/bumper.
  Small text and badges are what make them look like real team cars; ours are mostly big shapes.
- Number blocks are left as plain white cards/sticker boxes (iRacing draws the number), consistent with section 2.
- Weak one for contrast: the McLaren is big flat navy/orange swooshes with unused flat white panels and none of the tile/shard detail.

### 13e. Ideas to try next (not done)
1. Orange at 206/101 (and 156/77) in a spec test on a vivid orange base; white 74/77; navy 0/125.
2. A shared "GoFAST kit" (palette, tile base, shard shapes, banner, hornet outline, driver strip) with per-car placement config.
3. Add sponsor/driver-name layers as small decals; they cost little and sell the "real team car" look.
4. Decode the McLaren `.mip` (second layout) to see how the older paint finished its swooshes.

**Spec decoded from a hand-built team livery (GFR BMW, 2026-10-07)**: `.mip` files (iRacing's spec cache) decode with `tools/mipspec.py`.
All five GFR examples share one spec: body/white 74/77, orange 206/101 (metallic 81%, roughness 40%), navy/dark 0/125-130 (satin, non-metal), carbon trim 0/32. Paint: orange flat `#FF7E00`, navy flat `#2C395B`, white `#EDEDEF`.
Their shiny vibrant orange = high metallic + MID roughness over a bright base, not metallic with roughness 0-8 (which went dark/brown). `gofast/v24.py -Finish gfr` reproduces it. In-sim result pending.

### 13f. GFR BMW V2 (2026-10-11): what changed and what to copy
Friend's updated BMW M4 GT3 (`liveries/gfr-v2/`, the user's target look: "absolutely perfect"). Same layout as V1 (13d); the gains are in
**shading and finish**, not new shapes. Measured from the TGA and the decoded `.mip`:

| Area | V1 | V2 |
|---|---|---|
| Orange | flat `#FF7E00`, spec 206/101 | **faceted "low-poly" orange**: big triangles (~100-300 px) shaded `#CE4C00` -> `#FF7E18` (median `#F0690B`); spec **181/101** |
| Navy | flat `#2C395B`, 0/130 satin | still flat `#2C395B`, but **metallic 107/101**, plus a few darker navy streaks and white->transparent glint slivers inside the wedges |
| White/hex tiles | 74/77 | 74/77 (unchanged), tiles `#F0F0F0`/`#E8E8E8`/`#E0E0E0` |
| Carbon/template trim | 0/32 | **252/77-85** (metallic carbon) |
| Wing banner black | | 0/142 (matte) |
| Roof | big navy triangle | white hex with navy wedges and orange shards (lighter, more motion) |
| Extras | driver-name strip | names dropped; GFR roundel on the hood, GT3/PRO class card on the hood, small GFR logos on the mirrors, more islands covered |

Lessons for our scripts:
- **Facets, not smooth gradients.** Our rule "flat colour across seams" (section 6) holds for *smooth* gradients. Random facet shading
  has no direction, so a mismatch at a seam just looks like another facet edge: depth without the seam problem. How he built it
  (from his GIMP file, section 14): flat orange shapes underneath, one low-poly orange image laid over them, cut to the shape with
  feathered edges. `tools/lowpoly.py` makes that texture and the feathered cut.
- **Every colour gets a mid-roughness spec** (77-101). No body colour in V2 is near roughness 0; contrast comes from metallic (navy 107,
  orange 181, trim 252) vs white pearl 74. Untested by us in-sim.
- **Motion details inside flat areas**: darker streaks + glint slivers in navy, layered jagged shards (orange over navy over white) with
  thin white gaps between layers.
- Same design is ported per car by hand by the friend (V1 exists for BMW, Aston, Ford, Lambo; see `liveries/gfr-examples/`).

### 13g. Reusing someone's layered GIMP file (2026-10-12)
A hand-made livery's `.xcf` is far better source material than its flattened TGA: shapes, logos, cards and the base
pattern come apart cleanly. GIMP 3 reads it headless (`gimp-console -i --quit --batch-interpreter=python-fu-eval -b
"exec(open('script.py').read())"`). Export each layer by **hiding all leaf layers, showing one at a time and saving the
canvas**; copying layers into a new image (`Gimp.Layer.new_from_drawable`) silently lost pixels. Check the export by
re-compositing and comparing with GIMP's own flatten (`merge_visible_layers`). Artists draw shapes past the panel edges
and let the template mask clip them: warp those shape layers, stamp logos/cards undistorted, re-tile the base pattern
(`liveries/gfr-v2/port.py`). Fill holes in his layers first: he skipped spots that can't be painted on *his* car (hood
vents), which became hard-edged white notches on the Ford. Extend each layer into holes enclosed by a source panel only; spreading
into all unpaintable space dragged unrelated art (from around a tail light) onto the target. Inpaint the holes (OpenCV
Navier-Stokes) rather than nearest-pixel fill, which left blocky steps in-sim. Also erase art the source car hides under
3D parts (his bits at the BMW tail-light corner showed as a dark blotch on the Ford), and don't sample past a source panel's
edge where a neighbouring panel's art lives: extend the panel's own edge instead. When continuing art across a seam, follow
each edge's own direction (structure tensor), not the nearest pixel: nearest-pixel continuation bends diagonal shards to
right angles at the seam (Ford v17). Warp layers on **premultiplied alpha** (transparent pixels are often black: plain
interpolation puts a dark fringe on every edge), bilinear rather than Lanczos (rings where layers overlap), and supersample
anything computed per pixel (4x4) so edges stay anti-aliased; stretched UV strips magnify stair-steps.

---

## 14. Layer recipe from a pro GIMP livery (GFR BMW V2 .xcf, 2026-10-12)

The friend's working file for the paint in 13f (`liveries/gfr-v2/bmw-m4-gt3/reference/GFR_V2.xcf`, layers exported to
`xcf_layers/` with `manifest.json`). How a livery the user called "absolutely perfect" is put together, to copy in our scripts
and in any hand-finished `.ora`/`.xcf`.

### 14a. File structure
He kept iRacing's template structure and added his work inside it:

```
Custom Spec (hidden)                   template's spec groups (metal / rough / clearcoat), not his final finish (that was the .mip)
Turn Off Before Exporting TGA          Mask, wire, Number Blocks, Sponsor, License, Car Mandatory  (hidden for export)
Paintable Area #1
  GFRshort.png (x2)                    small logos (mirrors)          <- one-off logos, cards, banner on top, loose
  window fix, GFRwindowbanner.svg      banner art + a navy patch fixing its ends
  pro#.svg (x3)                        number cards (vector, one per block)
  Car_decal, Carbon Fiber              template trim, ABOVE all his art
  GFRLOGO2.0.png #2                    wing wordmark
  Top/                                 hood + roof: Bluie Top, Orange top, shading copies, roundel
  Side 1 copy #1/                      right door = the left-door group duplicated, flipped vertically, moved 574 px
  Side 1 copy/                         left door (the one he designs)
  Hex/                                 one hex tile image placed 9x, each copy erased to the body
  Paintable Area                       solid navy fill (whatever the hex doesn't cover reads navy)
  Car Patterns (hidden)
```

- **One group per area of the car** (left side, right side, top), plus loose layers for logos/cards that sit on top of everything.
- **Design one side, duplicate the group, flip it vertically about the centre line** for the other side, then swap in readable
  (rotated, not mirrored) copies of text logos. Our scripts do the same with `y_top = 2*mid - y` (section 3).
- **Shapes are drawn past the panel edges** and the template (mask + trim on top) clips them. Nothing is hand-trimmed to the
  UV outline except the hex. That is also why his layers port well to another car (section 13g).
- **Logos are imported files** (PNG/SVG) on their own layers at 100%, never painted into shape layers. Cards are one SVG per
  number block. Names show iteration (`Orange V2`, `Orange V2 on top`, `Blue side V2`): he adds a layer rather than repaint one.

### 14b. The shading recipe (per door, bottom -> top)
| Layer | What it is | Values measured |
|---|---|---|
| Orange side 2, Orange V2 | flat orange base shapes | `#FF7E00`, opaque |
| Blue side V2 | flat navy wedges (the door wedge, roof-line sweep) | `#2C395B`, opaque |
| Blue Faded | navy slivers over white = soft light-blue "glint" | navy at alpha ~171 (67%) |
| Blue details | darker navy streaks inside the wedges, fading out | `#1E273F`, alpha ramps 62 -> 255 |
| Orange V2 on top | small orange shards over the navy (with their own shading) | `#FF7E00` + texture |
| low-poly image x4-5 (`8fa48afc...png`) | one faceted orange image, copied, cut to the orange shapes, edges feathered | `#CE4C00`-`#FF7E18`, 26-56% of its px semi-transparent |
| Orange side detail | **black at 62%** under the facet copies, fading out: a shadow that darkens the front of the orange | black, alpha ~158 + gradient |
| GFRLOGO2.0.png, hornet, GFR | logos on top | - |

The depth comes from **three cheap passes over flat shapes**: a dark shadow layer (black ~60%, gradient fade), a faceted texture
cut to the shape with feathered edges (facets in some places, flat colour showing in others), and light/dark streak slivers in the
navy. All of it fades; nothing ends in a hard edge except the shapes themselves.
In our scripts: draw the flat shape, then `lowpoly.overlay(lowpoly.texture(...), shape_alpha)`, then a black ~60% copy of the
shape with a linear alpha ramp underneath the texture, then a few navy streak polygons with an alpha ramp.

### 14c. Design rules visible in it
- **Palette is tiny**: navy `#2C395B`, orange `#FF7E00` (shaded `#CE4C00`-`#FF7E18`), dark navy `#1E273F`, hex whites/greys
  `#E0E0E0`-`#F8F8F8`, black only as shadow. No other colours except inside logos.
- **Layering order tells the story**: white hex base -> orange sweep -> navy wedge -> orange shards on the navy -> logos.
  Each colour overlaps the previous one; no colour floats alone (section 6 "start from something").
- **Sharp, rear-pointing shapes**: wedges and lightning shards all point rearward and get thinner toward their tips.
- **Placement**: door wordmark inside the navy wedge right behind the number card; hornet on the rear quarter (white hex, so the
  orange line art reads); small GFR on the lower rear arch; roundel on the hood nose; class card (GT3 / PRO) beside it; GOFAST
  banner on the windshield; GOFAST on the wing; GFR on the mirrors. Sides, hood and roof carry the big graphics; bumpers stay calm.
- **Hex base**: hexes 52 px across (88.7 px per two rows), 3-4 light greys, flat (no gradient toward the rear).
- **Driver names were dropped** between versions (they were hidden layers in `Top`): keep such details on hidden layers so a
  variant is a visibility toggle.

### 14d. What we changed in our tooling because of it
- `tools/lowpoly.py`: the faceted texture + feathered cut (14b).
- `tools/ora.py`: layer groups (`Layer(..., group=("Paintable Area", "Top"))`, `hidden_groups=`), so our `.ora` files can follow
  his structure; `tools/ora2xcf.py` turns them into `.xcf` (perceptual compositing, so GIMP shows exactly the TGA).
- `liveries/gfr-v2/port.py`: ports his layers to another car and writes them back with his names and groups (13g).
- For new liveries: organise the `.ora` like 14a (template guides in a hidden "Turn Off Before Exporting TGA" group, one group per
  car area, logos/cards loose on top, template trim above the art), so a hand-finisher finds his way around.

---

## 15. Other tools and data out there (looked at 2026-10-14)

- **icarmap** (icarmap.com, Discord bot, closed source): wraps one image over 100+ cars with no breaks at seams. Method not
  published; that result on 300-panel cars needs the 3D mesh + UV per car (project the image in 3D, write it back to the
  sheet). Meshes would have to come from the sim's files or GPU captures (terms of service / anti-cheat grey area): not for us.
  Our nearest equivalents: the seam unfold (4b) and the length gradient (4c).
- **iRacing's template server is public, no login**: `https://ir-core-sites.iracing.com/members/member_images/cars/car_templates/<zip>`
  (e.g. `132_template_M4GT3.zip` = BMW M4 GT3). The zip names are on tradingpaints.com/cartemplates.
- **github.com/hugoUCV/iracing-ai-paint-generator** (MIT): `data/iracing_car_catalog.json` lists 183 cars with display name,
  **exact iRacing paint folder** and template zip, scraped from Trading Paints. Use it to look up a folder name instead of
  guessing. Also per-car wireframe PNGs; panel atlases for 3 NASCAR cars only. No seam data.
- **Overspray** (github.com/ModestoHagney/clearcoat, fork of OblivionsPeak's Clearcoat): browser livery editor. No 3D: its
  "Live" mode rewrites `car_<id>.tga` in the paint folder after every edit (Chrome/Edge folder access). Worth copying: its
  Map mode outlines panels by hand, names them, pairs twins and links edges; linked edges get **the same run of colour bands on
  both sides** (order reads differently backwards, so a link made the wrong way round shows) as a guide layer on the car.
- **SimWrapMarket** downloads: Photoshop automation templates for oval/dirt cars; nothing for alignment.
- "UV checker" maps (generic labelled chequerboards from 3D modelling) = what `tools/grid.py` already is.
- Nobody publishes panel names or seam connections for iRacing cars; our `cars/<car>/` seam maps fill that gap.
