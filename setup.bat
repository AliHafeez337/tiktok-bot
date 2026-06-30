@echo off
echo ========================================
echo TikTok Bot Setup (with VENV)
echo ========================================
echo.
echo Step 1: Creating virtual environment...
python -m venv venv
echo.
echo Step 2: Activating venv and installing packages...
call venv\Scripts\activate
pip install --upgrade pip
pip install selenium webdriver-manager beautifulsoup4 lxml pyyaml python-dotenv
echo.
echo Step 3: Creating necessary directories...
mkdir data\logs 2>nul
mkdir sessions\chrome 2>nul
echo.
echo Step 4: Setup complete!
echo.
echo ========================================
echo HOW TO RUN:
echo ========================================
echo 1. Activate venv: venv\Scripts\activate
echo 2. Edit config.yaml with your credentials
echo 3. Add comments to input/comments.txt
echo 4. Run: python main.py
echo.
echo MULTIPLE ACCOUNTS (separate Chrome windows):
echo   Terminal 1: python main.py --profile account1
echo   Terminal 2: python main.py --profile account2
echo   Terminal 3: python main.py --profile account3
echo   List profiles: python main.py --list-profiles
echo   Log in once per profile; sessions are saved under sessions\
echo.
pause