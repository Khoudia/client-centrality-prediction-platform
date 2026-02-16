@echo off
REM Script d'installation pour le projet Client Centrality Prediction Platform
REM ========================================================================

echo.
echo ========================================================================
echo  CLIENT CENTRALITY PREDICTION PLATFORM - INSTALLATION
echo ========================================================================
echo.

REM Vérifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installé ou n'est pas dans le PATH
    echo Veuillez installer Python 3.9+ depuis https://www.python.org/
    pause
    exit /b 1
)

echo [OK] Python détecté
python --version

REM Créer l'environnement virtuel (optionnel)
echo.
echo [INFO] Vérification de l'environnement virtuel...

if not exist "venv" (
    echo [INFO] Création d'un environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Impossible de créer l'environnement virtuel
        pause
        exit /b 1
    )
    echo [OK] Environnement virtuel créé
) else (
    echo [OK] Environnement virtuel existant
)

REM Activer l'environnement virtuel
echo.
echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Mettre à jour pip
echo.
echo [INFO] Mise à jour de pip...
python -m pip install --upgrade pip -q

REM Installer les dépendances
echo.
echo [INFO] Installation des dépendances...
echo Cela peut prendre quelques minutes...
echo.

pip install numpy pandas scipy scikit-learn networkx matplotlib seaborn plotly streamlit openpyxl pyarrow python-dotenv joblib -q

if errorlevel 1 (
    echo [ERREUR] Erreur lors de l'installation des dépendances
    pause
    exit /b 1
)

echo [OK] Dépendances installées

REM Installation optionnelle de XGBoost
echo.
echo [INFO] Installation de XGBoost (optionnel, pour meilleure performance)...
pip install xgboost -q
if errorlevel 1 (
    echo [AVERTISSEMENT] XGBoost n'a pas pu être installé (optionnel)
) else (
    echo [OK] XGBoost installé
)

REM Test des imports
echo.
echo [INFO] Test des imports...
python test_full_imports.py

echo.
echo ========================================================================
echo [OK] Installation terminée avec succès!
echo ========================================================================
echo.
echo Prochaines étapes:
echo 1. Exécutez: python demo.py
echo 2. Ou lancez: streamlit run app.py
echo.
pause

