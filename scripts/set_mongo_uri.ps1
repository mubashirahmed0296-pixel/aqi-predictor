param(
    [Parameter(Mandatory = $true)]
    [string]$MongoUri
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$envPath = Join-Path $PSScriptRoot "..\backend\.env"
$envPath = (Resolve-Path $envPath).Path

if (-not (Test-Path $envPath)) {
    throw "backend/.env not found. Run .\scripts\bootstrap_local.ps1 first."
}

$content = Get-Content -Raw $envPath
if ($content -match "(?m)^MONGODB_URI=") {
    $content = [regex]::Replace($content, "(?m)^MONGODB_URI=.*$", "MONGODB_URI=$MongoUri")
} else {
    $content = $content.TrimEnd() + "`r`nMONGODB_URI=$MongoUri`r`n"
}

$enc = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($envPath, $content, $enc)
Write-Host "Updated MONGODB_URI in backend/.env"
