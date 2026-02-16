@echo off
echo ====================================
echo Installation de la Plateforme
echo ====================================
echo.

echo [1/3] Creation de l'environnement virtuel...
python -m venv venv
echo     OK - Environnement virtuel cree

echo.
echo [2/3] Activation de l'environnement...
call venv\Scripts\activate.bat
echo     OK - Environnement active

echo.
echo [3/3] Installation des dependances...
pip install --upgrade pip
pip install -r requirements.txt
echo     OK - Dependances installees

echo.
echo ====================================
echo Installation terminee avec succes!
echo ====================================
echo.
echo Pour demarrer l'application:
echo   1. Activez l'environnement: venv\Scripts\activate
echo   2. Lancez la demo: python demo.py
echo   3. Ou lancez l'app web: streamlit run app.py
echo.
pause

