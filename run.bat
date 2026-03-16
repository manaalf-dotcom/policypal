@echo off
echo ========================================
echo    PolicyPal - Starting app...
echo ========================================
echo.

call .venv\Scripts\activate
python -m streamlit run app_1.py

pause
