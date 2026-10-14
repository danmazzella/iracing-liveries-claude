# Porsche 911 GT3 R (992), car key `porsche-992-gt3r`

Not the Porsche 911 GT3 Cup (992.2): that is a different car, `porsche-992-cup`.

iRacing paint folder: `porsche992rgt3`

Template: `Porsche 992r GT3.psd`

Layers: `Wire` (hidden), `Mask`, `Car_decal`, `IMSA Car_decal` (hidden), `Color Change Logos`, `pitbox colors`,
`Car_Mandatory`, `Number Blocks`, `Sponsor Blocks` (hidden guides), `car_pattern_*`, `Pitboard`,
`Custom Spec Map` (hidden; Red Metallic / Green Roughness `Parts` + `Base Paint`, Blue Clearcoat).

## Status

2026-10-13: grid mapped from 17 in-sim shots (`grid_*.webp`), part table below. Seam ruler (`seams.tga`) read from 15 shots
(`seam_*.webp`): front and roof/banner seams in `seams.json`, stripe test `seamcheck.tga` built (flat sheet clean, in-sim check
pending). Rear seams not read yet (list below).

2026-10-14: iRacing's hidden `Car Patterns` (LIVERY_GUIDE 4c) decoded: `patterns_sheet.png`, `length.npz` / `length_sheet.png`
(35 % of the sheet: hood C, fenders G/H, sides + roof A, banner L 0.40; NOT the lower bumper E, rear deck F, rear bumper D,
wing). Use `patterns.length("porsche-992-gt3r")` for anything that changes nose -> tail (fades, colour splits) on those panels.
- Hood side / fender (C19-C24 vs G26.9-G21.9): equal length lands within 0.05 segment of our readings (C15-C18 sit on the flat
  nose end: no reading there). Confirms that seam.
- No other lengthwise seam to fill: roof, sides and sills are one island (A), and the rear deck / quarter seams are off the
  gradient or run across the car. Rear seams still need the in-sim ruler.
- Fender -> door across the vent from the other patterns' stripe edges (`patterns.py vent porsche-992-gt3r G A 1580-1900 650-800
  780-950`): d = +37 (fender y 1720-1759), +40 (1760-1799), +42 (1800-1850), many patterns agreeing within a few px. Matches the
  in-sim-tuned socal curve there (~35-45). Above y 1720 the patterns disagree (20-80): keep the ruler value (70 at y 1610).

## Sheet map (first numbers, from the template; in-sim check pending)

**Mirror line y ~ 1299.5** (mask reflection test, best overlap 0.90; the door number blocks at y 770-841 / 1761-1831 centre on
~1300.8). Use `mirror_y: 1299.5` in `seams.json`.
Number Blocks (x, y): doors 873-970 x 770-841 and 870-967 x 1761-1831; others 284-380 / 497-593 x 392-464, 467-538 x 1253-1350,
1634-1707 x 304-371 (which parts: read from the grid shots).

Seam ruler: 87 panels. Big ones (guesses until the in-sim shots): A = both sides + roof in one island, H + C = hood / nose area,
G = lower front, D = rear wing (top of sheet), B = big rectangle top-left, F = rear deck, E = long strip on the left edge.

## Part table (from the grid shots; cell = `col.row`, col = x/64, row = y/64)

Front of the car = low x. Larger y = car's LEFT (right-side panels upside down), like the BMW.

| Part | Where on the sheet | Notes |
|---|---|---|
| Hood + nose (panel C) | cols 3-11, rows 16-24, centre row 20.3 | one island from the windshield to the lower nose; `64` number block on the hood at x467-538 y1253-1350 (cols 7-8). 3D on it: two slot vents ~(5,17.5)/(5,22.5), oval duct ~(6,18), round camera/light ~(8.5,21.5), 3D Porsche crest at the nose centre (~x 228-255, y 1298): it covers paint, keep logos at x > 265 (gfr-v2 v5 roundel sat under it) |
| Front fender + headlight surround | right (H): cols 3-12, rows 13-17; left (G): cols 3-12, rows 22-27 | headlights are 3D (cut a hole); fender meets the hood along a shut line that touches on the sheet |
| Lower front bumper (E) | cols 0-3, rows 15-27 (long strip on the left edge, x runs up the bumper face) | intake/splitter below are 3D; T/P/M pieces = small lower lip islands |
| Windshield banner (L) | x 919-1022, y 1053-1492 (cols 14-15, rows 16-23) | text across the car runs along y; top edge meets the roof (A) |
| Roof | cols 15-22, rows 16-24 (part of A) | clear of 3D parts: big-logo spot (letter tops toward the rear, rot -90); roof antenna ~(17,20) |
| Door | right: cols 13-21, rows 9-14 (row 14 = window line, rows 9-10 = sill); left: cols 13-22, rows 25-30 | number blocks x873-970 y770-841 (right) / x870-967 y1761-1831 (left): iRacing draws `64` |
| Front fender rear vent | right ~(12-13, 11-14); left ~(12-13, 26-29) | 3D gill between fender and door; joined across it in `seams.json` so graphics carry over |
| Rear quarter + side intake | right: cols 22-28, rows 11-16; left: cols 22-28, rows 24-29 | intake ~(22,13)/(22,27) is 3D |
| Rear deck / engine lid (F) | cols 27-31, rows 17-23 | rear window (A130-A134 frame) in front of it; wing stays sit on it |
| Rear bumper (D) | cols 13-31, rows 0-6 (x across the car; right corner cols 28-31, left corner cols 13-16, centre ~col 21.5) | tail-light bar, plate (~22,4), exhaust and diffuser are 3D; rear `64` block x1634-1707 y304-371 (right corner) |
| Lower rear / diffuser surround (J) | cols 17-28, rows 4-6 | |
| Rear wing top (B) | cols 0-11, rows 0-5 (x across the wing, car's left at low x); visible top face rows 3-4 | row 3 = leading edge. Wing text read from the FRONT (LIVERY_GUIDE 7) = letter tops toward the trailing edge (higher y): **rot 180** (untested) |
| Mirrors | right ~ Z (x~616 y~647), left Y (x~616 y~1952) | small; logo spot |
| Number blocks at x284-380 / 497-593, y392-464 | P/M strips (cols 4-9, rows 6-7) | not identified in the shots (front lip?); check before using |

## Seams (`seams.json`, mirror_y 1299.5)

Read (2026-10-13):
- Hood nose C10-C14 / lower bumper E34.35-E30.55: nearly straight across on the sheet (same y, ~12 px gap).
- Right fender H11-H13 / bumper E38.6-E36.6; left fender G1-G3 / bumper E28.6-E26.8 (both read; each also mirrored).
- Hood side C15-C24 / left fender G30.9-G21.9: the two edges touch on the sheet, pairs taken from that; right side by mirror (H).
- Roof front A41-A46 / windshield banner top L15-L10: also nearly straight across.

Not read yet (need close-ups): rear quarter / rear bumper (A157-A160 vs D37-D42: the side reflector sits on it, seam_rear34_right),
deck F / rear window frame and quarter (A112-A124), deck / ducktail (U, AB strips), bumper D / diffuser J, door / sill.
Fender / door: a 3D gill sits between them, but they are joined across it as a seam (read at equal height) so graphics carry over.

Stripe test round 1 (`seamcheck1_*.webp`, 2026-10-13): hood/fender, nose/bumper centre and roof/banner carried through. The bumper
corners under the headlights were wrong: stripes almost vertical on the bumper vs diagonal on the hood/fender. Cause: the bumper (E)
was pinned to the nose (C) only and the fender/bumper readings were ignored (not on the unfold tree); measured 73-110 px off at those
seams. Fixed in `tools/seams.py` (panels now fit all placed neighbours): 0.2 px off, no folds.
Round 1b (user close-ups 2026-10-13): stripes still bent into an S on the bumper corner and the middle line wiggled (bumper free
area pinned to one whole-panel rotation): fixed with distance-weighted local fits. Bumper stretch now 1.26 max.
Fender -> door across the vent added as a seam (`H37`/`A5.52`, `H36`/`A6.67`, mirrored to G): the grid shows the fender rows sit ~0.8
row lower than the door's. Stripe test now one group (root C: E, G, H -> C; A -> G; L -> A). Mild wiggle on the door right at the
vent (short reading).
Round 3 (`seamcheck3_*.webp`, user: "really close"): fender -> vent -> door carried over, but the door stripes bulged next to the
vent; bumper corner good inside, wrong at the outer end near the wheel (readings stopped at H11). Fixes: fender/door seam marked
`"gap": true` (positions joined, angle left free: door stretch p99 2.07 -> 1.22); fender/bumper extended to H10 (H10/E39.57; H9 at
the slot corner left out, it stretched the fender 8:1). Fenders now take the bend round the headlight (stretch p99 ~3.7). Round 4
(in-sim) pending.
Round 4 (`seamcheck4_*.webp`): bumper fine; at the vents the stripes stepped and changed angle (door ~30 px off, ~10 deg). The ruler
readings across the vent were off. Replaced with the grid (`grid_side_right.webp`): the door sits 48 sheet px lower than the fender at
every height, scale 1 -> H38/A4.85, H37/A6.13, H36/A6.95. `gap` flag dropped again (with good readings, carrying the angle is smooth:
door stretch max 3.4; with `gap` a 52:1 spike). Round 5 (in-sim) pending.

## Placements in use (2026-10-14, first liveries: gofast, white-gofast, polkadot v1; not yet checked in-sim)

- Number cards (block grown x1.47 along / x1.78 across, covers the template's PRO boards): left door (847,1733)-(990,1859) rot 0,
  right door (847,740)-(990,866) rot 180, hood (440,1230)-(566,1373) rot -90.
- Door logo / burst: x 1000-1300, y 1755-1845 (behind the card, ends before the side intake ~x 1320).
- Windshield banner box (905,1035)-(1040,1565) (template PORSCHE banner shape); text centre x ~962, <= 70 px.
- Roof logo/mascot centre (1190, 1299.5), ~300 px, rot -90. In-sim (kintsugi v2, 2026-10-14): a ~300 px circle centred at x 1190 runs onto the windshield
  banner's top edge; centre x ~1265 (r <= 150) keeps a big roof mark clear of it. Quarter hornet (1560-1590, 1570): rear quarter top behind the side window.
- Nose badge (300, 1299.5), <= 60 px (crest at x < 265). Wing: box (12,13)-(737,342), logo centre (375,256) rot 180.
- Mirror housing: island Y x 494-714, y 1893-2004 (Z mirrored).

- **Fender -> door offset (vent ruler, 2026-10-14, `liveries/socal/vent_ruler.py`, shots in `liveries/socal/.../reference/ruler_vent_*`)**:
  at the same height on the car the door sits LOWER on the sheet than the front fender, by ~70 px at the top of the shut (ruler read ~60: v4 with 60 was a bit low, v5 with 80 too high, socal v6 = 70)
  line (fender y ~1616, left side) and ~35 px at the vent (fender y ~1776); bands run level on both, no rotation. Sheet-y
  graphics on the fender: draw them at door y - off(y). A constant -48 (socal v2) was ~25 px low at the top; the seam map
  unfold rooted at A (socal v3) got the offsets but tilted the fender, which looked worse in-sim: don't use it for G/H.
