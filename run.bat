@echo off
echo ========================================
echo Starting TikTok Bot
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate

echo Starting bot...
python main.py

echo.
echo Bot stopped. Press any key to exit...
pause