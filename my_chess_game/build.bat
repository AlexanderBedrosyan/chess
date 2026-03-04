@echo off
REM ─────────────────────────────────────────────────────────────
REM  Chess Trainer – Build Script (Windows)
REM  Step 1: PyInstaller  → dist\ChessTrainer\
REM  Step 2: Inno Setup   → installer\Setup_ChessTrainer.exe
REM
REM  Requirements (one-time):
REM    python -m venv .venv
REM    .venv\Scripts\pip install -r requirements.txt
REM    Download Inno Setup: https://jrsoftware.org/isinfo.php
REM ─────────────────────────────────────────────────────────────
setlocal

SET VENV_PYTHON=%~dp0.venv\Scripts\python.exe
SET VENV_PIP=%~dp0.venv\Scripts\pip.exe
SET ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

IF NOT EXIST "%VENV_PYTHON%" (
    echo ERROR: venv not found at %VENV_PYTHON%
    echo Run: python -m venv .venv  then  .venv\Scripts\pip install -r requirements.txt
    pause & exit /b 1
)

echo [1/4] Installing / upgrading PyInstaller into the venv...
"%VENV_PIP%" install --quiet --upgrade pyinstaller
IF ERRORLEVEL 1 ( echo ERROR: pip install failed & pause & exit /b 1 )

echo [2/4] Building executable with venv Python...
"%VENV_PYTHON%" -m PyInstaller --clean -y chess_trainer.spec
IF ERRORLEVEL 1 ( echo ERROR: PyInstaller failed & pause & exit /b 1 )

echo [3/4] Checking for Inno Setup...
IF NOT EXIST %ISCC% (
    echo.
    echo  Inno Setup not found at %ISCC%
    echo  Download it free from: https://jrsoftware.org/isinfo.php
    echo  Then re-run this script to produce Setup_ChessTrainer.exe
    echo.
    echo  [SKIP] Skipping installer packaging.
    goto :done
)

echo  Inno Setup found – compiling installer...
%ISCC% setup.iss
IF ERRORLEVEL 1 ( echo ERROR: Inno Setup compilation failed & pause & exit /b 1 )

echo [4/4] Done!
echo.
echo  ==================================================
echo   Single installer created at:
echo     installer\Setup_ChessTrainer.exe
echo   Share ONLY this one file with users.
echo   No Python required on their machines.
echo  ==================================================
goto :final

:done
echo [4/4] Done!
echo.
echo  ==================================================
echo   PyInstaller output: dist\ChessTrainer\ChessTrainer.exe
echo   (Install Inno Setup and re-run to produce a single
echo    installer\Setup_ChessTrainer.exe for distribution)
echo  ==================================================

:final
echo.
endlocal
pause
