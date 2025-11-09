#!/usr/bin/env pwsh
#get flags from command line
param([switch]$major, [switch]$minor, [switch]$patch)
if (-not ($major -or $minor -or $patch)) {
    Write-Host "Please specify at least one of the following flags: -major, -minor, -patch"
    exit 1
}
$project_config = Get-Content -Path "pyproject.toml" -Raw
$project_config = [regex]::Replace(
    $project_config,
    'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"',
    { param($m) 'version = "' + ($major ? [int]$m.Groups[1].Value + 1 : [int]$m.Groups[1].Value) + '.' + ($minor ? [int]$m.Groups[2].Value + 1 : [int]$m.Groups[2].Value) + '.' + ($patch ? [int]$m.Groups[3].Value + 1 : [int]$m.Groups[3].Value) + '"' }
)
Set-Content -Path "pyproject.toml" -Value $project_config