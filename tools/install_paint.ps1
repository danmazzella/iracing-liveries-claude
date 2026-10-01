<#
.SYNOPSIS
  Install a livery (paint + spec) or a car's mapping grid into iRacing. Run with no options for help.
#>
param(
    [string]$Project = "",     # livery folder in liveries\, e.g. example, mylivery
    [string]$Car = "",         # car key from cars\ (bmw-m4-gt3, porsche-992-cup, ...) or an iRacing paint folder name
    [string]$Build = "",       # build tag, e.g. 1 or v3; default = newest build in <project>\<car>\out
    [switch]$Final,            # install the approved set in <project>\<car>\final (paint.tga + spec.tga)
    [string]$Variant = "",     # colourway subfolder of final\ when a car has more than one
    [string]$Finish = "gloss",   # any spec_<name>.tga the build / final has
    [string]$CustomerId = "",  # remembered after the first use
    [switch]$Grid,             # install cars\<car>\grid.tga (mapping grid, no spec)
    [switch]$Seams,            # install cars\<car>\seams.tga (seam ruler, tools\seams.py)
    [switch]$SeamCheck,        # install cars\<car>\seamcheck.tga (seam stripe test)
    [string]$File = "",        # install this paint file instead (any path)
    [string]$SpecFile = "",    # ... with this spec file
    [switch]$List,             # list the builds found for -Project (and -Car)
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path $PSScriptRoot -Parent
$IdFile = Join-Path $PSScriptRoot ".customer_id"      # gitignored
$Liveries = Join-Path $Repo "liveries"                # one folder per livery

function Get-Cars {
    # car key -> iRacing folder, read from the "iRacing paint folder: `...`" line in cars\<car>\README.md
    $cars = [ordered]@{}
    Get-ChildItem (Join-Path $Repo "cars") -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $readme = Join-Path $_.FullName "README.md"
        if ((Test-Path $readme) -and ((Get-Content $readme -Raw) -match 'iRacing paint folder: `([^`]+)`')) {
            $cars[$_.Name] = $Matches[1]
        }
    }
    $cars
}

function Get-Builds([string]$proj, [string]$car) {
    # builds live in liveries\<project>\<car>\out, named <project>_<car>_<build>.tga
    $dirs = if ($car) { @(Join-Path (Join-Path (Join-Path $Liveries $proj) $car) "out") }
            else { Get-ChildItem (Join-Path $Liveries $proj) -Directory | ForEach-Object { Join-Path $_.FullName "out" } }
    $dirs | Where-Object { Test-Path $_ } | ForEach-Object {
        Get-ChildItem $_ -Filter "${proj}_*.tga" | Where-Object { $_.BaseName -notmatch '_spec(_|$)' -and $_.BaseName -notmatch 'grid' }
    } | Sort-Object LastWriteTime -Descending
}

function Show-Help {
    $cars = Get-Cars
    $projects = Get-ChildItem $Liveries -Directory -ErrorAction SilentlyContinue | Where-Object { Get-ChildItem $_.FullName -Directory | Where-Object { Test-Path (Join-Path $_.FullName "out") } } |
        ForEach-Object { $_.Name }
    $saved = if (Test-Path $IdFile) { (Get-Content $IdFile -Raw).Trim() } else { "none yet" }
    Write-Host @"

install_paint.ps1: copy a livery into iRacing's paint folder.

USAGE (run from anywhere)
  .\install_paint.ps1 -Project <folder> -Car <car> [-Build <tag>] [-Finish <name>] [-CustomerId <id>]
  .\install_paint.ps1 -Project <folder> -Car <car> -Final [-Variant <name>] [-Finish <name>]
  .\install_paint.ps1 -Car <car> -Grid                  install the car's mapping grid
  .\install_paint.ps1 -Car <car> -Seams                 install the seam ruler (-SeamCheck: the stripe test)
  .\install_paint.ps1 -Car <car> -File <paint.tga> [-SpecFile <spec.tga>]
  .\install_paint.ps1 -Project <folder> [-Car <car>] -List    show available builds

OPTIONS
  -Project     livery folder in liveries\. Builds come from liveries\<folder>\<car>\out\<folder>_<car>_<build>.tga
  -Car         car key (below) or an iRacing paint folder name (Documents\iRacing\paint\...)
  -Build       build tag (e.g. 1, v3). Leave out to install the newest build.
  -Final       install the approved set from liveries\<folder>\<car>\final\ instead of a build:
               paint.tga + spec.tga (spec.tga is THE spec to use; spec_<name>.tga are optional alternates).
               If final\ holds colourway subfolders, pick one with -Variant.
  -Finish      which spec file: gloss = the default (_spec.tga / spec.tga), anything else = the alternate
               (_spec_<name>.tga / spec_<name>.tga, e.g. metal, chrome, gold). -List shows each build's finishes
  -CustomerId  your iRacing customer ID (iRacing account page). Remembered after the first time.
  -Grid        install cars\<car>\grid.tga, the labelled grid for mapping a car
  -Seams       install cars\<car>\seams.tga, the seam ruler (tools\seams.py ruler <car>)
  -SeamCheck   install cars\<car>\seamcheck.tga, the seam stripe test (tools\seams.py check <car>)
  -File        install any paint .tga (optional -SpecFile for its spec)
  -List        list builds for -Project instead of installing

CARS:        $(if ($cars.Count) { ($cars.Keys | ForEach-Object { "$_ ($($cars[$_]))" }) -join ', ' } else { 'none mapped yet' })
PROJECTS:    $(if ($projects) { $projects -join ', ' } else { 'none built yet' })
CUSTOMER ID: $saved

EXAMPLES
  .\install_paint.ps1 -Project example -Car bmw-m4-gt3 -CustomerId 123456
  .\install_paint.ps1 -Project mylivery -Car mclaren-720s-gt3 -Build 3 -Finish metal
  .\install_paint.ps1 -Project mylivery -Car porsche-992-cup -Final
  .\install_paint.ps1 -Car bmw-m4-gt3 -Grid

After installing, press Ctrl+R in the sim to reload paints.
If Windows says running scripts is disabled, first run:  Set-ExecutionPolicy -Scope Process Bypass

"@
}

if ($Help -or $PSBoundParameters.Count -eq 0) { Show-Help; exit 0 }

if ($Project) { $Project = Split-Path $Project.TrimEnd('\', '/') -Leaf }   # accept .\mylivery\ from tab completion

if ($List) {
    if (-not $Project) { throw "-List needs -Project. Run with no options for help." }
    $builds = Get-Builds $Project $Car
    if (-not $builds) { Write-Host "No builds in liveries\$Project$(if ($Car) { "\$Car" })\out."; exit 0 }
    $builds | ForEach-Object {
        $specs = Get-ChildItem $_.DirectoryName -Filter "$($_.BaseName)_spec*.tga" |
            ForEach-Object { ($_.BaseName -replace '^.*_spec_?', '') } | ForEach-Object { if ($_) { $_ } else { "gloss" } }
        "{0}  {1:yyyy-MM-dd HH:mm}  finishes: {2}" -f $_.Name, $_.LastWriteTime, ($(if ($specs) { $specs -join ', ' } else { 'none' }))
    }
    exit 0
}

# --- customer ID: option > saved file > IRACING_CUSTOMER_ID environment variable
if ($CustomerId) {
    Set-Content $IdFile $CustomerId
} elseif (Test-Path $IdFile) {
    $CustomerId = (Get-Content $IdFile -Raw).Trim()
} elseif ($env:IRACING_CUSTOMER_ID) {
    $CustomerId = $env:IRACING_CUSTOMER_ID
} else {
    throw "Give your iRacing customer ID once with -CustomerId <id> (it's on your iRacing account page)."
}

# --- car -> iRacing paint folder
if (-not $Car) { throw "Give a car with -Car. Run with no options to see the list." }
$cars = Get-Cars
$carFolder = if ($cars.Contains($Car)) { $cars[$Car] } else { $Car }
$paintRoot = Join-Path ([Environment]::GetFolderPath("MyDocuments")) "iRacing\paint"
$dest = Join-Path $paintRoot $carFolder
if (-not (Test-Path $dest)) {
    Write-Host "Paint folder not found: $dest" -ForegroundColor Red
    if ($cars.Count) { Write-Host "Mapped cars: $(($cars.Keys) -join ', ')" }
    if (Test-Path $paintRoot) {
        Write-Host "Car folders in iRacing:"; Get-ChildItem $paintRoot -Directory | ForEach-Object { "  " + $_.Name }
    }
    throw "Use a mapped car or one of the iRacing folder names above (drive the car once in iRacing if it's missing)."
}

# --- which files
$spec = $null
if ($Grid -or $Seams -or $SeamCheck) {
    $name = if ($Grid) { "grid" } elseif ($Seams) { "seams" } else { "seamcheck" }
    $paint = Join-Path $Repo "cars\$Car\$name.tga"
    if (-not (Test-Path $paint)) {
        $how = if ($Grid) { "tools\grid.py" } elseif ($Seams) { "tools\seams.py ruler $Car" } else { "tools\seams.py check $Car" }
        throw "No $name.tga at $paint. Make it with $how (or install any file with -File)."
    }
} elseif ($File) {
    $paint = $File
    if ($SpecFile) { $spec = $SpecFile }
} else {
    if (-not $Project) { throw "Give a livery folder with -Project (or use -Grid / -Seams / -File). Run with no options for help." }
    $carDir = Join-Path (Join-Path $Liveries $Project) $Car
    $suffix = if ($Finish -eq "gloss") { "" } else { "_$Finish" }
    if ($Final) {
        $fin = Join-Path $carDir "final"
        if ($Variant) { $fin = Join-Path $fin $Variant }
        $paint = Join-Path $fin "paint.tga"
        if (-not (Test-Path $paint)) {
            $variants = if (Test-Path (Join-Path $carDir "final")) { (Get-ChildItem (Join-Path $carDir "final") -Directory | Where-Object { $_.Name -ne "archive" } | ForEach-Object { $_.Name }) -join ', ' }
            throw "No paint.tga in $fin.$(if ($variants) { " Colourways in final\: $variants (use -Variant)." } else { " This car has no final yet: use -Build or leave -Final out." })"
        }
        $spec = Join-Path $fin "spec$suffix.tga"
        $have = Get-ChildItem $fin -Filter "spec*.tga" | ForEach-Object { ($_.BaseName -replace '^spec_?', '') } | ForEach-Object { if ($_) { $_ } else { "gloss" } }
        if (-not (Test-Path $spec)) { throw "No '$Finish' finish in $fin. It has: $($have -join ', ')" }
    } else {
        $out = Join-Path $carDir "out"
        if (-not (Test-Path $out)) { throw "No output folder: $out. Build the livery for this car first." }
        if ($Build) {
            $base = "${Project}_${Car}_$Build"
        } else {
            $newest = Get-Builds $Project $Car | Select-Object -First 1
            if (-not $newest) { throw "No builds named ${Project}_${Car}*.tga in $out. Try -List, -Final, or -File." }
            $base = $newest.BaseName
        }
        $paint = Join-Path $out "$base.tga"
        $spec = Join-Path $out "${base}_spec$suffix.tga"
        if (-not (Test-Path $spec)) {
            if ($PSBoundParameters.ContainsKey("Finish")) {
                $have = Get-ChildItem $out -Filter "${base}_spec*.tga" |
                    ForEach-Object { ($_.BaseName -replace '^.*_spec_?', '') } | ForEach-Object { if ($_) { $_ } else { "gloss" } }
                throw "No '$Finish' finish for $base. This build has: $($have -join ', ')"
            }
            Write-Host "No spec file ($spec): installing the paint without one." -ForegroundColor Yellow
            $spec = $null
        }
    }
}
foreach ($f in @($paint, $spec) | Where-Object { $_ }) {
    if (-not (Test-Path $f)) { throw "Missing file: $f" }
}

# --- copy
Copy-Item $paint (Join-Path $dest "car_$CustomerId.tga") -Force
Write-Host "paint -> $dest\car_$CustomerId.tga   (from $paint)"
$specTga = Join-Path $dest "car_spec_$CustomerId.tga"
if ($spec) {
    Copy-Item $spec $specTga -Force
    Write-Host "spec  -> $specTga   (from $spec)"
} elseif (Test-Path $specTga) {
    Remove-Item $specTga   # don't leave an old finish on the new paint
    Write-Host "spec  -> removed the old one"
}

# iRacing rebuilds the .mip from the TGA; remove the old one so it can't go stale
$specMip = Join-Path $dest "car_spec_$CustomerId.mip"
if (Test-Path $specMip) { Remove-Item $specMip }

Write-Host "Done. In the sim, press Ctrl+R to reload paints." -ForegroundColor Green
