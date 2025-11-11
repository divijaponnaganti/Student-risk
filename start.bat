@echo off
chcp 65001 >nul
echo ======================================================================
echo STUDENT RISK PREDICTION SYSTEM
echo ======================================================================
echo.
echo Starting Flask application...
echo.
echo Access the dashboard at: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
echo ======================================================================
echo.
py app.py
pause
