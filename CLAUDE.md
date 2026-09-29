# iRacing paints

Python-generated iRacing liveries. Each livery is its own project folder; car templates
and per-car knowledge are shared at the root.

```
<Car name>.psd          iRacing paint templates (2048x2048), downloaded by the user, repo root
LIVERY_GUIDE.md         everything learned so far: iRacing facts, spec values, placement lessons
cars/<car>/README.md    per-car sheet map + proven placements + gotchas (READ FIRST)
cars/<car>/grid_*.webp  in-sim screenshots of the labelled test grid; grid.tga = the grid paint
cars/bmw/projection/    grid-label correspondences per view (for projecting a reference image)
tools/grid.py           list PSD layers / write the labelled mapping grid for any car
tools/install_paint.ps1 install -Project <livery> -Car <car> [-Build N] [-Finish ...] (Windows; no args = help)
tools/labelproj.py      project a reference image onto the sheet from grid labels
example/livery.py       minimal working livery: start new liveries from this
logos/                  the user's logos (only logos/README.md is shared)
.venv/                  python env: pip install -r requirements.txt
```

Run scripts with the venv's python from inside the livery folder, e.g.
`cd example && ../.venv/bin/python livery.py bmw` (Windows: `..\.venv\Scripts\python livery.py bmw`).

@LIVERY_GUIDE.md

## Rules for Claude

- **Map a car before designing on it** (LIVERY_GUIDE section 4). If `cars/<car>/` doesn't exist,
  start with the grid.
- New livery = new folder `<name>/` with `livery.py`, `out/`, `reference/`, `final/` and a
  `CLAUDE.md` holding the design notes and a numbered version log (what changed, in-sim result).
- After every in-sim round, write what was learned down: per-car facts in `cars/<car>/README.md`,
  general lessons in `LIVERY_GUIDE.md`, version status in `<livery>/CLAUDE.md`.
- Ask the user for screenshot **file paths** and save useful screenshots into the repo.
- Never paint car numbers (iRacing draws them).
- The user may be new to coding: explain install steps plainly, give exact commands for their OS,
  and say which file to install and where.
