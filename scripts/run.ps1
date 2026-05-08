Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backendPath = Join-Path $repoRoot "backend"
$frontendPath = Join-Path $repoRoot "frontend"

function Stop-BackgroundJob {
	param([System.Management.Automation.Job]$Job)

	if ($null -ne $Job) {
		Stop-Job -Job $Job -ErrorAction SilentlyContinue
		Remove-Job -Job $Job -Force -ErrorAction SilentlyContinue
	}
}

Write-Host "Starting backend on http://127.0.0.1:8000"
Write-Host "Starting frontend on http://127.0.0.1:5173"

$backendJob = Start-Job -ScriptBlock {
	param([string]$Path)

	Set-Location $Path
	python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
} -ArgumentList $backendPath

Push-Location $frontendPath
try {
	corepack pnpm dev --host 127.0.0.1 --port 5173
}
finally {
	Pop-Location
	Stop-BackgroundJob -Job $backendJob
}