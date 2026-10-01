# McLaren 720S GT3 EVO — sheet → car notes

Template: `McLaren 720s EVO GT3.psd` (repo root). iRacing paint folder: `mclaren720sgt3`.

Mapped 2026-09-28 with the 64px grid (`grid.tga`, labels `col,row`; cell c,r = sheet x c*64,
y r*64). Screenshots: `grid_front_top`, `grid_front34_left`, `grid_rear34_left`, `grid_rear`,
`grid_side_right`, `grid_top` (.webp). `grid_sheet.png` = flat grid with the mask.

| Part | Columns | Rows | Notes |
|---|---|---|---|
| Hood / nose | 2-8 (130-560) | 14-23 | nose tip col 2-3, centre row 18.8 (y 1206) |
| Headlights | ~3-5 | 13-15 / 21-23 | orange surround goes on cols 3-8 rows 21-24 (left) |
| Front fender tops | 5-8 | 22-23 (and 13-14) | |
| Hood scoop (IMSA "64" spot) | 10-14 | 0-1 | separate island at the top of the sheet |
| Windshield / roof header banners | 7.5-9 / 11-13 | 15-22 | known boxes in cars.py |
| Roof | 12-17 (770-1090) | 16-21 | centre ≈ (930, 1206) |
| Engine cover / rear deck | 17-24 | 15-22 | louvred engine vent ≈ cols 18-21 rows 17-20 |
| Tail / rear upper | 26-28 | 14-22 | |
| Rear bumper | 19-28 | 0-3 | 20.0 ... 27.0 across the rear, 21.3-25.3 lower |
| Wing top | 0-9 | 3-4 | also 5.5/6.5 on the endplates |
| Left side | 5-27 | 24-31 | front fender cols 5-11, door 12-18, rear quarter 19-26; beltline row ~25-26, sill rows 30-31 |
| Right side (upside down) | 5-27 | 5-12 | mirror of the left |
| Side window / cockpit | 12-16 | 23-24 | black glass, seen from above |
| Side air intake (behind door, upper) | 19-22 | 23-25 | dark vent |

Uncertain: front bumper lower corners (labels around cols 19-20 / 27-30 rows 4-5 and cols 1-2
rows 17-21 showed up in the front shots); confirm with in-sim screenshots before designing there.

## Known

- Front of the car on the left; the sheet is mirrored about **y ≈ 1206.5** (confirmed by the grid) (door cards at
  y 1765–1908 and 505–648). Larger y = left side, right side upside down.
- The side panels are **tilted ~5°** (draw shapes level, then shift each point y -= 0.089*(x-880)). Door cards and
  sponsor strips rotate 5.3° (left) and 175° (right); a mirrored tilted logo needs `180 - rot`, not `rot + 180`.
- Layers: `Base Paint` is the paintable area. `Car_decal` is the black trim, splitter, diffuser
  and tow hooks: composite it over the paint. Drop the `IMSA Decals GTD PRO` decals (still used
  as the windshield banner shape). Keep `Pitbox Colors` on top. `Pitboard` is blue filler.
  Spec: hidden `Custom Spec Map/Green Channel Roughness`.

## Proven placements (checked in-sim, Polka Dot build)

| Item | Sheet position | Notes |
|---|---|---|
| Number cards | door L (817,1765)-(956,1908) rot 5.3; door R (817,505)-(956,648) rot 175; hood (302,930)-(469,1095) rot −68.6 | |
| Door strips | (945,1766)-(1276,1846) rot 5.1; (945,566)-(1276,646) rot 174.9 | shortened: the rear ~75px sits under the in-sim **IMSA LED position light** |
| Windshield banners | glass strip (478,986)-(596,1427); roof header (706,986)-(824,1427) | |
| Hood badge | centre (257,1206), 130px, rot −90 | nose sponsor zone |
| Roof mascot | centre (980,1206), 290px, rot 90 | |
| Wing logo | centre (330,228), max 460x72, rot 180 | nudged off the trailing edge (y 163) |

## Gotchas

- Thin panel behind the front wheel = col 4 rows 27-28 (x ≈ 200-330), just ahead of the side
  fender on the sheet (confirmed McLaren v8).
- **Front wheel-arch vent** + the small panel behind the front wheel = islands on the sheet's
  right edge, x ≈ 1775-2048, y ≈ 1240-2048 (left side; mirrored for the right). Not near the fender
  on the sheet (confirmed McLaren v6).

- Headlight inner end ≈ y 1400 (left; mirrored ≈ 1013) at the nose (x ~150-330). Orange whose
  inner edge goes below that spills past the light onto the nose (McLaren v3).

- The rear bumper (sheet top, y < ~366) is outside the mirrored band, so shapes there aren't
  copied/overwritten by the mirror. Draw both corners explicitly.

- Door decals can't grow lengthwise: number card in front, LED position light behind.

## Seams (tools/seams.py, LIVERY_GUIDE 4b)

Seam ruler built: `seams.tga` (97 panels, codes in `seams_sheet.png`).
Readings in `seams.json`: none yet. Add each seam read in-sim below (which seam, screenshot, checked?).
