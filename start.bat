@echo off
echo === PDF Signer - Avvio del programma ===
echo.

REM Controlla se Python è installato
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non è installato o non è nel PATH.
    echo Installa Python da https://python.org
    pause
    exit /b 1
)

REM Controlla se pip è disponibile
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: pip non è disponibile.
    pause
    exit /b 1
)

REM Installa le dipendenze se necessario
echo Controllo delle dipendenze...
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo.
    echo ERRORE: Impossibile installare le dipendenze.
    echo Controlla il file requirements.txt e la connessione internet.
    pause
    exit /b 1
)

echo.
echo Avvio del programma...
echo.

REM Avvia il programma Python
python pdf_signer_unified.py %*

echo.
pause
