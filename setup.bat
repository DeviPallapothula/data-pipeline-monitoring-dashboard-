@echo off
REM Setup Script for Data Pipeline Monitoring Dashboard (Windows)
REM This script automates the setup process for the project

echo 🚀 Setting up Data Pipeline Monitoring Dashboard...
echo ==================================================
echo.

REM Check if Python is installed
echo 📋 Checking prerequisites...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    exit /b 1
)
echo ✅ Python found

REM Check if pip is installed
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed. Please install pip.
    exit /b 1
)
echo ✅ pip found

echo.
echo 📦 Setting up virtual environment...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ⚠️  Virtual environment already exists
)

REM Activate virtual environment
echo.
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo.
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip --quiet

REM Install dependencies
echo.
echo 📥 Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt
    echo ✅ Dependencies installed
) else (
    echo ❌ requirements.txt not found!
    exit /b 1
)

REM Create necessary directories
echo.
echo 📁 Creating necessary directories...
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "config" mkdir config
echo ✅ Directories created

REM Initialize database
echo.
echo 🗄️  Initializing database...
python -c "from src.models.database import init_database; init_database()"
if errorlevel 1 (
    echo ❌ Failed to initialize database
    exit /b 1
)
echo ✅ Database initialized

REM Create .env file if it doesn't exist
echo.
echo ⚙️  Setting up environment variables...
if not exist ".env" (
    if exist "config\.env.example" (
        copy config\.env.example .env
        echo ✅ .env file created from template
        echo ⚠️  Please edit .env file with your configuration
    ) else (
        echo ⚠️  .env.example not found, skipping .env creation
    )
) else (
    echo ⚠️  .env file already exists, skipping
)

echo.
echo ==================================================
echo ✅ Setup completed successfully!
echo.
echo 📝 Next steps:
echo    1. Activate virtual environment: venv\Scripts\activate
echo    2. (Optional) Edit .env file with your settings
echo    3. Run the application: python app.py
echo    4. Open browser: http://localhost:5000
echo    5. (Optional) Add sample data: python scripts\add_sample_data.py
echo.
echo 💡 Tip: You can run this script again safely - it won't overwrite existing files

pause
