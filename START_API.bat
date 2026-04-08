@echo off
REM ============================================================
REM FRAUD DETECTION API - QUICK START (WINDOWS BATCH)
REM Run this file to start the API
REM ============================================================

echo.
echo ================================================
echo   Fraud Detection API - Quick Start
echo ================================================
echo.

REM Step 1: Navigate to project
echo [STEP 1] Navigating to project directory...
cd /d "c:\Projects\fraud-intelligence-network (1)"
echo OK - Current directory: %cd%
echo.

REM Step 2: Check model exists
echo [STEP 2] Checking if model exists...
if exist "results\models\dp_protected_model.pth" (
    echo OK - Model found
) else (
    echo ERROR - Model not found!
    echo Please run: python main_unified_pipeline.py
    pause
    exit /b 1
)
echo.

REM Step 3: Display info
echo [STEP 3] API Information:
echo   API URL: http://localhost:5000
echo.
echo   Endpoints:
echo     - GET /health          : Health check
echo     - GET /info            : API documentation
echo     - GET /privacy         : Privacy details
echo     - POST /predict        : Fraud prediction
echo     - POST /batch-predict  : Batch predictions
echo.

REM Step 4: Start API
echo [STEP 4] Starting API server...
echo   Command: python api/app.py
echo.
echo   >>> Press Ctrl+C to stop the server <<<
echo.

python api/app.py

pause
