@echo off
setlocal
title Idea Collector

cd /d "%~dp0"
set "ROOT=%~dp0"
set "VENV_PY=%ROOT%venv\Scripts\python.exe"

where python >nul 2>nul
if errorlevel 1 (
    echo Python was not found. Please install Python and add it to your PATH.
    pause
    exit /b 1
)

if not exist "%VENV_PY%" (
    echo Creating virtual environment and installing dependencies. This only takes time on the first start...
    python -m venv "%ROOT%venv"
    if errorlevel 1 goto :error
    "%VENV_PY%" -m pip install --upgrade pip
    if errorlevel 1 goto :error
    "%VENV_PY%" -m pip install -r "%ROOT%requirements.txt"
    if errorlevel 1 goto :error
)

echo.
echo Starting Idea Collector...
echo To stop the app, close the app window or this window.
echo.

"%VENV_PY%" "%ROOT%run_desktop.py" %*
goto :end

:error
echo.
echo Startup failed. Please check the error message above.
pause

:end
endlocal
