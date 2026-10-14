"""Seam map: make lines and graphics line up across panel seams the first time.

The grid tells you where each sheet cell lands on the car. It doesn't tell you which panel
(UV island) edges touch each other in 3D, and that's where stripes break. This tool maps the
seams, then lets a livery draw on an "unfolded" canvas where neighbouring panels are already
joined, so anything drawn across a seam continues on the other panel automatically.

    ../../.venv/bin/python ../../tools/seams.py ruler <car>      1. write the seam ruler paint
    ../../.venv/bin/python ../../tools/seams.py check <car>      3. write a stripe test for the seams read so far
    ../../.venv/bin/python ../../tools/seams.py codes <car> x,y  ruler code nearest a sheet point
                                                                 (F@x,y: on panel F's edges only)

1. `ruler` finds every panel on the template (from the Wire layer), gives it a code letter and
   paints a numbered ruler along all its edges: segments H0, H1, H2, ... every 64 sheet px,
   alternating dark/colour, with a tick at each segment start and the code underlined (so a
   rotated 6/9 still reads right). Writes cars/<car>/seams.tga (install: install_paint.ps1
   -Car <car> -Seams), seams_sheet.png (flat preview) and islands.npz (panels + edges, used by
   everything else; regenerate only together with the ruler).
2. In the sim, zoom on each seam you care about and screenshot it (save as
   cars/<car>/seam_<where>.webp). Read where the rulers meet: "the start tick of H12 is
   opposite the middle of B40" = ["H12", "B40.5"] (fraction = how far into the segment,
   going from its lower-numbered end). Two readings per seam minimum (both ends), one every
   ~150 px on curved or long seams. Write them to cars/<car>/seams.json:
       {"mirror_y": 1311.5,
        "seams": [{"name": "hood / front bumper", "pairs": [["H12", "B40.5"], ["H15", "B37"]]}]}
   Panels that don't touch but should carry a graphic over a gap (a 3D vent between fender and
   door): read the rulers across it at equal height and add "gap": true to that seam (positions
   are joined, the stripe angle is left free so the panels don't bend toward each other).
   With mirror_y set, a seam read on one side is copied to the mirrored panels automatically.
   A gap whose offset was measured with a vent ruler (constant-y bands: no rotation) goes in
   "shifts" instead: {"panels": ["X"], "onto": "A", "dy": [[1721, 74], [1900, 74]]} = X shows
   A's design 74 px further down the sheet (a short gap seam can't place a whole panel).
3. `check` unfolds every panel joined by a seam and paints continuous diagonal stripes across
   them (cars/<car>/seamcheck.tga). One in-sim look: stripes crossing a seam without a step
   or kink = that seam is right.

In a livery:
    sys.path.insert(0, "../../tools"); import seams
    car = seams.Car("bmw-m4-gt3")
    u = car.unfold("H")                      # root panel; everything seamed to it gets attached
    X, Y, on = u.field()                     # design coords of every sheet pixel on those panels
    sheet_rgba = u.pull(design_rgba)         # or draw on a design canvas and pull it onto the sheet
    right = car.flip(left_rgba)              # mirror a left-side layer (fixes twins off the reflection)
Design space = the root panel's own sheet coords, with the other panels warped to sit against
it along their seams. So draw on the hood as usual and a stripe that runs off its front edge
lands on the bumper exactly where the hood's edge meets it.
"""
import colorsys
import json
import math
import os
import re
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.interpolate import RBFInterpolator

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grid import REPO, SIZE, font, layer, open_psd  # noqa: E402

SEG = 64          # ruler segment length along an edge (sheet px)
BAND = 30         # ruler band width, inside the panel
MIN_AREA = 1500   # smaller panels get no ruler
LETTERS = "ABCDEFGHJKLMNPRSTUVWXYZ"   # no I, O, Q (read as 1, 0)


# ---------------------------------------------------------------- template / panels

def car_dir(key):
    return os.path.join(REPO, "cars", key)


def template_path(key):
    readme = open(os.path.join(car_dir(key), "README.md"), encoding="utf-8").read()
    m = re.search(r"Template: `([^`]+\.psd)`", readme)
    if not m:
        sys.exit(f"cars/{key}/README.md needs a line like: Template: `My Car.psd`")
    return m.group(1)


def psd_layer(psd, name):
    """A pixel layer (name not case sensitive) as a full-sheet RGBA array, or None."""
    lyr = next((l for l in psd.descendants() if l.kind == "pixel" and l.name.lower() == name), None)
    return None if lyr is None else np.array(layer(psd, lyr.name))


def find_islands(wire):
    """Label the panels (UV islands) drawn in the Wire layer.

    Inside a panel the mesh lines enclose small cells; outside is one huge cell. Holes in a
    panel (vent openings) are cells ringed only by the green outline. Touching panels are split
    along the green outline."""
    a = wire.astype(int)
    line = a[..., 3] > 10
    green = line & (a[..., 1] > a[..., 0] + 60)
    cells, n = ndimage.label(~line)
    area = np.bincount(cells.ravel())
    ring = ndimage.binary_dilation(~line, iterations=2) & line
    _, (iy, ix) = ndimage.distance_transform_edt(line, return_indices=True)
    near = cells[iy, ix][ring]
    gfrac = np.bincount(near, weights=green[ring], minlength=n + 1) / np.maximum(
        np.bincount(near, minlength=n + 1), 1)
    border = np.unique(np.r_[cells[0], cells[-1], cells[:, 0], cells[:, -1]])
    ok = (area < 60000) & (gfrac < 0.85)
    ok[0] = False
    ok[border] = False
    inside = ok[cells]
    inside = ndimage.binary_closing(inside | (line & ndimage.binary_dilation(inside, iterations=3)),
                                    iterations=2) & (inside | line)
    lab, n = ndimage.label(inside & ~ndimage.binary_dilation(green, iterations=1))
    # give the outline pixels back to the nearest panel
    _, (iy, ix) = ndimage.distance_transform_edt(lab == 0, return_indices=True)
    grown = lab[iy, ix]
    lab = np.where(inside, grown, 0)
    return lab


def contours_of(mask):
    """Closed edge polylines (outer edge first, then holes) as float arrays of (x, y)."""
    cs, hier = cv2.findContours(mask.astype(np.uint8), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    out = []
    for i, c in enumerate(cs):
        c = c[:, 0, :].astype(float)
        if len(c) < 3:
            continue
        # resample to ~1 px steps, lightly smoothed (pixel staircases -> clean tangents)
        closed = np.vstack([c, c[:1]])
        seg = np.hypot(*np.diff(closed, axis=0).T)
        s = np.r_[0, np.cumsum(seg)]
        L = s[-1]
        if L < 2 * SEG:
            continue
        t = np.arange(0, L, 1.0)
        pts = np.stack([np.interp(t, s, closed[:, 0]), np.interp(t, s, closed[:, 1])], 1)
        pts = ndimage.gaussian_filter1d(pts, 2, axis=0, mode="wrap")
        out.append((hier[0][i][3] != -1, pts))
    out.sort(key=lambda h: (h[0], -len(h[1])))
    return [p for _, p in out]


def codes(n):
    out = []
    for i in range(n):
        s = ""
        i += 1
        while i:
            i, r = divmod(i - 1, len(LETTERS))
            s = LETTERS[r] + s
        out.append(s)
    return out


# ---------------------------------------------------------------- ruler paint

def build_ruler(key):
    psd_name = template_path(key)
    psd = open_psd(psd_name)
    wire = psd_layer(psd, "wire")
    if wire is None:
        sys.exit("template has no Wire layer")
    mask = psd_layer(psd, "mask")
    paintable = np.ones((SIZE, SIZE), bool) if mask is None else mask[..., 3] < 128

    lab = find_islands(wire)
    n = lab.max()
    area = np.bincount(lab.ravel(), minlength=n + 1)
    pfrac = np.bincount(lab.ravel(), weights=paintable.ravel(), minlength=n + 1) / np.maximum(area, 1)
    keep = [i for i in range(1, n + 1) if area[i] >= MIN_AREA and pfrac[i] > 0.3]
    keep.sort(key=lambda i: -area[i])
    names = codes(len(keep))

    labels = np.zeros((SIZE, SIZE), np.uint16)
    edges, starts, info = [], [], {}
    img = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    arr = np.array(img)
    seg_img = np.full((SIZE, SIZE), -1, np.int32)     # ruler segment id per band pixel
    seg_col = []
    tick_marks = []
    texts = []
    for k, (li, code) in enumerate(zip(keep, names)):
        m = lab == li
        labels[m] = k + 1
        hue = (k * 0.618) % 1
        pale = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.18, 1))
        strong = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 0.9, 0.85))
        arr[m] = pale
        cs = contours_of(m)
        first = 0
        panel_edges = []
        for pts in cs:
            L = len(pts)
            nseg = math.ceil(L / SEG)
            panel_edges.append((len(edges), first, nseg))
            edges.append(pts)
            starts.append(first)
            # band pixels -> nearest edge point -> segment number
            for j in range(nseg):
                seg_col.append(strong if j % 2 else (25, 25, 25))
            first += nseg
        # assign band pixels of this panel to the nearest edge point of any of its edges
        if cs:
            allp = np.vstack(cs)
            segn = np.concatenate([starts[e] + np.arange(len(edges[e])) // SEG for e, _, _ in panel_edges])
            ring = np.zeros((SIZE, SIZE), bool)
            ip = np.clip(np.round(allp).astype(int), 0, SIZE - 1)
            ring[ip[:, 1], ip[:, 0]] = True
            idx = np.full((SIZE, SIZE), -1, np.int64)
            idx[ip[:, 1], ip[:, 0]] = np.arange(len(allp))
            d, (iy, ix) = ndimage.distance_transform_edt(~ring, return_indices=True)
            band = m & (d < BAND)
            base = len(seg_col) - first
            seg_img[band] = base + segn[idx[iy[band], ix[band]]]
            for e, f0, nseg in panel_edges:
                pts = edges[e]
                for j in range(nseg):
                    a0 = j * SEG
                    p = pts[a0]
                    tng = pts[min(a0 + 3, len(pts) - 1)] - pts[max(a0 - 3, 0)]
                    sid = base + f0 + j
                    tick_marks.append((p, tng, m, (sid, sid - 1 if j else sid + nseg - 1)))
                    mid = min(a0 + SEG // 2, len(pts) - 1)
                    if mid - a0 >= 20:
                        tm = pts[min(mid + 3, len(pts) - 1)] - pts[max(mid - 3, 0)]
                        texts.append((pts[mid], tm, f"{code}{f0 + j}", m,
                                      (255, 255, 255) if j % 2 == 0 else (0, 0, 0), (sid,)))
        info[code] = {"label": k + 1, "area": int(area[li]),
                      "edges": [[e, f0, nseg] for e, f0, nseg in panel_edges],
                      "centre": [float(v) for v in np.argwhere(m).mean(0)[::-1]]}
    sel = seg_img >= 0
    cols = np.array(seg_col, np.uint8)
    arr[sel] = cols[seg_img[sel]]
    img = Image.fromarray(arr)
    d = ImageDraw.Draw(img)

    def paste_owned(tile, x0, y0, own):
        """Paste a tick/label tile, but only onto its own ruler segments (or off-ruler pixels):
        on thin strips the rulers of both edges meet and would print over each other."""
        x1, y1 = x0 + tile.width, y0 + tile.height
        cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x1, SIZE), min(y1, SIZE)
        if cx0 >= cx1 or cy0 >= cy1:
            return
        region = seg_img[cy0:cy1, cx0:cx1]
        keep = np.isin(region, own) | (region < 0)
        a = np.array(tile)
        sub = a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0].copy()
        sub[..., 3] = sub[..., 3] * keep
        img.paste(Image.fromarray(sub), (cx0, cy0), Image.fromarray(sub))

    def normal_into(p, tng, m):
        t = tng / (np.hypot(*tng) or 1)
        nrm = np.array([-t[1], t[0]])
        qi = np.clip(np.round(p + nrm * 6).astype(int), 0, SIZE - 1)
        return t, (nrm if m[qi[1], qi[0]] else -nrm)

    # ticks: a red line across the band at each segment start
    for p, tng, m, own in tick_marks:
        _, nrm = normal_into(p, tng, m)
        a, b = p - nrm * 2, p + nrm * (BAND + 6)
        x0, y0 = int(min(a[0], b[0])) - 4, int(min(a[1], b[1])) - 4
        tile = Image.new("RGBA", (int(abs(a[0] - b[0])) + 9, int(abs(a[1] - b[1])) + 9))
        ImageDraw.Draw(tile).line([(a[0] - x0, a[1] - y0), (b[0] - x0, b[1] - y0)],
                                  fill=(255, 40, 40, 255), width=4)
        paste_owned(tile, x0, y0, own)

    # segment codes, rotated along the edge, underlined
    fonts = {}
    for p, tng, text, m, colr, own in texts:
        t, nrm = normal_into(p, tng, m)
        # how deep this segment's own band is here (thin strips: less than BAND)
        depth = 1
        while depth < BAND:
            q = np.clip(np.round(p + nrm * depth).astype(int), 0, SIZE - 1)
            if seg_img[q[1], q[0]] not in own:
                break
            depth += 1
        size = max(9, min(17, depth - 6))
        fnt = fonts.setdefault(size, font(size))
        c = p + nrm * (depth / 2)
        tw = int(d.textlength(text, font=fnt)) + 4
        h = size + 7
        tile = Image.new("RGBA", (tw, h))
        td = ImageDraw.Draw(tile)
        td.text((2, 0), text, font=fnt, fill=colr + (255,))
        td.line((2, h - 3, tw - 2, h - 3), fill=colr + (255,), width=2)
        ang = -math.degrees(math.atan2(t[1], t[0]))
        tile = tile.rotate(ang, expand=True, resample=Image.BICUBIC)
        paste_owned(tile, int(c[0] - tile.width / 2), int(c[1] - tile.height / 2), own)

    # big panel code in the middle of each panel
    for code, v in info.items():
        m = labels == v["label"]
        dist = ndimage.distance_transform_edt(m)
        y, x = np.unravel_index(np.argmax(dist), dist.shape)
        r = dist[y, x]
        if r < 12:
            continue
        size = int(min(90, max(14, r * 0.9)))
        f = font(size)
        d.text((x, y), code, font=f, fill=(0, 0, 0), anchor="mm")

    out = car_dir(key)
    img.save(os.path.join(out, "seams.tga"))
    prev = img.convert("RGBA")
    if mask is not None:
        prev.alpha_composite(Image.fromarray(mask))
    prev.convert("RGB").save(os.path.join(out, "seams_sheet.png"))
    np.savez_compressed(os.path.join(out, "islands.npz"), labels=labels,
                        info=json.dumps({"psd": psd_name, "seg": SEG, "panels": info}),
                        **{f"edge{i}": e.astype(np.float32) for i, e in enumerate(edges)})
    print(f"{len(info)} panels. wrote cars/{key}/seams.tga, seams_sheet.png, islands.npz")


# ---------------------------------------------------------------- seam data

class Car:
    def __init__(self, key):
        self.key = key
        z = np.load(os.path.join(car_dir(key), "islands.npz"))
        meta = json.loads(str(z["info"]))
        self.seg = meta["seg"]
        self.panels = meta["panels"]
        self.labels = z["labels"]
        self.edges = [z[f"edge{i}"].astype(float) for i in range(sum(1 for k in z.files if k.startswith("edge")))]
        self.code_of = {v["label"]: c for c, v in self.panels.items()}
        p = os.path.join(car_dir(key), "seams.json")
        self.cfg = json.load(open(p)) if os.path.exists(p) else {"seams": []}
        self.mirror_y = self.cfg.get("mirror_y")
        self.loose = set()     # panel pairs read across a gap (3D vent): positions pinned, angles not
        self.seams = self._merge(self._resolve())
        self.shifts = self._shifts()

    # -- panels
    def mask(self, code, grow=0):
        m = self.labels == self.panels[code]["label"]
        return ndimage.binary_dilation(m, iterations=grow) if grow else m

    def panel_at(self, x, y, reach=8):
        x, y = int(round(x)), int(round(y))
        y0, x0 = max(0, y - reach), max(0, x - reach)
        win = self.labels[y0:y + reach + 1, x0:x + reach + 1]
        if not win.any():
            return None
        yy, xx = np.nonzero(win)
        j = np.argmin((yy + y0 - y) ** 2 + (xx + x0 - x) ** 2)
        return self.code_of[int(win[yy[j], xx[j]])]

    # -- ruler codes <-> sheet points
    def _locate(self, ref):
        m = re.fullmatch(r"([A-Z]+)(\d+(?:\.\d+)?)", ref.strip())
        if not m:
            raise ValueError(f"bad ruler code {ref!r} (want e.g. H12 or H12.5)")
        code, s = m.group(1), float(m.group(2))
        for e, f0, nseg in self.panels[code]["edges"]:
            if f0 <= s < f0 + nseg or (s == f0 + nseg):
                return code, e, (s - f0) * self.seg
        raise ValueError(f"{ref}: panel {code} has segments 0..{sum(n for _, _, n in self.panels[code]['edges']) - 1}")

    def point(self, ref):
        _, e, arc = self._locate(ref)
        pts = self.edges[e]
        return _at(pts, arc)

    def code_at(self, x, y, panel=None):
        best = None
        for code, v in self.panels.items():
            if panel and code != panel:
                continue
            for e, f0, nseg in v["edges"]:
                pts = self.edges[e]
                d = np.hypot(pts[:, 0] - x, pts[:, 1] - y)
                i = int(np.argmin(d))
                if best is None or d[i] < best[0]:
                    best = (d[i], f"{code}{f0 + i / self.seg:.2f}")
        return self.panel_at(x, y), best[1] if best else None

    def _resolve(self):
        """seams.json readings -> dense matching point lists [(panelA, panelB, ptsA, ptsB)]."""
        out = []
        for s in self.cfg.get("seams", []):
            locs = [(self._locate(a), self._locate(b)) for a, b in s["pairs"]]
            pa, pb = locs[0][0][0], locs[0][1][0]
            if any(la[0] != pa or lb[0] != pb for la, lb in locs):
                raise ValueError(f"seam {s.get('name')}: every pair must be the same two panels")
            A, B = [], []
            if len(locs) == 1:
                A.append(_at(self.edges[locs[0][0][1]], locs[0][0][2]))
                B.append(_at(self.edges[locs[0][1][1]], locs[0][1][2]))
            for (la, lb), (na, nb) in zip(locs, locs[1:]):
                sa = _walk(self.edges[la[1]], la[2], na[2])
                sb = _walk(self.edges[lb[1]], lb[2], nb[2])
                k = max(2, int(max(_len(sa), _len(sb)) / 4))
                A.extend(_resample(sa, k))
                B.extend(_resample(sb, k))
            A, B = np.array(A), np.array(B)
            out.append((pa, pb, A, B, s.get("name", f"{pa}/{pb}")))
            if s.get("gap"):
                self.loose.add(frozenset((pa, pb)))
            if self.mirror_y is not None:
                mA, mB = A.copy(), B.copy()
                mA[:, 1] = 2 * self.mirror_y - mA[:, 1]
                mB[:, 1] = 2 * self.mirror_y - mB[:, 1]
                qa, qb = self.mirror_of(pa), self.mirror_of(pb)
                if qa and qb and self._on_edge(qa, mA, 6) and self._on_edge(qb, mB, 6):
                    if (qa, qb) == (pa, pb):   # both panels cross the mirror line: same seam, other half
                        # only where the readings don't already cover it: two slightly different
                        # matches a pixel apart make the spline zig-zag (BMW roof/banner v3)
                        new = np.array([np.hypot(*(A - q).T).min() > 8 for q in mA])
                        if new.any():
                            out[-1] = (pa, pb, np.vstack([A, mA[new]]), np.vstack([B, mB[new]]), out[-1][4])
                    else:
                        out.append((qa, qb, mA, mB, s.get("name", "") + " (mirrored)"))
                        if s.get("gap"):
                            self.loose.add(frozenset((qa, qb)))
        return out

    def twin(self, code):
        """(other, dx, dy): the panel `code` mirrors onto and how far it sits off the exact
        reflection about mirror_y: pixel (x, y) of `code` <-> (x + dx, 2*mirror_y - y + dy) of
        `other`. Best overlap over dy -40..40, dx -12..12; None if nothing overlaps well. Most
        twins sit within a few px; the BMW right front fender side (Y) is 27 px off its left twin X."""
        cache = self.__dict__.setdefault("_twin", {})
        if code not in cache:
            ys, xs = np.nonzero(self.mask(code))
            ys, xs = ys[::5], xs[::5]
            m2, best = 2 * self.mirror_y, None
            for dx in range(-12, 13, 2):
                for dy in range(-40, 41):
                    ry, rx = np.round(m2 - ys + dy).astype(int), xs + dx
                    ok = (ry >= 0) & (ry < SIZE) & (rx >= 0) & (rx < SIZE)
                    hit = self.labels[ry[ok], rx[ok]]
                    hit = hit[hit > 0]
                    if not len(hit):
                        continue
                    lab = np.bincount(hit).argmax()
                    inter = (hit == lab).sum() * 5
                    other = self.code_of[int(lab)]
                    iou = inter / (len(ys) * 5 + self.panels[other]["area"] - inter)
                    if best is None or iou > best[0]:
                        best = (iou, other, dx, dy)
            cache[code] = best[1:] if best and best[0] > 0.8 else None
        return cache[code]

    def flip(self, rgba, tol=6, bleed=24):
        """Mirror a design layer (HxWx4) about mirror_y, panel by panel: a plain flip, except that
        panels whose twin sits more than `tol` px off the exact reflection are resampled from
        their twin at the measured offset (a plain flip put the BMW right fender art 27 px off,
        with an unpainted strip along one edge). Bleeds `bleed` px past those panels' edges."""
        m2 = 2 * self.mirror_y
        src = np.round(m2 - np.arange(SIZE)).astype(int)
        out = np.zeros_like(rgba)
        ok = (src >= 0) & (src < SIZE)
        out[ok] = rgba[src[ok]]
        f = rgba.astype(np.float32)
        al = f[..., 3] / 255
        for c, v in self.panels.items():
            t = self.twin(c) if v["area"] >= MIN_AREA else None
            if not t or t[0] == c or max(abs(t[1]), abs(t[2])) <= tol:
                continue
            # pixels of c's twin take c's design: twin (x, y) <- c (x - dx, m2 - y + dy)
            other, dx, dy = t
            own = self.mask(other)
            reach = ndimage.binary_dilation(own, iterations=bleed) & ~((self.labels != 0) & ~own)
            ys, xs = np.nonzero(reach)
            gx, gy = (xs - dx).astype(np.float32), (m2 - ys + dy).astype(np.float32)
            A = ndimage.map_coordinates(al, [gy, gx], order=1, mode="constant")
            for k in range(3):                     # premultiplied: no dark fringes on the edges
                val = ndimage.map_coordinates(f[..., k] * al, [gy, gx], order=1, mode="constant")
                out[ys, xs, k] = np.clip(val / np.maximum(A, 1e-4), 0, 255)
            out[ys, xs, 3] = np.clip(A * 255, 0, 255)
        return out

    def _shifts(self):
        """seams.json "shifts": panels across a 3D gap that copy a neighbour's design at a measured
        sheet offset (vent ruler: "the door sits 74 px lower than the fender at the same height").
            {"panels": ["X", "N"], "onto": "A", "dy": [[1600, 106], [1712, 78], [1900, 74]]}
        = pixel (x, y) on X or N shows the design of A at (x, y + dy(y)), dy linear between the
        given sheet y values, flat outside. Mirrored panels get the reflected rule."""
        out = []
        for s in self.cfg.get("shifts", []):
            ys, ds = map(np.array, zip(*s["dy"]))

            def fn(p, ys=ys, ds=ds):
                return np.stack([p[:, 0], p[:, 1] + np.interp(p[:, 1], ys, ds)], 1)
            for c in s["panels"]:
                out.append((c, s["onto"], fn))
                if self.mirror_y is None:
                    continue
                tc, to = self.twin(c), self.twin(s["onto"])
                if not (tc and to) or tc[0] == c:
                    continue
                # twin pixel -> c (undo c's mirror offset) -> onto -> onto's twin (its offset)
                def mfn(p, fn=fn, tc=tc, to=to, m2=2 * self.mirror_y):
                    q = fn(np.stack([p[:, 0] - tc[1], m2 - p[:, 1] + tc[2]], 1))
                    return np.stack([q[:, 0] + to[1], m2 - q[:, 1] + to[2]], 1)
                out.append((tc[0], to[0], mfn))
        return out

    @staticmethod
    def _merge(seams):
        """One entry per pair of panels (a seam can be read in pieces: left half, right corner)."""
        out = {}
        for pa, pb, A, B, name in seams:
            key = (pa, pb) if (pa, pb) in out or (pb, pa) not in out else (pb, pa)
            if key != (pa, pb):
                A, B = B, A
            if key in out:
                qa, qb, QA, QB, qn = out[key]
                keep = np.array([np.hypot(*(QA - q).T).min() > 8 for q in A])
                out[key] = (qa, qb, np.vstack([QA, A[keep]]), np.vstack([QB, B[keep]]), qn + " + " + name)
            else:
                out[key] = (key[0], key[1], A, B, name)
        return list(out.values())

    def mirror_of(self, code):
        """The panel that is `code` reflected about mirror_y (itself for panels across the
        line), by overlap of the reflected shape; None if nothing matches well. Seam points
        can't decide it: neighbouring panels' edges can sit a few px apart on the sheet."""
        cache = self.__dict__.setdefault("_mirror", {})
        if code not in cache:
            m = self.mask(code)
            ys, xs = np.nonzero(m)
            ry = np.round(2 * self.mirror_y - ys).astype(int)
            ok = (ry >= 0) & (ry < SIZE)
            hit = self.labels[ry[ok], xs[ok]]
            hit = hit[hit > 0]
            best = None
            if len(hit):
                lab = np.bincount(hit).argmax()
                other = self.code_of[int(lab)]
                inter = (hit == lab).sum()
                iou = inter / (len(ys) + self.panels[other]["area"] - inter)
                best = other if iou > 0.6 else None
            cache[code] = best
        return cache[code]

    def _on_edge(self, code, pts, tol=4.0):
        """True if the points lie along panel `code`'s edges (a mirrored seam is only copied
        where the template really is symmetric)."""
        e = np.vstack([self.edges[i] for i, _, _ in self.panels[code]["edges"]])
        d = np.array([np.hypot(e[:, 0] - x, e[:, 1] - y).min() for x, y in pts[::5]])
        return np.median(d) < tol

    def graph(self):
        g = {}
        for pa, pb, A, B, _ in self.seams:
            g.setdefault(pa, []).append((pb, B, A))   # to go pb -> pa: B points map to A points
            g.setdefault(pb, []).append((pa, A, B))
        return g

    def unfold(self, root, only=None):
        return Unfold(self, root, only)


def _at(pts, arc):
    L = len(pts)
    i = int(math.floor(arc)) % L
    f = arc - math.floor(arc)
    return pts[i] * (1 - f) + pts[(i + 1) % L] * f


def _walk(pts, a0, a1):
    """Edge points from arc a0 to a1 along a closed edge, the shorter way round."""
    L = len(pts)
    fwd = (a1 - a0) % L
    step = 1 if fwd <= L / 2 else -1
    n = int(fwd if step == 1 else L - fwd)
    arcs = [a0 + step * t for t in range(n + 1)] + [a1]
    return np.array([_at(pts, a % L) for a in arcs])


def _len(p):
    return float(np.hypot(*np.diff(p, axis=0).T).sum()) if len(p) > 1 else 0.0


def _resample(p, k):
    """k points spread evenly between two readings. Progress is measured along the straight
    line between them, not along the edge: a small notch in one edge (the BMW bumper next to
    the roundel) doesn't touch the other panel and would otherwise stretch the match 2:1."""
    d = p[-1] - p[0]
    L = np.hypot(*d)
    if L < 1:
        return [p[0]] * k
    t = np.maximum.accumulate(((p - p[0]) @ d) / L ** 2)
    keep = np.r_[True, np.diff(t) > 1e-6]
    t, q = t[keep], p[keep]
    tt = np.linspace(t[0], t[-1], k)
    return list(np.stack([np.interp(tt, t, q[:, 0]), np.interp(tt, t, q[:, 1])], 1))


def _normals(pts, mask, inward):
    """Unit edge normals at seam points (local PCA of the neighbouring seam points), pointing
    into `mask` (inward) or away from it. NaN where the side can't be told."""
    out = np.full(pts.shape, np.nan)
    for i, p in enumerate(pts):
        nb = pts[np.hypot(*(pts - p).T) < 32]
        if len(nb) < 3:
            continue
        w, v = np.linalg.eigh(np.cov((nb - nb.mean(0)).T))
        n = v[:, 0]                      # smallest spread = across the edge
        a = np.clip(np.round(p + n * 5).astype(int), 0, SIZE - 1)
        b = np.clip(np.round(p - n * 5).astype(int), 0, SIZE - 1)
        ia, ib = mask[a[1], a[0]], mask[b[1], b[0]]
        if ia == ib:
            continue
        into = n if ia else -n
        out[i] = into if inward else -into
    return out


def _similarity_w(src, dst, reflect, w):
    """Weighted least-squares similarity src -> dst (Umeyama with point weights)."""
    w = w / w.sum()
    ms, md = (src * w[:, None]).sum(0), (dst * w[:, None]).sum(0)
    s0, d0 = src - ms, dst - md
    U, S, Vt = np.linalg.svd((d0 * w[:, None]).T @ s0)
    sgn = np.sign(np.linalg.det(U) * np.linalg.det(Vt))
    D = np.diag([1, -sgn if reflect else sgn])
    R = U @ D @ Vt
    sc = (S * np.diag(D)).sum() / (w * (s0 ** 2).sum(1)).sum()
    return lambda p: (p - ms) @ (sc * R).T + md


def _similarity(src, dst, reflect):
    """Least-squares similarity src -> dst (Umeyama), optionally with a reflection."""
    ms, md = src.mean(0), dst.mean(0)
    s0, d0 = src - ms, dst - md
    U, S, Vt = np.linalg.svd(d0.T @ s0)
    sgn = np.sign(np.linalg.det(U) * np.linalg.det(Vt))
    D = np.diag([1, -sgn if reflect else sgn])
    R = U @ D @ Vt
    sc = (S * np.diag(D)).sum() / (s0 ** 2).sum()
    T = lambda p: (p - ms) @ (sc * R).T + md  # noqa: E731
    T.scale = sc
    return T


# ---------------------------------------------------------------- unfolding

class Unfold:
    """Panels joined along their seams around a root panel.

    Each attached panel gets a smooth warp (thin-plate spline) from its sheet coords straight
    into design coords (the root's sheet coords), pinned to the seam readings along its seams
    and to the best-fit similarity transform away from them. Panels are reached along a
    spanning tree, then refitted to EVERY placed neighbour they share a seam with, so a panel
    between three others (a bumper under the nose and both fenders) follows all of them, not
    just the one it was reached by (Porsche GT3 R: the bumper corners followed only the nose
    and their stripes turned vertical under the headlights). Seams whose readings disagree
    can still step a little; check in-sim."""

    def __init__(self, car, root, only=None):
        self.car, self.root = car, root
        self.parent, self.fit = {root: None}, {}
        g = car.graph()
        self._g = g
        order, queue = [], [root]
        while queue:
            p = queue.pop(0)
            for c, cpts, ppts in g.get(p, []):
                if c in self.parent or (only and c not in only):
                    continue
                self.parent[c] = p
                # every panel already placed that c has readings with (a big panel reached by one
                # short seam gets its rotation and scale from all of them: GT3 R side via both fenders)
                nb = [(n, cp, npp) for n, npp, cp in g.get(c, [])
                      if n == self.root or n in self.fit]
                self.fit[c] = self._fit(c, nb, p)
                order.append(c)
                queue.append(c)
        # second pass: every seam to a placed panel pins the warp
        for c in order:
            # placed neighbours, but not the panels hanging off c (they were placed from c's
            # first fit: refitting c to them goes round in a circle and folded the GT3 R fender)
            nb = [(n, cpts, npts) for n, npts, cpts in g.get(c, [])
                  if n in self.parent and not self._below(n, c)]
            off = max(np.hypot(*(self.to_design(c, cp) - self.to_design(n, npp)).T).max()
                      for n, cp, npp in nb)
            if len(nb) > 1 and off > 3:
                self.fit[c] = self._fit(c, nb, self.parent[c])
        # panels across a gap that copy a neighbour at a measured offset (only if no seam placed them)
        for c, onto, dy in car.shifts:
            if c in self.parent or onto not in self.parent or (only and c not in only):
                continue
            self.parent[c] = onto
            ys, xs = np.nonzero(car.mask(c))
            y0, y1, x0, x1 = ys.min() - 8, ys.max() + 9, xs.min() - 8, xs.max() + 9
            cy, cx = np.mgrid[y0:y1 + 4:4, x0:x1 + 4:4].astype(float)
            q = self._extrapolate(onto, dy(np.stack([cx.ravel(), cy.ravel()], 1))).reshape(cy.shape + (2,))
            self.fit[c] = (x0, y0, q)
        self.skipped = []

    def _extrapolate(self, c, pts):
        """Design coords of sheet points that may lie OFF panel c (a shifted fender maps into the
        vent in front of the door): from the nearest point 6 px inside c, linearly with the warp's
        local Jacobian there (to_design alone clamps at the panel's edge and squashes the shape)."""
        inner = ndimage.binary_erosion(self.car.mask(c), iterations=6)
        _, idx = ndimage.distance_transform_edt(~inner, return_indices=True)
        ip = np.clip(np.round(pts).astype(int), 0, SIZE - 1)
        pin = np.stack([idx[1][ip[:, 1], ip[:, 0]], idx[0][ip[:, 1], ip[:, 0]]], 1).astype(float)
        d0 = self.to_design(c, pin)
        jx = (self.to_design(c, pin + [3, 0]) - self.to_design(c, pin - [3, 0])) / 6
        jy = (self.to_design(c, pin + [0, 3]) - self.to_design(c, pin - [0, 3])) / 6
        v = pts - pin
        return d0 + jx * v[:, :1] + jy * v[:, 1:]

    def _below(self, n, c):
        """True if panel n hangs off c in the tree (c is one of its ancestors)."""
        while n is not None:
            n = self.parent[n]
            if n == c:
                return True
        return False

    def _fit(self, c, nbrs, p):
        """Warp panel c -> design coords from its seams to placed panels nbrs
        [(n, c_pts, n_pts)]; p = the tree parent (decides whether the panel is flipped)."""
        cm = self.car.mask(c)
        ys, xs = np.nonzero(cm)
        cs_all, ds_all, out_all = [], [], []
        for n, cpts, npts in nbrs:
            key = np.round(cpts, 1)
            _, u = np.unique(key, axis=0, return_index=True)
            cs, ns = cpts[u], npts[u]
            D = self.to_design(n, ns)
            # direction straight out of the neighbour, in design coords: step a little inside
            # n along its edge normal and look where that lands
            nn = _normals(ns, self.car.mask(n), inward=False)
            ok = ~np.isnan(nn).any(1)
            out = np.full(ns.shape, np.nan)
            if ok.any() and frozenset((c, n)) not in self.car.loose:
                Din = self.to_design(n, ns[ok] - nn[ok] * 6)
                v = D[ok] - Din
                out[ok] = v / np.maximum(np.hypot(*v.T), 1e-6)[:, None]
            # no angle pin next to another seam: where two seams meet at a corner their
            # directions disagree and the pins fold the warp (GT3 R bumper corners)
            others = [x[1] for x in nbrs if x[0] != n]
            if others:
                o = np.vstack(others)
                near = np.array([np.hypot(*(o - q).T).min() < 150 for q in cs])
                out[near] = np.nan
            cs_all.append(cs)
            ds_all.append(D)
            out_all.append(out)
        cs, ds, outd = np.vstack(cs_all), np.vstack(ds_all), np.vstack(out_all)
        dseam = np.full((SIZE, SIZE), True)
        ip = np.clip(np.round(cs).astype(int), 0, SIZE - 1)
        dseam[ip[:, 1], ip[:, 0]] = False
        dist = ndimage.distance_transform_edt(dseam)
        step = 24
        gy, gx = np.mgrid[0:SIZE:step, 0:SIZE:step]
        far = cm[gy, gx] & (dist[gy, gx] > 120)
        anchors = np.stack([gx[far], gy[far]], 1).astype(float)
        # flipped or not: decided against the tree parent's own sheet, as before
        p_cs = [x for x in nbrs if x[0] == p][0]
        pm = self.car.mask(p, grow=4)
        sample = np.stack([xs[::97], ys[::97]], 1).astype(float)
        best = None
        for refl in (False, True):
            Tp = _similarity(p_cs[1], p_cs[2], refl)
            q = np.round(Tp(sample)).astype(int)
            okq = (q >= 0).all(1) & (q < SIZE).all(1)
            overlap = pm[q[okq, 1], q[okq, 0]].mean() if okq.any() else 0
            err = np.hypot(*(Tp(p_cs[1]) - p_cs[2]).T).mean()
            score = overlap * 1000 + err
            if best is None or score < best[0]:
                best = (score, refl)
        T = _similarity(cs, ds, best[1])
        # Angle continuity: pinning positions alone let the spline shear the child right at the
        # seam (BMW bumper: 4:1 stretch, stripes kinked and bent). UV unwraps are close to
        # angle-preserving, so the direction straight into the child must continue the
        # direction straight out of the neighbour, at the seam's scale: pin points stepped
        # inward along the child's edge normal to points stepped outward from the neighbour.
        nc = _normals(cs, cm, inward=True)
        ok = ~(np.isnan(nc).any(1) | np.isnan(outd).any(1))
        extra_s, extra_d = [], []
        for dd in (12, 28, 48, 72):
            extra_s.append(cs[ok] + nc[ok] * dd)
            extra_d.append(ds[ok] + outd[ok] * dd * T.scale)
        # away from the seams: follow the NEAREST seams' similarity (weighted by distance), not
        # one fit for the whole panel. A strip seamed to three panels at different angles (GT3 R
        # bumper: nose + two fender corners) otherwise turns in an S between the seams.
        if len(anchors) and len(nbrs) > 1:
            # seams read across a gap are too short and loose to set a local rotation
            firm = np.concatenate([np.full(len(x[1][np.unique(np.round(x[1], 1), axis=0, return_index=True)[1]]),
                                           frozenset((c, x[0])) not in self.car.loose) for x in nbrs])
            if not firm.any():
                firm[:] = True
            at = np.array([_similarity_w(cs[firm], ds[firm], best[1],
                                         np.exp(-(np.hypot(*(cs[firm] - a).T) / 250) ** 2) + 0.2)(a[None])[0]
                           for a in anchors])
        else:
            at = T(anchors) if len(anchors) else anchors
        src = np.vstack([cs] + extra_s + [anchors])
        dst = np.vstack([ds] + extra_d + ([at] if len(anchors) else []))
        rbf = RBFInterpolator(src, dst, kernel="thin_plate_spline", smoothing=1.0)
        # evaluate on a coarse grid over the panel (+margin), interpolate per pixel later
        y0, y1, x0, x1 = ys.min() - 8, ys.max() + 9, xs.min() - 8, xs.max() + 9
        cy, cx = np.mgrid[y0:y1 + 4:4, x0:x1 + 4:4]
        q = rbf(np.stack([cx.ravel(), cy.ravel()], 1).astype(float)).reshape(cy.shape + (2,))
        return (x0, y0, q)

    def to_parent(self, c, pts):
        x0, y0, q = self.fit[c]
        gx, gy = (pts[:, 0] - x0) / 4, (pts[:, 1] - y0) / 4
        return np.stack([ndimage.map_coordinates(q[..., k], [gy, gx], order=1, mode="nearest")
                         for k in range(2)], 1)

    def to_design(self, c, pts):
        """Sheet points on panel c -> design coords (the root panel's sheet coords)."""
        pts = np.asarray(pts, float)
        return pts if c == self.root else self.to_parent(c, pts)

    def field(self, grow=4):
        """(X, Y, on): design coords for every sheet pixel on the unfolded panels (NaN off them).
        Panels are grown by `grow` px so colours bleed past the edges like a normal paint."""
        X = np.full((SIZE, SIZE), np.nan, np.float32)
        Y = np.full((SIZE, SIZE), np.nan, np.float32)
        labs = {self.car.panels[c]["label"]: c for c in self.parent}
        lab = self.car.labels
        _, (iy, ix) = ndimage.distance_transform_edt(lab == 0, return_indices=True)
        d = ndimage.distance_transform_edt(lab == 0)
        near = np.where(d <= grow, lab[iy, ix], 0)
        for L, c in labs.items():
            ys, xs = np.nonzero(near == L)
            p = self.to_design(c, np.stack([xs, ys], 1).astype(float))
            X[ys, xs], Y[ys, xs] = p[:, 0], p[:, 1]
        return X, Y, ~np.isnan(X)

    def pull(self, design, origin=(0, 0), scale=1.0):
        """Sample a design image (drawn in design coords: pixel = (x - ox) * scale) onto the
        sheet. Returns a 2048x2048 RGBA image, transparent off the unfolded panels."""
        X, Y, on = self.field()
        src = np.asarray(design.convert("RGBA"), np.float32)
        gx = (X[on] - origin[0]) * scale
        gy = (Y[on] - origin[1]) * scale
        out = np.zeros((SIZE, SIZE, 4), np.float32)
        for k in range(4):
            out[..., k][on] = ndimage.map_coordinates(src[..., k], [gy, gx], order=1, mode="constant")
        return Image.fromarray(out.clip(0, 255).astype(np.uint8), "RGBA")


# ---------------------------------------------------------------- stripe check

def build_check(key):
    car = Car(key)
    if not car.seams:
        sys.exit(f"no seams in cars/{key}/seams.json yet: read them off the ruler first")
    arr = np.full((SIZE, SIZE, 3), 200, np.uint8)
    arr[car.labels > 0] = (235, 235, 235)
    done = set()
    notes = []
    # one unfold per group of connected panels, rooted at its best-connected panel (a big
    # panel hanging off one short seam makes a poor root: everything else chains through it)
    g = car.graph()
    for pa, pb, *_ in car.seams:
        if pa in done:
            continue
        group = _component(car, pa)
        # most seam length read (GT3 R: the side panel has as many neighbours as the hood, but
        # through two short readings across the fender vents; rooted there the front came out garbled)
        root = max(group, key=lambda c: (round(sum(_len(own) for _, _, own in g.get(c, [])) / 100),
                                         car.panels[c]["area"]))
        u = car.unfold(root)
        X, Y, on = u.field()
        for c in set(u.parent) & done:   # a shifted panel an earlier group already painted
            on &= ~car.mask(c, grow=4)
        done |= set(u.parent)
        # black stripes at 30 deg + red stripes at -60 deg: a step or a kink at a seam shows in both
        s1 = ((X * math.cos(0.52) + Y * math.sin(0.52)) % 72) < 22
        s2 = ((X * math.cos(-1.05) + Y * math.sin(-1.05)) % 150) < 10
        arr[on] = (255, 255, 255)
        arr[on & s1] = (20, 20, 20)
        arr[on & s2] = (230, 30, 30)
        notes.append(f"root {root}: " + ", ".join(f"{c}->{p}" for c, p in u.parent.items() if p))
        for pa2, pb2, name in u.skipped:
            notes.append(f"  not on the tree (may step): {name}")
    Image.fromarray(arr).save(os.path.join(car_dir(key), "seamcheck.tga"))
    print("\n".join(notes))
    print(f"wrote cars/{key}/seamcheck.tga (install: install_paint.ps1 -Car {key} -SeamCheck)")


def _component(car, start):
    g = car.graph()
    seen, todo = {start}, [start]
    while todo:
        for c, *_ in g.get(todo.pop(), []):
            if c not in seen:
                seen.add(c)
                todo.append(c)
    return seen


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        sys.exit(__doc__)
    cmd, key = args[0], args[1]
    if cmd == "ruler":
        build_ruler(key)
    elif cmd == "check":
        build_check(key)
    elif cmd == "codes":
        car = Car(key)
        for a in args[2:]:
            panel, _, xy = a.rpartition("@")
            x, y = map(float, xy.split(","))
            print(a, "->", car.code_at(x, y, panel or None))
    else:
        sys.exit(__doc__)
