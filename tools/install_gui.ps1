<#
.SYNOPSIS
  Small window for tools\install_paint.ps1: pick livery, car, build/finish, click Install.
  Start it by double-clicking install_gui.bat (repo root), or:  powershell -ExecutionPolicy Bypass -File tools\install_gui.ps1
#>
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[System.Windows.Forms.Application]::EnableVisualStyles()

$Repo = Split-Path $PSScriptRoot -Parent
$Liveries = Join-Path $Repo "liveries"
$Installer = Join-Path $PSScriptRoot "install_paint.ps1"
$IdFile = Join-Path $PSScriptRoot ".customer_id"

$MODE_FINAL = "Approved final"
$MODE_BUILD = "A build (work in progress)"
$MODE_MAP   = "Mapping paint (grid / seams)"

function Sub-Dirs($path) {
    if (Test-Path $path) { @(Get-ChildItem $path -Directory | Where-Object { $_.Name -ne "archive" -and $_.Name -notlike "_*" } | ForEach-Object { $_.Name }) } else { @() }
}

# the folder that holds paint.tga for the current final selection (handles colourway subfolders)
function Final-Dir($livery, $car, $variant) {
    $d = Join-Path (Join-Path (Join-Path $Liveries $livery) $car) "final"
    if ($variant) { $d = Join-Path $d $variant }
    $d
}

function Spec-Names($files, $stripPattern) {
    # the plain spec file (no finish name) is the default; shown first, labelled "default"
    $names = @($files | ForEach-Object { ($_.BaseName -replace $stripPattern, '') } | Where-Object { $_ } | Sort-Object -Unique)
    if (@($files | Where-Object { ($_.BaseName -replace $stripPattern, '') -eq '' }).Count) { $names = @("default") + $names }
    $names
}

# ---- controls
$form = New-Object System.Windows.Forms.Form
$form.Text = "iRacing paint installer"
$form.Size = New-Object System.Drawing.Size(560, 520)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedSingle"
$form.MaximizeBox = $false

$y = 15
function Add-Row($label, $control) {
    $l = New-Object System.Windows.Forms.Label
    $l.Text = $label; $l.Location = New-Object System.Drawing.Point(15, ($script:y + 3)); $l.Size = New-Object System.Drawing.Size(110, 20)
    $control.Location = New-Object System.Drawing.Point(130, $script:y); $control.Size = New-Object System.Drawing.Size(400, 24)
    $form.Controls.Add($l); $form.Controls.Add($control)
    $script:y += 33
}
function New-Combo { $c = New-Object System.Windows.Forms.ComboBox; $c.DropDownStyle = "DropDownList"; $c }

$cbMode = New-Combo; $cbMode.Items.AddRange(@($MODE_FINAL, $MODE_BUILD, $MODE_MAP)); $cbMode.SelectedIndex = 0
$cbLivery = New-Combo
$cbCar = New-Combo
$cbVariant = New-Combo
$cbBuild = New-Combo
$cbFinish = New-Combo
$tbId = New-Object System.Windows.Forms.TextBox
if (Test-Path $IdFile) { $tbId.Text = (Get-Content $IdFile -Raw).Trim() }

Add-Row "What to install" $cbMode
Add-Row "Livery" $cbLivery
Add-Row "Car" $cbCar
Add-Row "Colourway" $cbVariant
Add-Row "Build" $cbBuild
Add-Row "Finish (spec)" $cbFinish
Add-Row "Customer ID" $tbId

$btn = New-Object System.Windows.Forms.Button
$btn.Text = "Install"; $btn.Location = New-Object System.Drawing.Point(130, $y); $btn.Size = New-Object System.Drawing.Size(120, 32)
$form.Controls.Add($btn)
$hint = New-Object System.Windows.Forms.Label
$hint.Text = "Then press Ctrl+R in iRacing."; $hint.Location = New-Object System.Drawing.Point(265, ($y + 8)); $hint.Size = New-Object System.Drawing.Size(260, 20)
$form.Controls.Add($hint)
$y += 45

$log = New-Object System.Windows.Forms.TextBox
$log.Multiline = $true; $log.ReadOnly = $true; $log.ScrollBars = "Vertical"; $log.Font = New-Object System.Drawing.Font("Consolas", 9)
$log.Location = New-Object System.Drawing.Point(15, $y); $log.Size = New-Object System.Drawing.Size(515, 235)
$form.Controls.Add($log)

# ---- list refresh (each step fills the next dropdown; guarded so programmatic changes don't loop)
$script:busy = $false

function Fill($combo, $items, $keep) {
    $combo.Items.Clear()
    foreach ($i in $items) { [void]$combo.Items.Add($i) }
    if ($keep -and $combo.Items.Contains($keep)) { $combo.SelectedItem = $keep }
    elseif ($combo.Items.Count) { $combo.SelectedIndex = 0 }
}

function Refresh-Lists([string]$from) {
    if ($script:busy) { return }
    $script:busy = $true
    try {
        $mode = $cbMode.SelectedItem
        $isMap = ($mode -eq $MODE_MAP); $isFinal = ($mode -eq $MODE_FINAL); $isBuild = ($mode -eq $MODE_BUILD)
        $cbLivery.Enabled = -not $isMap
        $cbVariant.Enabled = $isFinal
        $cbBuild.Enabled = $isBuild

        if ($isMap) {
            $cars = @(Get-ChildItem (Join-Path $Repo "cars") -Directory | Where-Object {
                (Test-Path (Join-Path $_.FullName "grid.tga")) -or (Test-Path (Join-Path $_.FullName "seams.tga")) } | ForEach-Object { $_.Name })
            Fill $cbCar $cars $cbCar.SelectedItem
            Fill $cbVariant @() $null
            Fill $cbBuild @() $null
            Fill $cbFinish @("grid", "seams", "seam check") $cbFinish.SelectedItem
            return
        }

        if ($from -in @("mode")) {
            $want = if ($isFinal) { "final" } else { "out" }
            $liv = @(Sub-Dirs $Liveries | Where-Object {
                $l = $_; (Sub-Dirs (Join-Path $Liveries $l) | Where-Object { Test-Path (Join-Path (Join-Path (Join-Path $Liveries $l) $_) $want) }) })
            Fill $cbLivery $liv $cbLivery.SelectedItem
        }
        if ($from -in @("mode", "livery")) {
            $want = if ($isFinal) { "final" } else { "out" }
            $cars = @(Sub-Dirs (Join-Path $Liveries $cbLivery.SelectedItem) | Where-Object {
                Test-Path (Join-Path (Join-Path (Join-Path $Liveries $cbLivery.SelectedItem) $_) $want) })
            Fill $cbCar $cars $cbCar.SelectedItem
        }
        $liv = $cbLivery.SelectedItem; $car = $cbCar.SelectedItem
        if (-not $liv -or -not $car) { Fill $cbVariant @() $null; Fill $cbBuild @() $null; Fill $cbFinish @() $null; return }

        if ($isFinal) {
            $fin = Final-Dir $liv $car $null
            $hasPaint = Test-Path (Join-Path $fin "paint.tga")
            $variants = if ($hasPaint) { @() } else { @(Sub-Dirs $fin) }
            if ($from -ne "variant") { Fill $cbVariant $variants $cbVariant.SelectedItem }
            Fill $cbBuild @() $null
            $dir = Final-Dir $liv $car $cbVariant.SelectedItem
            $specs = if (Test-Path $dir) { Spec-Names (Get-ChildItem $dir -Filter "spec*.tga") '^spec_?' } else { @() }
            Fill $cbFinish $specs $cbFinish.SelectedItem
        } else {
            Fill $cbVariant @() $null
            $out = Join-Path (Join-Path (Join-Path $Liveries $liv) $car) "out"
            $builds = @(Get-ChildItem $out -Filter "${liv}_*.tga" -ErrorAction SilentlyContinue |
                Where-Object { $_.BaseName -notmatch '_spec(_|$)' -and $_.BaseName -notmatch 'grid|ruler|proj' } | Sort-Object LastWriteTime -Descending)
            $names = @("(newest)") + @($builds | ForEach-Object { $_.BaseName.Substring("${liv}_${car}_".Length) })
            if ($from -ne "build") { Fill $cbBuild $names $cbBuild.SelectedItem }
            $base = if ($cbBuild.SelectedItem -and $cbBuild.SelectedItem -ne "(newest)") { "${liv}_${car}_$($cbBuild.SelectedItem)" }
                    elseif ($builds.Count) { $builds[0].BaseName } else { $null }
            $specs = if ($base) { Spec-Names (Get-ChildItem $out -Filter "${base}_spec*.tga") '^.*_spec_?' } else { @() }
            Fill $cbFinish $specs $cbFinish.SelectedItem
        }
    } finally { $script:busy = $false }
}

$cbMode.Add_SelectedIndexChanged({ Refresh-Lists "mode" })
$cbLivery.Add_SelectedIndexChanged({ Refresh-Lists "livery" })
$cbCar.Add_SelectedIndexChanged({ Refresh-Lists "car" })
$cbVariant.Add_SelectedIndexChanged({ Refresh-Lists "variant" })
$cbBuild.Add_SelectedIndexChanged({ Refresh-Lists "build" })

$btn.Add_Click({
    $mode = $cbMode.SelectedItem; $car = $cbCar.SelectedItem; $fin = $cbFinish.SelectedItem
    $a = @{}
    if ($tbId.Text.Trim()) { $a.CustomerId = $tbId.Text.Trim() }
    if (-not $car) { $log.Text = "Pick a car first."; return }
    $a.Car = $car
    if ($mode -eq $MODE_MAP) {
        switch ($fin) { "grid" { $a.Grid = $true } "seams" { $a.Seams = $true } "seam check" { $a.SeamCheck = $true } default { $log.Text = "Pick what to install."; return } }
    } else {
        $a.Project = $cbLivery.SelectedItem
        if (-not $a.Project) { $log.Text = "Pick a livery first."; return }
        if ($mode -eq $MODE_FINAL) {
            $a.Final = $true
            if ($cbVariant.SelectedItem) { $a.Variant = $cbVariant.SelectedItem }
        } elseif ($cbBuild.SelectedItem -and $cbBuild.SelectedItem -ne "(newest)") { $a.Build = $cbBuild.SelectedItem }
        if ($fin -and $fin -ne "default") { $a.Finish = $fin }
    }
    $log.Text = "Installing..."
    $form.Refresh()
    try {
        $text = (& $Installer @a *>&1 | Out-String)
    } catch {
        $text = "ERROR: " + $_.Exception.Message
    }
    $log.Text = $text.Trim()
})

$form.Add_Shown({ Refresh-Lists "mode" })
[void]$form.ShowDialog()
