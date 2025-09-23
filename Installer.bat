@echo off
echo Starting HomeCenter Installer...
echo.

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Downloading Python 3.13...
    curl -o python-3.13.3.exe https://www.python.org/ftp/python/3.13.3/python-3.13.3-amd64.exe
    echo Installing Python 3.13...
    python-3.13.3.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-3.13.3.exe
)

@REM :: Create virtual environment
@REM echo Creating virtual environment...
@REM python -m venv venv

@REM :: Activate virtual environment
@REM echo Activating virtual environment...
@REM call venv\Scripts\activate.bat

:: Upgrade pip
python -m pip install --upgrade pip

:: Install required packages
echo Installing required packages...
pip install flask==3.1.0
pip install flask-socketio==5.5.1
pip install eventlet==0.40.0
pip install python-dotenv==1.1.1
pip install requests==2.32.3
pip install wakeonlan==3.1.0
pip install flask-httpauth==4.8.0
pip install werkzeug==3.1.3
pip install psutil==7.0.0
pip install ipaddress==1.0.23
pip install playwright==1.55.0

:: Install Playwright browsers
echo Installing Playwright browsers...
playwright install chromium

:: Create necessary directories
echo Creating required directories...
mkdir static\logs 2>nul
mkdir static\DB 2>nul

:: Create config file if it doesn't exist
if not exist config.env (
    echo Creating config.env file...
    copy config.env.example config.env
    echo Please edit config.env with your credentials and API keys
)

echo.
echo Installation complete!
echo Please edit config.env with your credentials and API keys before running the application
echo To start the application, run HCStartup.bat
echo.
pause
