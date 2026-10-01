# Porsche 911 GT3 Cup (992.2), car key `porsche-992-cup`

Not the Porsche 911 GT3 R (that is a different car: `porsche-992-gt3r`, folder when mapped).

iRacing paint folder: `porsche9922cup`

(Confirmed from the user's `Documents\iRacing\paint\` listing 2026-10-01. `porsche992cup` also exists there: that is the older 992 Cup, a different car. The 992.2 Cup is `porsche9922cup`. `porsche992rgt3` = the GT3 R.)

Template: `psd/Porsche 992_2 Cup.psd`. Layers: `Wire`, `Mask`, `Car_decal`, `Car_Mandatory`,
`Super Cup Branding`, `X tape`, `pitbox colors`, `Color Change Logos`, `Windshield Name Locations`,
`Number Blocks`, `Sponsor Blocks` (hidden guides), `Custom Spec Map` (hidden; `Green Channel Roughness/Parts` etc.).

## Status

Mapped 2026-10-01 from the 11 in-sim grid shots (below). Seams NOT mapped yet (run `tools/seams.py ruler porsche-992-cup` before
designing graphics that cross panels). Cell = `col.row`, col = x/64, row = y/64.

## Sheet map

**Mirror line y ~ 1335.5** (mask reflection test, number blocks 815/1857). Larger y = car's LEFT, right-side panels upside down.
Front of the car = low x. Hood, roof and rear deck straddle the line; draw them in lower-half (left) coords and mirror.

| Part | Where on the sheet | Notes |
|---|---|---|
| Hood | cols 4-11, rows 17-23 (centre ~ row 20.5) | text across the hood runs along y; Porsche crest at ~(4,20.5); two air vents cols 6-8, rows 19-22; nose slot ~(5-6, 20-21) |
| Windshield banner ("Mazzella" box) | cols ~14-15 + 24-26 rows 17-23; template `Windshield Name Locations` x1173-1705, y461-618 | name strips also on the rear window |
| Roof | cols 15-22, rows 17-24 | roof radar/bump at ~(17,17.5) and (20,21) |
| Front bumper / fascia | cols 1-3, rows 14-26 (face runs along y, col 2 = lower lip, col 3-4 = upper) | wide splitter is 3D carbon below |
| Headlights (X-shaped LED, 3D) | right (5,15) / left (5,26): cols 4-6, rows 14-16 and 25-27 | covered by the lamp: no paint shows |
| Front fender + louvres | left: cols 5-11, rows 24-28 (louvre block ~cols 9-11 rows 26-27); right: mirror | louvres 3D |
| Door | left: cols 12-20, rows 27-30; right: cols 12-20, rows ~11-14 (upside down) | number block x782-902 (cols 12-14), y 815 (right) / 1857 (left): iRacing draws `64` here |
| Rocker / lower door | row 30, cols 12-21 | |
| Side window / B pillar | left: cols 18-19 rows 25-26 (strip "18.25 19.2") | glass is 3D |
| Rear quarter + intake | left: cols 21-27, rows 25-29 (intake slot ~cols 22-23, rows 27-28) | |
| Rear deck (engine lid) | cols 24-30, rows 15-23 | rear glass in the middle shows no paint |
| Rear bumper | cols 0-19, rows 0-3 (x across the car, left corner cols 1-5, centre ~ col 9.5, right corner cols 13-19) | plate area at 9-10, row 2; tow strap 12 row 2 |
| Rear lid / light bar | cols 5-14, row 1 | tail-light bar is 3D |
| Rear wing top | cols 20-31, rows 0-3 | text reads from the FRONT: see wing rule in LIVERY_GUIDE; wing stays are 3D black |
| Wing endplates | cols ~16-19, rows 5-9 | not confirmed (readable only as "17.5 18.5 16.6") |
| Mirrors | not read | take close-up if a design needs them |

Unmapped: roof/deck cols 0-3 rows 4-13 (tangle of islands at the top-left), the disc at cols 27-29 rows 11-12 (not a body panel
we saw), the sheet's bottom rows 28-31. Ask for close-ups if a livery needs them.

## 3D parts over paint

Headlights, front splitter, side louvres, side window glass and frame, rear tail-light bar, tow strap, wing stays, mirrors, tyres/wheels, exhaust.

## Gotchas

- Both doors carry `64` (iRacing draws it). Leave the number block plain, or put a card ~1.5x bigger behind it.
- Rear bumper is rotated like the front bumper on other cars: x runs across the car, y is height.
- Hood (x250-715, y1090-1580): two 3D air vents sit over x~380-515 (y~1190-1300 and 1370-1495) plus a central duct; they hide anything big placed mid-hood (a logo there lost half its text). Keep hood art small, or on the nose/rear of the vents.
- Roof (x955-1415, y1090-1585) is clear of 3D parts: best spot for a big logo (letter tops toward the rear, rot -90).
- Rear deck (x1525-1995, y960-1712) is full of cut-outs (hatch, wing stays): large art gets chopped.
- Rear quarter (left x~1525-1795, y~1560-1830): door-like orientation, rot 0 upright on the left, 180 on the right. Art ~200 px fits; its rear/lower edge meets the bumper at an unmapped seam, so art cut there.
- Wing: visible face is about sheet y127-287; a label centred y~205 reads fully, upright from the front (wing_rot 180).

## Screenshots so far

Verified against the in-sim shots (camera facing right = right side, facing left = left side; both doors carry a `64`):
- RIGHT side = sheet rows ~11-17 on the door/quarter (`grid_front34_right`, `grid_rear34_right`, `grid_side_right`).
- LEFT side = sheet rows ~26-30 (`grid_front34_left`, `grid_rear34_left`, `grid_side_left`, `grid_top_full_left_near`).
- So larger y = car's left, same as the BMW rule in LIVERY_GUIDE section 3.
- Also: `grid_front`, `grid_top_front`, `grid_top_rear`, `grid_rear_high`.
Coverage is complete for mapping; the part -> columns/rows table is still to be written.
