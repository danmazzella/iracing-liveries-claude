# Ford Mustang NASCAR Next Gen, car key `ford-mustang-nextgen`

iRacing paint folder: `stockcars fordmustang2022`

(Confirmed from the user's `Documents\iRacing\paint\` listing 2026-10-01. The folder name contains a space: quote it in PowerShell.
Sibling Next Gen cars: `stockcars chevycamarozl12022`, `stockcars toyotacamry2022`.)

Template: `psd/Ford Mustang Nextgen.psd`. Layers: `Wire` (hidden), `Mask`, `Car_Mandatory`, `Car Decal`, `Base`, `Rear Spoiler`,
`Rocker Panel`, `Window Blackout`, `Nose Blackout`, `Color Change`, `Pitboard`, `Pitbox Colors`, `Car Patterns/*` (hidden),
`Number Blocks` + `Sponsor Blocks` (hidden guides), `Custom Spec Map` (hidden; `Green Channel Roughness/{Carbon Fiber,Parts}`,
`Red Channel Metallic/Parts`).

## Status

Part map first pass 2026-10-01 from 13 in-sim grid shots (`grid_*.webp`; the grid is `grid.tga`, flat view `grid_preview.png`).
Body sides, hood, roof, rear deck and fascia are solid; bumpers, spoiler and small islands are **approximate** (`~`) and need close-ups.
Seams NOT mapped. Cell = `col.row`, col = x/64, row = y/64.

## Sheet layout (differs from the GT3 sheets)

- **Front of the car = HIGH x (right of the sheet), rear = low x.**
- **Centre line y ~ 1240** for hood, roof, rear deck (the hood Ford oval sits at y 1240; the grid labels split at 1280 but the art is centred ~40 px higher, verified on the v3 preview). Side panels mirror about y 1238 (left body y ~560-935, right ~1540-1910).
- On a side panel the **sill/rocker is at the panel's outer top (left) edge and the beltline/roof rail at the bottom** (left side: sill y ~560, wheel arch hole at x 350-585 top; right side flipped).
- **Smaller y (rows 9-14) = car's RIGHT side and upside down on the sheet; larger y (rows 24-31) = car's LEFT side, upright** (corrected from the v3 in-sim shot: logo on the low-row panel read upside down).
- Side panels mirror about ~ 38 instead (left row 12 <-> right row 26, rocker row 8 <-> 30): the mask is not symmetric, so place each side separately.
- Front fascia (cols 0-15) and rear fascia (cols 17-27) sit in the top strip, rows 0-4; their lateral axis runs along x. Car's right = lower col at both ends.
- Visible side in a shot with the nose on the left = car's LEFT (window net, rows 9-12).

## Part map

| Part | Where on the sheet | Notes |
|---|---|---|
| Hood | cols 21-29, y ~1000-1480 only (rows ~15.6-23), x 1300-2040 | centre row 19|20; front edge cols 28-29 |
| Hood louvres (vents) | ~ cols 23-27, rows 15-17 and rows 22-24 | open 3D vents, paint under them hidden |
| Windshield banner ("MAZZELLA" strip) | cols 16-17, rows 16-22 | text reads along the sheet y axis |
| Windshield glass / cockpit | cols ~17-21, rows 14-25 | not paintable |
| A-pillars | left ~ cols 17-20, rows 14-15; right ~ rows 24-25 | |
| Roof | cols 9-16, rows 16-23 | roof "64" box ~ cols 10-15, rows 16-22; letter tops toward sheet +x? number is drawn by iRacing |
| Roof rails / quarter-window frame | left rows 13-15, right rows 24-25, cols 2-17 | |
| Rear window glass | cols 3-8, rows 16-23 | not paintable (guard bars, orange tow tabs) |
| Rear deck / trunk lid | cols 1-2 (+ ~3), rows 16-22 | continues into the rear fascia |
| Rear fascia (bumper cover) | cols 17-27, rows 0-4, centre x ~ 1408 (col 21|22) | lights ~ cols 17-19 and 24-26, rows 1-2 (3D); small "64" at ~ 25.3 |
| Rear spoiler | ~ cols 28-31, rows 0-10 | PSD layer bbox; lateral axis along rows; glass-like end plates are 3D |
| Diffuser | carbon, not paintable | |
| LEFT body side (door + quarter) | cols 2-21, rows 9-12 | beltline row 12, sill row 9; "64" ~ cols 16-21, rows 10-12 |
| RIGHT body side | cols 2-23, rows 26-29 | beltline row 26, sill row 29; "64" ~ cols 17-22, rows 26-28 |
| LEFT / RIGHT rocker panel, side vents | left ~ row 8, right rows 30-31, cols 10-26 | exhaust ~ col 19, row 30; vents ~ cols 12-16 |
| LEFT front fender | cols ~21-28, rows 9-14 | wheel arch ~ cols 22-26 |
| RIGHT front fender | cols ~21-28, rows 24-29 | |
| Rear quarters | left cols 2-9, rows 9-14; right cols 2-9, rows 24-29 | rear arch ~ cols 5-9; tail-lamp side marker ~ col 2-3 |
| Front fascia / nose | cols 0-15, rows 0-4, centre ~ col 7-8 | right corner ~ cols 1-5, left corner ~ cols 10-14; grille/pony ~ centre; `Nose Blackout` strip row 4 |
| Front splitter | carbon, not paintable | |
| Pitboard | cols 5-9, rows 29-32 | PSD layer, not on the car |

3D parts that cover paint: hood louvres, tail lights, side vents/exhaust, window net (left), rear window guard bars.
Number blocks: iRacing draws the number on the doors, roof and rear fascia (do not paint numbers).

## Proven placements

None yet.

## Gotchas

- Labels read `col.row` (e.g. `17.22`). Rows 0-4 and cols 0-31 overlap between fascias: check which strip a label is in by its col (front 0-15, rear 17-27).
- Nose is at HIGH x here: the opposite of the Mustang GT3 and BMW sheets.

## Next

1. Close-ups for the `~` rows: front fascia from the front, rear spoiler, both wheel arches, rocker/side vents.
2. Add the car to `tools/seams.py`, run the ruler, read hood/fender, roof/rails, deck/fascia seams.
