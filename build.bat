@echo off
echo Building PIIUA Windows Installer & Portable Package...
cd /d "%~dp0"
"venv\Scripts\python.exe" "build_installer.py"
pause
