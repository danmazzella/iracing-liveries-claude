# Ferrari 296 GT3 — sheet → car notes

Template: `Ferrari 296 GT3.psd` (repo root). iRacing paint folder: `ferrari296gt3` (confirmed).

Mapping grid: `grid.tga` (64px cells labelled `col,row`; cell c,r = sheet x c*64..c*64+63,
y r*64..r*64+63). `grid_sheet.png` = grid + wireframe with the not-paintable mask drawn over.

## Template layers

- `Paintable Area/Base`: paint colour. `Car_decal` (Ferrari badges, windshield banner),
  `Carbon No Pattern - Non Metallic`, `Carbon Splitter Wrap`, `Arrow Decals`: composite over paint.
- `Turn Off Before Exporting TGA`: `Mask` (not paintable), `Wire` (UV wireframe, hidden),
  `Car Mandatory`, number board layers (hidden).
- `Custom Spec Map`: hidden R/G/B groups (metallic, roughness, clearcoat) incl. `Parts`.

## Sheet layout (from the template, not yet checked in-sim)

- Mirrored about **y ≈ 1023.5** (mask ~90% symmetric; edge parts differ).
- Windshield "Ferrari" banner: vertical, x ~770-900, y ~780-1270 (on the centre line).
- Big carbon piece x ~1340-1860, y ~800-1250: unknown (rear deck/engine cover?).
- Side panels: bands y ~250-760 (upper) and ~1290-1790 (lower).
- Carbon/diffuser with red light strip at the top right (y 0-200); large carbon piece
  bottom left (y 1720-2048).
- Ferrari shields at (~640,430) and (~640,1620); `PRO` class boxes near (1375,440) / (1375,1600).

## Part → columns/rows

From `grid_front`, `grid_front34_right/left`, `grid_side_right/left`, `grid_top(_right)`,
`grid_rear`, `grid_rear34_right`. Right side = upper half (labels read upside down in-sim),
left side = lower half, mirrored about y 1023.5 (row r ↔ row 31-r). Confirmed by the left
views: door 13-19 rows 24-27, rear quarter 20-27 rows 22-27, number at ~21,24.

Left side details (lower half): front wheel between the bumper corner (col 2 rows 22-23) and
col 10 rows 25-27; rear arch ~cols 22-26; sill row 28; haunch/rear-quarter top rows 22-23;
side intake behind the door col 19-20 rows 19-21. Front fender top cols 7-10 rows 20-22.
Rear fascia (around exhausts) = row 1 cols 2-11 (sheet top, not mirrored); lower rear
panel row 31 cols 5-7; wing rear face row 31 cols 22-31.

| Part | Cols | Rows | Notes |
|---|---|---|---|
| Front bumper nose (upper face) | 2-3 | 12-19 | x runs bottom→top of the bumper; Ferrari shield at 15/16 |
| Lower bumper / grille surround | 1 | 11-20 | |
| Front lip / splitter face | 19-29 | 2 | sheet top strip (not mirrored?) |
| Headlights | ~4-5 | 11-12 / 19-20 | 3D, sit over paint |
| Hood | 4-7 | 12-19 | nose at col 4, windshield at col 7-8; vent opening cols 4-6 rows 14-17 |
| Front fender tops | 5-8 | 9-11 / 20-22 | louvred fender cols 8-10 row 9-10 |
| Front fender side | 9-12 | 4-10 | 10,10 / 9,10 above the arch |
| Canards / dive planes | ~6-9 | 6-9 | small islands, check |
| Roof | 12-18 | 12-19 | windshield header ≈ col 12 |
| Roof rear / B-pillar strip | 19-20 | 10-21 | |
| Door | 13-19 | 4-7 | sill row 3 |
| Door-top intake | 19 | 10-12 | |
| Rear quarter (side) | 20-27 | 4-9 | **iRacing number block here** (~22,7) |
| Rear quarter top / haunch | 21-24 | 8-9 | |
| Engine cover | 21-29 | 12-19 | scoop 23,15-23,16; vents cols 23-25 |
| Rear deck top edge | 30 | 12-19 | |
| Rear bumper / tail | 4-12 | 0-2 and 29-31 | plate area cols 5-8; tail lights cols ~10-12 |
| Wing top | 22-31 | 28-29 | wing endplate labels 29,6 / 8,6? (unclear) |
| Hood number block | ~6 | 13 | iRacing also draws the number on the hood (car's left) |

## Proven placements

From white-gofast v1 in-sim:
- Roof/engine-cover centre stripe: y 1023.5 ± ~140, x 760-1900; rearward spikes at y ~1170-1200,
  x 1340-1710 land on the engine-cover vents.
- Door logo box (875-1285, 1592-1708) fills the door; the Car_decal number board sits behind it on
  the rear quarter (1320-1443, 1555-1661), and there's a hood board (375-477, 763-881, car's right only).
- GFR badge at (228, 1023.5) size 118 rot -90 sits on the nose, reads from the front.
- Wing top (1400-2048, 1792-2048): logo at rot 180 reads from behind the car; **use rot 0** (reads
  from the front, the user's rule). Keep letters in y ~1826-1910 (lower y = trailing edge, cuts them).

## Gotchas

- The template's `Carbon No Pattern - Non Metallic` layer covers the engine cover and the wing, but
  they're paintable: skip those boxes when compositing it.
- Row 22 above the rear arch (y ~1410-1470) is the top of the rear haunch, seen from above, not the
  side. The rear-quarter side above the arch is rows 23-25 (y ~1490-1600).
- Anything at x < ~140 in rows 19-23 lands on the lower bumper corner / grille struts.
- The Mask island at 16,22 (x 1008-1141, y 1399-1500) is carbon in the template = the mirror stalk.
  The mirror housing is on the right sheet edge: island 31,24 (x 1971-2020, y 1539-1592) plus
  cols 30-31 rows 25-27 below it (right mirror: 31,7 etc.). From `grid_mirror_left/right.png`.
- Front bumper face = col 2 (x 128-192): from the centre (rows 15/16) it runs under the headlight
  (2.19) and wraps round the corner to the side in front of the wheel (2.22-2.23). x rises upward on
  the bumper. Fender louvres: cols 7-10 rows 21-23 (their sides are in row 23).
- Hood/fender seam near the headlight ≈ y 1280 (between rows 19 and 20), but the hood side of it
  sits a bit further in: an orange edge at y ~1225-1260 on the hood showed only as a sliver next to the
  fully orange fender. Start hood orange from y ~1200 for a visible band.
- Hood/bumper seam at the headlight's inner tip: **same sheet y on both sides** (ruler test, white-gofast
  `reference/ruler_insim_headlight_right.png`). An edge crossing it must have one constant y there
  (x ~128-300)... but in practice: bumper part (x < 256) at 1208-1213 fell short and at 1201
  overshot ~15 px, with the hood at ~1201-1203. white-gofast final uses bumper 1207 / hood 1201
  (unverified). The strip is squashed on the sheet, so tiny moves swing a lot: budget for it.
- Hood/nose: the hood/nose seam runs at x ~178 and the hood vent's front lip at x ~256 (centre
  line). A nose badge must fit in that band (v2's 118 px badge was cut by both).
- Windshield banner (768-909, 779-1269): the high-x end sits under the roof edge in-sim; keep text
  toward low x (centre ~818, ≤ 80 px tall).
- Wing endplate outer face = cells 28-29,25 (and 28-29,6); template carbon there.

## Seams (tools/seams.py, LIVERY_GUIDE 4b)

Seam ruler built: `seams.tga` (125 panels, codes in `seams_sheet.png`).
Readings in `seams.json`: none yet. Add each seam read in-sim below (which seam, screenshot, checked?).
