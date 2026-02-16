@echo off
echo ====================================
echo Lancement de la Demo
echo ====================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo ERREUR: Environnement virtuel non trouve!
    echo Veuillez d'abord executer install.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python demo.py

echo.
pause

