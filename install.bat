@echo off
chcp 65001 >nul
title PIIUA - Автоматичне встановлення
echo ======================================================================
echo   PIIUA - Встановлення залежностей та моделей (Open Source)
echo ======================================================================
echo.

cd /d "%~dp0"

:: 1. Перевірка наявності Python у системі
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ПОМИЛКА] Python не знайдено в системній змінній PATH!
    echo.
    echo Інструкція зі встановлення Python:
    echo 1. Завантажте Python 3.11 або 3.12 з офіційного сайту: https://www.python.org/downloads/
    echo 2. ПІД ЧАС ВСТАНОВЛЕННЯ обов'язково поставте галочку: "Add python.exe to PATH"
    echo.
    echo Або встановіть через консоль Windows (winget):
    echo    winget install Python.Python.3.11
    echo.
    pause
    exit /b 1
)

echo [1/4] Знайдено Python у системі:
python --version
echo.

:: 2. Створення віртуального середовища venv
if not exist "venv" (
    echo [2/4] Створення віртуального середовища venv...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ПОМИЛКА] Не вдалося створити venv. Перевірте інсталяцію Python.
        pause
        exit /b 1
    )
) else (
    echo [2/4] Віртуальне середовище venv вже існує.
)
echo.

:: 3. Оновлення pip та встановлення залежностей
echo [3/4] Встановлення необхідних пакетах та моделей spaCy...
echo Це може зайняти кілька хвилин (завантаження моделей мови)...
echo.
".\venv\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
if %errorlevel% neq 0 (
    echo [ПОМИЛКА] Не вдалося оновити pip.
    pause
    exit /b 1
)

".\venv\Scripts\python.exe" -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ПОМИЛКА] Помилка при встановленні залежностей з requirements.txt.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo   [УСПІХ] Встановлення PIIUA завершено успішно!
echo ======================================================================
echo.
echo Для запуску програми використуйте файл: run_app.bat
echo.
pause
