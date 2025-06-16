# PDF Signer - Script di avvio PowerShell
Write-Host "=== PDF Signer - Avvio del programma ===" -ForegroundColor Cyan
Write-Host ""

# Controlla se Python è installato
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Python non trovato"
    }
    Write-Host "✓ Python trovato: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERRORE: Python non è installato o non è nel PATH." -ForegroundColor Red
    Write-Host "Installa Python da https://python.org" -ForegroundColor Yellow
    Read-Host "Premi Invio per uscire"
    exit 1
}

# Controlla se pip è disponibile
try {
    $pipVersion = pip --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "pip non trovato"
    }
    Write-Host "✓ pip disponibile" -ForegroundColor Green
} catch {
    Write-Host "❌ ERRORE: pip non è disponibile." -ForegroundColor Red
    Read-Host "Premi Invio per uscire"
    exit 1
}

# Installa le dipendenze se necessario
Write-Host "Controllo delle dipendenze..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt --quiet
    if ($LASTEXITCODE -ne 0) {
        throw "Errore nell'installazione"
    }
    Write-Host "✓ Dipendenze verificate" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "❌ ERRORE: Impossibile installare le dipendenze." -ForegroundColor Red
    Write-Host "Controlla il file requirements.txt e la connessione internet." -ForegroundColor Yellow
    Read-Host "Premi Invio per uscire"
    exit 1
}

Write-Host ""
Write-Host "Avvio del programma..." -ForegroundColor Green
Write-Host ""

# Avvia il programma Python con eventuali parametri passati
try {
    python pdf_signer.py $args
} catch {
    Write-Host "❌ Errore durante l'esecuzione del programma" -ForegroundColor Red
}

Write-Host ""
Read-Host "Premi Invio per uscire"
