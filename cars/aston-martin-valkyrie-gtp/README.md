# Aston Martin Valkyrie GTP

iRacing paint folder: `amvalkyriegtp`

Template: `psd/Aston Martin Valkyrie GTP.psd`. Layers: `Wire`, `Mask`, `Car_decal` (Aston/sponsor
logos, windscreen banner, number boards, **opaque grey hatch over both wing elements**),
`Car_Mandatory`, `Number Blocks`, `Sponsor Blocks` (hidden guides), `Custom Spec Map`
(`Green Channel Roughness` etc.). No carbon paint layer (use `trim=None`).

Grid screenshots: `grid_*.webp` (labels read `col.row`, cell = 64 px).

## Sheet layout

- Front on the left. **Mirror line y = 1332.5** (from mask symmetry). Larger y = car's left.
- The band **y < 618 is not mirrored**: roof, engine cover halves, shark fin, rear tail panels and
  the lower wing element live there, each side drawn separately.

## Part -> columns/rows

| Part | Left side | Right side |
|---|---|---|
| Nose top (front of hood, number "64") | cols 1-3, rows 17-24 (centre 20.8) | same island |
| Hood between front fenders | cols 4-5, rows 19-22 | same island |
| Headlights (3D, cover paint) | ~3-4, 24-25 | ~3-4, 15-16 |
| Front fender pods | cols 4-8, rows 24-26 | cols 4-8, rows 14-17 |
| Nose side below headlight | cols 2-3, rows 27-30 | cols 2-3, rows 10-12 |
| Blade behind front wheel | cols 9-12, rows 29-31 | cols 9-12, rows 9-12 |
| Windscreen brow / banner | col 11, rows 18-22 (Car_decal banner x 699-897, y 1132-1536) | |
| Mirrors | 16,22 (+14,23) | 16,19 |
| Cockpit side / upper sidepod (flat, burst decal) | cols 11-19, rows 24-26 | cols 11-19, rows 15-17 |
| Lower sidepod, number board | cols 14-20, rows 30-31; number x 1196-1289, y 1956-2023 | x 1196-1289, y 643-710 |
| LED number display (3D) | 14-16, 30 | |
| Rear haunch / fender top | cols 20-25, rows 23-27 | cols 20-25, rows 13-17 |
| Engine-cover spine (centre) | cols 19-24, rows 20-21 | same island |
| Roof (canopy top) | cols 0-5, rows 4-6 (front at x 64; top band, x = front->rear) | |
| Engine cover halves | cols 7-15, rows 7-8 | cols 6-15, rows 3-4 |
| Shark fin | cols 17-25, rows 6-8 | cols 17-25, rows 3-5 |
| Rear tail panels (behind rear wheel) | cols 24-27, rows 7-10 | cols 28-31, rows 7-10 |
| Rear wing top | col 31 (Car_decal hatch x 1832-2047), rows 15-26, span along y | |
| Rear wing lower element | row 1, cols 0-11 (hatch x 0-755, y 0-115) | |

Other Number Blocks at x 1706-1794 y 1968-2032 and x 1901-1989 y 1881-1945: not located in-sim yet.

## Unmapped / to check

- Rear bumper/diffuser faces and wing endplate outer faces (rear shot had no readable labels).
- Which sheet direction is the wing's trailing edge (assumed +x, like the roof).

## Proven placements

- Polka Dot v1 (in-sim): side burst on the upper sidepod (830-1180, 1612-1700 + mirror) reads well;
  wing logo (1984, 1344, rot -90) fine; nose number card fine.
- Roof/engine-cover top is ONE island (x 9-981, y 134-600) with its own centre line at **y 367**.
- Hood badge must stay at x < ~345 (canopy edge); 80 px at x 298 between the nose number and the canopy.
- Windscreen banner: only the brow island x 709-787 is visible; the rest of the Car_decal banner is glass.

- White GoFAST v5 (final): front orange over headlights + fender pods, navy arrow block with logo on the
  upper sidepod (700-1250, 1585-1722), shards from under it over the haunch, navy roof/engine stripe
  y 292-442 (top band, not mirrored), hornets on fin sides (1400, 468 / 266), navy wing with
  `decal_skip` of the template hatch, bigger number cards. Config: `liveries/white-gofast/designs.py`.

- Seams (`seams.json`, ruler `seams.tga`, shots `seam_*.webp`): panel codes A = sides + hood (both sides),
  B = roof/engine cover, C = nose + fenders, R = spine, L/M = fin sides, W = windscreen brow.
  C/A touch on the sheet at x 284 (no reading needed). R/B read both sides (R8-R12 / B46-B43,
  R25-R28 / B62-B59, ~1 seg each). L/M/R readings exist but folded the stripe test: unverified.
  `seams.py unfold("B")` folds R; a plain thin-plate fit on the R/B pairs is clean (polkadot `seam_warp`).

## Gotchas

- iRacing paints a white plate over the whole Number Block. A number card must be bigger than the
  block (BMW ratio: x1.47 along the number, x1.78 across, same centre) or it disappears. Template
  WeatherTech number boards (Car_decal): L x 1176-1307 y 1931-2029, R y 637-735, nose x 135-272 y 1268-1399.

- The roof/engine island, the centre spine (x 1208-1632, y 1222-1443) and both shark-fin sides
  (x 1015-1584, y 173-357 / 377-561) touch in 3D but sit far apart on the sheet: sheet-based patterns
  break up across them. Give them a pattern that doesn't need to line up (or map the seams).

- `Number Blocks` / `Wire` are hidden: `layer.composite()` returns nothing, use `topil()` + offset.
