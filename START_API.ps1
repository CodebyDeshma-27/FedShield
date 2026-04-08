#!/usr/bin/env powershell
# ============================================================
# FRAUD DETECTION API - QUICK START
# Run this file to start the API and test it
# ============================================================

Write-Host "================================================"
Write-Host "  Fraud Detection API - Quick Start"
Write-Host "================================================" -ForegroundColor Green

# Step 1: Navigate to project directory
Write-Host "`n[STEP 1] Navigating to project directory..." -ForegroundColor Yellow
Set-Location "c:\Projects\fraud-intelligence-network (1)"
Write-Host "✅ Current directory: $(Get-Location)" -ForegroundColor Green

# Step 2: Check if model exists
Write-Host "`n[STEP 2] Checking if model exists..." -ForegroundColor Yellow
if (Test-Path "results/models/dp_protected_model.pth") {
    Write-Host "✅ Model found: results/models/dp_protected_model.pth" -ForegroundColor Green
} else {
    Write-Host "❌ Model not found! Run this first:" -ForegroundColor Red
    Write-Host "   python main_unified_pipeline.py" -ForegroundColor Yellow
    exit
}

# Step 3: Check if dependencies are installed
Write-Host "`n[STEP 3] Checking dependencies..." -ForegroundColor Yellow
$packages = @("flask", "torch", "numpy")
foreach ($package in $packages) {
    try {
        python -c "import $package" 2>$null
        Write-Host "✅ $package installed" -ForegroundColor Green
    } catch {
        Write-Host "❌ $package not found. Installing..." -ForegroundColor Red
        pip install $package
    }
}

# Step 4: Display API info
Write-Host "`n[STEP 4] API Information:" -ForegroundColor Yellow
Write-Host "  API URL: http://localhost:5000" -ForegroundColor Cyan
Write-Host "  Endpoints:" -ForegroundColor Cyan
Write-Host "    - GET /health          : Health check" -ForegroundColor Cyan
Write-Host "    - GET /info            : API documentation" -ForegroundColor Cyan
Write-Host "    - GET /privacy         : Privacy details" -ForegroundColor Cyan
Write-Host "    - POST /predict        : Fraud prediction" -ForegroundColor Cyan
Write-Host "    - POST /batch-predict  : Batch predictions" -ForegroundColor Cyan

# Step 5: Start API
Write-Host "`n[STEP 5] Starting API server..." -ForegroundColor Yellow
Write-Host "  Command: python api/app.py" -ForegroundColor Cyan
Write-Host "`n  >>> Press Ctrl+C to stop the server <<<" -ForegroundColor Red

python api/app.py
