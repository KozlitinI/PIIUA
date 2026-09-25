@echo off
chcp 65001 >nul
title PIIUA - Ukrainian PII Pseudonymization Service
echo ======================================================================
echo   PIIUA - Веб-сервіс псевдонімізації персональних даних
echo ======================================================================
echo.

cd /d "%~dp0"

if not exist ".\venv\Scripts\python.exe" (
    echo [ПОМИЛКА] Віртуальне середовище venv не знайдено!
    echo Будь ласка, спочатку запустіть install.bat для автоматичного встановлення.
    echo.
    pause
    exit /b 1
)

echo Запуск сервера PIIUA...
echo Відкриваємо http://127.0.0.1:8000 у вашому браузері...
echo.
".\venv\Scripts\python.exe" "run_server.py"
pause
