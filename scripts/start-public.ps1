# SmartInvoice AI - Start Public Tunnel (No Same Wi-Fi Needed)
# Runs locally on your PC, but creates a public HTTPS link accessible on mobile from ANY network (4G/5G/any Wi-Fi)

$ErrorActionPreference = "SilentlyContinue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Resolve-Path "$ScriptDir\.."
$Cloudflared = "$ScriptDir\bin\cloudflared.exe"

Write-Host "==========================================================" -ForegroundColor Red
Write-Host "::: SMARTINVOICE AI - PUBLIC MOBILE ACCESS (ANY NETWORK) :::" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Red
Write-Host ""

# 1. Start FastAPI Backend in separate window
Write-Host "[1/3] Starting Backend on port 8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot\backend'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

# 2. Start Vite Frontend in separate window
Write-Host "[2/3] Starting Frontend on port 5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot\frontend'; npm.cmd run dev"

Start-Sleep -Seconds 3

# 3. Start Cloudflare Tunnel for Port 5173 (which automatically proxies to Backend)
Write-Host "[3/3] Creating Public HTTPS Link for Mobile..." -ForegroundColor Yellow
Write-Host ""
Write-Host ">>> Look for the generated 'https://xxxx.trycloudflare.com' link below:" -ForegroundColor Green
Write-Host ">>> Open that link on your phone from ANY Wi-Fi or Mobile Data (4G/5G)!" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Red
Write-Host ""

& $Cloudflared tunnel --url http://localhost:5173
