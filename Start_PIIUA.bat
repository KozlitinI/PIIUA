@echo off
title PIIUA - Ukrainian PII Pseudonymization Service
echo ======================================================================
echo   Launching PIIUA Web Application...
echo   Opening http://127.0.0.1:8000 in your browser...
echo ======================================================================
cd /d "%~dp0"
".\venv\Scripts\python.exe" "run_server.py"
pause
