@echo off
:: 🤖 WINDOWS BATCH WRAPPER for Auto Test Script

setlocal

:: Set colors
set "GREEN=[32m"
set "RED=[31m"
set "YELLOW=[33m" 
set "CYAN=[36m"
set "RESET=[0m"

echo %CYAN%==========================================%RESET%
echo %CYAN%🤖 AUTO TEST RUNNER - WINDOWS LAUNCHER%RESET%
echo %CYAN%==========================================%RESET%
echo.

:: Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%❌ Node.js not found! Please install Node.js first.%RESET%
    echo %YELLOW%Download from: https://nodejs.org%RESET%
    pause
    exit /b 1
)

echo %GREEN%✅ Node.js detected%RESET%

:: Check if auto-test.js exists
if not exist "auto-test.js" (
    echo %RED%❌ auto-test.js not found in current directory%RESET%
    pause
    exit /b 1
)

echo %GREEN%✅ Auto test script found%RESET%
echo.

:: Run the auto test script
echo %CYAN%🚀 Starting automated test runner...%RESET%
echo.

if "%1"=="--auto" (
    node auto-test.js --auto
) else if "%1"=="-a" (
    node auto-test.js --auto
) else if "%1"=="--help" (
    node auto-test.js --help
) else if "%1"=="-h" (
    node auto-test.js --help
) else (
    node auto-test.js
)

echo.
echo %CYAN%🏁 Auto test runner completed%RESET%
pause
