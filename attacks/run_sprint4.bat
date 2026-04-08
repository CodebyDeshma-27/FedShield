@echo off
REM ========================================================================
REM Sprint 4 - Attack Evaluation Setup & Run Script
REM Windows Batch Script
REM ========================================================================

setlocal enabledelayedexpansion

echo.
echo ========================================================================
echo Privacy-Preserving Fraud Detection: Attack Evaluation
echo Sprint 4 Execution Script
echo ========================================================================
echo.

REM Check Python installation
echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found!
    echo Please install Python 3.8+ from https://www.python.org/
    exit /b 1
)
echo ✅ Python installed

REM Check if in correct directory
echo.
echo [2/4] Checking project directory...
if not exist "config.py" (
    echo ❌ ERROR: Not in project root directory!
    echo Please run this from: c:\Projects\fraud-intelligence-network
    echo Current directory: %CD%
    exit /b 1
)
echo ✅ In correct project directory

REM Install/update dependencies
echo.
echo [3/4] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ⚠️  Some packages may have failed to install, but continuing...
)
echo ✅ Dependencies checked

REM Run the evaluation
echo.
echo [4/4] Running attack evaluation...
echo ========================================================================
python attacks/run_evaluation.py

if errorlevel 1 (
    echo.
    echo ❌ Evaluation failed!
    echo Check errors above and run:
    echo   python attacks/run_evaluation.py
    exit /b 1
)

echo.
echo ========================================================================
echo ✅ EVALUATION COMPLETE!
echo ========================================================================
echo.
echo Results saved to:
echo   - results\attack_evaluation_results.json
echo   - results\attack_evaluation_report.txt
echo   - results\graphs\
echo.
echo View the text report:
echo   type results\attack_evaluation_report.txt
echo.
echo View JSON results:
echo   python -m json.tool results\attack_evaluation_results.json
echo.
echo Next sprint (Sprint 5):
echo   python experiments/all_experiments.py
echo.
echo ========================================================================

pause
