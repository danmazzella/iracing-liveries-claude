# BMW M4 GT3 — sheet → car mapping

Template: `BMW M4 GT3.psd` (repo root). iRacing paint folder: `bmwm4gt3`.

Files here:
- `grid.tga` — the labelled grid (install with `tools/install_paint.ps1 -Car bmw-m4-gt3 -Grid`)
- `projection/` — per-view `(screen px) -> (col,row)` label readings from the grid screenshots (+ landmarks to our own mockup), for `tools/labelproj.py`
- `uv_*.webp` — screenshots of the failed colour-code approach (`tools/uvcode.py`), kept for reference
- `grid_sheet.png` — flat grid with the template mask drawn over it
- `grid_front.webp`, `grid_front34_left.webp`, `grid_side_right.webp`, `grid_rear.webp`,
  `grid_top.webp` — in-sim screenshots of the grid

In-sim screenshots of `grid.tga` (2026-09-28). Cells are 64px and labelled
`column,row`, so cell `c,r` covers sheet x `c*64 .. c*64+63`, y `r*64 .. r*64+63`.
`grid_sheet.png` is the flat sheet with the template mask over it.

The sheet is mirrored about y ≈ 1311 (row 20.5). Larger y = car's **left** side,
smaller y = car's right side. The top side panel (rows 10–15) is upside down.

| Part | Columns (x) | Rows (y) | Notes |
|---|---|---|---|
| Front bumper | 0–3 (0–255) | 14–26 (900–1720) | x = height: col 0–1 bottom by the splitter, col 3 top under the headlights/hood. y = across the car, centre row 20. BMW roundel at 3.20/4.20 |
| Kidney grille frame | 15–18 | 25 (1600–1664) | Also 1.20/2.20 for the centre bar. The dark rounded rects at x 955–1215, y 1580–1690 are the grille mesh, not windows |
| Hood | 4–11 (256–760) | 15–25 | Nose at col 4. Big vents around cols 6–8. Upper fenders/headlight surrounds at rows 22–25 (and mirrored 15–18) |
| Windshield banner | 14–15 (880–1015) | 17–23 | |
| Roof | 16–23 (1024–1500) | 17–23 (1088–1500) | Centre ≈ (1262, 1310). Nose side = small x |
| Rear window / trunk | 23–26 | 17–23 | |
| Rear bumper | 27–30 (1730–1980) | 16–23 | Col 27 top by the tail lights, col 30 bottom by the diffuser |
| Wing top | 22–31 (1385–2040) | 5–9 (312–598) | Wing texture "up" = car rear. Top surface shows rows 5–6 in-sim |
| Left side (upright) | 9–28 | 22–31 | Front fender cols 9–12; door cols 13–19 (x 830–1260), door top row 26.5 (y ≈ 1700), bottom row 30.5; rear arch cols 21–24, rows 28–31; tail light ≈ col 28, rows 24–26; upper rear quarter / C-pillar cols 20–27, rows 24–26 (x 1300–1750, y 1540–1690); upper front fender cols 9–11, rows 22–25 |
| Right side (upside down) | 9–28 | 9–18 | Mirror of the left side (y_top = 2623 − y) |

## Layers

`Paintable Area/Carbon Fiber` (trim, composite over paint), `Paintable Area/Car_decal`
(bmw-m.com, M4 GT3, windshield banner shape — keep on top), `Turn Off Before Exporting TGA/Mask`
(alpha = not paintable), `.../wire`, hidden `Custom Spec/rough` (trim roughness).

## Proven placements (checked in-sim)

| Item | Sheet position | Notes |
|---|---|---|
| Number cards (league card replaces PRO boxes) | door L (820,1780)-(951,1894) rot 0; door R (820,729)-(951,843) rot 180; hood (621,1067)-(735,1198) rot −90 | iRacing draws the number on top |
| Door logo strip | (968,1792)-(1339,1871) left; mirrored + rot 180 on the right | GOFAST RACING / comic burst both fit |
| Windshield banner | (880,1070)-(1015,1552), logo rot −90 | shape comes from `Car_decal` |
| Wing logo | centre (1715,372), max 460x95, rot 180 | |
| Roof centre graphic | centre (1262,1300), ~390px, rot 90 = top of graphic toward the nose | reads upright in top view |
| Hood mascot | centre (350,1312), ~210px, rot −90 = head toward windshield | reads upright from the front. rot 90 looked upside down |
| Upper rear quarter mascot | centre (1672,1612), ~100px, left side | clear of the template gap at y≈1520–1560 and of the tail light |

## Gotchas found the hard way

- The rounded dark rects at x 955–1215, y 1580–1690 are the **kidney grille**, and the band
  above the door (rows 24–26, cols 15–19) is the grille frame. Stripes drawn there end up on
  the front of the car.
- The **tail light** (≈ col 28, rows 24–26) covers paint: a mascot at (1800,1742) was cut off.
- Front bumper is the sheet's far-left column (x 0–255): x runs bottom→top, y runs across
  the car. Design it separately from the sides; loose break-off tiles look messy on it.
- Kidney grille on the bumper spans y ≈ 1150–1470 (outer edge on the car's left ≈ y 1405–1470).
  Upper outer corners: x 192–255 (cells 3.18 / 3.22). Lower outer corners, next to the lower
  intakes: x ≈ 70–140, y ≈ 1405–1420 (mirrored ≈ 1203–1218). The bumper top edge (x 255)
  continues straight onto the hood front (x 262).
- v3 lesson: a wedge placed at the top of the bumper/hood front (x 212–262) shows up **above**
  the headlights in-sim, not beside the grille. To get orange "coming out of the grille" the way
  the GoFAST mockup has it, start the band at the kidney's **lower** outer corner and run it up and
  out to under the headlight. v4 confirmed this works: a band starting at (72–138, ~1410) met
  the kidney about **halfway up**, so bumper x ≈ 100 ≈ the kidney's mid-height. v5 starts at
  x 28–92 to reach its lower corner, and runs its outer edge to x 118 so the fog light
  (outer bumper, roughly x 120–250, y 1600–1745) sits inside the orange.
- Bumper curve direction: in bumper coords (x = height), a Bezier control point toward
  **higher x and lower y** (up and in, toward the kidney) bulges the orange onto the grille side.
  For the GoFAST mockup look (concave, white beside the upper kidney), put the control point
  **low and outward** (e.g. (110,1545) between (92,1410) and (255,1560)).
- Hood/bumper seam above the headlight: the same sheet y does **not** line up across it. To
  continue an edge from bumper (x 255, y 1490) onto the hood, use hood y ≈ 1462 (v15 was ~35px out, v16's 1452 ~10px in). Match the edge's
  **angle** across the seam too, not just its position.
- **Front fender louvers** (slats on top of the front wheel arch): sheet x ≈ 1212-1482,
  y ≈ 1588-1672 (left; cols 19-22 row 25; the slat sides sample a bit beyond that, so paint
  x 1195-1500, y 1558-1700), mirrored y ≈ 951-1035. They are next to the grille
  frame (cols 15-18 row 25) on the sheet, not near the fender.
- Hood vents (left): ≈ x 380-530, y 1400-1520.
- Fog light on the bumper ≈ x 80–150, y 1540–1670 (left side). Hood pin ≈ (315, 1483).
- Roof logo: centre (1262,1312), rot 90 = text top toward the nose. `fit()` rotates first, so
  give the box in sheet axes (narrow x, long y).
- Loose break-off tiles and dark speed bars look messy on the bumper (v3 in-sim), so keep it calm.
- Door top is at y ≈ 1700 (row 26.5). Anything above that at cols 13–19 is window/grille, not door.
- Rear arch is unpainted (cols 21–24, rows 28–31), so graphics can run over it freely.
- Hood/bumper seam near the **centre line** (aero livery, 2026-09-28): the sheet-y shift across the
  seam is small there. A stripe at hood y 1435-1466 (x 262) needs bumper y ≈ 1437-1472 (scale
  1.04 about y 1311.5). Scaling by 1.186 (from the 1490<->1462 point by the headlight) put it
  ~20 px outboard in-sim, and no offset (plus a diagonal) put it inboard. v3 at 1.04 confirmed in-sim ("that works").

## Seams (tools/seams.py, LIVERY_GUIDE 4b)

Seam ruler built: `seams.tga` (93 panels, codes in `seams_sheet.png`). Main panels: `C` hood, `F` front bumper, `A` left side, `B` right side, `D` roof.
Screenshots of the ruler: `seam_front`, `seam_top_front`, `seam_side_left`, `seam_side_right`,
`seam_front34_right`, `seam_rear`, `seam_top_rear` (first ruler), `seam2_*` (ruler with the
thin-strip fix), `seamcheck1_top` / `seamcheck1_front` (stripe test v1). All .webp, 2026-09-29.

| Seam | Readings | Status |
|---|---|---|
| Hood C ↔ front bumper F, C7.5-C13 (headlights beyond) | C8↔F55.42, C9↔F54.24, C10↔F52.28 (+ mirror); right corner C12↔F48.94, C13↔F47.96 from `seam3_front` (C12 matches the mirrored left half to 0.01 segment) | ticks line up within ~0.1 segment: hood and bumper edges share the same sheet y there. Stripe test v1: position joined, stripes kinked/bent on the bumper (warp artefact, fixed in v2) |
| Roof front D ↔ windshield banner K | D1↔K14.18 ... D6↔K9.22 (K runs the other way), re-read from `seam3_front` at the tick bases | v2 step and v3 torn stripes (`seamcheck3_front`) were a tool bug (duplicate mirror copy), not the readings; fixed. v4 to check. Some angle change stays: the banner bends down to the glass |
| Roof side D ↔ roof rail B (right), mirrored to A (left) | D23↔B69.18 ... D28↔B64.02 (B runs the other way) | read from `seam2_side_right`. On the sheet the rail's edge sits 1-10 px from the roof's edge: nearly 1:1. **Mirror verified**: the left side read independently from `seam2_side_left` (D9↔A0.5, D10↔A96.44 ... D13↔A93.36; A's outer edge wraps A96 → A0) lands 5-9 px from the mirrored prediction |
| Door front edge B28-B31 ↔ fender M/Y | - | **not a seam**: a 3D vent/gill sits between them (`seam3_side_right`) |
| Hood C ↔ front fender tops M (right) / N (left, mirrored), C0-C3 | C0↔M14.47 ... C3↔M8.92 | fender-side labels too small to read (`seam4_hood_fender_left`), but the two edges are drawn 1-2 px apart on the sheet (like the roof rails, which joined 1:1 in-sim), so pairs come from the sheet. **Unverified in-sim.** Stops at C3: extending to C4 (by the headlight, where the fender edge turns a corner) made a 13:1 warp spike |
| Trunk W ↔ rear bumper R/L | - | not read yet |

Stripe test v4 (`seamcheck4_front.webp`): banner clean (no step, no tearing), hood → bumper
continuous out to the headlights. User: "close enough for now". The BMW seam map is usable for
designs across hood/bumper, roof/banner and roof/rails/sides.

Stripe test v2 (`seamcheck2_*.webp`): hood → bumper clean (no step, no curl); roof → rails →
sides → doors/rear quarters continuous, a few px jog at the roof edge; roof → banner stepped
~13 px (fixed in v3, see table). Front fenders (M, N, Y), trunk and rear bumper not seamed yet.


- The bumper's sheet edge detours round the roundel on the centre line: the hood and bumper
  don't touch there, so no reading may span it. Read one half and let `mirror_y` add the other.
