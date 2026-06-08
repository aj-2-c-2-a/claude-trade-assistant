@echo off
REM ===========================================================================
REM  Claude Trade Assistant  |  Windows installer
REM ---------------------------------------------------------------------------
REM  Fully transparent. It ONLY:
REM    1) checks Git + Python are installed
REM    2) clones this public repository
REM    3) creates a virtual environment and installs the package
REM  It does NOT download or run any remote script, and it never places trades.
REM ===========================================================================
setlocal

echo.
echo  ==================================================
echo   Claude Trade Assistant  ::  Windows setup
echo  ==================================================
echo.

where git >nul 2>nul
if errorlevel 1 ( echo  [X] Git not found. Install from https://git-scm.com/download/win & goto :end )

where python >nul 2>nul
if errorlevel 1 ( echo  [X] Python not found. Install Python 3.10+ from https://www.python.org & goto :end )

echo  [1/4] Cloning repository...
if exist claude-trade-assistant (
  echo        Folder exists, skipping clone.
) else (
  git clone https://github.com/aj-2-c-2-a/claude-trade-assistant.git
  if errorlevel 1 ( echo  [X] Clone failed. & goto :end )
)
cd claude-trade-assistant

echo  [2/4] Creating virtual environment...
python -m venv .venv
if errorlevel 1 ( echo  [X] venv creation failed. & goto :end )

echo  [3/4] Installing...
call .venv\Scripts\python.exe -m pip install --upgrade pip >nul
call .venv\Scripts\pip.exe install -e ".[web]"
if errorlevel 1 ( echo  [X] Install failed. & goto :end )

echo  [4/4] Setting up config...
if not exist .env copy .env.example .env >nul
if not exist config.yaml copy config.example.yaml config.yaml >nul

echo.
echo  [OK] Installed. Try a scan (free data, no key needed):
echo        .venv\Scripts\cta.exe scan
echo.
echo  For AI news briefings, put your key in .env then run:
echo        .venv\Scripts\cta.exe scan --briefing
echo.

:end
endlocal
pause
