@echo off
cd /d "%~dp0"
echo Gene Analysis Assistant - Database Downloader
echo =============================================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing requests library...
    pip install requests urllib3
)

echo Running download script...
python download_data.py
pause
