import os
import sys
import shutil
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DIST_DIR = ROOT_DIR / "dist"
PORTABLE_DIR = DIST_DIR / "PIIUA_Portable"
ZIP_PATH = DIST_DIR / "PIIUA_Portable_v1.0.0.zip"
INSTALLER_DIR = ROOT_DIR / "dist_installer"

def build_portable_dist():
    print("=" * 70)
    print("  BUILDING SELF-CONTAINED PORTABLE DISTRIBUTION FOR PIIUA")
    print("=" * 70)

    # 1. Clean previous builds
    print("\n[STEP 1/5] Cleaning previous dist folders...")
    if PORTABLE_DIR.exists():
        print(f"  Removing {PORTABLE_DIR}...")
        shutil.rmtree(PORTABLE_DIR, ignore_errors=True)
    if ZIP_PATH.exists():
        print(f"  Removing {ZIP_PATH}...")
        ZIP_PATH.unlink()

    PORTABLE_DIR.mkdir(parents=True, exist_ok=True)
    INSTALLER_DIR.mkdir(parents=True, exist_ok=True)

    # 2. Copy source code
    print("\n[STEP 2/5] Copying application code and static assets...")
    shutil.copytree(
        ROOT_DIR / "app",
        PORTABLE_DIR / "app",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )
    shutil.copy2(ROOT_DIR / "run_server.py", PORTABLE_DIR / "run_server.py")

    # 3. Copy virtualenv
    print("\n[STEP 3/5] Copying Python virtual environment and spaCy models...")
    shutil.copytree(
        ROOT_DIR / "venv",
        PORTABLE_DIR / "venv",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc")
    )

    # 4. Create launchers & README
    print("\n[STEP 4/5] Creating 1-click launcher scripts & instructions...")
    bat_content = (
        "@echo off\r\n"
        "title PIIUA - Ukrainian PII Pseudonymization Service\r\n"
        "echo ======================================================================\r\n"
        "echo   Запуск системи PIIUA (Псевдонімізація Персональних Даних)...\r\n"
        "echo   Сервер запускається на http://127.0.0.1:8000\r\n"
        "echo   Веб-браузер відкриється автоматично через декілька секунд...\r\n"
        "echo ======================================================================\r\n"
        "cd /d \"%~dp0\"\r\n"
        "\".\\venv\\Scripts\\python.exe\" \"run_server.py\"\r\n"
        "pause\r\n"
    )
    with open(PORTABLE_DIR / "Start_PIIUA.bat", "w", encoding="utf-8") as f:
        f.write(bat_content)

    readme_content = (
        "======================================================================\n"
        "  PIIUA - Система Псевдонімізації та Відновлення Персональних Даних\n"
        "======================================================================\n\n"
        "ІНСТРУКЦІЯ З ЗАПУСКУ:\n"
        "1. Двічі клацніть мишкою на файл 'Start_PIIUA.bat'.\n"
        "2. Зачекайте 1-2 секунди. Сервер запуститься і ваш веб-браузер\n"
        "   автоматично відкриє робочу сторінку: http://127.0.0.1:8000\n\n"
        "ПЕРЕВАГИ ПОРТАТИВНОГО ПАКЕТУ:\n"
        "- Не вимагає встановлення Python чи додаткових бібліотек.\n"
        "- Всі 3 спасі-моделі (uk_core_news_trf, uk_core_news_lg, uk_core_news_sm)\n"
        "  вже включено у склад пакунка.\n"
        "- Не вимагає прав Адміністратора чи змін у Захиснику Windows 11.\n\n"
        "Розробник: Козлітін Ігор (igor@kozlitin.net), Україна 2026.\n"
        "======================================================================\n"
    )
    with open(PORTABLE_DIR / "README_UA.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # 5. Pack into ZIP archive
    print("\n[STEP 5/5] Compiling Portable ZIP Distribution Archive...")
    shutil.make_archive(str(DIST_DIR / "PIIUA_Portable_v1.0.0"), "zip", PORTABLE_DIR)
    shutil.copy2(
        str(DIST_DIR / "PIIUA_Portable_v1.0.0.zip"),
        str(INSTALLER_DIR / "PIIUA_Portable_v1.0.0.zip")
    )

    print("\n" + "=" * 70)
    print("  PORTABLE DISTRIBUTION SUCCESSFULLY CREATED!")
    print(f"  Unpacked folder: {PORTABLE_DIR}")
    print(f"  ZIP Archive:     {ZIP_PATH}")
    print("=" * 70)

if __name__ == "__main__":
    build_portable_dist()
