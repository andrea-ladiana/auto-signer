# PDF Signer - Programma per aggiungere marchi ai PDF

Questo programma permette di aggiungere un marchio (watermark) a tutte le pagine di un file PDF. Il marchio viene posizionato in fondo a destra di ogni pagina.

## Installazione

1. Assicurati di avere Python 3.6 o superiore installato
2. Installa le dipendenze richieste:

```bash
pip install -r requirements.txt
```

## Avvio rapido (Windows)

Per un avvio semplificato, usa uno dei file di avvio:

**Command Prompt / Batch:**
```cmd
start.bat
```

**PowerShell:**
```powershell
.\start.ps1
```

Questi script verificheranno automaticamente le dipendenze e avvieranno il programma in modalità interattiva.

## Utilizzo

### Modalità interattiva (raccomandata)

Avvia il programma senza parametri per accedere al menu interattivo:

```bash
python pdf_signer.py
```

Il programma ti permetterà di scegliere tra:
1. **Modalità guidata**: Ti guida passo passo nell'inserimento dei parametri
2. **Aiuto riga di comando**: Mostra le opzioni disponibili per l'uso da terminale

### Modalità da riga di comando

```bash
python pdf_signer.py percorso/del/file.pdf
```

#### Opzioni disponibili:

- `-o, --output`: Specifica il percorso del file PDF di output (default: aggiunge "_signed" al nome originale)
- `-s, --scale`: Fattore di scala per il marchio (default: 1.0)
- `-w, --watermark`: Percorso dell'immagine del marchio (default: signAL.png)

#### Esempi:

```bash
# Uso base (usa sign.png come marchio, scala 1.0)
python pdf_signer.py documento.pdf

# Specifica il file di output
python pdf_signer.py documento.pdf -o documento_firmato.pdf

# Ridimensiona il marchio al 30%
python pdf_signer.py documento.pdf -s 0.3

# Usa un marchio diverso e scala personalizzata
python pdf_signer.py documento.pdf -w mio_marchio.png -s 0.8 -o output.pdf
```

## File richiesti

- `sign.png`: L'immagine del marchio (deve essere nella stessa directory dello script, o specificare il percorso)
- Il file PDF da modificare

## Formati supportati

- **Immagini marchio**: PNG, JPG, JPEG, GIF, BMP
- **PDF**: Tutti i PDF standard

## Caratteristiche

- **Doppia modalità**: Interfaccia interattiva guidata o uso da riga di comando
- **Auto-rilevamento marchio**: Cerca automaticamente `sign.png`
- **Posizionamento intelligente**: Il marchio viene posizionato in fondo a destra
- **Gestione margini**: Mantiene automaticamente un margine di 20 punti dai bordi
- **Ridimensionamento automatico**: Previene che il marchio esca dai bordi della pagina
- **File sicuro**: Il file originale non viene mai modificato

## Note

- Il marchio viene posizionato in fondo a destra di ogni pagina
- Il programma mantiene un margine di 20 punti dai bordi della pagina
- Se il marchio è troppo grande, viene automaticamente riposizionato per rimanere all'interno della pagina
- Il file originale non viene modificato, viene creato un nuovo file
- In modalità interattiva, il fattore di scala di default è 0.2 (20% della dimensione originale)
- In modalità riga di comando, il fattore di scala di default è 1.0 (dimensione originale)

## Risoluzione problemi

1. **Errore "File non trovato"**: Verifica che i percorsi dei file siano corretti
2. **Errore di memoria con PDF grandi**: Prova a ridurre il fattore di scala del marchio
3. **Marchio non visibile**: Aumenta il fattore di scala o verifica che l'immagine non sia troppo piccola
4. **Errore dipendenze**: Usa `start.bat` su Windows per l'installazione automatica
