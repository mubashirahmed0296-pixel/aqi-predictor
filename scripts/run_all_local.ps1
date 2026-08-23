$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$root = Split-Path -Parent $PSScriptRoot
Set-Location "$root\backend"
& ".\.venv\Scripts\Activate.ps1"

function Invoke-Step {
    param(
        [string]$Label,
        [scriptblock]$Action
    )
    Write-Host "==> $Label"
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Label (exit code $LASTEXITCODE)"
    }
}

Invoke-Step "Checking MongoDB connectivity..." { python -c "from app.config import settings; from pymongo import MongoClient; c=MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=3000); c.admin.command('ping'); print('MongoDB ping ok:', settings.mongodb_uri)" }
Invoke-Step "Running historical backfill..." { python -m scripts.run_backfill }
Invoke-Step "Running training..." { python -m scripts.run_train }
Invoke-Step "Running quality audit..." { python -m scripts.run_quality_audit }
Invoke-Step "Generating EDA artifacts..." { python -m scripts.run_eda }
Invoke-Step "Generating SHAP explainability..." { python -m scripts.run_explainability }

Set-Location "$root"
Invoke-Step "Generating evidence snapshot..." { python -m backend.scripts.generate_evidence_pack }

Write-Host "Run complete. Start API with:"
Write-Host "  cd backend; .\.venv\Scripts\Activate.ps1; uvicorn app.api:app --reload --port 8000"
Write-Host "Start UI with:"
Write-Host "  cd frontend; npm run dev"
