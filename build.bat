@echo off

cd /d "%~dp0"

echo [1/3] Check the virtual environment...

if not exist ".venv" (
    echo .venv not found. Creating virtual environment...

    python -m venv .venv
    .venv\Scripts\pip.exe install -r requirements.txt
)

echo.
echo [2/3] Building with PyInstaller...

.venv\Scripts\pyinstaller.exe --noconfirm --onefile --uac-admin ^
 --name="BB Close Process Lasso GUI" ^
 bb-close-process-lasso-gui.py

if errorlevel 1 (
    echo PyInstaller failed.
    pause
    exit /b 1
)

echo.
echo [3/3] Cleaning up build files...

timeout /t 2 /nobreak >nul

if exist "build" (
    rmdir /S /Q "build"
)

if exist "BB Close Process Lasso GUI.spec" (
    del /Q "BB Close Process Lasso GUI.spec"
)

echo.
echo Build completed.
pause