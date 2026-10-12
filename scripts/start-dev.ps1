# SmartInvoice AI - 1-Click Local Launch Script
# Starts both FastAPI Backend and Vite Frontend in separate windows

$ErrorActionPreference = "SilentlyContinue"

# Detect Primary Local Network IPv4 Address
$primaryIp = (Get-CimInstance Win32_NetworkAdapterConfiguration | Where-Object IPEnabled | Select-Object -ExpandProperty IPAddress | Where-Object { $_ -match "^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$" -and $_ -notmatch "^127\." -and $_ -notmatch "^169\.254\." } | Select-Object -First 1)
if (-not $primaryIp) { $primaryIp = "127.0.0.1" }

Write-Host "==========================================================" -ForegroundColor Red
Write-Host "::: SMARTINVOICE AI - INDUSTRIAL WORKSPACE [NOTHING OS] :::" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Red
Write-Host ""
Write-Host "  PC Web App   : http://localhost:5173" -ForegroundColor Green
Write-Host "  Phone Wi-Fi  : http://$($primaryIp):5173" -ForegroundColor Yellow
Write-Host "  API Backend  : http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "==========================================================" -ForegroundColor Red

# 1. Start FastAPI Backend in a new window using the virtualenv python directly
Write-Host "[1/2] Starting FastAPI Backend on port 8000 (0.0.0.0)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\backend'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# 2. Start Vite Frontend in a new window
Write-Host "[2/2] Starting Vite Frontend on port 5173 (0.0.0.0)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\frontend'; npm.cmd run dev"

Write-Host ""
Write-Host ">>> Both servers launched successfully in separate windows!" -ForegroundColor Green
Write-Host ">>> On your PC: Open http://localhost:5173" -ForegroundColor White
Write-Host ">>> On your Phone: Connect to same Wi-Fi and open http://$($primaryIp):5173" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Red
