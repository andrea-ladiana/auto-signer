#!/usr/bin/env python3
"""
Programma unificato per aggiungere un marchio (watermark) a tutte le pagine di un file PDF.
Il marchio viene posizionato in fondo a destra di ogni pagina.

Supporta sia l'uso da riga di comando che l'interfaccia interattiva.
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfWriter, PdfReader
from PIL import Image
import tempfile
import argparse
import sys
from pathlib import Path


def create_watermark_pdf(image_path, scale_factor=1.0, output_path=None):
    """
    Crea un PDF temporaneo contenente solo il marchio (watermark).
    
    Args:
        image_path (str): Percorso dell'immagine del marchio
        scale_factor (float): Fattore di scala per ridimensionare il marchio
        output_path (str): Percorso del file PDF temporaneo (opzionale)
    
    Returns:
        str: Percorso del file PDF temporaneo creato
    """
    if output_path is None:
        # Crea un file temporaneo
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        output_path = temp_file.name
        temp_file.close()
    
    # Apri l'immagine per ottenere le dimensioni
    try:
        with Image.open(image_path) as img:
            img_width, img_height = img.size
    except Exception as e:
        raise ValueError(f"Errore nell'aprire l'immagine {image_path}: {e}")
    
    # Applica il fattore di scala
    img_width *= scale_factor
    img_height *= scale_factor
    
    # Crea un PDF con l'immagine
    c = canvas.Canvas(output_path, pagesize=letter)
    page_width, page_height = letter
    
    # Posiziona l'immagine in fondo a destra
    # Lascia un margine di 20 punti dai bordi
    margin = 20
    x_position = page_width - img_width - margin
    y_position = margin
    
    # Assicurati che l'immagine non esca dai bordi della pagina
    if x_position < 0:
        x_position = margin
    if y_position + img_height > page_height:
        y_position = page_height - img_height - margin
    
    c.drawImage(image_path, x_position, y_position, 
                width=img_width, height=img_height, mask='auto')
    c.save()
    
    return output_path


def add_watermark_to_pdf(input_pdf_path, watermark_image_path, output_pdf_path, scale_factor=1.0):
    """
    Aggiunge un marchio a tutte le pagine di un file PDF.
    
    Args:
        input_pdf_path (str): Percorso del file PDF di input
        watermark_image_path (str): Percorso dell'immagine del marchio
        output_pdf_path (str): Percorso del file PDF di output
        scale_factor (float): Fattore di scala per il marchio (default: 1.0)
    """
    # Verifica che i file esistano
    if not os.path.exists(input_pdf_path):
        raise FileNotFoundError(f"File PDF non trovato: {input_pdf_path}")
    
    if not os.path.exists(watermark_image_path):
        raise FileNotFoundError(f"Immagine marchio non trovata: {watermark_image_path}")
    
    # Crea il PDF temporaneo con il marchio
    print(f"Creazione del marchio con fattore di scala: {scale_factor}")
    watermark_pdf_path = create_watermark_pdf(watermark_image_path, scale_factor)
    
    try:
        # Leggi il PDF originale
        print(f"Lettura del PDF: {input_pdf_path}")
        with open(input_pdf_path, 'rb') as input_file:
            input_pdf = PdfReader(input_file)
            
            # Leggi il PDF del marchio
            with open(watermark_pdf_path, 'rb') as watermark_file:
                watermark_pdf = PdfReader(watermark_file)
                watermark_page = watermark_pdf.pages[0]
                
                # Crea il PDF di output
                output_pdf = PdfWriter()
                
                # Aggiungi il marchio a ogni pagina
                total_pages = len(input_pdf.pages)
                print(f"Elaborazione di {total_pages} pagine...")
                
                for i, page in enumerate(input_pdf.pages, 1):
                    print(f"Elaborazione pagina {i}/{total_pages}")
                    
                    # Aggiungi il marchio alla pagina
                    page.merge_page(watermark_page)
                    output_pdf.add_page(page)
                
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


def interactive_mode():
    """Modalità interattiva del programma."""
    print("=== Modalità Interattiva - Programma per aggiungere marchio ai PDF ===\n")
    
    # Input del percorso del PDF
    while True:
        pdf_path = input("Inserisci il percorso completo del file PDF: ").strip().strip('"')
        if os.path.exists(pdf_path) and pdf_path.lower().endswith('.pdf'):
            break
        else:
            print("File non trovato o non è un PDF. Riprova.")
    
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
    
    # Percorso dell'immagine marchio
    watermark_path = "signAL.png"
    if not os.path.exists(watermark_path):
        watermark_path = "sign.png"
        if not os.path.exists(watermark_path):
            print(f"Attenzione: Nessun file marchio trovato (signAL.png o sign.png).")
            watermark_path = input("Inserisci il percorso completo dell'immagine marchio: ").strip().strip('"')
    
    # Input del percorso di output (opzionale)
    output_input = input("Inserisci il percorso di output (lascia vuoto per generarlo automaticamente): ").strip().strip('"')
    
    if output_input:
        output_path = output_input
    else:
        # Genera il percorso di output automaticamente
        input_path = Path(pdf_path)
        output_path = str(input_path.parent / (input_path.stem + "_signed" + input_path.suffix))
    
    print(f"\n=== Configurazione ===")
    print(f"PDF di input: {pdf_path}")
    print(f"Marchio: {watermark_path}")
    print(f"Fattore di scala: {scale_factor}")
    print(f"PDF di output: {output_path}")
    
    confirm = input("\nProcedere con l'elaborazione? (s/n): ").strip().lower()
    if confirm not in ['s', 'si', 'y', 'yes']:
        print("Operazione annullata.")
        return
    
    try:
        add_watermark_to_pdf(pdf_path, watermark_path, output_path, scale_factor)
        print(f"\n✅ Successo! PDF firmato salvato in: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Errore durante l'elaborazione: {e}")


def command_line_mode():
    """Modalità da riga di comando del programma."""
    parser = argparse.ArgumentParser(
        description="Aggiunge un marchio a tutte le pagine di un file PDF"
    )
    
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
        default=1.0,
        help="Fattore di scala per il marchio (default: 1.0)"
    )
    
    parser.add_argument(
        "-w", "--watermark",
        default="signAL.png",
        help="Percorso dell'immagine del marchio (default: signAL.png)"
    )
    
    args = parser.parse_args()
    
    # Verifica se il file watermark di default esiste, altrimenti prova sign.png
    if args.watermark == "signAL.png" and not os.path.exists(args.watermark):
        if os.path.exists("sign.png"):
            args.watermark = "sign.png"
    
    # Determina il percorso di output se non specificato
    if args.output is None:
        input_path = Path(args.input_pdf)
        output_name = input_path.stem + "_signed" + input_path.suffix
        args.output = str(input_path.parent / output_name)
    
    try:
        add_watermark_to_pdf(
            args.input_pdf,
            args.watermark,
            args.output,
            args.scale
        )
        
    except Exception as e:
        print(f"Errore: {e}")
        return 1
    
    return 0


def main():
    """Funzione principale del programma."""
    # Se vengono passati argomenti da riga di comando (escludendo il nome del programma)
    if len(sys.argv) > 1:
        # Modalità riga di comando
        return command_line_mode()
    else:
        # Modalità interattiva
        print("=== PDF Signer - Programma per aggiungere marchio ai PDF ===")
        print("\nScegli la modalità:")
        print("1. Modalità interattiva (guidata)")
        print("2. Mostra aiuto per modalità riga di comando")
        print("3. Esci")
        
        while True:
            try:
                choice = input("\nScegli un'opzione (1-3): ").strip()
                
                if choice == "1":
                    interactive_mode()
                    break
                elif choice == "2":
                    print("\n=== Modalità Riga di Comando ===")
                    print("Usa il programma da terminale con questi parametri:")
                    print(f"python {sys.argv[0]} <file_pdf> [opzioni]")
                    print("\nOpzioni disponibili:")
                    print("  -o, --output PATH     Percorso del file PDF di output")
                    print("  -s, --scale FLOAT     Fattore di scala per il marchio (default: 1.0)")
                    print("  -w, --watermark PATH  Percorso dell'immagine marchio (default: signAL.png)")
                    print("  -h, --help           Mostra questo aiuto")
                    print("\nEsempio d'uso:")
                    print(f"python {sys.argv[0]} documento.pdf -s 0.3 -o documento_firmato.pdf")
                    
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


if __name__ == "__main__":
    exit(main())
