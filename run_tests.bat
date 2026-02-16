@echo off
echo ====================================
echo Execution des Tests
echo ====================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo ERREUR: Environnement virtuel non trouve!
    echo Veuillez d'abord executer install.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
pytest tests/ -v --cov=src --cov-report=term-missing

echo.
pause

