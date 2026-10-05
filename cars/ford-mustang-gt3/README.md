# Ford Mustang GT3, car key `ford-mustang-gt3`

iRacing paint folder: `fordmustanggt3`

(Confirmed from the user's `Documents\iRacing\paint\` listing 2026-10-01. `fordmustanggt4` is the GT4, a different car.)

Template: `psd/Ford Mustang GT3.psd`. Layers: `Wire` (hidden), `Mask`, `Car mandatory`, `Car Decal`,
`Arrows`, `Base`, `Car Patterns/*`, `Pitbox Colors`, `Pitboard`, `GT3` (hidden), `IMSA Decals GTD` (hidden),
`IMSA Decals GTD PRO`, `Color Change Logos`, `Number Blocks` + `Sponsor Blocks` (hidden guides),
`Custom Spec Map` (hidden; `Green Channel Roughness/{Carbon Fiber,Plastic Matte Rocker}`, `Red Channel Metallic/{Carbon Fiber,Parts}`).

## Status

Part map first pass 2026-10-01 from 12 in-sim grid shots (`grid_*.webp`; the grid itself is `grid.tga`, flat view `grid_preview.png`).
Read at screenshot scale: body panels, wing, hood, roof are solid; bumpers, fender details and small islands are
**approximate** (marked `~`) and need close-ups. Seams NOT mapped (`tools/seams.py ruler ford-mustang-gt3` needs the car added first).
Cell = `col.row`, col = x/64, row = y/64.

## Sheet map

**Mirror line y ~ 1023 (between rows 15 and 16)**: hood centre labels split 7.15 | 7.16, and the Mask reflects best about y 1023
(it is only roughly symmetric). Row r on the left side = row 31-r on the right. **Larger y = car's LEFT**, front = low x,
right-side panels upside down. Hood, roof and rear deck straddle the line: design in lower-half (left) coords and mirror.

| Part | Where on the sheet | Notes |
|---|---|---|
| Hood | cols 5-14, rows 12-19 | number block (grey "64") at ~ col 10, rows 15-16 |
| Hood extractor vents | ~ cols 9-13, rows 11-13 (right) and rows 18-20 (left) | open black 3D vents; paint under them is hidden |
| Hood nostril/lip near the nose | ~ cols 5-7, rows 13-18 | small oval vent at ~ (6.2, 13.4) and mirrored (6.2, 17.6) |
| Windshield | cols ~13-15, rows 12-19 | not paintable (glass); windshield banner/strip area not mapped |
| Roof | cols 15-23, rows 12-19 | roof hatch ~ cols 18-21, rows 15-17; text on roof: letter tops toward sheet +x (guide section 7) |
| Rear window / C-pillars, rear deck (trunk) | cols 23-27, rows 12-19 | deck continues to the rear fascia |
| Rear fascia upper | cols 26-28, rows 12-19 | tail lights at col 28, rows 13 and 18 (3D, cut decals) |
| Rear bumper (face) | cols 28-31, rows 11-20 | camera/badge/tow holes ~ cols 29-31, rows 15-17; lower-centre light at 31.15-31.16 |
| Rear lower valence | top strip, row 0-1, cols ~16-28 (centre ~ col 23.5) | lateral axis runs along x here, not along y |
| Diffuser | carbon/3D, not paintable | |
| LEFT door | cols 14-24, rows 23-27 | beltline row 23, sill row 27; grey "64" at ~ cols 15-16, rows 24-25; handle ~ cols 19-21, row 23.5 |
| RIGHT door | cols 14-24, rows 4-8 (upside down) | sill row 4, beltline row 8, "64" ~ cols 15-16, rows 6-7 |
| LEFT rocker/side skirt, side-exit exhaust | cols 12-23, rows 27-28 | exhaust tip ~ col 14, row 27.5; skirt louvers ~ cols 16-23 |
| LEFT front fender (top + sides) | ~ cols 0-13, rows 19-27 | front fender vent/gill behind the wheel ~ cols 7-9, rows 24-26 |
| LEFT rear quarter | cols 23-31, rows 21-27 | rear wheel arch + side window frame strip at rows 21-22 |
| Side windows | rows 21-22 (left) / 9-10 (right), cols 14-27 | not paintable |
| Mirrors | small islands near cols 7-10, rows 4-6 / 25-27 (~) | exact ids not read |
| Front bumper, right corner (car's right) | ~ cols 0-3, rows 9-13 | labels 1.10-2.12 |
| Front bumper, left corner (car's left) | ~ cols 0-3, rows 19-23 | labels 1.19-2.22 |
| Front bumper centre / grille | ~ cols 0-3, rows 14-17 | round blob at col 0, rows 16-17 is the grille Mustang pony area |
| Front upper lip / grille top | ~ cols 1-3, rows 4-7 (labels 2.4-2.7) | runs left-right along the nose: rows = lateral axis |
| Front splitter | ~ cols 3-9, rows 0-1 and 30-31 (tips, 8.0 / 8.31), centre ~ cols 3-4 rows 15-17 | carbon parts are 3D |
| Wing main plane | cols 10-31, rows 29-31 | labels x.29 / x.30 / x.31; rows 30-31 = top face read from the rear shot |
| Wing end plates | cols 24-27, rows 25-27 (left) and 4-6 (right) | "25.27 26.27" / "25.4 26.4" |
| Wing pylons/stays | black carbon 3D | not paintable |
| Headlights, taillights, tyres, wheels, glass | not on the paint | |

3D parts that cover paint: hood extractors, tail lights, side-exit exhaust, mirrors (own islands), side window glass.

## Proven placements

None yet.

## Gotchas

- Grid label format on the car is `col.row` (e.g. `17.24`), comma-like in places.
- The visible side in a shot with the nose on the left is the car's LEFT side (rows 21-27, upright text).
- The sheet has no centre-line on the bumper: it is cut into corner islands, so mirror it by row (31-r) rather than around y 1023.

## Next

1. Close-ups to pin down the `~` rows: front bumper from the front, front fender/wheel arch (both sides), mirrors, rear bumper.
2. `tools/seams.py ruler ford-mustang-gt3` + read hood/bumper, fender/door, roof/pillars seams before any graphic crosses them.
