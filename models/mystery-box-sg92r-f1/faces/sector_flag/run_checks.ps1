$ErrorActionPreference = 'Stop'
$env:PYTHONDONTWRITEBYTECODE = '1'
$sectorBlender = 'C:/Program Files/Blender Foundation/Blender 5.1/blender.exe'
$sectorDir = $PSScriptRoot
$sectorOut = Join-Path $sectorDir '_local'
New-Item -ItemType Directory -Force -Path $sectorOut | Out-Null
& $sectorBlender --background --factory-startup --python-exit-code 1 --python (Join-Path $sectorDir 'check_local.py') -- --step .25 --all --compare
$sectorCode = $LASTEXITCODE
Write-Output ('sector_flag checks exit=' + $sectorCode)
if ($sectorCode -ne 0) { exit $sectorCode }
