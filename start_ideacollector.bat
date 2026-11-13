@echo off
setlocal
title Idea Collector

cd /d "%~dp0"
set "ROOT=%~dp0"
set "VENV_PY=%ROOT%venv\Scripts\python.exe"
set "HOST=127.0.0.1"
set "PORT=8000"
set "URL=http://%HOST%:%PORT%"

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

cd /d "%ROOT%idea_collector"

echo Applying database migrations...
"%VENV_PY%" manage.py migrate
if errorlevel 1 goto :error

echo.
echo Starting Idea Collector at %URL%
echo The browser will open in a few seconds.
echo To stop the server, close this window or press Ctrl+C.
echo.

start "" /min cmd /c "timeout /t 2 /nobreak >nul & start %URL%"
"%VENV_PY%" manage.py runserver %HOST%:%PORT%
goto :end

:error
echo.
echo Startup failed. Please check the error message above.
pause

:end
endlocal
