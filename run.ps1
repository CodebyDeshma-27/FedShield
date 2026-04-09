#!/usr/bin/env powershell
# FedShield Launcher - Clean output
# Suppresses verbose dependency logs

# Get the project directory
$projectDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition

# Set PYTHONPATH to include project directory for sitecustomize.py
$env:PYTHONPATH = $projectDir

# Activate virtual environment if needed (adjust if using different shell)
# . .\venv\Scripts\Activate.ps1

# Run the pipeline with clean output
Write-Host "🚀 Starting FedShield Pipeline..." -ForegroundColor Green
Write-Host ""

python "$projectDir\run.py" @args

Write-Host ""
Write-Host "✅ Pipeline execution complete!" -ForegroundColor Green
