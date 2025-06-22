@echo off
REM Zep Temporal Knowledge Graph Evaluation Setup Script for Windows
REM This script automates the setup process for running the Zep evaluation

echo 🚀 Zep Temporal Knowledge Graph Evaluation Setup
echo ================================================

REM Check if we're in the right directory
if not exist "requirements.txt" (
    echo [ERROR] Please run this script from the OpenDeepSearch project root directory
    pause
    exit /b 1
)

REM Step 1: Check Python version
echo [INFO] Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://python.org
    pause
    exit /b 1
)

REM Step 2: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    echo [SUCCESS] Virtual environment created
) else (
    echo [INFO] Virtual environment already exists
)

REM Step 3: Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat
echo [SUCCESS] Virtual environment activated

REM Step 4: Upgrade pip
echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

REM Step 5: Install dependencies
echo [INFO] Installing Python dependencies...
pip install -r requirements.txt

REM Step 6: Install Zep Cloud
echo [INFO] Installing Zep Cloud...
pip install zep-cloud
echo [SUCCESS] Zep Cloud installed

REM Step 7: Check for .env file
if not exist ".env" (
    echo [WARNING] No .env file found. Creating template...
    (
        echo # Zep Cloud Configuration
        echo ZEP_API_KEY=your_zep_api_key_here
        echo ZEP_BASE_URL=https://api.getzep.com
        echo.
        echo # LiteLLM Configuration ^(for evaluation^)
        echo LITELLM_MODEL=gemini/gemini-1.5-flash
    ) > .env
    echo [WARNING] Please edit .env file and add your Zep API key
    echo [WARNING] Get your API key from: https://www.getzep.com/
) else (
    echo [SUCCESS] .env file exists
)

REM Step 8: Check if Zep API key is configured
if exist ".env" (
    findstr /C:"your_zep_api_key_here" .env >nul
    if not errorlevel 1 (
        echo [WARNING] Zep API key not configured in .env file
        echo [WARNING] Please edit .env and replace 'your_zep_api_key_here' with your actual API key
    ) else (
        echo [SUCCESS] Zep API key appears to be configured
    )
)

REM Step 9: Check if SEC data exists
if not exist "temporal_evaluation\datasets\sec_filings_enhanced.json" (
    echo [WARNING] SEC filing dataset not found
    echo [WARNING] You may need to generate the dataset first
    echo [INFO] Checking if dataset generation script exists...
    
    if exist "temporal_evaluation\create_all_datasets.py" (
        echo [INFO] Found dataset generation script. Running it...
        cd temporal_evaluation
        python create_all_datasets.py
        cd ..
        echo [SUCCESS] Dataset generation completed
    ) else (
        echo [ERROR] Dataset generation script not found
        echo [ERROR] Please ensure the SEC filing dataset exists at: temporal_evaluation\datasets\sec_filings_enhanced.json
    )
) else (
    echo [SUCCESS] SEC filing dataset found
)

REM Step 10: Test basic setup
echo [INFO] Testing basic setup...
cd temporal_evaluation\zep

REM Test if we can import the required modules
python -c "import sys; sys.path.insert(0, 'tools'); from zep_temporal_kg_tool import ZepTemporalKGTool; print('✅ Zep tool import successful')"
if errorlevel 1 (
    echo [ERROR] Zep tool import failed
    cd ..\..
    pause
    exit /b 1
)

cd ..\..

echo [SUCCESS] Basic setup test completed

REM Step 11: Final instructions
echo.
echo 🎉 Setup completed successfully!
echo ================================
echo.
echo Next steps:
echo 1. Edit .env file and add your Zep API key
echo 2. Run: cd temporal_evaluation\zep
echo 3. Run: python load_sec_data_to_zep.py
echo 4. Run: python test_basic_zep.py
echo 5. Run: python run_zep_evaluation.py
echo.
echo For detailed instructions, see: ZEP_SETUP_GUIDE.md
echo.
echo To activate the virtual environment in the future:
echo   venv\Scripts\activate.bat
echo.

REM Check if user wants to proceed with data loading
set /p proceed="Would you like to proceed with loading SEC data into Zep? (y/n): "
if /i "%proceed%"=="y" (
    echo [INFO] Proceeding with SEC data loading...
    cd temporal_evaluation\zep
    python load_sec_data_to_zep.py
    cd ..\..
    echo [SUCCESS] SEC data loading completed
    
    set /p test="Would you like to run the basic Zep test? (y/n): "
    if /i "%test%"=="y" (
        echo [INFO] Running basic Zep test...
        cd temporal_evaluation\zep
        python test_basic_zep.py
        cd ..\..
        echo [SUCCESS] Basic Zep test completed
    )
)

echo [SUCCESS] Setup script completed!
echo [INFO] You can now run the full evaluation when ready
pause 