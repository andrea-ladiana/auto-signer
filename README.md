# PDF Signer - Programma per aggiungere marchi ai PDF

Questo programma permette di aggiungere un marchio (watermark) a tutte le pagine di un file PDF. Il marchio viene posizionato in fondo a destra di ogni pagina.

## Installazione

1. Assicurati di avere Python 3.6 o superiore installato
2. Installa le dipendenze richieste:

```bash
pip install -r requirements.txt
```

## Utilizzo

### Versione da riga di comando

```bash
python pdf_signer.py percorso/del/file.pdf
```

#### Opzioni disponibili:

- `-o, --output`: Specifica il percorso del file PDF di output (default: aggiunge "_signed" al nome originale)
- `-s, --scale`: Fattore di scala per il marchio (default: 1.0)
- `-w, --watermark`: Percorso dell'immagine del marchio (default: sign.png)

#### Esempi:

```bash
# Uso base (usa sign.png come marchio, scala 1.0)
python pdf_signer.py documento.pdf

# Specifica il file di output
python pdf_signer.py documento.pdf -o documento_firmato.pdf

# Ridimensiona il marchio al 50%
python pdf_signer.py documento.pdf -s 0.5

# Usa un marchio diverso e scala personalizzata
python pdf_signer.py documento.pdf -w mio_marchio.png -s 0.8 -o output.pdf
```

### Versione interattiva

Per un uso più semplice, usa la versione interattiva:

```bash
python pdf_signer_interactive.py
```

Questo script ti guiderà passo passo nell'inserimento dei parametri.

## File richiesti

- `sign.png`: L'immagine del marchio (deve essere nella stessa directory dello script, o specificare il percorso)
- Il file PDF da modificare

## Formati supportati

- **Immagini marchio**: PNG, JPG, JPEG, GIF, BMP
- **PDF**: Tutti i PDF standard

## Note

- Il marchio viene posizionato in fondo a destra di ogni pagina
- Il programma mantiene un margine di 20 punti dai bordi della pagina
- Se il marchio è troppo grande, viene automaticamente riposizionato per rimanere all'interno della pagina
- Il file originale non viene modificato, viene creato un nuovo file

## Risoluzione problemi

1. **Errore "File non trovato"**: Verifica che i percorsi dei file siano corretti
2. **Errore di memoria con PDF grandi**: Prova a ridurre il fattore di scala del marchio
3. **Marchio non visibile**: Aumenta il fattore di scala o verifica che l'immagine non sia troppo piccola
