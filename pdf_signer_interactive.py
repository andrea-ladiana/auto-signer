#!/usr/bin/env python3
"""
Script semplificato per aggiungere un marchio a un PDF.
Uso interattivo con input dell'utente.
"""

import os
from pdf_signer import add_watermark_to_pdf
from pathlib import Path


def main():
    """Versione interattiva del programma."""
    print("=== Programma per aggiungere marchio ai PDF ===\n")
    
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
    watermark_path = "sign.png"
    if not os.path.exists(watermark_path):
        print(f"Attenzione: Il file {watermark_path} non è stato trovato nella directory corrente.")
        watermark_path = input("Inserisci il percorso completo dell'immagine marchio: ").strip().strip('"')
    
    # Genera il percorso di output
    input_path = Path(pdf_path)
    output_path = str(input_path.parent / (input_path.stem + "_signed" + input_path.suffix))
    
    print(f"\nConfigurazione:")
    print(f"PDF di input: {pdf_path}")
    print(f"Marchio: {watermark_path}")
    print(f"Fattore di scala: {scale_factor}")
    print(f"PDF di output: {output_path}")
    
    confirm = input("\nProcedere? (s/n): ").strip().lower()
    if confirm not in ['s', 'si', 'y', 'yes']:
        print("Operazione annullata.")
        return
    
    try:
        add_watermark_to_pdf(pdf_path, watermark_path, output_path, scale_factor)
        print(f"\n✅ Successo! PDF firmato salvato in: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Errore durante l'elaborazione: {e}")


if __name__ == "__main__":
    main()
