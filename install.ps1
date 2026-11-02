# kid-compass installer (Windows PowerShell)
#
# Copies the kid-compass skill into the folders AI agents load skills from:
#   %USERPROFILE%\.claude\skills\kid-compass   -> Claude Code (Cursor reads it too)
#   %USERPROFILE%\.agents\skills\kid-compass   -> Codex, Cursor, GitHub Copilot, Gemini CLI and other agents
#
# Usage:
#   irm https://raw.githubusercontent.com/brainydarts/kid-compass/main/install.ps1 | iex
#   .\install.ps1 -Agent codex
#   .\install.ps1 -Project
#   .\install.ps1 -Uninstall
param(
  [string]$Agent = "all",
  [switch]$Project,
  [string]$Ref = "main",
  [switch]$Uninstall
)
$ErrorActionPreference = "Stop"
$Repo  = if ($env:KID_COMPASS_REPO) { $env:KID_COMPASS_REPO } else { "brainydarts/kid-compass" }
$Skill = "kid-compass"
$Base  = if ($Project) { (Get-Location).Path } else { $HOME }

$wantClaude = $false; $wantAgents = $false
foreach ($a in ($Agent -split ",")) {
  switch ($a.Trim().ToLower()) {
    "all"            { $wantClaude = $true; $wantAgents = $true }
    "claude"         { $wantClaude = $true }
    "claude-code"    { $wantClaude = $true }
    { $_ -in @("codex","cursor","copilot","github-copilot","gemini","gemini-cli","agents","universal") } { $wantAgents = $true }
    default { throw "Unknown agent: $a (try: claude, codex, cursor, copilot, gemini, all)" }
  }
}
$targets = @()
if ($wantClaude) { $targets += Join-Path $Base ".claude\skills" }
if ($wantAgents) { $targets += Join-Path $Base ".agents\skills" }

function Test-Ours($dir) {
  $f = Join-Path $dir "SKILL.md"
  return (Test-Path $f) -and (Select-String -Path $f -Pattern "^name: $Skill$" -Quiet)
}

if ($Uninstall) {
  foreach ($t in $targets) {
    $d = Join-Path $t $Skill
    if (Test-Ours $d) { Remove-Item -Recurse -Force $d; Write-Host "removed $d" } else { Write-Host "nothing to remove in $t" }
  }
  return
}

# Use a local clone if this script sits in one; otherwise download from GitHub.
$src = $null
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "skills\$Skill\SKILL.md"))) {
  $src = Join-Path $PSScriptRoot "skills\$Skill"
} else {
  $tmp = Join-Path ([IO.Path]::GetTempPath()) ("kid-compass-" + [guid]::NewGuid())
  New-Item -ItemType Directory -Path $tmp | Out-Null
  $zip = Join-Path $tmp "src.zip"
  Write-Host "Downloading $Repo ($Ref)..."
  Invoke-WebRequest -Uri "https://codeload.github.com/$Repo/zip/$Ref" -OutFile $zip -UseBasicParsing
  Expand-Archive -Path $zip -DestinationPath $tmp -Force
  $found = Get-ChildItem -Path $tmp -Recurse -Filter "SKILL.md" | Where-Object { $_.Directory.Name -eq $Skill } | Select-Object -First 1
  if (-not $found) { throw "Couldn't find skills\$Skill in the download." }
  $src = $found.Directory.FullName
}

foreach ($t in $targets) {
  New-Item -ItemType Directory -Force -Path $t | Out-Null
  $dest = Join-Path $t $Skill
  if (Test-Path $dest) {
    if (Test-Ours $dest) { Remove-Item -Recurse -Force $dest }
    else { Write-Warning "$dest exists and isn't kid-compass - skipped"; continue }
  }
  Copy-Item -Recurse -Path $src -Destination $dest
  Write-Host "installed to $dest"
}

Write-Host ""
Write-Host "Optional: the helper scripts need Python 3 and PyYAML ->  py -m pip install pyyaml"
Write-Host "Restart your agent, then ask something like:"
Write-Host '  "My daughter is 10, Class 5, in Pune and loves drawing - what can she take part in this year?"'
