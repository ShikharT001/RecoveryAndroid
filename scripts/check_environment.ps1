# RecoveryAndroid Environment Diagnostic Check
Write-Host "[*] Checking RecoveryAndroid Environment..." -ForegroundColor Cyan

# 1. Python in .venv
if (Test-Path ".venv\Scripts\python.exe") {
    $ver = & ".\.venv\Scripts\python.exe" --version
    Write-Host "[OK] Virtual Python: $ver" -ForegroundColor Green
} else {
    Write-Host "[FAIL] .venv\Scripts\python.exe not found!" -ForegroundColor Red
}

# 2. Check ADB
$adb = Get-Command adb -ErrorAction SilentlyContinue
if ($adb) {
    Write-Host "[OK] Android ADB found in PATH: $($adb.Source)" -ForegroundColor Green
} else {
    Write-Host "[!] ADB not in PATH. Will check Android SDK local paths or RecoverX settings." -ForegroundColor Yellow
}

# 3. Run application environment check
& ".\.venv\Scripts\python.exe" main.py --cli-check
