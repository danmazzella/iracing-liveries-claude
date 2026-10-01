# iRacing paints

Python-generated iRacing liveries. Each livery is its own folder under `liveries/`; car
templates (`psd/`), per-car knowledge (`cars/`) and tools (`tools/`) are shared.

```
psd/<Car name>.psd      iRacing paint templates (2048x2048), downloaded by the user
LIVERY_GUIDE.md         everything learned so far: iRacing facts, spec values, placement lessons
cars/<car>/README.md    per-car sheet map + proven placements + gotchas (READ FIRST)
cars/<car>/grid_*.webp  in-sim screenshots of the labelled test grid; grid.tga = the grid paint
cars/bmw-m4-gt3/projection/  grid-label correspondences per view (for projecting a reference image)
tools/grid.py           list PSD layers / write the labelled mapping grid for any car
tools/seams.py          seam ruler + seams.json readings -> unfolded canvas (LIVERY_GUIDE 4b)
tools/install_paint.ps1 install -Project <livery> -Car <car-key> [-Build N | -Final] [-Finish ...] (Windows; no args = help)
                        -Car <car> -Grid / -Seams / -SeamCheck installs a car's mapping paints
install_gui.bat         (repo root) double-click window over install_paint.ps1: pick livery, car, build/final, finish (tools/install_gui.ps1)
tools/labelproj.py      project a reference image onto the sheet from grid labels
tools/ora.py            write layered .ora files (GIMP/Krita) so a livery can be finished by hand
liveries/<livery>/      one folder per livery: livery.py, CLAUDE.md, and per car <car-key>/{out,reference,final,archive}/
liveries/example/       minimal working livery: start new liveries from this (the only shared one)
logos/                  the user's logos (only logos/README.md is shared)
.venv/                  python env: pip install -r requirements.txt
```

Run scripts with the venv's python from inside the livery folder, e.g.
`cd liveries/example && ../../.venv/bin/python livery.py bmw-m4-gt3`
(Windows: `cd liveries\example; ..\..\.venv\Scripts\python livery.py bmw-m4-gt3`).
Livery scripts find the repo root two levels up (`liveries/<name>/` -> root) and open
templates from `psd/`.

@LIVERY_GUIDE.md

## First-time setup (when a new user asks to get started)

Most users will just say "read the docs and get me set up". Check each item and fix or guide
them through it, one step at a time, in plain language:
1. Their OS (Windows with iRacing, or a Mac building for a Windows PC).
2. Python 3 installed; `.venv` exists with `requirements.txt` installed (create it for them).
3. The car's `.psd` template is in `psd/` (they download it from iRacing; list what's
   there). The car is mapped in `cars/<car>/`? If not, mapping comes first.
4. Their iRacing customer ID (for the installer, which remembers it).
5. Build `liveries/example/` for their car as a smoke test, show them how to install it, then ask what
   livery they want.

## Rules for Claude

- **Car keys are `<make>-<model>-<class>`** (e.g. `porsche-992-cup`, `bmw-m4-gt4`); see LIVERY_GUIDE
  section 2. Never reuse a key for another car.
- **Map a car before designing on it** (LIVERY_GUIDE section 4). If `cars/<car>/` doesn't exist,
  start with the grid.
- **Graphics that cross panel seams**: read those seams off the ruler first (LIVERY_GUIDE 4b),
  then draw them on the unfolded canvas (`tools/seams.py`) instead of nudging by hand.
- New livery = new folder `liveries/<name>/` (never at the repo root) with `livery.py`, a `CLAUDE.md`
  and per car `<car-key>/{out,reference,final}/` (LIVERY_GUIDE section 2: `final/` = `paint.tga` + `spec.tga` + alternates) holding the design notes and a numbered version log (what changed, in-sim result).
- After every in-sim round, write what was learned down: per-car facts in `cars/<car>/README.md`,
  general lessons in `LIVERY_GUIDE.md`, version status in `liveries/<livery>/CLAUDE.md`.
- Ask the user for screenshot **file paths** and save useful screenshots into the repo.
- Never paint car numbers (iRacing draws them).
- The user may be new to coding: explain install steps plainly, give exact commands for their OS,
  and say which file to install and where.
