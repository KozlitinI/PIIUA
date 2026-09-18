#!/usr/bin/env python
"""
Build script for PIIUA Windows Installer & Portable Executable.
Uses PyInstaller to bundle Python + Uvicorn + FastAPI + Presidio + spaCy,
and optional Inno Setup / Zip archiving to produce final distribution installer.
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DIST_DIR = ROOT_DIR / "dist"
INSTALLER_DIR = ROOT_DIR / "dist_installer"
VENV_PYTHON = ROOT_DIR / "venv" / "Scripts" / "python.exe"
PYINSTALLER_EXE = ROOT_DIR / "venv" / "Scripts" / "pyinstaller.exe"

def run_cmd(cmd, cwd=ROOT_DIR):
    print(f"\n[BUILD] Running command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    res = subprocess.run(cmd, cwd=cwd, shell=True if isinstance(cmd, str) else False)
    if res.returncode != 0:
        print(f"[BUILD ERROR] Command failed with return code {res.returncode}")
        sys.exit(res.returncode)

def kill_existing_processes():
    try:
        subprocess.run("taskkill /F /IM PIIUA.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def main():
    print("=" * 70)
    print("  BUILDING PIIUA WINDOWS INSTALLER & PORTABLE PACKAGE")
    print("=" * 70)

    kill_existing_processes()

    # 1. Check Python virtual environment
    if not VENV_PYTHON.exists():
        print(f"[ERROR] Virtual environment python not found at {VENV_PYTHON}")
        sys.exit(1)

    # 2. Clean previous build artifacts
    print("\n[STEP 1/3] Cleaning previous build folders...")
    for folder in [ROOT_DIR / "build", DIST_DIR, INSTALLER_DIR]:
        if folder.exists():
            print(f"  Removing {folder}...")
            shutil.rmtree(folder, ignore_errors=True)

    INSTALLER_DIR.mkdir(parents=True, exist_ok=True)

    # 3. Run PyInstaller build
    print("\n[STEP 2/3] Compiling standalone executable with PyInstaller...")
    spec_path = ROOT_DIR / "piiua.spec"
    
    if PYINSTALLER_EXE.exists():
        pyinstaller_bin = str(PYINSTALLER_EXE)
    else:
        pyinstaller_bin = f'"{VENV_PYTHON}" -m PyInstaller'

    run_cmd([pyinstaller_bin, str(spec_path), "--noconfirm"])

    built_exe = DIST_DIR / "PIIUA" / "PIIUA.exe"
    if not built_exe.exists():
        print(f"[ERROR] PyInstaller build failed. {built_exe} was not created.")
        sys.exit(1)

    print(f"\n[SUCCESS] PyInstaller bundle compiled at: {built_exe.parent}")

    # 4. Packaging
    print("\n[STEP 3/3] Creating Windows Installer & Zip Packages...")
    
    # Check for Inno Setup compiler
    iscc_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
    ]
    iscc_bin = None
    for p in iscc_paths:
        if os.path.exists(p):
            iscc_bin = p
            break

    if iscc_bin:
        print(f"  Found Inno Setup Compiler: {iscc_bin}")
        iss_file = ROOT_DIR / "PIIUA_Setup.iss"
        run_cmd([f'"{iscc_bin}"', f'"{iss_file}"'])
        print(f"  [SUCCESS] Inno Setup Installer created in: {INSTALLER_DIR}")
    else:
        print("  [NOTE] Inno Setup (ISCC.exe) not found on PATH. Creating Portable Zip Archive...")

    # Always create a Portable ZIP archive as well
    zip_path = INSTALLER_DIR / "PIIUA_Portable_v1.0.0"
    shutil.make_archive(str(zip_path), 'zip', DIST_DIR / "PIIUA")
    print(f"  [SUCCESS] Portable Zip Archive created at: {zip_path}.zip")

    print("\n" + "=" * 70)
    print("  BUILD COMPLETE SUCCESSFULLY!")
    print(f"  Executable location: {built_exe}")
    print(f"  Distribution files:  {INSTALLER_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
