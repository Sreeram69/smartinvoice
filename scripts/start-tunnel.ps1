# SmartInvoice AI - Start Backend & Public HTTPS Tunnel
# Use this when running the frontend on Vercel or accessing from anywhere outside Wi-Fi!

Write-Host "==========================================================" -ForegroundColor Red
Write-Host "::: SMARTINVOICE AI - PUBLIC HTTPS BACKEND TUNNEL :::" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Red
Write-Host ""
Write-Host "1. Starting FastAPI Backend on port 8000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\..\backend'; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --host 0.0.0.0 --port 8000"

Start-Sleep -Seconds 2

Write-Host "2. Launching Public HTTPS Tunnel via Localtunnel..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Copy the generated 'https://xxxx.loca.lt' URL and paste it into your Vercel app's Backend Connection setting!" -ForegroundColor Green
Write-Host ""

cmd /c "npx --yes localtunnel --port 8000"
