@echo off
REM Set Alpha Vantage API Key for Windows

echo Setting Alpha Vantage API Key...
setx ALPHA_VANTAGE_API_KEY JSET7HHTHBL8I5WM

echo.
echo ✓ API Key has been set!
echo.
echo IMPORTANT: You must restart your terminal/command prompt for the change to take effect.
echo.
echo Next steps:
echo 1. Close this terminal
echo 2. Open a new terminal
echo 3. Navigate to backend folder: cd backend
echo 4. Restart the backend: python -m uvicorn main:app --reload
echo.
echo The API key will now be used automatically by the application.
echo.
pause
