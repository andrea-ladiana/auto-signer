# PDF Signer GUI - Avvio con installazione dipendenze

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   PDF Signer GUI - Installazione" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Installazione dipendenze Python..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host ""
Write-Host "Installazione dipendenze aggiuntive per GUI..." -ForegroundColor Yellow
python -m pip install PyMuPDF==1.23.26
python -m pip install tkinterdnd2==0.3.0

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Avvio PDF Signer GUI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    python pdf_signer_gui.py
}
catch {
    Write-Host "Errore nell'avvio della GUI: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Premi un tasto per continuare..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
