# SmartInvoice AI - Database Backup Utility
# Performs safe online snapshot backup of the local SQLite database

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path "$ScriptDir\.."
$PythonExe = "$ProjectRoot\backend\.venv\Scripts\python.exe"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  SMARTINVOICE AI - DATABASE BACKUP" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan

if (-Not (Test-Path $PythonExe)) {
    Write-Host "[ERROR] Python virtual environment not found at: $PythonExe" -ForegroundColor Red
    exit 1
}

Write-Host "[1/2] Creating online SQLite snapshot..." -ForegroundColor Yellow
$BackupOutput = & $PythonExe -c "import sys; sys.path.insert(0, 'backend'); from app.services.backup_service import backup_database, list_backups; b = backup_database(); backups = list_backups(); print(f'OK|{b.name}|{len(backups)}')"

if ($LASTEXITCODE -eq 0 -and $BackupOutput -match "OK\|(?<name>[^|]+)\|(?<count>\d+)") {
    $BackupName = $Matches["name"]
    $BackupCount = $Matches["count"]
    Write-Host "[2/2] Backup created successfully: $BackupName" -ForegroundColor Green
    Write-Host "      Total stored snapshots: $BackupCount (data/backups/)" -ForegroundColor DarkGray
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "  DATABASE SECURED" -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Database backup failed. Details:" -ForegroundColor Red
    Write-Host $BackupOutput -ForegroundColor Red
    exit 1
}
