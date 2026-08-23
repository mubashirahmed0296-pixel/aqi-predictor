$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "==> Starting local MongoDB with Docker Compose..."
try {
    docker compose -f docker-compose.local.yml up -d mongo
} catch {
    Write-Warning "Docker-based MongoDB startup failed. You can still continue if you have MongoDB running elsewhere and set MONGODB_URI in backend/.env."
}

Write-Host "==> Preparing backend virtual environment..."
Set-Location "$root\backend"
if (-Not (Test-Path ".venv")) {
    python -m venv .venv
}

& ".\.venv\Scripts\Activate.ps1"
python -m pip install --upgrade pip
pip install -r requirements.txt

if (-Not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created backend .env from template."
}

Write-Host "==> Bootstrapping frontend dependencies..."
Set-Location "$root\frontend"
if (-Not (Test-Path ".env.local")) {
    Copy-Item ".env.local.example" ".env.local"
}
npm install

Write-Host "Bootstrap complete."
