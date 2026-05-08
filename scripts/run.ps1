Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendPath = Join-Path $repoRoot "backend"

Write-Host "Starting backend on http://127.0.0.1:8000"
Write-Host "Frontend bootstrap is pending Fase 2."

Push-Location $backendPath
try {
	python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
}
finally {
	Pop-Location
}