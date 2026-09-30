# Make iRacing liveries with Claude Code

Describe the livery you want, and Claude builds it for you. This folder holds everything we
learned making our own iRacing paints with **Claude Code** (an AI assistant that works with the
files on your computer), so Claude can skip the trial and error and get straight to your design.

## Quick start

1. **Download this folder**: green **`<> Code`** button at the top of this page → **Download ZIP** → unzip it.
2. **Install Claude Code**: <https://code.claude.com/docs/en/setup> (needs a paid Claude plan).
3. **Open Claude in this folder** (open a terminal in the folder and type `claude`, or pick the
   folder in the Claude desktop app's **Code** tab) and say something like:

   > Read the README and the .md files in this folder, then get me set up to make an iRacing
   > livery. I'm on Windows and I want to paint the BMW M4 GT3.

Claude checks what's missing (Python, the car's paint template, your iRacing customer ID) and walks
you through it. Then just describe your livery: colours, stripes, logos, a picture you like.
Claude builds it, tells you how to install it, and fixes whatever you don't like after you try it
in the sim.

That's it. Everything below is detail, for when you're curious or something goes wrong.

---

**What's in here:**

- `LIVERY_GUIDE.md`: the lessons from three finished liveries and ~40 test rounds (what the
  paint files are, which finish values look good, where things end up on the car, mistakes to avoid).
  Claude reads it automatically.
- `cars/`: maps of the **BMW M4 GT3** and the **McLaren 720S GT3 EVO** (which part of the paint
  file lands on which part of the car), with screenshots. Other cars work too: Claude maps them first.
- `tools/`: a mapping-grid maker for any car, and an installer that copies a paint into iRacing.
- `liveries/`: one folder per livery. `liveries/example/` is a small working livery to start from;
  your own liveries go next to it.
- `psd/`: put iRacing's car templates here (not included, see Step 4).

**What's not in here:** our own liveries, team logos, or iRacing's template files. You make your own.

---

# Detailed setup (step by step)

Claude can do or explain all of this for you. It's here if you'd rather do it yourself, or
want to know what's going on. No coding experience needed.

## What you need

- A **Windows PC with iRacing** (that's where paints get installed). You can do all of this on
  that PC. A Mac works too for the building part; you then copy the finished files to the PC.
- A **Claude account with Claude Code access** (a paid Claude plan such as Pro or Max, or an
  Anthropic API account). See <https://claude.com/pricing>.
- About 30 minutes for the first-time setup.

---

## Step 1: Download this folder

This page is a GitHub "repository": a shared folder of files. You don't need a GitHub account
to download it.

**Easiest way (no extra software):**

1. At the top of this repository's GitHub page, click the green **`<> Code`** button.
2. Click **Download ZIP**.
3. Unzip it somewhere easy to find, e.g. `Documents\iracing-paints`.
   (On Windows: right-click the ZIP → **Extract All**.)

**Or, with Git** (lets you grab updates later with one command): install Git from
<https://git-scm.com/downloads> (the defaults are fine), open a terminal (see below) and run:

```
cd Documents
git clone <the URL shown under the green Code button>
```

> **What's a terminal?** A window where you type commands.
> **Windows:** press Start, type `PowerShell`, open **Windows PowerShell**.
> **Mac:** press Cmd+Space, type `Terminal`, press Enter.
> Type (or paste) a command and press Enter. `cd` means "go into this folder".

---

## Step 2: Install Python

The liveries are small Python programs, so your computer needs Python (free).

1. Go to <https://www.python.org/downloads/> and download the latest Python 3.
2. **Windows:** on the first installer screen, **tick "Add python.exe to PATH"**, then click
   Install Now. (If you miss this, uninstall and reinstall with the box ticked.)
   **Mac:** run the installer with the defaults.
3. Check it worked: open a **new** terminal and type `python --version` (Mac: `python3 --version`).
   You should see something like `Python 3.13.1`.

## Step 3: Install the Python add-ons

In the terminal, go into the folder you unzipped and create a private Python environment
(`.venv`) with the add-ons this project uses:

**Windows (PowerShell):**
```
cd $HOME\Documents\iracing-paints
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

**Mac:**
```
cd ~/Documents/iracing-paints
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

(Change the path if you unzipped somewhere else. If the unzipped folder is called
`iracing-paints-main`, use that name.)

You can also skip this step and ask Claude to do it for you in Step 6.

## Step 4: Get the car's paint template from iRacing

iRacing publishes a paint template (a Photoshop `.psd` file) for each car. The scripts read it to
know the car's shape, what's paintable and where the trim goes. We can't share these, so download
the ones you need:

1. Get the template for your car from iRacing (each car has a paint template download; search
   "iRacing paint template <car name>" if you can't find it).
2. Unzip it if needed, and put the `.psd` file in the **`psd` folder**. Keep the original file name, e.g. `BMW M4 GT3.psd` or `McLaren 720s EVO GT3.psd`.

You don't need Photoshop.

## Step 5: Install Claude Code

Follow the official instructions: <https://code.claude.com/docs/en/setup>. In short:

**Windows (PowerShell):**
```
irm https://claude.ai/install.ps1 | iex
```
On Windows, Claude Code also needs **Git for Windows** (<https://git-scm.com/downloads>).

**Mac (Terminal):**
```
curl -fsSL https://claude.ai/install.sh | bash
```

Close and reopen the terminal afterwards. (Prefer an app? The Claude desktop app has Claude Code
built in: open it, pick the **Code** tab, and choose this folder.)

## Step 6: Start Claude in this folder

```
cd $HOME\Documents\iracing-paints      (Mac: cd ~/Documents/iracing-paints)
claude
```

The first time, it asks you to log in to your Claude account in the browser. Then you get a
prompt where you type in plain English. Claude asks before running commands or changing files;
read what it wants to do and press Enter to allow it.

Good first messages:

> I'm new to this. I'm on Windows and I've put `BMW M4 GT3.psd` in the psd folder. Check my setup
> works by building the example livery.

> I want a livery for the BMW M4 GT3: dark green with a gold stripe from the nose over the roof,
> and my team logo on the doors. My logo is in `logos/myteam.png`.

> Here's a design I like: `reference/idea.jpg`. Make something in that style for the McLaren.

---

## Step 7: The build → test → fix loop

This is how every livery gets made. Expect several rounds. That's normal.

1. **Claude builds** your livery and tells you where the files are, e.g.
   `liveries\mylivery\out\mylivery_bmw_1.tga` (the paint) and `..._spec.tga` (the finish: gloss, metallic...).
2. **Install it** with the installer in the `tools` folder (PowerShell). Tell it which livery
   folder and which car; it picks the newest build:
   ```
   cd $HOME\Documents\iracing-paints\tools
   Set-ExecutionPolicy -Scope Process Bypass
   .\install_paint.ps1 -Project mylivery -Car bmw -CustomerId 123456
   ```
   - Run `.\install_paint.ps1` with no options to see every option, the cars and livery
     folders it found, and examples.
   - `-CustomerId`: your iRacing customer ID (on your iRacing account page). Only needed the
     first time; the script remembers it.
   - `-Car`: `bmw` or `mclaren` (mapped cars), or the car's folder name in
     `Documents\iRacing\paint\`. That folder only exists once you've driven the car in iRacing.
   - `-Build 3` installs build 3 instead of the newest; `-Finish metal` or `-Finish chrome`
     picks another finish if the livery made one; `-List` shows the builds you have.
   - The `Set-ExecutionPolicy` line lets Windows run the script, for that window only.
   - Built on a Mac? Copy the `out` folder to the PC first (USB stick, cloud drive...).
3. **Look at it in iRacing.** Open the car (Test Drive is easiest), and press **Ctrl+R** to
   reload paints after each install.
4. **Screenshot it** from a few angles (front, side, rear, top) and save the images **into this
   folder** (e.g. `mylivery\reference\v1_front.png`). Then tell Claude the file path and what you
   want changed:
   > Screenshots are in `mylivery/reference/v1_*.png`. The stripe is too far forward on the
   > hood and the door logo is cut off at the back. Everything else is good, keep it.

   Be specific about **where** ("on the front bumper, left of the grille") and say what's good,
   so it doesn't get changed.
5. Repeat until you love it. Ask Claude to copy the approved version into `mylivery/final/`.

**Good to know:**
- iRacing adds **your car number** itself. Pick the number and wheel colours in iRacing's
  paint screen.
- Each car can only have **one** custom paint on your account. Installing replaces the old one
  (keep your files and you can always put it back).
- Small tweaks don't show on the car. If you can't see a change, ask for a bigger one.

## Painting a car that isn't mapped yet

Only the BMW M4 GT3 and McLaren 720S GT3 EVO are mapped. For any other car, ask Claude:

> I want to paint the <car>. I've put its template in the folder. Let's map it first.

Claude makes a **grid paint**: coloured squares labelled with numbers. Install it with
`.\install_paint.ps1 -Car <car> -Grid` (Claude tells you the car name to use), take screenshots from the front, both sides, rear and top, save them into
`cars/<car>/`, and tell Claude where they are. Claude reads the labels to learn which part of the
paint file lands where on the car, and writes that down in `cars/<car>/README.md`. Skipping this
costs more time later: parts of the paint file are rarely where they look.

Want stripes or graphics that run across several panels (hood onto bumper, door onto fender)?
Ask Claude to **map the seams** too. It installs a "ruler" paint (`.\install_paint.ps1 -Car <car>
-Seams`) with numbered marks along every panel edge. You take close-up screenshots where panels
meet, and Claude reads which marks line up. From then on, lines drawn across those seams line up
the first time.

---

## Getting updates

- Downloaded the ZIP: download it again and copy your own folders (`liveries/`, `logos/`,
  `psd/`) across.
- Used `git clone`: in the folder, run `git pull`.

Your own livery folders, logos and templates are never uploaded or overwritten by updates: the
`.gitignore` file tells Git to ignore everything except the shared toolkit files.

## Sharing what you learn

Mapped a new car or found a finish that looks great? The knowledge lives in plain text files
(`LIVERY_GUIDE.md`, `cars/<car>/README.md`, `cars/<car>/grid_*` screenshots). Ask Claude to help
you share it back: open an Issue on this repository's GitHub page, or ask Claude to walk you
through making a "pull request".

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` / `pip` "not recognized" | Reinstall Python with **Add python.exe to PATH** ticked, then open a new terminal. |
| `claude` "not recognized" | Close and reopen the terminal. Still no? Re-run the install command in Step 5. |
| "running scripts is disabled on this system" | Run `Set-ExecutionPolicy -Scope Process Bypass` in that PowerShell window first. |
| "Paint folder not found" | Drive the car once in iRacing, then use one of the folder names the script lists. |
| The car still shows the old paint | Press **Ctrl+R** in the sim. Check the customer ID is yours. |
| Claude can't find the template | The `.psd` must be in the `psd` folder, with its original name. |
| Anything else | Paste the exact error message to Claude and ask what it means. |

---

Folder layout, for the curious:

```
README.md             this guide
LIVERY_GUIDE.md       everything we learned (Claude reads it via CLAUDE.md)
CLAUDE.md             instructions Claude reads automatically when started in this folder
requirements.txt      Python add-ons
cars/<car>/           car maps, grid screenshots, grid paint (grid.tga), seam ruler (seams.tga)
tools/grid.py         makes the mapping grid for a new car / lists template layers
tools/seams.py        maps where panels meet, so graphics line up across them
tools/install_paint.ps1   copies a paint into iRacing (Windows)
tools/labelproj.py    advanced: projects a reference image onto the paint file
liveries/<livery>/    one folder per livery (only liveries/example/ is shared)
liveries/example/     a minimal livery to start from
psd/                  iRacing's car templates go here (only its README is shared)
logos/                put your logos here (only its README is shared)
```
