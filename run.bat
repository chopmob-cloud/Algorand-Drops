@echo off
setlocal enabledelayedexpansion

REM =========================
REM CONFIG
REM =========================
set PROJECT_DIR=C:\algo\airdrop
set DAILY_DIR=%PROJECT_DIR%\daily
set VENV_DIR=%PROJECT_DIR%\venv
set PYTHON=%VENV_DIR%\Scripts\python.exe

echo.
echo ======================================
echo 🚀 Starting daily airdrop pipeline
echo ======================================
echo.

REM =========================
REM VERIFY PYTHON
REM =========================
if not exist "%PYTHON%" (
    echo ❌ Python not found at %PYTHON%
    exit /b 1
)

echo ✅ Using Python: %PYTHON%
echo.

REM =========================
REM STEP 1: SCAN HOLDERS
REM =========================
echo ▶ Running scan.py
"%PYTHON%" "%PROJECT_DIR%\scan.py"
if errorlevel 1 (
    echo ❌ scan.py failed
    exit /b 1
)
echo ✅ scan.py complete
echo.

REM =========================
REM STEP 2: CALCULATE PERCENTAGE
REM =========================
echo ▶ Running percentage.py
"%PYTHON%" "%PROJECT_DIR%\percentage.py"
if errorlevel 1 (
    echo ❌ percentage.py failed
    exit /b 1
)
echo ✅ percentage.py complete
echo.

REM =========================
REM STEP 3: COPY TO DAILY
REM =========================
echo ▶ Copying one_percent CSV to daily folder

for %%f in ("%PROJECT_DIR%\*_one_percent.csv") do (
    copy "%%f" "%DAILY_DIR%\" >nul
)

if errorlevel 1 (
    echo ❌ Failed copying CSV to daily
    exit /b 1
)

echo ✅ CSV copied to daily
echo.

REM =========================
REM STEP 4: DROP TOKENS (RUN FROM DAILY)
REM =========================
echo ▶ Running drop.py from daily folder

pushd "%DAILY_DIR%"
"%PYTHON%" "drop.py"
set DROP_EXIT_CODE=%ERRORLEVEL%
popd

if %DROP_EXIT_CODE% neq 0 (
    echo ❌ drop.py failed
    exit /b %DROP_EXIT_CODE%
)

echo ✅ drop.py complete
echo.

echo ======================================
echo 🎉 Daily airdrop pipeline finished
echo ======================================
echo.

endlocal
