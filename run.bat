@echo off

:: 檢查管理員權限
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Requesting administrator privileges...

    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

echo Running "bb-close-process-lasso-gui.py"...

if not exist ".venv" (
    echo .venv not found. Creating virtual environment...

    python -m venv .venv
    .venv\Scripts\pip.exe install -r requirements.txt
)

.venv\Scripts\python.exe bb-close-process-lasso-gui.py

echo.
echo Application exited.
pause