@echo off
setlocal
cd /d "%~dp0"

echo === WorkPlan Windows build ===
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python was not found.
    echo Install Python 3.11 or 3.12 and enable "Add python.exe to PATH".
    pause
    exit /b 1
)

python --version

if not exist ".venv\Scripts\python.exe" (
    echo.
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 goto fail
)

set "PY=.venv\Scripts\python.exe"

echo.
echo Installing dependencies...
"%PY%" -m pip install --upgrade pip
if errorlevel 1 goto fail
"%PY%" -m pip install -r requirements.txt
if errorlevel 1 goto fail

set "ICON="
if exist "app.ico" set "ICON=--icon app.ico"

echo.
echo Building exe...
"%PY%" -m PyInstaller --noconfirm --onefile --windowed --name WorkPlan %ICON% run.py
if errorlevel 1 goto fail

echo.
echo Build finished: dist\WorkPlan.exe
echo You can rename WorkPlan.exe after build if needed.
pause
exit /b 0

:fail
echo.
echo BUILD FAILED.
echo Copy the error text above and send it back.
pause
exit /b 1
