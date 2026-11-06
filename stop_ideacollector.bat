@echo off
setlocal
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo The Python virtual environment was not found:
    echo   %~dp0venv\Scripts\python.exe
    echo Please set up the virtual environment first.
    pause
    exit /b 1
)

"venv\Scripts\python.exe" "%~dp0launcher.py" stop %*
