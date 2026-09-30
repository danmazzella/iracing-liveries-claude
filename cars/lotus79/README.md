# Lotus 79 — sheet → car notes

Template: `Lotus 79.psd` (repo root). iRacing paint folder: `lotus79`

Mapped 2026-09-29 from the 64px grid. Screenshots: `grid_front_top`, `grid_front34_left`,
`grid_rear34_left`, `grid_side_right`, `grid_top` (.webp). `part_map.png` = the part boxes
below drawn on the template. (Installer found the `lotus79` folder: confirmed.)

`grid.tga` = labelled 64px grid (cell c,r = sheet x c*64, y r*64). `grid_sheet.png` = flat grid
with the mask, `template_sheet.png` = template body + wire + number/sponsor blocks.

## Template facts

- Layers: `Main Car Body`, hidden `Car Patterns` (iRacing's 24 patterns), `Pitbox Color`,
  `Car_Mandatory`, `Number Block Locations`, `Sponsor Block Locations`, `Mask`, `Wire` (hidden),
  hidden `Custom Spec Map` (Red Metallic / Green Roughness incl. `Parts` / Blue Clearcoat).
- **Mirror line y ≈ 1259.5** (mask symmetry + the paired number/sponsor blocks).
- **Nose is on the left of the sheet** (like the GT3s). Larger y = car's left; the right-side
  panels are upside down (checked: right sidepod labels read upside down in `grid_side_right`).
- Wings and endplates are separate islands across the top of the sheet and are NOT mirrored
  about y 1259.5: draw each explicitly.
- Number blocks: x 1300-1416 at y 574-676 and 1844-1945 (a mirrored pair), and x 261-354,
  y 1203-1317 on the centre line.
- Sponsor blocks: x 747-1286 y 565-663 / 1857-1955 (pair), x 932-1447 y 1020-1112 / 1408-1500
  (pair), x 303-349 y 912-1130 / 1391-1609 (pair), x 335-479 y 12-467, x 558-753 and 804-1000
  y 122-160, and two on the centre line near x 370-579.

## Part map

Right side listed; left side = mirror (`y' = 2519 - y`).

| Part | Columns | Rows (right / left) | Notes |
|---|---|---|---|
| Nose top | 2-10 (x 130-640) | 17-22 (centre) | tip at col 2; widens to the scuttle at col 9-10. Number block x 261-354 y 1203-1317 ("64" sits on it, reads nose→up) |
| Front wing top | 4-5 (x 256-383) | 14-17 / 21-24 | span runs along sheet y; cols 0-3 = rest of the wing (under/flap), white `Car_Mandatory` strip x 0-70 |
| Front wing endplates | ~0-5 | ~8-12 / 26-30 | teardrop islands; e.g. `3,29 4,29` on the left endplate |
| Tub side (cockpit + under engine) | 10-27 | 14-17 / 22-25 | runs nose→gearbox; labels 11,16 ... 27,17 along the right side; sponsor block x 932-1447 |
| Cockpit surround / scuttle | 11-19 | 17-21 (centre) | cockpit opening; the "6"-shaped island x 790-1000 is inside it |
| Engine cover top | 19-28 | 17-21 (centre) | oval hole = the open engine / trumpets; `28,19`, `27,21` at the tail |
| Sidepod side | 9-21 | 7-10 / 29-32 | big flat panel, the main "billboard". Sponsor x 747-1286; number block x 1300-1416 (rear end) |
| Sidepod top | 9-24 | 10.5-13 / 25.5-28.5 | radiator louvres x 780-900; flares up into the engine flank at cols 21-28 |
| Rear wing top | 4-7.5 (x 256-480) | 0-7 | span along sheet y (0-450), chord along x; sponsor x 335-479 |
| Rear wing (under / rear?) | 0-4 | 0-7 | not seen in screenshots, assumed underside |
| Rear wing endplates, outer | L 8-11, R 12-15 | 0.5-6 | two trapezoids; sponsor strips y 122-160. Inner faces probably the pair at cols 15-23 |
| Headrest / roll hoop | 29-31 | 0-5 | top-right island; `29,0 30,1 31,0` behind the driver's head |


## Gotchas

- The `Mask` layer covers almost nothing; the UV islands are outlined in green (1,255,0) in the
  `Wire` layer. Label the areas enclosed by the green lines to get each panel
  (`gfr79/livery.py` `islands()`, pick one with a seed point).
- Sidepod side (left island x 605-1442, y 1815-1969) is tilted on the sheet (top edge ~2.5-4
  deg: y 1859 at x 700 -> 1820 at x 1260; bottom edge ~1 deg) and only ~110-125 px tall at any
  x: a full inset frame leaves no room for lettering. Text tilted 2 deg sits parallel (left
  rot +2, right side 180-2 = 178). Fit text to its box first, then rotate.

## Proven placements (in-sim)

- GFR badge on the nose top at (470, 1260), rot -90: reads upright from the front (v2).
- Rear wing top lettering at (380, 240), rot 90, box 150x400: reads left-to-right from behind (v2).
- Sidepod-side lettering at (1010, 1902) left / mirrored y right with 180-rot: both read correctly (v2).

- 3D parts over paint: chrome intake trumpets in the engine cover hole, two chrome mirrors on
  the tub sides by the cockpit, radiator mesh inserts in the sidepod tops, the exposed engine /
  gearbox at the rear. Keep key graphics off those spots.
- iRacing draws the number on the nose (cols 4-5 rows 19-20) and on the rear of both sidepod
  sides (cols 20-22): leave those clear or put a card behind them.

## Seams (tools/seams.py, LIVERY_GUIDE 4b)

Seam ruler built: `seams.tga` (90 panels, codes in `seams_sheet.png`).
Readings in `seams.json`: none yet. Add each seam read in-sim below (which seam, screenshot, checked?).
