# Formula IR04 (F4): sheet → car notes

Template: `Formula IR04.psd` (repo root). iRacing paint folder: `formulair04`

Mapped 2026-09-29 from the 64px grid (the grid showed up in-sim via the installer, so the
folder name works). Screenshots: `grid_top_front`, `grid_front34_left`, `grid_front34_right`,
`grid_side_right`, `grid_side_right2`, `grid_top`, `grid_top_right`, `grid_rear`, `grid_rear34_left`,
`grid_front`, `grid_cockpit_top`, `grid_halo_right` (.webp). The paint-screen camera can't reach
low or underside angles, so wing undersides and the floor stay unmapped.
`part_map.png` = the part boxes below drawn on the template.

`grid.tga` = labelled 64px grid (cell c,r = sheet x c*64, y r*64). `template_sheet.png` =
template base + decals + mask + wire + number/sponsor blocks.

## Template facts

- Layers: `Paintable Area` group (`Base`, hidden `Car Patterns` (23), `Pitbox Colors`,
  `Car_decal`), `Turn Off Before Exporting TGA` group (`Car_Mandatory`, `Number Blocks`,
  `Sponsor Blocks`, `Mask`, `Wire` (hidden)), hidden `Custom Spec Map` (Red Metallic / Green
  Roughness incl. `Parts` / Blue Clearcoat / Alpha spec).
- **Nose is on the left of the sheet** (nose tip = col 1, row 17). Smaller y = car's **right**
  side, larger y = left (checked: `grid_top` has rows 4-8 on the right sidepod, rows 26-27 on the left).
- **Mirror line y ≈ 1128.5** (best mask-symmetry fit; sidepod row 4 ↔ row 31, tub row 11 ↔ row 23).
  Wings and rear-wing endplates are NOT mirrored about it: they sit side by side, draw each one explicitly.
- Number blocks: nose x 323-422 y 1072-1186 (cols 5-6, "64" reads nose→cockpit), and both
  rear-wing endplate outer faces: x 1124-1225 (left endplate) and x 1846-1946 (right), y 75-175.
- Sponsor blocks: sidepod sides x 305-806 y 288-366 / 1892-1970; front wing top x 1407-1653
  (right half) and 1764-2011 (left half) y 538-644; engine cover sides x 1403-1597 y 875-909 /
  1348-1382; rear wing top x 1020-1410 y 1651-1712; nose top x 570-711 y 1053-1206 and
  x 202-278 y 1083-1176.
- Dark `Car_Mandatory` rectangles x 1000-1398 y 644-858 and 1401-1614: not seen in the
  screenshots (floor / inner faces). F4 logos (`Car_decal`) sit on the nose tip (col 1-2) and on
  the airbox sides behind the roll hoop (x ~1380-1460, y ~1030-1180).

## Part map

Right side listed first; left side ≈ mirror (`y' = 2257 - y`). See `part_map.png`.

| Part | Columns | Rows (right / left) | Notes |
|---|---|---|---|
| Nose top | 0-13 | 16-19.5 (centre) | tip 1,17; "64" at cols 5-6; widens to the cockpit at col 13 |
| Nose / tub side | 1-16 | 10.5-13.5 / 21.5-24.5 | the whole side under the nose and beside the cockpit; front suspension arms mount at cols 7-10 |
| Cockpit rim / cockpit sides | 6-16 | 14-15.5 / 19.5-21.5 | curved islands around the centre; `9.14 10.14 11.15` on the right rim, `18.21 19.21` on the left; `12.20 13.20` inside the cockpit |
| Sidepod outer side | 2-14 | 3.5-6.5 / 28-32 | the main "billboard"; row 4 / row 31 = bottom edge; sponsor x 305-806 |
| Sidepod top | 2-14 | 6.5-9.5 / 25-28 | front inlet lip at cols 2-4 (`3.8`, `4.7`); rear tapers into the engine cover at col ~13 |
| Engine cover side | 16-31 | 12.5-16.5 / 20-23.5 | from the roll hoop back to the tail; sponsor strip x 1403-1597 |
| Engine cover top / airbox | 18-31 | 16.5-20 (centre) | spine behind the roll hoop; `30.19` at the tail; F4 logos on the airbox sides |
| Front wing, right half | 19-26 | 6-10 | top face rows 8-9 (`22.8 ... 25.9`); endplate/tip `19.7 20.7 21.7`; grey flap boxes in rows 6-7 |
| Front wing, left half | 27-32 | 6-10 | `28.8 ... 31.8`, `29.7 30.7` at the tip |
| Rear wing endplates | L 16-24, R 24-32 | 0-5 | two trapezoid pairs: outer face with the number (`17.2 18.3 19.1` left, `28.1 29.3 30.3` right), inner face next to it (`21.0-23.3` seen through the gap) |
| Rear wing main plane | 15.5-22 | 25-27.5 | `16.26 ... 21.26` along the span, reads upside down from behind; sponsor x 1020-1410 |
| Rear wing lower element | 15.5-22 | 28-30.5 | `16.29 ... 21.29` |
| Halo | 22.5-23.5 | 23-32 | the long thin strip: hoop reads `23` with rows `29 30 31` along it; centre pillar ends at the row-30/31 end by the nose (`grid_cockpit_top`) |
| Mirrors | 0-3 | 13-15 (left mirror, `1.15`) / 19-21 (right mirror, probably: its label wasn't readable) | small islands at the sheet's left edge. Not mirrored the usual way: the car's LEFT mirror uses the smaller-y island |
| Cockpit rim | 15-16 | 15 / 19 | `16.15` right rim, `15.19` left rim; headrest / rear cockpit wall ≈ `12.20 13.20` |

Not mapped (camera can't reach): the island cluster at cols 24-31 rows 23-31 (probably
gearbox/rear crash structure/suspension covers), front wing underside, floor.

## Proven placements

From `neonhornet` v1 (checked in-sim):
- Nose: GFR badge rot -90 at (640, 1128) reads right from the front; chevrons x 480-850 fine.
- Sidepod side: wordmark (430x86) at (520, 1905) left upright / (520, 350) right rot 180.
- Sidepod top: hornet rot 90 at (440, 1706), right side = vertically flipped copy: head forward.
- Rear wing main plane: lettering rot 180 at (1215, 1681) reads right from behind; lower element
  (1215, 1905) likewise. Front wing tops: upright at (1530, 591) and (1887, 591).
- Number cards drawn around the number blocks (+22 px) show iRacing's number cleanly.

## Gotchas

- **Sidepod shoulder seam:** the sidepod top and side strips are separate on the sheet: a
  wedge-shaped gap between them (true edges 4-36 px apart at x 200-430, ~200 px at x 900, same
  on both sides). The mask bleeds ~10 px past each true edge and even joins the strips at
  x ~220-400, so measure the seam from the **Wire outlines** (the consecutive outline pair
  nearest the boundary), not the mask. In 3D the top strip's outer edge meets the side strip's
  inner edge, so any field drawn in plain sheet coords jumps at the shoulder. Fix: per column,
  shift the side strip by the gap (sigma ~4 px smoothing). `liveries/neonhornet/livery.py`
  `shoulder_fix()` (v1 jumped, v2 with mask edges "very close", v3 with outlines: confirmed in-sim).
- **Engine cover side crease:** same kind of seam as the sidepod. The engine side is two strips
  with a wedge gap from x ~1440 (outline gap 11 px at x 1480 → ~110 px at x 1800), centred on
  y ≈ 927 → 913 (right; left = mirror). A small separate black part (Car_decal) sits inside
  the wedge at x ~1730-2000: skip its outlines when measuring. `neonhornet` `engine_fix()`
  (confirmed in-sim, v4).
- The engine cover top is split down the centre line on the sheet (unpaintable wedge
  x ~1330-1900, up to ~40 px wide): a logo across it gets sliced. Put centred logos elsewhere.
- `Car_decal` paints the halo (strip x 1430-1515, y 1460-2048) and the left-edge cluster incl.
  the left mirror (x 0-260, y 780-1000) black. They ARE paintable: lift `Car_decal` there
  to colour them (neonhornet v1: orange/black halo bands and pink mirrors worked in-sim).
- 3D parts over paint: front and rear suspension arms cross the nose side (cols 7-10) and the
  engine cover side; the halo and mirrors sit over the cockpit rim; exposed engine/gearbox and
  the rain light under the rear wing.
- iRacing draws the number on the nose (cols 5-6) and on the outer face of both rear-wing
  endplates: leave those clear.

## Seams (tools/seams.py, LIVERY_GUIDE 4b)

Seam ruler built: `seams.tga` (64 panels, codes in `seams_sheet.png`).
Readings in `seams.json`: none yet. Add each seam read in-sim below (which seam, screenshot, checked?).
