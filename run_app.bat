@echo off
title PIIUA - Ukrainian PII Pseudonymization Service

cd /d "%~dp0"

if not exist ".\venv\Scripts\python.exe" goto ERR_NO_VENV

echo ======================================================================
echo   PIIUA - Ukrainian PII Pseudonymization and Restoration Service
echo ======================================================================
echo.
echo Launching PIIUA Server...
echo Opening http://127.0.0.1:8000 in your browser...
echo.
".\venv\Scripts\python.exe" "run_server.py"
goto END

:ERR_NO_VENV
echo ======================================================================
echo [ERROR] Virtual environment venv not found!
echo Please run install.bat first to set up the environment.
echo ======================================================================
echo.
pause
exit /b 1

:END
pause
