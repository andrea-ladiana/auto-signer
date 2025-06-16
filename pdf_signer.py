#!/usr/bin/env python3
"""
Programma unificato per aggiungere un marchio (watermark) a tutte le pagine di un file PDF.
Il marchio viene posizionato in fondo a destra di ogni pagina.

Supporta sia l'uso da riga di comando che l'interfaccia interattiva.
Versione avanzata con supporto per pagine specifiche, formati multipli, effetti e metadati.
"""

import os
import smtplib
import json
import yaml
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfWriter, PdfReader
from PIL import Image, ImageDraw
import tempfile
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Tutte le funzionalità avanzate sono ora integrate direttamente


def create_watermark_pdf(
    image_path,
    scale_factor=1.0,
    output_path=None,
    position="bottom-right",
    page_size=None,
    original_pdf_path=None,
):
    """
    Crea un PDF temporaneo contenente solo il marchio (watermark).
    
    Args:
        image_path (str): Percorso dell'immagine del marchio
        scale_factor (float): Fattore di scala per ridimensionare il marchio
        output_path (str): Percorso del file PDF temporaneo (opzionale)
        position (str): Posizione del marchio ("bottom-right", "bottom-left", "top-right", "top-left")
        page_size (tuple): Dimensioni pagina (larghezza, altezza) in punti.
        original_pdf_path (str): PDF da cui ricavare la dimensione pagina se page_size non 
            è fornito.
    
    Returns:
        str: Percorso del file PDF temporaneo creato
    """
    if output_path is None:
        # Crea un file temporaneo
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        output_path = temp_file.name
        temp_file.close()    # Usa la funzione condivisa per calcolare le dimensioni
    img_width, img_height, _, _ = calculate_watermark_size_points(image_path, scale_factor)
    
    # Crea un PDF con l'immagine
    # Determina dimensioni pagina
    if page_size is None and original_pdf_path:
        try:
            with open(original_pdf_path, "rb") as f:
                reader = PdfReader(f)
                first_page = reader.pages[0]
                page_width = float(first_page.mediabox.width)
                page_height = float(first_page.mediabox.height)
                page_size = (page_width, page_height)
        except Exception:
            page_size = letter
    if page_size is None:
        page_size = letter
    page_width, page_height = page_size

    # Crea un PDF con l'immagine
    c = canvas.Canvas(output_path, pagesize=page_size)
      # Calcola la posizione dell'immagine in base al parametro position
    # Lascia un margine di 20 punti dai bordi
    margin = 20
    
    # Gestisce posizioni personalizzate dal formato "custom:x,y" (coordinate relative 0-1)
    if position.startswith("custom:"):
        try:
            coords = position.split(":")[1].split(",")
            rel_x, rel_y = float(coords[0]), float(coords[1])
            x_position = rel_x * page_width
            y_position = rel_y * page_height
        except:
            # Fallback a bottom-right se formato non valido
            x_position = page_width - img_width - margin
            y_position = margin
    else:
        # Definisce le posizioni predefinite disponibili
        positions = {
            "bottom-right": (page_width - img_width - margin, margin),
            "bottom-left": (margin, margin),
            "top-right": (page_width - img_width - margin, page_height - img_height - margin),
            "top-left": (margin, page_height - img_height - margin)
        }
        
        # Verifica che la posizione sia valida
        if position not in positions:
            raise ValueError(f"Posizione non valida: {position}. Posizioni disponibili: {', '.join(positions.keys())}")
        
        x_position, y_position = positions[position]
    
    # Assicurati che l'immagine non esca dai bordi della pagina
    if x_position < 0:
        x_position = margin
    if x_position + img_width > page_width:
        x_position = page_width - img_width - margin
    if y_position < 0:
        y_position = margin
    if y_position + img_height > page_height:
        y_position = page_height - img_height - margin
    
    c.drawImage(image_path, x_position, y_position, 
                width=img_width, height=img_height, mask='auto')
    c.save()
    
    return output_path


def add_watermark_to_pdf(input_pdf_path, watermark_image_path, output_pdf_path, 
                         scale_factor=1.0, position="bottom-right", **kwargs):
    """
    Aggiunge un marchio a tutte le pagine di un file PDF.
    Versione estesa con supporto per funzionalità avanzate.
    
    Args:
        input_pdf_path (str): Percorso del file PDF di input
        watermark_image_path (str): Percorso dell'immagine del marchio
        output_pdf_path (str): Percorso del file PDF di output
        scale_factor (float): Fattore di scala per il marchio (default: 1.0)
        position (str): Posizione del marchio ("bottom-right", "bottom-left", "top-right", "top-left")
        **kwargs: Parametri avanzati (pages, opacity, border_enabled, timestamp_enabled, etc.)
    """
    # Verifica che i file esistano
    if not os.path.exists(input_pdf_path):
        raise FileNotFoundError(f"File PDF non trovato: {input_pdf_path}")
    
    if not os.path.exists(watermark_image_path):
        raise FileNotFoundError(f"Immagine marchio non trovata: {watermark_image_path}")
      # Se sono richieste funzionalità avanzate, usa la funzione avanzata
    if _has_advanced_features(kwargs):
        print("🚀 Modalità avanzata attivata")
        return add_watermark_to_pdf_advanced(input_pdf_path, watermark_image_path, output_pdf_path, 
                                            scale_factor, position, **kwargs)
    
    # Modalità standard (retrocompatibilità)
    print(f"Creazione del marchio con fattore di scala: {scale_factor}")
    print(f"Posizione del marchio: {position}")
    
    # Gestione pagine specifiche anche in modalità standard
    pages_to_process = kwargs.get('pages', 'all')
    exclude_pages = kwargs.get('exclude_pages', None)

    # Ricava dimensioni pagina dal PDF originale
    with open(input_pdf_path, 'rb') as f:
        reader_tmp = PdfReader(f)
        first_page = reader_tmp.pages[0]
        page_size = (
            float(first_page.mediabox.width),
            float(first_page.mediabox.height),
        )

    watermark_pdf_path = create_watermark_pdf(
        watermark_image_path,
        scale_factor,
        position=position,
        page_size=page_size,
    )
    
    try:
        # Leggi il PDF originale
        print(f"Lettura del PDF: {input_pdf_path}")
        with open(input_pdf_path, 'rb') as input_file:
            input_pdf = PdfReader(input_file)
            total_pages = len(input_pdf.pages)            # Determina pagine da processare
            if pages_to_process != 'all':
                pages_indices = parse_pages_specification(pages_to_process, total_pages)
                if exclude_pages:
                    excluded = parse_pages_specification(exclude_pages, total_pages)
                    pages_indices = [p for p in pages_indices if p not in excluded]
            else:
                pages_indices = list(range(total_pages))
            
            # Leggi il PDF del marchio
            with open(watermark_pdf_path, 'rb') as watermark_file:
                watermark_pdf = PdfReader(watermark_file)
                watermark_page = watermark_pdf.pages[0]
                
                # Crea il PDF di output
                output_pdf = PdfWriter()
                
                # Aggiungi il marchio a ogni pagina
                print(f"Elaborazione di {total_pages} pagine...")
                
                for i, page in enumerate(input_pdf.pages):
                    if i in pages_indices:
                        print(f"Firmo pagina {i+1}/{total_pages}")
                        # Aggiungi il marchio alla pagina
                        page.merge_page(watermark_page)
                    else:
                        print(f"Salto pagina {i+1}/{total_pages}")
                    
                    output_pdf.add_page(page)
                
                # Aggiungi metadati base se specificati
                if kwargs.get('add_metadata', False):
                    metadata = {}
                    if kwargs.get('author'):
                        metadata['/Author'] = kwargs['author']
                    if kwargs.get('title'):
                        metadata['/Title'] = kwargs['title']
                    if kwargs.get('subject'):
                        metadata['/Subject'] = kwargs['subject']
                    metadata['/Creator'] = 'PDF Signer'
                    metadata['/ModDate'] = f"D:{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    output_pdf.add_metadata(metadata)
                
                # Salva il PDF modificato
                print(f"Salvataggio del PDF modificato: {output_pdf_path}")
                with open(output_pdf_path, 'wb') as output_file:
                    output_pdf.write(output_file)
    
    finally:
        # Elimina il file temporaneo
        try:
            os.unlink(watermark_pdf_path)
        except:
            pass
    
    print(f"Operazione completata! PDF salvato in: {output_pdf_path}")


def _has_advanced_features(kwargs):
    """Verifica se sono richieste funzionalità avanzate."""
    advanced_keys = [
        'pages', 'exclude_pages', 'opacity', 'border_width', 'shadow_enabled', 
        'timestamp', 'add_metadata', 'email_config', 'email_recipients'
    ]
    return any(key in kwargs for key in advanced_keys)


def _parse_pages_basic(pages_spec, total_pages):
    """Analisi base delle pagine senza il modulo avanzato."""
    pages = []

    if pages_spec == 'first':
        if total_pages > 0:
            pages.append(0)
    elif pages_spec == 'last':
        if total_pages > 0:
            pages.append(total_pages - 1)
    elif pages_spec.isdigit():
        page_num = int(pages_spec) - 1
        if 0 <= page_num < total_pages:
            pages.append(page_num)
    else:
        # Gestione base di range separati da virgole
        for part in pages_spec.split(','):
            part = part.strip()
            if '-' in part:
                try:
                    start, end = map(int, part.split('-'))
                    pages.extend(range(start - 1, min(end, total_pages)))
                except ValueError:
                    continue
            elif part.isdigit():
                page_num = int(part) - 1
                if 0 <= page_num < total_pages:
                    pages.append(page_num)

    return sorted(list(set(pages)))


def interactive_mode():
    """Modalità interattiva del programma con opzioni avanzate."""
    print("=== Modalità Interattiva - Programma per aggiungere marchio ai PDF ===\n")
    
    # Input del percorso del PDF
    while True:
        pdf_path = input("Inserisci il percorso completo del file PDF: ").strip().strip('"')
        if os.path.exists(pdf_path) and pdf_path.lower().endswith('.pdf'):
            break
        else:
            print("File non trovato o non è un PDF. Riprova.")
    
    # Conta le pagine del PDF
    try:
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            total_pages = len(reader.pages)
            print(f"ℹ️  Il PDF contiene {total_pages} pagine")
    except:
        total_pages = 0
        print("⚠️  Impossibile leggere il numero di pagine")
    
    # Input del fattore di scala
    while True:
        try:
            scale_input = input("Inserisci il fattore di scala per il marchio (default 0.2): ").strip()
            if scale_input == "":
                scale_factor = 0.2
            else:
                scale_factor = float(scale_input)
            if scale_factor > 0:
                break
            else:
                print("Il fattore di scala deve essere maggiore di 0.")
        except ValueError:
            print("Inserisci un numero valido.")
    
    # Input della posizione del marchio
    print("\nPosizioni disponibili per il marchio:")
    print("1. Basso a destra (default)")
    print("2. Basso a sinistra")
    print("3. Alto a destra")
    print("4. Alto a sinistra")
    print("5. Centro")
    
    position_map = {
        "1": "bottom-right",
        "2": "bottom-left", 
        "3": "top-right",
        "4": "top-left",
        "5": "center",
        "": "bottom-right"  # default
    }
    
    while True:
        position_input = input("Scegli la posizione (1-5, default 1): ").strip()
        if position_input in position_map:
            position = position_map[position_input]
            break
        else:
            print("Scelta non valida. Inserisci un numero da 1 a 5.")
    
    # Selezione pagine da firmare
    print("\nPagine da firmare:")
    print("1. Tutte le pagine (default)")
    print("2. Solo la prima pagina")
    print("3. Solo l'ultima pagina")
    print("4. Pagine specifiche")
    
    pages_choice = input("Scegli (1-4, default 1): ").strip()
    
    if pages_choice == "2":
        pages_to_sign = "first"
    elif pages_choice == "3":
        pages_to_sign = "last"
    elif pages_choice == "4":
        pages_to_sign = input("Inserisci le pagine (es: 1,3,5-10): ").strip()
        if not pages_to_sign:
            pages_to_sign = "all"
    else:
        pages_to_sign = "all"
      # Opzioni avanzate
    advanced_options = {}
    print("\n=== Opzioni Avanzate ===")
    
    # Opacità
    opacity_input = input("Opacità della firma (0.1-1.0, default 0.8): ").strip()
    if opacity_input:
        try:
            opacity = float(opacity_input)
            if 0.1 <= opacity <= 1.0:
                advanced_options['opacity'] = opacity
        except ValueError:
            pass
      # Bordi
    border_choice = input("Aggiungere bordo alla firma? (s/n, default n): ").strip().lower()
    if border_choice in ['s', 'si', 'y', 'yes']:
        advanced_options['border_enabled'] = True
        border_color = input("Colore del bordo (default black): ").strip()
        if border_color:
            advanced_options['border_color'] = border_color
        
        # Ombra
        shadow_choice = input("Aggiungere ombra alla firma? (s/n, default n): ").strip().lower()
        if shadow_choice in ['s', 'si', 'y', 'yes']:
            advanced_options['shadow_enabled'] = True
        
        # Timestamp
        timestamp_choice = input("Aggiungere timestamp? (s/n, default n): ").strip().lower()
        if timestamp_choice in ['s', 'si', 'y', 'yes']:
            advanced_options['timestamp_enabled'] = True
            timestamp_pos = input("Posizione timestamp (above/below/left/right, default below): ").strip()
            if timestamp_pos in ['above', 'below', 'left', 'right']:
                advanced_options['timestamp_position'] = timestamp_pos
        
        # Metadati
        metadata_choice = input("Aggiungere metadati personalizzati? (s/n, default n): ").strip().lower()
        if metadata_choice in ['s', 'si', 'y', 'yes']:
            advanced_options['add_metadata'] = True
            author = input("Autore (opzionale): ").strip()
            if author:
                advanced_options['author'] = author
            title = input("Titolo (opzionale): ").strip()
            if title:
                advanced_options['title'] = title
    
    # Percorso dell'immagine marchio
    watermark_path = "sign.png"
    if not os.path.exists(watermark_path):
        # Prova altri file comuni
        possible_files = ["signAL.png", "signature.png", "sign.jpg", "signature.jpg"]
        found_file = None
        for file in possible_files:
            if os.path.exists(file):
                found_file = file
                break
        
        if found_file:
            use_found = input(f"Trovato {found_file}, usare questo file? (s/n): ").strip().lower()
            if use_found in ['s', 'si', 'y', 'yes']:
                watermark_path = found_file
            else:
                watermark_path = input("Inserisci il percorso completo dell'immagine marchio: ").strip().strip('"')
        else:
            print(f"Attenzione: Nessun file marchio trovato.")
            watermark_path = input("Inserisci il percorso completo dell'immagine marchio: ").strip().strip('"')
    
    # Input del percorso di output (opzionale)
    output_input = input("Inserisci il percorso di output (lascia vuoto per generarlo automaticamente): ").strip().strip('"')
    
    if output_input:
        output_path = output_input
    else:
        # Genera il percorso di output automaticamente
        input_path = Path(pdf_path)
        output_path = str(input_path.parent / (input_path.stem + "_signed" + input_path.suffix))
    
    # Riepilogo configurazione
    print(f"\n=== Configurazione ===")
    print(f"PDF di input: {pdf_path}")
    print(f"Marchio: {watermark_path}")
    print(f"Fattore di scala: {scale_factor}")
    print(f"Posizione: {position}")
    print(f"Pagine da firmare: {pages_to_sign}")
    print(f"PDF di output: {output_path}")
    
    if advanced_options:
        print("\n=== Opzioni Avanzate ===")
        for key, value in advanced_options.items():
            print(f"{key}: {value}")
    
    confirm = input("\nProcedere con l'elaborazione? (s/n): ").strip().lower()
    if confirm not in ['s', 'si', 'y', 'yes']:
        print("Operazione annullata.")
        return
    
    try:
        # Combina tutte le opzioni
        kwargs = {
            'pages': pages_to_sign,
            **advanced_options
        }
        
        add_watermark_to_pdf(pdf_path, watermark_path, output_path, scale_factor, position, **kwargs)
        print(f"\n✅ Successo! PDF firmato salvato in: {output_path}")
        
        # Opzione per aprire il file
        if sys.platform == "win32":
            open_choice = input("Aprire il file firmato? (s/n): ").strip().lower()
            if open_choice in ['s', 'si', 'y', 'yes']:
                os.startfile(output_path)
    except Exception as e:
        print(f"\n❌ Errore durante l'elaborazione: {e}")
        print("💡 Suggerimento: Controlla i percorsi dei file e riprova")
    


def command_line_mode():
    """Modalità da riga di comando del programma con supporto opzioni avanzate."""
    parser = argparse.ArgumentParser(
        description="Aggiunge un marchio a tutte le pagine di un file PDF",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi d'uso:

  # Firma base
  %(prog)s documento.pdf -w sign.png -o documento_firmato.pdf

  # Firma solo prima pagina con scala personalizzata
  %(prog)s documento.pdf -w sign.png -s 0.3 --pages first

  # Firma con opzioni avanzate (richiede pdf_signer_advanced.py)
  %(prog)s documento.pdf -w sign.png --opacity 0.6 --border --timestamp

Formati immagine supportati: PNG, JPG, JPEG, GIF (SVG con modulo avanzato)
        """
    )
    
    # Argomenti base
    parser.add_argument(
        "input_pdf",
        help="Percorso del file PDF di input"
    )
    parser.add_argument(
        "-o", "--output",
        help="Percorso del file PDF di output (default: aggiunge '_signed' al nome originale)"
    )
    parser.add_argument(
        "-s", "--scale",
        type=float,
        default=0.2,
        help="Fattore di scala per il marchio (default: 0.2)"
    )
    parser.add_argument(
        "-w", "--watermark",
        default="sign.png",
        help="Percorso dell'immagine del marchio (default: sign.png)"
    )
    parser.add_argument(
        "-p", "--position",
        choices=["bottom-right", "bottom-left", "top-right", "top-left", "center"],
        default="bottom-right",
        help="Posizione del marchio (default: bottom-right)"
    )
    
    # Opzioni per selezione pagine
    parser.add_argument(
        "--pages",
        default="all",
        help="Pagine da firmare: 'all', 'first', 'last', '1,3,5-10' (default: all)"
    )
    parser.add_argument(
        "--exclude",
        help="Pagine da escludere (stesso formato di --pages)"
    )
      # Opzioni per effetti
    parser.add_argument(
        "--border-width",
        type=int,
        default=0,
        help="Spessore bordo in pixel (0=disabilitato, default: 0)"
    )
    parser.add_argument(
        "--border-color",
        default="0,0,0",
        help="Colore bordo formato 'R,G,B' (default: 0,0,0)"
    )
    parser.add_argument(
        "--shadow",
        action='store_true',
        help="Abilita ombra sulla firma"
    )
    parser.add_argument(
        "--shadow-offset",
        default="5,5",
        help="Offset ombra formato 'x,y' (default: 5,5)"
    )
    
    # Opzioni timestamp
    parser.add_argument(
        "--timestamp",
        action='store_true',
        help="Aggiungi timestamp"
    )
    parser.add_argument(
        "--timestamp-format",
        choices=["short", "long", "full", "iso", "custom"],
        default="short",
        help="Formato timestamp (default: short)"
    )
    parser.add_argument(
        "--timestamp-custom",
        help="Formato personalizzato per timestamp (per format=custom)"
    )
    
    # Opzioni metadati
    parser.add_argument(
        "--add-metadata",
        action='store_true',
        help="Aggiungi metadati al PDF"
    )
    parser.add_argument(
        "--author",
        help="Autore del documento"
    )
    parser.add_argument(
        "--title",
        help="Titolo del documento"
    )
    parser.add_argument(
        "--subject",
        help="Soggetto del documento"
    )
    
    # Opzioni email
    parser.add_argument(
        "--email-config",
        help="Percorso file configurazione email (YAML/JSON)"
    )
    parser.add_argument(
        "--email-recipients",
        help="Destinatari email separati da virgola"
    )
    parser.add_argument(
        "--email-template",
        help="Percorso template email"
    )
    
    args = parser.parse_args()
    
    # Verifica se il file watermark di default esiste, altrimenti prova altri file comuni
    if args.watermark == "sign.png" and not os.path.exists(args.watermark):
        # Lista di file comuni da provare
        common_files = ["signAL.png", "signature.png", "sign.jpg", "signature.jpg"]
        found_file = None
        
        for file in common_files:
            if os.path.exists(file):
                found_file = file
                print(f"📁 File marchio di default non trovato, uso: {file}")
                break
        
        if found_file:
            args.watermark = found_file
        else:
            print(f"❌ Errore: File marchio non trovato: {args.watermark}")
            print("💡 File disponibili nella directory:")
            for file in os.listdir('.'):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg')):
                    print(f"   - {file}")
            return 1
    
    # Determina il percorso di output se non specificato
    if args.output is None:
        input_path = Path(args.input_pdf)
        output_name = input_path.stem + "_signed" + input_path.suffix
        args.output = str(input_path.parent / output_name)
    
    try:
        # Prepara parametri avanzati    try:
        # Prepara parametri avanzati
        kwargs = {}
        
        # Pagine
        if args.pages != "all":
            kwargs['pages'] = args.pages
        if args.exclude:
            kwargs['exclude_pages'] = args.exclude
        
        # Effetti
        if args.border_width > 0:
            kwargs['border_width'] = args.border_width
            try:
                color_parts = [int(x) for x in args.border_color.split(',')]
                if len(color_parts) == 3:
                    kwargs['border_color'] = tuple(color_parts)
            except ValueError:
                print("⚠️ Formato colore bordo non valido, uso nero")
                kwargs['border_color'] = (0, 0, 0)
        
        if args.shadow:
            kwargs['shadow_enabled'] = True
            try:
                offset_parts = [int(x) for x in args.shadow_offset.split(',')]
                if len(offset_parts) == 2:
                    kwargs['shadow_offset'] = tuple(offset_parts)
            except ValueError:
                print("⚠️ Formato offset ombra non valido, uso default")
                kwargs['shadow_offset'] = (5, 5)
        
        # Timestamp
        if args.timestamp:
            kwargs['timestamp'] = True
            kwargs['timestamp_format'] = args.timestamp_format
            if args.timestamp_custom:
                kwargs['timestamp_custom'] = args.timestamp_custom
        
        # Metadati
        if args.add_metadata or args.author or args.title or args.subject:
            kwargs['add_metadata'] = True
            if args.author:
                kwargs['author'] = args.author
            if args.title:
                kwargs['title'] = args.title
            if args.subject:
                kwargs['subject'] = args.subject
        
        # Email
        if args.email_config and args.email_recipients:
            kwargs['email_config'] = args.email_config
            kwargs['email_recipients'] = [r.strip() for r in args.email_recipients.split(',')]
            if args.email_template:
                kwargs['email_template'] = args.email_template
        
        print(f"🔄 Inizio elaborazione: {args.input_pdf}")
        if kwargs:
            features = []
            if 'pages' in kwargs and kwargs['pages'] != 'all':
                features.append(f"pagine: {kwargs['pages']}")
            if 'border_width' in kwargs:
                features.append("bordo")
            if 'shadow_enabled' in kwargs:
                features.append("ombra")
            if 'timestamp' in kwargs:
                features.append("timestamp")
            if 'add_metadata' in kwargs:
                features.append("metadati")
            if 'email_config' in kwargs:
                features.append("email")
            
            if features:
                print(f"⚙️ Funzionalità attive: {', '.join(features)}")
        
        success = add_watermark_to_pdf(
            args.input_pdf,
            args.watermark,
            args.output,
            args.scale,
            args.position,
            **kwargs
        )
        
        if success:
            print(f"✅ Completato! File salvato: {args.output}")
            return 0
        else:
            print("❌ Errore nell'elaborazione")
            return 1
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        return 1


def main():
    """Funzione principale del programma."""
    # Se vengono passati argomenti da riga di comando (escludendo il nome del programma)
    if len(sys.argv) > 1:
        # Modalità riga di comando
        return command_line_mode()
    else:
        # Modalità interattiva        print("=== PDF Signer - Programma per aggiungere marchio ai PDF ===")
        print("🚀 Versione avanzata con funzionalità estese")
        print("\nScegli la modalità:")
        print("1. Modalità interattiva (guidata)")
        print("2. Mostra aiuto per modalità riga di comando")
        print("3. Esci")
        
        while True:
            try:
                choice = input("\nScegli un'opzione: ").strip()
                
                if choice == "1":
                    interactive_mode()
                    break
                elif choice == "2":                    
                    print("\n=== Modalità Riga di Comando ===")
                    print("Usa il programma da terminale con questi parametri:")
                    print(f"python {sys.argv[0]} <file_pdf> [opzioni]")
                    print("\nOpzioni base:")
                    print("  -o, --output PATH     Percorso del file PDF di output")
                    print("  -s, --scale FLOAT     Fattore di scala per il marchio (default: 0.2)")
                    print("  -w, --watermark PATH  Percorso dell'immagine marchio (default: sign.png)")
                    print("  -p, --position POS    Posizione del marchio")
                    print("  --pages SPEC          Pagine da firmare (all/first/last/1,3,5-10)")
                    print("  --exclude SPEC        Pagine da escludere")
                    print("  --border-width N      Spessore bordo")
                    print("  --shadow              Abilita ombra")
                    print("  --timestamp           Aggiungi data/ora")
                    print("  --add-metadata        Aggiungi metadati")
                    print("  --email-config PATH   Configurazione email")
                    
                    print("\nEsempi d'uso:")
                    print(f"  python {sys.argv[0]} doc.pdf -s 0.3 -p top-left")
                    print(f"  python {sys.argv[0]} doc.pdf --pages first --timestamp")
                    print(f"  python {sys.argv[0]} doc.pdf --border-width 2 --shadow")
                    input("\nPremi Invio per continuare...")
                    continue
                elif choice == "3":
                    print("Arrivederci!")
                    break
                else:
                    print("Opzione non valida. Scegli 1, 2 o 3.")
                    
            except KeyboardInterrupt:
                print("\n\nProgramma interrotto dall'utente.")
                break
            except EOFError:
                print("\n\nProgramma terminato.")
                break
    
    return 0


# Funzioni avanzate integrate
def parse_pages_specification(pages_str: str, total_pages: int):
    """
    Converte una stringa di pagine in una lista di numeri di pagina.
    
    Args:
        pages_str: Stringa formato "1,3,5-10" o "first", "last", "all", "odd", "even"
        total_pages: Numero totale di pagine nel PDF
        
    Returns:
        Lista di numeri di pagina (0-indexed)
    """
    if not pages_str or pages_str.lower() == "all":
        return list(range(total_pages))
    
    if pages_str.lower() == "first":
        return [0] if total_pages > 0 else []
    
    if pages_str.lower() == "last":
        return [total_pages - 1] if total_pages > 0 else []
    
    if pages_str.lower() == "odd":
        return [i for i in range(0, total_pages, 2)]
    
    if pages_str.lower() == "even":
        return [i for i in range(1, total_pages, 2)]
    
    pages = []
    for part in pages_str.split(','):
        part = part.strip()
        
        if '-' in part:
            # Range di pagine (es: 5-10)
            try:
                start, end = part.split('-', 1)
                start = int(start) - 1  # Converti a 0-indexed
                end = int(end) - 1
                pages.extend(range(max(0, start), min(total_pages, end + 1)))
            except ValueError:
                print(f"Formato pagina non valido: {part}")
        else:
            # Singola pagina
            try:
                page = int(part) - 1  # Converti a 0-indexed
                if 0 <= page < total_pages:
                    pages.append(page)
            except ValueError:
                print(f"Numero pagina non valido: {part}")
    
    return sorted(list(set(pages)))  # Rimuovi duplicati e ordina


def process_image_format(image_path: str) -> str:
    """
    Verifica e converte l'immagine in un formato supportato se necessario.
    
    Args:
        image_path: Percorso dell'immagine
        
    Returns:
        Percorso dell'immagine processata (potrebbe essere un file temporaneo)
    """
    supported_formats = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    
    if Path(image_path).suffix.lower() not in supported_formats:
        print(f"Formato non supportato: {Path(image_path).suffix}")
        return image_path
    
    try:
        # Verifica che l'immagine sia valida
        with Image.open(image_path) as img:
            # Converti in PNG se ha trasparenza e non è già PNG
            if img.mode in ('RGBA', 'LA') and not image_path.lower().endswith('.png'):
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                temp_path = temp_file.name
                temp_file.close()
                img.save(temp_path, 'PNG')
                print(f"Immagine convertita in PNG: {temp_path}")
                return temp_path
            
    except Exception as e:
        print(f"Errore nell'elaborazione dell'immagine: {e}")
    
    return image_path


def add_image_effects(image_path: str, border_width: int = 0, border_color=(0, 0, 0),
                     shadow_enabled: bool = False, shadow_offset=(5, 5)) -> str:
    """
    Aggiunge effetti all'immagine (bordo, ombra).
    
    Args:
        image_path: Percorso dell'immagine
        border_width: Spessore del bordo
        border_color: Colore del bordo (R, G, B)
        shadow_enabled: Abilita ombra
        shadow_offset: Offset dell'ombra (x, y)
        
    Returns:
        Percorso dell'immagine con effetti applicati
    """
    if border_width == 0 and not shadow_enabled:
        return image_path
    
    try:
        with Image.open(image_path) as img:
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Aggiungi bordo
            if border_width > 0:
                new_size = (img.width + 2 * border_width, img.height + 2 * border_width)
                bordered_img = Image.new('RGBA', new_size, (*border_color, 255))
                bordered_img.paste(img, (border_width, border_width), img)
                img = bordered_img            # Aggiungi ombra (implementazione semplificata)
            if shadow_enabled:
                shadow_x, shadow_y = shadow_offset
                shadow_size = (img.width + abs(shadow_x), img.height + abs(shadow_y))
                shadow_img = Image.new('RGBA', shadow_size, (0, 0, 0, 0))
                
                # Crea ombra semplice
                shadow = Image.new('RGBA', img.size, (50, 50, 50, 128))
                shadow_img.paste(shadow, (max(0, shadow_x), max(0, shadow_y)), img.split()[-1])
                shadow_img.paste(img, (max(0, -shadow_x), max(0, -shadow_y)), img)
                img = shadow_img
            
            # Salva immagine con effetti
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_path = temp_file.name
            temp_file.close()
            img.save(temp_path, 'PNG')
            return temp_path
            
    except Exception as e:
        print(f"Errore nell'applicazione degli effetti: {e}")
        return image_path


def create_timestamp_image(format_type: str = 'short', custom_format: Optional[str] = None) -> str:
    """
    Crea un'immagine con timestamp.
    
    Args:
        format_type: Tipo di formato ('short', 'long', 'full', 'iso', 'custom')
        custom_format: Formato personalizzato se format_type='custom'
        
    Returns:
        Percorso dell'immagine timestamp
    """
    formats = {
        'short': '%d/%m/%Y',
        'long': '%d/%m/%Y %H:%M',
        'full': '%d/%m/%Y %H:%M:%S',
        'iso': '%Y-%m-%d %H:%M:%S'
    }
    
    if format_type == 'custom' and custom_format:
        date_format = custom_format
    else:
        date_format = formats.get(format_type, formats['short'])
    
    # Genera timestamp
    now = datetime.now()
    timestamp_text = now.strftime(date_format)
    
    # Crea immagine semplice
    font_size = 12
    char_width = font_size * 0.6
    text_width = int(len(timestamp_text) * char_width)
    text_height = int(font_size * 1.5)
    
    img = Image.new('RGBA', (text_width + 20, text_height + 10), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.text((10, 5), timestamp_text, fill=(0, 0, 0, 255))
    
    # Salva in file temporaneo
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    temp_path = temp_file.name
    temp_file.close()
    img.save(temp_path, 'PNG')
    return temp_path


def add_pdf_metadata(pdf_path: str, metadata: dict) -> None:
    """
    Aggiunge metadati a un PDF esistente.
    
    Args:
        pdf_path: Percorso del PDF
        metadata: Dizionario con metadati da aggiungere
    """
    try:
        # Leggi PDF esistente
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            writer = PdfWriter()
            
            # Copia tutte le pagine
            for page in reader.pages:
                writer.add_page(page)
            
            # Aggiungi metadati esistenti
            if reader.metadata:
                for key, value in reader.metadata.items():
                    writer.add_metadata({key: value})
            
            # Aggiungi nuovi metadati
            writer.add_metadata(metadata)
        
        # Sovrascrivi il file
        with open(pdf_path, 'wb') as file:
            writer.write(file)
            
    except Exception as e:
        print(f"Errore nell'aggiunta dei metadati: {e}")


def send_email_with_pdf(pdf_path: str, email_config: dict, recipients: list, 
                       subject: Optional[str] = None, body: Optional[str] = None, template_path: Optional[str] = None) -> bool:
    """
    Invia PDF firmato via email.
    
    Args:
        pdf_path: Percorso del PDF da inviare
        email_config: Configurazione server email
        recipients: Lista destinatari
        subject: Oggetto email
        body: Corpo email
        template_path: Percorso template email
        
    Returns:
        True se invio riuscito
    """
    try:
        # Carica template se specificato
        if template_path and os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
                body = template_content.format(
                    pdf_name=Path(pdf_path).name,
                    timestamp=datetime.now().strftime("%d/%m/%Y %H:%M")
                )
        
        if not subject:
            subject = f"PDF Firmato: {Path(pdf_path).name}"
        
        if not body:
            body = f"In allegato il PDF firmato: {Path(pdf_path).name}"
          # Crea messaggio email
        msg = MIMEMultipart()
        
        # Gestisci diversi formati di configurazione
        from_addr = email_config.get('from_address') or email_config.get('sender', {}).get('email')
        if not from_addr:
            from_addr = email_config.get('smtp', {}).get('username')
        
        msg['From'] = from_addr
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        # Aggiungi corpo
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Aggiungi allegato PDF
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as attachment:
                part = MIMEBase('application', 'pdf')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {Path(pdf_path).name}'
                )
                msg.attach(part)
        
        # Connetti al server e invia - gestisci diverse strutture config
        smtp_config = email_config.get('smtp', email_config)
        smtp_server = smtp_config.get('server') or smtp_config.get('smtp_server')
        smtp_port = smtp_config.get('port') or smtp_config.get('smtp_port', 587)
        username = smtp_config.get('username')
        password = smtp_config.get('password')
        use_tls = smtp_config.get('use_tls', True)
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        if use_tls:
            server.starttls()
        
        if username and password:
            server.login(username, password)
        
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Errore nell'invio email: {e}")
        return False


def load_email_config(config_path: str) -> dict:
    """Carica configurazione email da file YAML."""
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                return yaml.safe_load(file)
            else:
                return json.load(file)
    except Exception as e:
        raise ValueError(f"Errore nel caricamento configurazione email: {e}")


# Versione migliorata della funzione principale
def add_watermark_to_pdf_advanced(input_pdf_path, watermark_image_path, output_pdf_path, 
                                 scale_factor=1.0, position="bottom-right", **kwargs):
    """
    Versione avanzata per aggiungere watermark con tutte le funzionalità extra.
    
    Parametri extra supportati:
    - pages: "all", "first", "last", "odd", "even", "1,3,5-10"
    - exclude_pages: "2,4"
    - opacity: 0.0-1.0
    - border_width: spessore bordo in pixel
    - border_color: (R, G, B)
    - shadow_enabled: True/False
    - shadow_offset: (x, y)
    - timestamp: True/False
    - timestamp_format: "short", "long", "full", "iso", "custom"
    - timestamp_custom: formato personalizzato
    - add_metadata: True/False
    - author, title, subject: metadati PDF
    - email_config: percorso file configurazione email
    - email_recipients: lista email destinatari
    - email_template: percorso template email
    """
    temp_files = []  # Lista file temporanei da pulire
    
    try:
        # Verifica esistenza file
        if not os.path.exists(input_pdf_path):
            raise FileNotFoundError(f"File PDF non trovato: {input_pdf_path}")
        
        if not os.path.exists(watermark_image_path):
            raise FileNotFoundError(f"Immagine firma non trovata: {watermark_image_path}")
        
        print(f"🔄 Elaborazione PDF: {Path(input_pdf_path).name}")
        
        # Processa immagine (formato, effetti)
        processed_image = process_image_format(watermark_image_path)
        if processed_image != watermark_image_path:
            temp_files.append(processed_image)
        
        # Applica effetti immagine
        if kwargs.get('border_width', 0) > 0 or kwargs.get('shadow_enabled', False):
            processed_image = add_image_effects(
                processed_image,
                kwargs.get('border_width', 0),
                kwargs.get('border_color', (0, 0, 0)),
                kwargs.get('shadow_enabled', False),
                kwargs.get('shadow_offset', (5, 5))
            )
            temp_files.append(processed_image)
          # Crea timestamp se richiesto
        timestamp_image = None
        if kwargs.get('timestamp', False):
            timestamp_format = kwargs.get('timestamp_format', 'short')
            timestamp_custom = kwargs.get('timestamp_custom')
            timestamp_image = create_timestamp_image(timestamp_format, timestamp_custom)
            temp_files.append(timestamp_image)
        
        # Determina pagine da processare e dimensioni pagina
        with open(input_pdf_path, 'rb') as file:
            reader = PdfReader(file)
            total_pages = len(reader.pages)
            first_page = reader.pages[0]
            page_size = (
                float(first_page.mediabox.width),
                float(first_page.mediabox.height),
            )

            pages_to_sign = parse_pages_specification(
                kwargs.get('pages', 'all'), total_pages
            )
              # Escludi pagine se specificato
            exclude_pages_str = kwargs.get('exclude_pages')
            if exclude_pages_str:
                excluded = parse_pages_specification(exclude_pages_str, total_pages)
                pages_to_sign = [p for p in pages_to_sign if p not in excluded]
        
        print(f"📄 Pagine da firmare: {len(pages_to_sign)}/{total_pages}")
        if len(pages_to_sign) < total_pages:
            pages_display = [str(p+1) for p in pages_to_sign[:5]]
            if len(pages_to_sign) > 5:
                pages_display.append('...')
            print(f"📋 Pagine selezionate: {', '.join(pages_display)}")
        
        # Crea watermark principale
        watermark_pdf_path = create_watermark_pdf(
            processed_image,
            scale_factor,
            position=position,
            page_size=page_size,
        )
        temp_files.append(watermark_pdf_path)
        
        # Crea watermark timestamp se necessario
        timestamp_pdf_path = None
        if timestamp_image:
            # Posiziona timestamp in base alla firma
            timestamp_position = _get_timestamp_position(position, kwargs.get('timestamp_position', 'below'))
            timestamp_pdf_path = create_watermark_pdf(
                timestamp_image,
                0.5,
                position=timestamp_position,
                page_size=page_size,
            )
            temp_files.append(timestamp_pdf_path)
        
        # Processa PDF
        with open(input_pdf_path, 'rb') as input_file:
            input_pdf = PdfReader(input_file)
            output_pdf = PdfWriter()
            
            # Carica watermark
            with open(watermark_pdf_path, 'rb') as wm_file:
                watermark_pdf = PdfReader(wm_file)
                watermark_page = watermark_pdf.pages[0]
                
                timestamp_page = None
                if timestamp_pdf_path:
                    with open(timestamp_pdf_path, 'rb') as ts_file:
                        timestamp_pdf = PdfReader(ts_file)
                        timestamp_page = timestamp_pdf.pages[0]
                
                # Processa ogni pagina
                for i, page in enumerate(input_pdf.pages):
                    if i in pages_to_sign:
                        # Aggiungi firma
                        page.merge_page(watermark_page)
                        # Aggiungi timestamp se presente
                        if timestamp_page:
                            page.merge_page(timestamp_page)
                        print(f"✓ Firmata pagina {i+1}")
                    
                    output_pdf.add_page(page)
            
            # Aggiungi metadati se richiesti
            if kwargs.get('add_metadata', False):
                metadata = {}
                if kwargs.get('author'):
                    metadata['/Author'] = kwargs['author']
                if kwargs.get('title'):
                    metadata['/Title'] = kwargs['title']
                if kwargs.get('subject'):
                    metadata['/Subject'] = kwargs['subject']
                
                metadata.update({
                    '/Creator': 'PDF Signer Advanced',
                    '/Producer': 'PDF Signer Advanced',
                    '/CreationDate': f"D:{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    '/ModDate': f"D:{datetime.now().strftime('%Y%m%d%H%M%S')}"
                })
                
                output_pdf.add_metadata(metadata)
                print("📝 Metadati aggiunti")
            
            # Salva PDF
            with open(output_pdf_path, 'wb') as output_file:
                output_pdf.write(output_file)
        
        print(f"✅ PDF firmato salvato: {output_pdf_path}")
        
        # Invia email se richiesto
        if kwargs.get('email_config') and kwargs.get('email_recipients'):
            try:
                config = load_email_config(kwargs['email_config'])
                success = send_email_with_pdf(
                    output_pdf_path, 
                    config, 
                    kwargs['email_recipients'],
                    kwargs.get('email_subject'),
                    kwargs.get('email_body'),
                    kwargs.get('email_template')
                )
                if success:
                    print(f"📧 Email inviata a: {', '.join(kwargs['email_recipients'])}")
                else:
                    print("⚠️ Errore nell'invio email")
            except Exception as e:
                print(f"⚠️ Errore configurazione email: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False
        
    finally:
        # Pulizia file temporanei
        for temp_file in temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            except Exception:
                pass


def _get_timestamp_position(signature_position: str, timestamp_relative: str) -> str:
    """Calcola posizione timestamp relativa alla firma."""
    positions_map = {
        "bottom-right": {
            "below": "bottom-right",
            "above": "bottom-right", 
            "left": "bottom-left",
            "right": "bottom-right"
        },
        "bottom-left": {
            "below": "bottom-left",
            "above": "bottom-left",
            "left": "bottom-left", 
            "right": "bottom-right"
        },
        "top-right": {
            "below": "bottom-right",
            "above": "top-right",
            "left": "top-left",
            "right": "top-right"
        },
        "top-left": {
            "below": "bottom-left",
            "above": "top-left", 
            "left": "top-left",
            "right": "top-right"
        }
    }
    
    return positions_map.get(signature_position, {}).get(
        timestamp_relative, "bottom-right"
    )


def calculate_watermark_size_points(image_path, scale_factor, dpi=300):
    """
    Calcola la dimensione del watermark in punti PDF in modo coerente.
    
    Args:
        image_path: Percorso all'immagine del watermark
        scale_factor: Fattore di scala da applicare
        dpi: DPI da assumere per la conversione pixel->punti
    
    Returns:
        Tuple (width_points, height_points, width_pixels, height_pixels)
    """
    try:
        with Image.open(image_path) as img:
            img_width_px, img_height_px = img.size
    except Exception as e:
        raise ValueError(f"Errore nell'aprire l'immagine {image_path}: {e}")
    
    # Converti da pixel a punti PDF (1 punto = 1/72 pollici)
    base_width_points = (img_width_px / dpi) * 72
    base_height_points = (img_height_px / dpi) * 72
    
    # Applica il fattore di scala
    final_width_points = base_width_points * scale_factor
    final_height_points = base_height_points * scale_factor
    
    return final_width_points, final_height_points, img_width_px, img_height_px
