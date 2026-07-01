@echo off
title TikTok Automation Bot
color 0A

echo ==========================================
echo        TikTok Automation Bot
echo ==========================================
echo.

REM Change to the folder where this BAT file is located
cd /d "%~dp0"

REM Activate virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo.
    pause
    exit /b
)

call venv\Scripts\activate

echo Existing Profiles
echo -----------------

set count=0

for /d %%D in (sessions\*) do (
    set /a count+=1
    call set profile[%%count%%]=%%~nxD
    call echo %%count%%. %%~nxD
)

echo.
echo N. Create New Profile
echo.

set /p choice=Select profile number or press N:

if /I "%choice%"=="N" goto NEWPROFILE

REM Get selected profile
call set PROFILE=%%profile[%choice%]%%

if "%PROFILE%"=="" (
    echo.
    echo Invalid selection.
    pause
    exit /b
)

goto STARTBOT

:NEWPROFILE
echo.
set /p PROFILE=Enter new profile name:

if "%PROFILE%"=="" (
    echo Profile name cannot be empty.
    pause
    exit /b
)

:STARTBOT
echo.
echo Target profiles (optional)
echo ---------------------------
echo Enter comma-separated TikTok usernames to use for this run.
echo Example: guiltyxapparel, brandymelvilleusa, lift_the_label
echo Press Enter to use target.txt instead.
echo.
set /p TARGETS=Targets:

echo.
echo ==========================================
echo Starting Profile: %PROFILE%
echo ==========================================
if not "%TARGETS%"=="" (
    echo Using custom targets: %TARGETS%
) else (
    echo Using targets from target.txt
)
echo.

if "%TARGETS%"=="" (
    python main.py -p %PROFILE%
) else (
    python main.py -p %PROFILE% --targets "%TARGETS%"
)

echo.
echo ==========================================
echo Bot Finished
echo ==========================================
pause