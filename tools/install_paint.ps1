<#
.SYNOPSIS
  Install a livery (paint + spec) or a car's mapping grid into iRacing. Run with no options for help.
#>
param(
    [string]$Project = "",     # livery folder in the repo, e.g. example, mylivery
    [string]$Car = "",         # car key from cars\ (bmw, mclaren) or an iRacing paint folder name
    [string]$Build = "",       # build tag, e.g. 1 or v3; default = newest build in <project>\out
    [string]$Finish = "gloss",   # any _spec_<name>.tga the build has
    [string]$CustomerId = "",  # remembered after the first use
    [switch]$Grid,             # install cars\<car>\grid.tga (mapping grid, no spec)
    [string]$File = "",        # install this paint file instead (any path)
    [string]$SpecFile = "",    # ... with this spec file
    [switch]$List,             # list the builds found for -Project (and -Car)
    [switch]$Help
)

$ErrorActionPreference = "Stop"
$Repo = Split-Path $PSScriptRoot -Parent
$IdFile = Join-Path $PSScriptRoot ".customer_id"      # gitignored

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
    $out = Join-Path (Join-Path $Repo $proj) "out"
    if (-not (Test-Path $out)) { return @() }
    $pattern = if ($car) { "${proj}_${car}*.tga" } else { "${proj}_*.tga" }
    Get-ChildItem $out -Filter $pattern | Where-Object { $_.BaseName -notmatch '_spec(_|$)' -and $_.BaseName -notmatch 'grid' } |
        Sort-Object LastWriteTime -Descending
}

function Show-Help {
    $cars = Get-Cars
    $projects = Get-ChildItem $Repo -Directory | Where-Object { Test-Path (Join-Path $_.FullName "out") } |
        ForEach-Object { $_.Name }
    $saved = if (Test-Path $IdFile) { (Get-Content $IdFile -Raw).Trim() } else { "none yet" }
    Write-Host @"

install_paint.ps1: copy a livery into iRacing's paint folder.

USAGE (run from anywhere)
  .\install_paint.ps1 -Project <folder> -Car <car> [-Build <tag>] [-Finish <name>] [-CustomerId <id>]
  .\install_paint.ps1 -Car <car> -Grid                  install the car's mapping grid
  .\install_paint.ps1 -Car <car> -File <paint.tga> [-SpecFile <spec.tga>]
  .\install_paint.ps1 -Project <folder> [-Car <car>] -List    show available builds

OPTIONS
  -Project     livery folder in this repo. Files come from <folder>\out\<folder>_<car>_<build>.tga
  -Car         car key (below) or an iRacing paint folder name (Documents\iRacing\paint\...)
  -Build       build tag (e.g. 1, v3). Leave out to install the newest build.
  -Finish      which spec file: gloss = _spec.tga, anything else = _spec_<name>.tga (e.g. metal,
               chrome, gold). -List shows the finishes each build has
  -CustomerId  your iRacing customer ID (iRacing account page). Remembered after the first time.
  -Grid        install cars\<car>\grid.tga, the labelled grid for mapping a car
  -File        install any paint .tga (optional -SpecFile for its spec)
  -List        list builds for -Project instead of installing

CARS:        $(if ($cars.Count) { ($cars.Keys | ForEach-Object { "$_ ($($cars[$_]))" }) -join ', ' } else { 'none mapped yet' })
PROJECTS:    $(if ($projects) { $projects -join ', ' } else { 'none built yet' })
CUSTOMER ID: $saved

EXAMPLES
  .\install_paint.ps1 -Project example -Car bmw -CustomerId 123456
  .\install_paint.ps1 -Project mylivery -Car mclaren -Build 3 -Finish metal
  .\install_paint.ps1 -Car bmw -Grid

After installing, press Ctrl+R in the sim to reload paints.
If Windows says running scripts is disabled, first run:  Set-ExecutionPolicy -Scope Process Bypass

"@
}

if ($Help -or $PSBoundParameters.Count -eq 0) { Show-Help; exit 0 }

if ($Project) { $Project = Split-Path $Project.TrimEnd('\', '/') -Leaf }   # accept .\mylivery\ from tab completion

if ($List) {
    if (-not $Project) { throw "-List needs -Project. Run with no options for help." }
    $builds = Get-Builds $Project $Car
    if (-not $builds) { Write-Host "No builds in $Project\out$(if ($Car) { " for $Car" })."; exit 0 }
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
if ($Grid) {
    $paint = Join-Path $Repo "cars\$Car\grid.tga"
    if (-not (Test-Path $paint)) {
        throw "No grid at $paint. Make one with tools\grid.py and save it there (or install it with -File)."
    }
} elseif ($File) {
    $paint = $File
    if ($SpecFile) { $spec = $SpecFile }
} else {
    if (-not $Project) { throw "Give a livery folder with -Project (or use -Grid / -File). Run with no options for help." }
    $out = Join-Path (Join-Path $Repo $Project) "out"
    if (-not (Test-Path $out)) { throw "No output folder: $out. Build the livery first." }
    if ($Build) {
        $base = "${Project}_${Car}_$Build"
    } else {
        $newest = Get-Builds $Project $Car | Select-Object -First 1
        if (-not $newest) { throw "No builds named ${Project}_${Car}*.tga in $out. Try -List, or -File." }
        $base = $newest.BaseName
    }
    $paint = Join-Path $out "$base.tga"
    $suffix = if ($Finish -eq "gloss") { "" } else { "_$Finish" }
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
