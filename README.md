# 🖊️ Auto-Signer v2.0 - Sistema Avanzato per Firma Digitale PDF

**Il sistema completo per la firma digitale automatizzata di documenti PDF** con interfaccia grafica avanzata, modalità riga di comando e funzionalità enterprise integrate.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

## ✨ Caratteristiche Principali v2.0

### 🖥️ **Interfaccia Grafica Avanzata**
- **Interfaccia a schede**: 6 schede organizzate per funzionalità specifiche
- **Drag & Drop**: Trascina PDF e immagini direttamente nell'applicazione  
- **Anteprima in tempo reale**: Visualizza il risultato prima di salvare
- **Editor visuale**: Trascina la firma per riposizionarla interattivamente
- **Profili avanzati**: Salva e carica tutte le configurazioni incluse quelle avanzate
- **Gestione completa**: Controllo totale su tutte le funzionalità dalla GUI

### 📝 **Modalità CLI Completa**
- **Tutte le funzioni integrate**: Non più dipendenza da moduli esterni
- **Selezione pagine avanzata**: Firma su pagine specifiche (1,3,5-10, pari/dispari)
- **Automazione completa**: Script e batch processing con tutte le opzioni
- **Elaborazione batch**: Processamento multipli documenti
- **Integrazione enterprise**: API per sistemi esterni

### 🎯 **Funzionalità Enterprise v2.0**
- **📄 Selezione pagine**: Supporto completo (all, first, last, range, odd, even, exclude)
- **🎨 Effetti grafici**: Bordi personalizzabili, ombreggiature, trasparenza
- **⏰ Timestamp automatico**: 3 formati (breve, lungo, completo) + personalizzato
- **📧 Invio email**: Spedizione automatica con template personalizzabili
- **🔍 Metadati avanzati**: Aggiunta informazioni complete al PDF (autore, titolo, soggetto)
- **🖼️ Supporto immagini**: PNG, JPG, JPEG, GIF, BMP, SVG con conversione automatica
- **🔐 Posizionamento preciso**: Coordinate assolute e relative con precisione

## 🚀 Installazione e Avvio Rapido

### ⚡ Installazione

**1. Clone del repository:**
```bash
git clone https://github.com/your-username/auto-signer.git
cd auto-signer
```

**2. Installazione dipendenze:**
```bash
pip install -r requirements.txt
```

### 🏃‍♂️ Avvio Immediato

Se all'avvio vengono segnalate dipendenze mancanti, installa manualmente
`PyMuPDF` e `tkinterdnd2`:

```bash
pip install PyMuPDF tkinterdnd2
```


## 🖥️ Interfaccia Grafica v2.0

### 🚀 Avvio GUI
```bash
python pdf_signer_gui.py
```

### ✨ Nuova Interfaccia a Schede

La GUI v2.0 è organizzata in 6 schede specializzate:

#### 📋 **1. Base** - Controlli Fondamentali
- **Dimensione firma**: Slider preciso (0.05x - 1.0x)
- **Posizione**: 4 angoli predefiniti + coordinate personalizzate
- **Opacità**: Controllo trasparenza (0.1 - 1.0)
- **File I/O**: Drag & Drop per PDF e immagini firma

#### 📄 **2. Pagine** - Selezione Avanzata
- **Tutte le pagine**: Firma su ogni pagina del documento
- **Prima/Ultima**: Selezione veloce prima o ultima pagina
- **Range personalizzato**: Sintassi avanzata (es: "1-5,7,10-12")
- **Pagine pari/dispari**: Selezione automatica
- **Esclusione**: Specificare pagine da escludere

#### 🎨 **3. Effetti** - Personalizzazione Grafica
- **Bordi**: Larghezza (0-10px) e colore personalizzabile
- **Ombreggiature**: Offset orizzontale/verticale regolabile
- **Anteprima effetti**: Preview in tempo reale
- **Formato immagine**: Conversione automatica tra formati

#### ⏰ **4. Timestamp** - Data e Ora
- **Formati predefiniti**: Breve, lungo, completo
- **Formato personalizzato**: Sintassi strftime
- **Posizione indipendente**: Separata dalla firma principale
- **Stile personalizzabile**: Font e dimensioni

#### 📝 **5. Metadati** - Informazioni PDF  
- **Autore**: Nome del firmatario
- **Titolo**: Titolo del documento
- **Soggetto**: Descrizione del contenuto
- **Aggiornamento automatico**: Metadati di firma e data

#### 📧 **6. Email** - Invio Automatico
- **Destinatari**: TO, CC multipli
- **Template**: Email personalizzabili
- **Configurazione SMTP**: Server email personalizzato
- **Allegati**: Supporto file multipli

### 🎯 **Profili Avanzati v2.0**

I profili ora salvano **tutte** le opzioni delle 6 schede:
- Impostazioni base (dimensione, posizione, opacità)
- Selezione pagine specifica
- Effetti grafici personalizzati
- Configurazione timestamp
- Metadati predefiniti
- Impostazioni email

**Profili Predefiniti Inclusi:**
- **Firma Standard**: Configurazione classica completa
- **Documento Ufficiale**: Con timestamp e metadati
- **Email Automatica**: Firma + invio immediato
- **Pagine Selettive**: Solo prima e ultima pagina
- **Effetti Avanzati**: Bordi e ombreggiature

## 💻 Interfaccia CLI Avanzata

### 📖 Sintassi Completa
```bash
python pdf_signer.py <input.pdf> [opzioni_base] [opzioni_avanzate]
```

### 🎛️ Parametri Base
| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `input_pdf` | File PDF da firmare | *richiesto* |
| `-o, --output` | File PDF output | `input_signed.pdf` |
| `-s, --scale` | Fattore scala (0.05-1.0) | `1.0` |
| `-w, --watermark` | Immagine firma | `sign.png` |
| `-p, --position` | Posizione firma | `bottom-right` |
| `--opacity` | Opacità (0.1-1.0) | `0.8` |

### 🚀 Parametri Avanzati v2.0

#### 📄 Selezione Pagine
| Parametro | Descrizione | Esempi |
|-----------|-------------|---------|
| `--pages` | Pagine specifiche | `all`, `first`, `last`, `1-5,7,10` |
| `--pages-odd` | Solo pagine dispari | - |
| `--pages-even` | Solo pagine pari | - |
| `--exclude` | Escludere pagine | `2,4,6` |

#### 🎨 Effetti Grafici
| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `--border-width` | Larghezza bordo (px) | `0` |
| `--border-color` | Colore bordo | `black` |
| `--shadow` | Abilita ombreggiatura | `false` |
| `--shadow-offset` | Offset ombra (x,y) | `2,2` |

#### ⏰ Timestamp
| Parametro | Descrizione | Formati |
|-----------|-------------|---------|
| `--timestamp` | Abilita timestamp | - |
| `--timestamp-format` | Formato timestamp | `short`, `long`, `full` |
| `--timestamp-position` | Posizione timestamp | `top-left`, `top-right`, etc. |
| `--timestamp-custom` | Formato personalizzato | `%Y-%m-%d %H:%M` |

#### 📝 Metadati
| Parametro | Descrizione | Esempio |
|-----------|-------------|---------|
| `--author` | Autore documento | `"Mario Rossi"` |
| `--title` | Titolo documento | `"Contratto Firmato"` |
| `--subject` | Soggetto documento | `"Documento Legale"` |

#### 📧 Email
| Parametro | Descrizione | Esempio |
|-----------|-------------|---------|
| `--email-to` | Destinatari (TO) | `user@email.com,user2@email.com` |
| `--email-cc` | Destinatari (CC) | `boss@company.com` |
| `--email-config` | File configurazione SMTP | `email_config.yaml` |
| `--email-template` | Template email | `template.txt` |

### 📚 Esempi CLI Avanzati

#### 🏃‍♂️ Esempi Rapidi
```bash
# Firma semplice
python pdf_signer.py documento.pdf

# Con ridimensionamento
python pdf_signer.py documento.pdf -s 0.3 -p top-left

# Con output personalizzato
python pdf_signer.py input.pdf -o firmato_oggi.pdf
```

#### 📄 Selezione Pagine Avanzata
```bash
# Solo prima pagina
python pdf_signer.py documento.pdf --pages first

# Range personalizzato
python pdf_signer.py documento.pdf --pages "1-5,8,10-12"

# Pagine dispari
python pdf_signer.py documento.pdf --pages-odd

# Tutte tranne alcune
python pdf_signer.py documento.pdf --pages all --exclude "2,4,6"
```

#### 🎨 Effetti Grafici
```bash
# Bordo nero 2px
python pdf_signer.py documento.pdf --border-width 2 --border-color black

# Ombreggiatura personalizzata
python pdf_signer.py documento.pdf --shadow --shadow-offset 3,3

# Combinazione effetti
python pdf_signer.py documento.pdf --border-width 1 --border-color red --shadow
```

#### ⏰ Timestamp Avanzati
```bash
# Timestamp breve
python pdf_signer.py documento.pdf --timestamp --timestamp-format short

# Timestamp completo in alto a sinistra
python pdf_signer.py documento.pdf --timestamp --timestamp-format full --timestamp-position top-left

# Formato personalizzato
python pdf_signer.py documento.pdf --timestamp --timestamp-custom "%d/%m/%Y alle %H:%M"
```

#### 📝 Metadati Completi
```bash
# Metadati base
python pdf_signer.py documento.pdf --author "Mario Rossi" --title "Contratto Firmato"

# Metadati completi
python pdf_signer.py documento.pdf --author "Azienda SpA" --title "Fattura N.123" --subject "Documento Contabile"
```

#### 📧 Invio Email Automatico
```bash
# Firma e invia
python pdf_signer.py documento.pdf --email-to cliente@email.com

# Invio con CC e configurazione
python pdf_signer.py documento.pdf --email-to cliente@email.com --email-cc boss@azienda.com --email-config smtp_config.yaml

# Con template personalizzato
python pdf_signer.py documento.pdf --email-to cliente@email.com --email-template email_template.txt
```

#### 🚀 Esempi Completi (All-in-One)
```bash
# Firma professionale completa
python pdf_signer.py contratto.pdf \
  --pages "1,3-5" \
  --scale 0.3 \
  --position bottom-right \
  --border-width 2 \
  --border-color blue \
  --shadow \
  --timestamp \
  --timestamp-format long \
  --author "Studio Legale ABC" \
  --title "Contratto Firmato Digitalmente" \
  --email-to cliente@email.com \
  --email-cc segreteria@studio.com

# Elaborazione batch con automazione
python pdf_signer.py documento.pdf \
  --pages all \
  --scale 0.2 \
  --opacity 0.6 \
  --timestamp \
  --timestamp-custom "%d/%m/%Y - %H:%M:%S" \
  --author "Sistema Automatico" \
  --email-to archivio@azienda.com
```

## ⚙️ File di Configurazione

### 📁 Struttura Directory
```
~/.pdf_signer/                  # Directory configurazione utente
├── config.yaml                # Configurazione generale
├── profiles.json              # Profili GUI salvati
├── email_config.yaml          # Configurazione SMTP
└── email_template.txt         # Template email default
```

### 🔧 config.yaml - Configurazione Generale
```yaml
# Impostazioni default
default_scale: 0.2
default_position: 'bottom-right'
default_opacity: 0.8
default_watermark: 'sign.png'

# Paths
last_output_dir: '~/Documents/Signed'
last_watermark_path: '~/signatures/official.png'

# GUI Settings
window_geometry: '1200x800'
preview_quality: 'high'  # high, medium, low
theme: 'default'

# Advanced defaults
default_pages: 'all'
default_border_width: 0
default_border_color: 'black'
default_shadow: false
default_timestamp: false
default_timestamp_format: 'short'
```

### 📧 email_config.yaml - Configurazione SMTP
```yaml
smtp:
  server: 'smtp.gmail.com'
  port: 587
  username: 'your-email@gmail.com'
  password: 'your-app-password'  # Usa App Password per Gmail
  use_tls: true

sender:
  name: 'Sistema PDF Signer'
  email: 'your-email@gmail.com'

default_subject: 'Documento PDF Firmato'
default_body: |
  Gentile destinatario,
  
  In allegato trova il documento PDF firmato digitalmente.
  
  Cordiali saluti,
  Sistema PDF Signer
```

### 📧 email_template.txt - Template Email
```text
Subject: Documento {filename} firmato digitalmente

Gentile {recipient},

In allegato trova il documento "{filename}" firmato digitalmente in data {timestamp}.

Dettagli firma:
- Autore: {author}
- Titolo: {title}
- Pagine firmate: {pages}
- Data firma: {date}

Cordiali saluti,
{sender_name}
```

### 👤 profiles.json - Profili GUI Avanzati
```json
{
  "Firma Standard v2": {
    "scale": 0.25,
    "position": "bottom-right",
    "opacity": 0.8,
    "pages": "all",
    "border_width": 1,
    "border_color": "black",
    "shadow": false,
    "timestamp": true,
    "timestamp_format": "short",
    "author": "Utente Standard",
    "description": "Configurazione standard con timestamp"
  },
  
  "Documento Legale": {
    "scale": 0.3,
    "position": "bottom-center",
    "opacity": 1.0,
    "pages": "first,last",
    "border_width": 2,
    "border_color": "blue",
    "shadow": true,
    "shadow_offset": "2,2",
    "timestamp": true,
    "timestamp_format": "full",
    "timestamp_position": "top-right",
    "author": "Studio Legale",
    "title": "Documento Legale Certificato",
    "email_enabled": true,
    "email_to": ["cliente@email.com"],
    "description": "Per documenti legali con invio automatico"
  },
  
  "Processing Batch": {
    "scale": 0.15,
    "position": "top-left",
    "opacity": 0.6,
    "pages": "all",
    "border_width": 0,
    "shadow": false,
    "timestamp": true,
    "timestamp_custom": "%Y%m%d_%H%M%S",
    "author": "Sistema Automatico",
    "description": "Per elaborazione automatica batch"
  }
}
```

## 🔧 Dipendenze e Installazione Completa

### 📋 requirements.txt Completo
```text
# Core PDF processing
PyPDF2>=3.0.0
reportlab>=4.0.0
Pillow>=10.0.0

# GUI components
tkinter>=8.6  # Usually included with Python
tkinterdnd2>=0.3.0

# Advanced PDF features
PyMuPDF>=1.23.0  # High-quality PDF rendering

# Configuration and utilities
pyyaml>=6.0
python-dateutil>=2.8.0

# Email functionality
smtplib  # Included with Python
email  # Included with Python

# Image processing
opencv-python>=4.8.0  # Optional, for advanced image effects
```

### 📦 Installazione Step by Step

```bash
# 1. Clona repository
git clone https://github.com/your-username/auto-signer.git
cd auto-signer

# 2. Crea ambiente virtuale (raccomandato)
python -m venv venv

# 3. Attiva ambiente virtuale
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Installa dipendenze base
pip install -r requirements.txt

# 5. Installa componenti opzionali
pip install opencv-python>=4.8.0

# 6. Test installazione
python test_advanced_features.py
```

### 🚀 Script di Avvio Automatico

**Windows - start_gui_v2.bat:**
```batch
@echo off
echo Avvio PDF Signer GUI v2.0...
python pdf_signer_gui.py
pause
```

**Windows - start_cli_v2.bat:**  
```batch
@echo off
echo PDF Signer CLI v2.0
echo Trascina un file PDF su questa finestra o usa parametri avanzati
echo.
python pdf_signer.py %*
pause
```

**Linux/Mac - start_gui_v2.sh:**
```bash
#!/bin/bash
echo "Avvio PDF Signer GUI v2.0..."
python3 pdf_signer_gui.py
```

## 🧪 Test e Verifica

### 🔬 Test Suite Integrata
```bash
# Esegui tutti i test
python test_advanced_features.py

# Test specifici
python -c "from test_advanced_features import *; test_parse_pages()"
python -c "from test_advanced_features import *; test_timestamp_generation()"
```

### ✅ Test Manuale Rapido

**1. Test GUI:**
```bash
python pdf_signer_gui.py
# Verifica: tutte le 6 schede si aprono correttamente
```

**2. Test CLI Base:**
```bash
python pdf_signer.py --help
# Verifica: mostra tutti i parametri avanzati
```

**3. Test Funzionalità Avanzate:**
```bash
python pdf_signer.py pdf/Abstract_Tesi_di_Laurea_Magistrale.pdf --pages first --timestamp --author "Test User"
# Verifica: crea PDF con firma solo su prima pagina + timestamp
```

## 🆘 Risoluzione Problemi v2.0

### 🚫 Errori di Installazione

**Import Error: tkinterdnd2**
```bash
pip uninstall tkinterdnd2
pip install tkinterdnd2==0.3.0
```

**Import Error: PyMuPDF**
```bash
pip install PyMuPDF==1.23.0
# Se fallisce:
pip install --upgrade pip
pip install PyMuPDF --no-cache-dir
```

**Import Error: yaml**
```bash
pip install pyyaml>=6.0
```

### ⚙️ Problemi di Configurazione

**GUI non salva profili:**
- Verifica permessi directory: `~/.pdf_signer/`
- Crea manualmente: `mkdir ~/.pdf_signer`

**Email non funziona:**
- Verifica `email_config.yaml`
- Usa App Password per Gmail
- Controlla firewall/antivirus

**Timestamp formato errato:**
- Usa sintassi Python strftime
- Esempi validi: `%Y-%m-%d`, `%d/%m/%Y %H:%M`

### 🐛 Problemi Funzionali

**Selezione pagine non funziona:**
```bash
# Sintassi corretta:
--pages "1-3,5,7-9"  # ✅ Virgole senza spazi
--pages "1- 3, 5"    # ❌ Spazi non validi
```

**Bordi non visibili:**
```bash
# Assicurati larghezza > 0:
--border-width 1 --border-color black  # ✅
--border-width 0  # ❌ Bordo invisibile
```

**Timestamp non appare:**
```bash
# Verifica posizione non sovrapposta:
--timestamp --timestamp-position top-left  # ✅
# Controlla formato:
--timestamp-format short  # ✅
--timestamp-format invalid  # ❌
```

## 📊 Confronto Versioni

| Caratteristica | v1.0 | v2.0 |
|----------------|------|------|
| **GUI** | Base, singola scheda | 6 schede specializzate |
| **Selezione Pagine** | ❌ | ✅ Avanzata (all, range, odd/even) |
| **Effetti Grafici** | ❌ | ✅ Bordi e ombreggiature |
| **Timestamp** | ❌ | ✅ 3 formati + personalizzato |
| **Metadati PDF** | ❌ | ✅ Autore, titolo, soggetto |
| **Invio Email** | ❌ | ✅ SMTP + template |
| **Profili** | Base | Completi (tutte le opzioni) |
| **CLI Avanzata** | Parametri base | 25+ parametri avanzati |
| **Formati Immagine** | PNG, JPG | PNG, JPG, GIF, BMP, SVG |
| **Test Automatici** | ❌ | ✅ Suite completa |

## 🎯 Casi d'Uso Avanzati v2.0

### 🏢 **Enterprise/Aziendale**

**Workflow Documentale Automatico:**
```bash
# Script batch per contratti
for file in *.pdf; do
  python pdf_signer.py "$file" \
    --pages "first,last" \
    --scale 0.3 \
    --border-width 2 \
    --border-color "corporate-blue" \
    --timestamp \
    --timestamp-format full \
    --author "Azienda SpA" \
    --title "Contratto Firmato - $(date +%Y)" \
    --email-to "archivio@azienda.com" \
    --email-cc "legale@azienda.com"
done
```

**Firma Automatica Server:**
```python
# Integrazione in sistema aziendale
import subprocess
import os

def auto_sign_document(pdf_path, client_email):
    output_path = f"firmati/{os.path.basename(pdf_path)}"
    
    cmd = [
        "python", "pdf_signer.py", pdf_path,
        "--pages", "all",
        "--timestamp",
        "--author", "Sistema Aziendale",
        "--email-to", client_email,
        "--output", output_path
    ]
    
    return subprocess.run(cmd, capture_output=True, text=True)
```

### 📚 **Educativo/Accademico**

**Certificazione Tesi:**
```bash
python pdf_signer.py tesi_laurea.pdf \
  --pages "1" \
  --scale 0.4 \
  --position center \
  --border-width 3 \
  --border-color gold \
  --timestamp \
  --timestamp-format "Certificato il %d/%m/%Y alle ore %H:%M" \
  --author "Università XYZ" \
  --title "Tesi di Laurea Certificata" \
  --subject "Documento Accademico Ufficiale"
```

### 🏥 **Settore Medico/Legale**

**Documentazione Clinica:**
```bash
python pdf_signer.py referto_medico.pdf \
  --pages "all" \
  --scale 0.25 \
  --position bottom-center \
  --border-width 1 \
  --border-color medical-blue \
  --timestamp \
  --timestamp-format full \
  --author "Dr. Mario Rossi - N. Albo 12345" \
  --title "Referto Medico Certificato" \
  --email-to "paziente@email.com" \
  --email-cc "archivio.clinico@ospedale.it"
```

### 🤖 **Automazione e Integrazione**

**Watch Folder (Monitoraggio Directory):**
```python
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PDFHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_file and event.src_path.endswith('.pdf'):
            # Auto-firma immediata
            os.system(f'python pdf_signer.py "{event.src_path}" --timestamp --email-to admin@azienda.com')

observer = Observer()
observer.schedule(PDFHandler(), path='./incoming_pdfs', recursive=False)
observer.start()
```

## 📈 Roadmap e Sviluppi Futuri

### 🔮 v2.1 - Prevista Q1 2024
- **OCR Integration**: Riconoscimento testo per posizionamento intelligente
- **Batch GUI**: Interfaccia grafica per elaborazione multipla
- **Cloud Storage**: Integrazione Google Drive, Dropbox
- **API REST**: Endpoint per integrazione web

### 🚀 v2.2 - Prevista Q2 2024  
- **Firma Biometrica**: Supporto tablet e touch screen
- **Template Grafici**: Editor visual per layout firma
- **Audit Trail**: Log completo delle operazioni
- **Multi-lingua**: Interfaccia in più lingue

### 🌟 v3.0 - Visione Futura
- **AI-Powered**: Posizionamento intelligente firma
- **Blockchain**: Certificazione immutabile documenti
- **Mobile App**: Companion app per iOS/Android
- **Plugin Office**: Integrazione Word, Excel, PowerPoint

## 🤝 Contribuire al Progetto

### 📋 Come Contribuire

1. **Fork** del repository
2. **Crea branch** per la tua feature: `git checkout -b feature/AmazingFeature`
3. **Commit** delle modifiche: `git commit -m 'Add some AmazingFeature'`
4. **Push** del branch: `git push origin feature/AmazingFeature`
5. **Apri Pull Request**

### 🐛 Segnalazione Bug

Usa GitHub Issues includendo:
- **OS**: Windows/Linux/macOS + versione
- **Python**: Versione Python utilizzata
- **Errore**: Messaggio completo di errore
- **Riproducibilità**: Passi per riprodurre il problema

### ⭐ Feature Request

Per richiedere nuove funzionalità:
- **Descrizione chiara** della funzionalità
- **Caso d'uso** specifico
- **Mockup/Screenshot** se applicabile

## 📄 Licenza

Questo progetto è rilasciato sotto **Licenza MIT**. Vedi il file `LICENSE` per i dettagli completi.

```
MIT License

Copyright (c) 2024 Auto-Signer Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 📞 Supporto e Contatti

- **📧 Email**: support@pdf-signer.dev
- **🐛 Issues**: [GitHub Issues](https://github.com/your-username/auto-signer/issues)
- **📖 Documentazione**: [GitHub Wiki](https://github.com/your-username/auto-signer/wiki)
- **💬 Discussioni**: [GitHub Discussions](https://github.com/your-username/auto-signer/discussions)

---

### 🎉 Ringraziamenti

- **PyPDF2** team per le librerie PDF
- **Tkinter** community per i componenti GUI  
- **PyMuPDF** per il rendering di alta qualità
- **Pillow** per l'elaborazione immagini
- Tutti i **contributor** e **beta tester**

---

**⭐ Se questo progetto ti è stato utile, considera di mettere una stella su GitHub!**

**🔄 Ultimo aggiornamento**: Gennaio 2024  
**📦 Versione**: 2.0  
**🐍 Python**: 3.8+  
**💻 Piattaforme**: Windows, Linux, macOS
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
