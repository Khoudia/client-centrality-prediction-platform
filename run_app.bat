@echo off
echo ====================================
echo Lancement de l'Application Web
echo ====================================
echo.

if not exist "venv\Scripts\activate.bat" (
    echo ERREUR: Environnement virtuel non trouve!
    echo Veuillez d'abord executer install.bat
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
streamlit run app.py

echo.
pause

