@echo off
echo ========================================
echo    PolicyPal - Setting up environment
echo ========================================
echo.

echo Creating virtual environment...
python -m venv .venv

echo Activating environment...
call .venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ========================================
echo    Setup complete! Run run.bat to start
echo ========================================
pause
