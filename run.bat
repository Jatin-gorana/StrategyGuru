@echo off
REM Trading Strategy Backtester - Quick Start Script for Windows

echo ================================
echo Trading Strategy Backtester
echo Quick Start Setup
echo ================================
echo.

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Found: %PYTHON_VERSION%
echo.

REM Check Node.js
echo Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed. Please install Node.js 18 or higher.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Found: Node.js %NODE_VERSION%
echo.

REM Setup Backend
echo Setting up Backend...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
pip install -q -r requirements.txt
echo [OK] Backend dependencies installed
echo.

REM Setup Frontend
echo Setting up Frontend...
cd frontend

if not exist "node_modules" (
    echo Installing Node dependencies...
    call npm install -q
)

REM Create .env.local if it doesn't exist
if not exist ".env.local" (
    echo Creating .env.local...
    (
        echo NEXT_PUBLIC_API_URL=http://localhost:8000
    ) > .env.local
)

echo [OK] Frontend dependencies installed
cd ..
echo.

REM Display instructions
echo ================================
echo Setup Complete!
echo ================================
echo.
echo To start the application, open TWO command prompt windows:
echo.
echo Terminal 1 - Backend API:
echo   venv\Scripts\activate.bat
echo   python backend/main.py
echo.
echo Terminal 2 - Frontend:
echo   cd frontend
echo   npm run dev
echo.
echo Then open your browser to:
echo   http://localhost:3000
echo.
echo API Documentation:
echo   http://localhost:8000/docs
echo.
echo Happy backtesting! 🚀
echo.
pause
