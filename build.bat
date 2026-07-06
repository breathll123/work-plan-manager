@echo off
chcp 65001 >nul
echo === 工作计划 打包脚本(需要 Windows + Python 3.11+)===
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt
if exist app.ico (
    set ICON=--icon app.ico
) else (
    set ICON=
)
pyinstaller --noconfirm --onefile --windowed --name 工作计划 %ICON% run.py
echo.
echo 打包完成:dist\工作计划.exe
pause
