# PDF Signer - Programma Avanzato per Firma Digitale PDF

Programma completo per aggiungere firme digitali e watermark ai documenti PDF con interfaccia grafica avanzata e modalità riga di comando.

## ✨ Caratteristiche Principali

### 🖥️ **Interfaccia Grafica Completa (NEW!)**
- **Drag & Drop**: Trascina PDF e immagini direttamente nell'applicazione
- **Anteprima in tempo reale**: Visualizza il risultato prima di salvare
- **Editor visuale**: Trascina la firma per riposizionarla interattivamente
- **Profili personaliz​zabili**: Salva e carica configurazioni predefinite
- **Gestione avanzata**: Configurazioni YAML/JSON per utenti esperti

### 📝 **Modalità Riga di Comando**
- Automazione e scripting
- Elaborazione batch
- Integrazione con altri sistemi
- Tutte le funzionalità disponibili via CLI

### 🎯 **Funzionalità Avanzate**
- **4 posizioni predefinite**: angoli del documento
- **Posizionamento personalizzato**: coordinate precise
- **Controllo opacità**: da trasparente a completamente opaco
- **Ridimensionamento**: scala personalizzabile
- **Supporto formati**: PNG, JPG, JPEG, GIF, BMP
- **Anteprima PDF**: visualizzazione con PyMuPDF per qualità ottimale

## 🚀 Installazione e Avvio

### Avvio Rapido GUI (Raccomandato)

**Windows - Command Prompt:**
```cmd
start_gui.bat
```

**Windows - PowerShell:**
```powershell
.\start_gui.ps1
```

**Manuale:**
```bash
pip install -r requirements.txt
pip install PyMuPDF tkinterdnd2
python pdf_signer_gui.py
```

### Avvio Modalità Riga di Comando

**Windows:**
```cmd
start.bat
```

**Manuale:**
```bash
python pdf_signer.py
```

## 🎮 Utilizzo GUI

### Funzionalità Principali

1. **📁 Gestione File**
   - Trascina PDF e immagini firma direttamente nell'interfaccia
   - Browse per selezionare file manualmente
   - Percorso output generato automaticamente

2. **👀 Anteprima Interattiva**
   - Visualizzazione PDF in tempo reale
   - Trascinamento firma per riposizionamento
   - Navigazione tra pagine
   - Zoom e adattamento automatico

3. **⚙️ Controlli Avanzati**
   - **Dimensione**: Slider per ridimensionamento (0.05x - 1.0x)
   - **Posizione**: 4 angoli predefiniti + posizionamento custom
   - **Opacità**: Da trasparente (0.1) a completamente opaco (1.0)
   - **Anteprima firma**: Miniatura dell'immagine caricata

4. **📊 Sistema Profili**
   - **Salva profili**: Configurazioni personalizzate con nome e descrizione
   - **Carica profili**: Un click per applicare impostazioni salvate
   - **Gestione avanzata**: Dialog dedicato per organizzare profili
   - **Profili predefiniti**: Configurazioni pronte all'uso

### Profili Inclusi

- **🖊️ Firma Standard**: Classica firma in basso a destra
- **📄 Firma Piccola**: Discreta e compatta  
- **🏛️ Firma Ufficiale**: Grande per documenti formali
- **📍 Firma Alto Sinistra**: Posizionamento alternativo
- **💧 Watermark Trasparente**: Marchio di filigrana

### Drag & Drop

L'interfaccia supporta completamente il trascinamento:

- **📑 PDF**: Trascina file PDF nell'area "PDF"
- **🖼️ Immagini**: Trascina PNG/JPG nell'area "Firma"  
- **🎯 Posizionamento**: Trascina la firma nell'anteprima per riposizionarla

## 📱 Utilizzo Modalità Interattiva (CLI)

### Menu Principale

```bash
python pdf_signer.py
```

Il programma presenta 3 opzioni:
1. **Modalità guidata**: Procedura step-by-step
2. **Aiuto riga di comando**: Documentazione parametri CLI
3. **Esci**: Chiude l'applicazione

### Processo Guidato

1. **Seleziona PDF**: Inserisci percorso o trascina file
2. **Imposta scala**: Fattore ridimensionamento (default: 0.2)
3. **Scegli posizione**: Menu numerato per gli angoli
4. **Configura output**: Percorso generato automaticamente o personalizzato
5. **Conferma ed elabora**: Revisione finale e processing

## ⌨️ Utilizzo Riga di Comando

### Sintassi Base

```bash
python pdf_signer.py <input.pdf> [opzioni]
```

### Parametri Disponibili

| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `input_pdf` | File PDF da firmare | *richiesto* |
| `-o, --output` | File PDF output | `input_signed.pdf` |
| `-s, --scale` | Fattore scala (0.05-1.0) | `1.0` |
| `-w, --watermark` | Immagine firma | `sign.png` |
| `-p, --position` | Posizione firma | `bottom-right` |
| `-h, --help` | Mostra aiuto | - |

### Posizioni Disponibili

- `bottom-right` ← Default
- `bottom-left`
- `top-right`  
- `top-left`

### Esempi Pratici

**Firma standard:**
```bash
python pdf_signer.py documento.pdf
```

**Firma personalizzata:**
```bash
python pdf_signer.py contratto.pdf -s 0.3 -p top-left -o contratto_firmato.pdf
```

**Con watermark custom:**
```bash
python pdf_signer.py report.pdf -w mia_firma.png -s 0.15 -p bottom-left
```

## ⚙️ Configurazione Avanzata

### File di Configurazione

La GUI crea automaticamente file di configurazione in:
- **Windows**: `%USERPROFILE%\.pdf_signer\`
- **Linux/Mac**: `~/.pdf_signer/`

**Struttura directory:**
```
.pdf_signer/
├── config.yaml          # Configurazione generale
└── profiles.json        # Profili salvati
```

### Personalizzazione config.yaml

```yaml
last_watermark_path: 'path/to/signature.png'
last_output_dir: '~/Documents/Signed'
default_scale: 0.2
default_position: 'bottom-right'
default_opacity: 0.8
window_geometry: '1200x800'
preview_quality: 'high'
```

### Gestione Profili JSON

```json
{
  "Mio Profilo Custom": {
    "scale": 0.25,
    "position": "top-right",
    "opacity": 0.9,
    "watermark_path": "signatures/official.png",
    "description": "Firma ufficiale aziendale"
  }
}
```

## 🔧 Dipendenze

### Core (CLI)
- `PyPDF2` - Manipolazione PDF
- `Pillow` - Elaborazione immagini
- `reportlab` - Generazione PDF

### GUI Aggiuntive
- `PyMuPDF` - Anteprima PDF ad alta qualità
- `tkinterdnd2` - Drag & Drop
- `pyyaml` - Configurazioni YAML

### Installazione Completa

```bash
pip install -r requirements.txt
pip install PyMuPDF==1.23.0 tkinterdnd2==0.3.0 pyyaml==6.0.1
```

## 🏗️ Struttura Progetto

```
auto-signer/
├── pdf_signer.py          # Modulo core + CLI
├── pdf_signer_gui.py      # Interfaccia grafica completa
├── requirements.txt       # Dipendenze base
├── start.bat             # Avvio CLI Windows
├── start.ps1            # Avvio CLI PowerShell  
├── start_gui.bat        # Avvio GUI Windows
├── start_gui.ps1        # Avvio GUI PowerShell
├── config_example.yaml  # Esempio configurazione
├── profiles_example.json # Esempi profili
├── sign.png             # Firma predefinita
├── signAL.png          # Firma alternativa
└── README.md           # Documentazione
```

## 🎯 Casi d'Uso

### 👔 Professionali
- **Contratti**: Firma automatica su documenti legali
- **Fatture**: Watermark aziendale su documenti contabili
- **Report**: Marchio di autenticità su relazioni
- **Certificati**: Timbro ufficiale su attestati

### 🏠 Personali  
- **Documenti**: Firma su PDF personali
- **CV**: Watermark di autenticità
- **Ricevute**: Marchio personale
- **Backup**: Firma automatica per archiviazione

### 🤖 Automazione
- **Batch processing**: Script per multiple firme
- **Workflow**: Integrazione in pipeline documentali
- **Server**: API per firma automatizzata
- **Monitoraggio**: Watch folder per auto-firma

## 🆘 Risoluzione Problemi

### Errori Comuni

**🚫 Import Error tkinterdnd2**
```bash
pip install tkinterdnd2==0.3.0
```

**🚫 Import Error fitz (PyMuPDF)**
```bash
pip install PyMuPDF==1.23.0
```

**🚫 File non trovato**
- Verifica path assoluti per file PDF e immagini
- Controlla permessi di lettura/scrittura

**🚫 Anteprima non funziona**
- Assicurati che PyMuPDF sia installato correttamente
- Prova con PDF più semplici

### Performance

**🐌 Anteprima lenta**
- Riduci qualità anteprima in `config.yaml`: `preview_quality: 'low'`
- Usa PDF con meno pagine per test

**💾 Memoria elevata**
- Chiudi anteprime non utilizzate
- Riduci dimensione immagini firma

## 📞 Supporto

Per problemi, suggerimenti o richieste di funzionalità:

1. **Issues**: Usa GitHub Issues per bug report
2. **Documentazione**: Consulta questo README
3. **Esempi**: Vedi file di esempio inclusi

## 🔄 Changelog

### v2.0 - GUI Completa
- ✅ Interfaccia grafica drag-and-drop
- ✅ Anteprima interattiva in tempo reale  
- ✅ Sistema profili con salvataggio
- ✅ Configurazione YAML/JSON
- ✅ Posizionamento visuale trascinando
- ✅ Gestione avanzata profili

### v1.0 - Base CLI
- ✅ Modalità riga di comando
- ✅ Modalità interattiva guidata
- ✅ 4 posizioni predefinite
- ✅ Controllo scala e opacità
- ✅ Supporto multipli formati immagine

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi file LICENSE per dettagli.

---

**PDF Signer v2.0** - *Firma Digitale Avanzata per PDF* 🖊️
