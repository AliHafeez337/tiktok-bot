@echo off

title TikTok Automation Bot - Bulk Run

color 0A



echo ==========================================

echo     TikTok Automation Bot - Bulk Run

echo ==========================================

echo.



REM Change to the folder where this BAT file is located

cd /d "%~dp0"



REM Activate virtual environment

if not exist "venv\Scripts\activate.bat" (

    echo ERROR: Virtual environment not found.

    echo Run setup.bat first.

    echo.

    pause

    exit /b 1

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



if %count%==0 (

    echo No profiles found. Create one with run.bat first.

)



echo.

echo Bulk input format

echo -----------------

echo profile1; target1, target2. profile2; target3, target4

echo.

echo Example:

echo profile1; brandymelvilleusa, lift_the_label. profile2; freeflyapparel, citychicpl

echo.

echo Each profile runs in series. Separate log files are saved under logs\

echo.



if "%~1"=="" (

    set /p BULK_INPUT=Enter bulk input:

) else (

    set "BULK_INPUT=%~1"

)



if "%BULK_INPUT%"=="" (

    echo.

    echo ERROR: Bulk input cannot be empty.

    pause

    exit /b 1

)



echo.

echo ==========================================

echo Starting Bulk Run

echo ==========================================

echo Input: %BULK_INPUT%

echo.



python bulk_run.py "%BULK_INPUT%"

set EXIT_CODE=%ERRORLEVEL%



echo.

echo ==========================================

echo Bulk Run Finished

echo ==========================================

echo Check logs\ for per-profile log files.

echo.



pause

exit /b %EXIT_CODE%

