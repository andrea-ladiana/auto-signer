@echo off
echo ========================================
echo   PDF Signer GUI - Installazione
echo ========================================
echo.

echo Installazione dipendenze Python...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Installazione dipendenze aggiuntive per GUI...
python -m pip install PyMuPDF==1.23.0
python -m pip install tkinterdnd2==0.3.0

echo.
echo ========================================
echo   Avvio PDF Signer GUI
echo ========================================
echo.

python pdf_signer_gui.py

pause
