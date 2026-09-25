@echo off
title PIIUA - Automatic Setup

cd /d "%~dp0"

echo ======================================================================
echo   PIIUA - Setup Dependencies and Models (Open Source)
echo ======================================================================
echo.

:: 1. Check Python installation
python --version >nul 2>&1
if errorlevel 1 goto ERR_NO_PYTHON

echo [1/4] Found Python in PATH:
python --version
echo.

:: 2. Create virtual environment
if exist "venv\Scripts\python.exe" goto VENV_EXISTS

echo [2/4] Creating virtual environment (venv)...
python -m venv venv
if errorlevel 1 goto ERR_VENV_FAIL
goto VENV_DONE

:VENV_EXISTS
echo [2/4] Virtual environment venv already exists.

:VENV_DONE
echo.

:: 3. Upgrade pip and install requirements
echo [3/4] Installing required packages and spaCy models...
echo This may take a few minutes (downloading language models)...
echo.

".\venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto ERR_PIP_FAIL

".\venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto ERR_REQ_FAIL

echo.
echo ======================================================================
echo   [SUCCESS] PIIUA installation completed successfully!
echo ======================================================================
echo.
echo To launch the application, run: run_app.bat
echo.
pause
exit /b 0

:ERR_NO_PYTHON
echo ======================================================================
echo [ERROR] Python was not found in your system PATH!
echo.
echo Installation steps:
echo 1. Download Python 3.11 or 3.12 from: https://www.python.org/downloads/
echo 2. Check the box: "Add python.exe to PATH" during installation.
echo.
echo Or via Windows console (winget):
echo    winget install Python.Python.3.11
echo ======================================================================
echo.
pause
exit /b 1

:ERR_VENV_FAIL
echo [ERROR] Failed to create virtual environment venv.
pause
exit /b 1

:ERR_PIP_FAIL
echo [ERROR] Failed to upgrade pip.
pause
exit /b 1

:ERR_REQ_FAIL
echo [ERROR] Failed to install packages from requirements.txt.
pause
exit /b 1
