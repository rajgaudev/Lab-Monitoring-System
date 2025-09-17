@echo off
SETLOCAL ENABLEEXTENSIONS

echo [*] Creating monitoring folder...
mkdir C:\Monitoring >nul 2>&1

echo [*] Copying script...
xcopy /Y "%~dp0system.py" "C:\Monitoring\"

echo [*] Checking Python installation...
where python >nul 2>&1
IF ERRORLEVEL 1 (
    echo ❌ Python not found. Please install Python 3.x and try again.
    pause
    exit /b 1
) ELSE (
    echo ✅ Python found.
)

echo [*] Installing required Python packages...
python -m ensurepip --upgrade
python -m pip install --upgrade pip
python -m pip install psutil requests

echo [*] Installing PyInstaller...
pip install pyinstaller

echo [*] Building standalone executable from system.py...
cd C:\Monitoring
pyinstaller --noconsole --onefile system.py

echo.
echo ✅ Installation and Build Complete!
echo ▶️ Executable created at: C:\Monitoring\dist\system.exe
echo.
echo You can run it directly by double-clicking:
echo C:\Monitoring\dist\system.exe
echo ===========================================

pause

