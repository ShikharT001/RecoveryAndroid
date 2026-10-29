# RecoveryAndroid Development Setup Script for Windows PowerShell
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   RecoveryAndroid -- Development Environment Setup       " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Python version
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[!] Python not found on PATH. Checking uv..." -ForegroundColor Yellow
}

# 2. Check virtual environment
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[+] Creating Python 3.12 virtual environment..." -ForegroundColor Green
    uv venv --python 3.12 .venv
} else {
    Write-Host "[*] Existing virtual environment found in .venv" -ForegroundColor Green
}

# 3. Install dependencies
Write-Host "[+] Installing required dependencies..." -ForegroundColor Green
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt

# 4. Verify installation
Write-Host "[+] Verifying core modules..." -ForegroundColor Green
& ".\.venv\Scripts\python.exe" main.py --cli-check

Write-Host "`n[OK] RecoverX development environment is ready!" -ForegroundColor Green
Write-Host "Run the application with: .\.venv\Scripts\python.exe main.py" -ForegroundColor Cyan
