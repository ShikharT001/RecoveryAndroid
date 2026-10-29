# RecoveryAndroid Windows PyInstaller Build Script
Write-Host "==========================================================" -ForegroundColor Magenta
Write-Host "   RecoveryAndroid -- Windows Standalone App Builder      " -ForegroundColor Magenta
Write-Host "==========================================================" -ForegroundColor Magenta

$pyinstaller = ".\.venv\Scripts\pyinstaller.exe"

if (-not (Test-Path $pyinstaller)) {
    Write-Host "[!] PyInstaller not found in .venv." -ForegroundColor Yellow
    exit 1
}

Write-Host "[+] Cleaning previous build artifacts..." -ForegroundColor Gray
Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue

Write-Host "[+] Running PyInstaller build..." -ForegroundColor Cyan

$buildArgs = @(
    "--noconfirm",
    "--onedir",
    "--windowed",
    "--name", "RecoveryAndroid",
    "--add-data", "app/resources;app/resources",
    "--hidden-import", "PIL",
    "--hidden-import", "pydantic",
    "--hidden-import", "platformdirs",
    "--hidden-import", "cryptography",
    "--hidden-import", "sqlite3",
    "--hidden-import", "PySide6",
    "main.py"
)

$proc = Start-Process -FilePath $pyinstaller -ArgumentList $buildArgs -NoNewWindow -Wait -PassThru

if ($proc.ExitCode -eq 0) {
    Write-Host "`n[OK] Build completed successfully!" -ForegroundColor Green
    Write-Host "Standalone binary located at: dist\RecoveryAndroid\RecoveryAndroid.exe" -ForegroundColor Cyan
} else {
    Write-Host "`n[FAIL] Build failed with exit code $($proc.ExitCode)" -ForegroundColor Red
}
