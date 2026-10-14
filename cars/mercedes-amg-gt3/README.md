iRacing paint folder: `mercedesamgevogt3`

# Mercedes-AMG GT3 2020 (Evo) — `mercedes-amg-gt3`

Template: `psd/Mercedes-AMG GT3 2020.psd` (wire layer = `Wire`). Grid made 2026-10-05; first-pass part
table from 20 in-sim grid shots (`grid_NN_<view>.webp`). **Approximate: read from whole-car shots, seams not read.**
Cell `c,r` = sheet x `c*64..c*64+63`, y `r*64..r*64+63`.

## Sheet layout

- **Mirror line y = 1327** (measured 2026-10-05 by flipping the `Mask` about candidate lines: IoU 0.98 at 1327 on hood, sides and trunk; the first-pass 1312 from grid labels put everything ~15 px off-centre in-sim). Larger y = car's **left** side (rows 26-31 = left door/fender/skirt);
  smaller y = right side (rows ~10-14 = right door, **upside-down** labels). Hood and roof sit across the line.
- Front of car = left of the sheet for the body panels (hood col 1 at the nose, col 8-9 at the windshield).
- **iRacing draws the number (64) NOT on the template Number Blocks layer** (those sit on the PRO plates; v6 cards there missed): real spots read off grid_04/grid_14: hood front-right (x ~290-420, y ~1090-1190), lower front fender/skirt behind the wheel arch on both sides (~x 450-640, y 1920-2040 left, mirrored right), rear bumper. Old note: hood front-right (~5-6,17-18),
  both side skirts (~7-9, 30-31 left; mirrored right), rear bumper (~4-6,6-8). Leave plain.

## Part -> cells (first pass)

| Part | Cells | Notes |
|---|---|---|
| Rear wing main plane | cols 0-10, rows 0-4 | leading edge row 0 (`1.0..10.0`), reads from rear; top-view labels `1.3..10.3`. Wing text rot 0 (guide s7) |
| Wing end plates | cols 26-31, rows 0-3 | `27.0`, `29.2/30.2/31.2` seen on the end plate |
| Hood | cols 1-9, rows 17-24 | col 1 = nose lip, col 8-9 = windshield; row 17 = car right, row 24 = left. Labels read rotated in the front view |
| Hood scoop/intake (3D hole) | ~cols 2-4, rows 18-23 | fan visible; don't put logos there. Approximate |
| Hood side vents (black louvres) | ~cols 5-8, rows 17-18 and 22-24 | 3D parts over paint |
| Roof | cols 12-19, rows 17-24 | `13.18..18.22`; centre line row ~20.5 |
| Windshield banner / roof front edge | cols 12-13, rows 17-24 | seen from the front as `12.17, 13.20, 12.23` |
| Rear deck / trunk lid | cols 20-27, rows ~14-24 | `24.19..26.21`; rear star at ~26,20; two small oval tail-deck items `29.4/30.4/31` |
| Front bumper (upper + grille) | cols 14-22, rows 0-3 | centre = col ~18.3 (star at 18.1). Upright `15.1..21.1` in the front view |
| Front bumper corners / headlight surround | cols 12-14 and 22-25, rows 0-4 | `14.0`, `22.0` at the headlights; `13.2-13.4` / `23.2-23.4` lower corners |
| Front splitter / lower lip | row 4, cols 13-23 | `13.4..23.4` along the lip |
| Left front fender | cols 4-9, rows 26-30 | `6.27-9.27` top, `5.28/6.28`; wheel arch below |
| Left door | cols 10-17, rows 27-29 | door handle ~cols 12-14 row 27; AMG decals cols 13-17, rows 27-29 (Car_decal) |
| Left rear quarter | cols 17-21, rows 27-29 | `17.28..21.28`; rear arch `1.6-3.6` area on the rear fender (cols 1-4, rows 6-7) |
| Left side skirt + exhaust | cols 5-17, rows 30-31 | exhaust at cols ~12-13, row 30; gill/louvres at cols 7-10 |
| Left front-fender vent (gill) | cols 25-28, rows 28-29 | island on the right edge of the sheet (`25.28, 26.28, 27.28, 27.29`) |
| Left rear fender lower / arch | cols 25-28, rows 24-25 | `27.24, 27.25` behind the rear wheel |
| Right side | rows ~9-15, same cols, **upside down** | mirror of the left (door `7..19,11-14`) |
| Rear bumper / fascia | cols 1-15, rows 5-9 | x runs across the car (col 1 = left corner, col ~14 = right corner); row 6 top, 9 bottom; number block 4-6, 6-8 |
| Rear diffuser | ~cols 1-15, rows 9-10 | 3D carbon fins sit over the paint; unconfirmed |
| Mirrors | bright green islands at the top-middle/left (see `grid_13`) | unmapped |

## Gotchas

- Windshield banner (Car_decal, two strips x 642-730 and 741-824): only the outer strip x ~741-824 shows above the
  glass in-sim (socal v1). Keep banner text inside it. Wing text rot 180 + the plain foam cards on iRacing's real
  number spots (hood 255-450 x 1060-1215) read right (socal v1 top-front shot).
- iRacing's side number "64" sits at ~x 440-535, y 1965-2035 (left; mirror for the right), low on the fender behind the
  front wheel: a card 418-562 x 1942-2046 frames it (socal v3: a 420-670 x 1890-2045 card read as a huge empty box).
  Lower door rear / sill ahead of the rear wheel = separate panels AA (left) / AL: include them with the side panel A.
- Panel islands: `islands.npz` / `seams.tga` generated 2026-10-14 (no seams read). Left side = panel A, right = B,
  hood C, roof F, trunk J, wing D, rear bumper E, front bumper G; twins within 1 px of mirror 1327.

- Wing leading edge is the visible face from behind; paint the wing from the front-reading orientation (rot 0).
- Hood front edge labels read sideways from the front: x (col) runs nose -> windshield, so the hood is "long in x".
- Template `Car_decal` carries the AMG door decals and the banner; composite it over the paint.
- The mirror line passes through hood/roof/trunk; design body graphics once and mirror in y (`2*1327 - y`), but text/logos rotate 180 on the right side.

## Not mapped yet

Seams (hood/bumper, hood/fender, roof/rails/windshield, trunk/quarters), side mirrors, A-pillar, rear light surrounds,
the top-middle panels at cols 11-25 rows 5-9 (circles at ~21,8 and star ~27,8), wheel-arch liners, pitboard,
`Splitter Color` / `Dive Plane Color` layers (pattern-tinted). Need: close-ups of the mirrors, A-pillar and a low front 3/4.
