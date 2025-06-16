#!/usr/bin/env python3
"""
Programma per aggiungere un marchio (watermark) a tutte le pagine di un file PDF.
Il marchio viene posizionato in fondo a destra di ogni pagina.
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfWriter, PdfReader
from PIL import Image
import tempfile
import argparse
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


def main():
    """Funzione principale del programma."""
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
        default="sign.png",
        help="Percorso dell'immagine del marchio (default: sign.png)"
    )
    
    args = parser.parse_args()
    
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


if __name__ == "__main__":
    exit(main())
