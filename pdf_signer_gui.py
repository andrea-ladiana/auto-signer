#!/usr/bin/env python3
"""
GUI completa per PDF Signer con drag-and-drop, preview in tempo reale,
editor visuale per posizionamento e gestione profili.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
import tkinter.font as tkFont
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:  # Gestito in main()
    DND_FILES = None
    TkinterDnD = None
import json
import yaml
import os
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw
import threading
import queue
from datetime import datetime
import tempfile
try:
    import fitz  # PyMuPDF per anteprima PDF
except ImportError:  # Gestito in main()
    fitz = None
import subprocess
import sys
import time

# Import delle funzioni dal modulo originale
from pdf_signer import add_watermark_to_pdf, create_watermark_pdf, calculate_watermark_size_points

class ConfigManager:
    """Gestisce i profili e le configurazioni dell'applicazione."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".pdf_signer"
        self.config_file = self.config_dir / "config.yaml"
        self.profiles_file = self.config_dir / "profiles.json"
        self.ensure_config_dir()
        self.load_config()
        self.load_profiles()
    
    def ensure_config_dir(self):
        """Crea la directory di configurazione se non esiste."""
        self.config_dir.mkdir(exist_ok=True)
    
    def load_config(self):
        """Carica la configurazione generale."""        
        default_config = {
            'last_watermark_path': '',
            'last_output_dir': str(Path.home() / "Documents"),
            'default_scale': 1.0,
            'default_position': 'bottom-right',
            'default_opacity': 0.8,
            'window_geometry': '1200x800',
            'preview_quality': 'medium',
            'benchmark_preview': False
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or default_config
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            print(f"Errore nel caricamento config: {e}")
            self.config = default_config
    
    def save_config(self):
        """Salva la configurazione generale."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"Errore nel salvataggio config: {e}")
    
    def load_profiles(self):
        """Carica i profili di firma salvati."""
        try:
            if self.profiles_file.exists():
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    self.profiles = json.load(f)
            else:
                self.profiles = self.get_default_profiles()
                self.save_profiles()
        except Exception as e:
            print(f"Errore nel caricamento profili: {e}")
            self.profiles = self.get_default_profiles()
    
    def save_profiles(self):
        """Salva i profili di firma."""
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump(self.profiles, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Errore nel salvataggio profili: {e}")
    
    def get_default_profiles(self):
        """Restituisce i profili predefiniti con nuove funzionalità."""
        return {
            "Firma Standard": {
                "scale": 1.0,
                "position": "bottom-right",
                "opacity": 0.8,
                "watermark_path": "sign.png",
                "description": "Firma standard in basso a destra",
                "pages": "all",
                "border_width": 0,
                "border_color": (0, 0, 0),
                "shadow_enabled": False,
                "shadow_offset": (5, 5),
                "timestamp_enabled": False,
                "timestamp_format": "short",
                "timestamp_position": "bottom-left",
                "add_metadata": False,
                "email_enabled": False,
                "email_to": "",
                "email_subject": "PDF Firmato",
                "email_template": ""
            },
            "Firma Piccola": {
                "scale": 0.5,
                "position": "bottom-right",
                "opacity": 0.6,
                "watermark_path": "sign.png", 
                "description": "Firma piccola e discreta",
                "pages": "all",
                "border_width": 0,
                "border_color": (0, 0, 0),
                "shadow_enabled": False,
                "shadow_offset": (5, 5),
                "timestamp_enabled": False,
                "timestamp_format": "short",
                "timestamp_position": "bottom-left",
                "add_metadata": False,
                "email_enabled": False,
                "email_to": "",
                "email_subject": "PDF Firmato",
                "email_template": ""
            },            "Firma Ufficiale": {
                "scale": 1.5,
                "position": "bottom-left",
                "opacity": 1.0,
                "watermark_path": "signAL.png",
                "description": "Firma grande per documenti ufficiali",
                "pages": "all",
                "border_width": 2,
                "border_color": (0, 0, 0),
                "shadow_enabled": True,
                "shadow_offset": (3, 3),
                "timestamp_enabled": True,
                "timestamp_format": "long",
                "timestamp_position": "bottom-left",
                "add_metadata": True,
                "email_enabled": False,
                "email_to": "",
                "email_subject": "Documento Ufficiale Firmato",
                "email_template": ""
            },
            "Prima Pagina": {
                "scale": 1.2,
                "position": "bottom-right",
                "opacity": 0.9,
                "watermark_path": "sign.png",
                "description": "Firma solo sulla prima pagina",
                "pages": "first",
                "border_width": 1,
                "border_color": (50, 50, 50),
                "shadow_enabled": False,
                "shadow_offset": (5, 5),
                "timestamp_enabled": True,
                "timestamp_format": "short",
                "timestamp_position": "bottom-left",
                "add_metadata": True,
                "email_enabled": False,
                "email_to": "",
                "email_subject": "PDF Firmato",
                "email_template": ""
            },
            "Effetti Completi": {
                "scale": 1.0,
                "position": "bottom-right", 
                "opacity": 0.8,
                "watermark_path": "sign.png",
                "description": "Firma con tutti gli effetti",
                "pages": "all",
                "border_width": 3,
                "border_color": (100, 100, 100),
                "shadow_enabled": True,
                "shadow_offset": (4, 4),
                "timestamp_enabled": True,
                "timestamp_format": "full",
                "timestamp_position": "bottom-left",
                "add_metadata": True,
                "email_enabled": False,
                "email_to": "",
                "email_subject": "PDF con Effetti Avanzati",
                "email_template": ""
            }
        }


class PDFPreviewCanvas(tk.Canvas):
    """Canvas personalizzato per l'anteprima PDF con posizionamento interattivo."""
    
    def __init__(self, parent, preview_callback=None):
        super().__init__(parent, bg='white', relief='sunken', bd=2)
        self.preview_callback = preview_callback
        self.pdf_doc = None
        self.pdf_path = None
        self.current_page = 0
        self.page_image = None
        self.watermark_image = None
        self.watermark_position = (0, 0)
        self.watermark_size = (100, 50)
        self.scale_factor = 1.0
        self.dragging = False
        
        # Bind eventi mouse
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Configure>", self.on_resize)
    
    def load_pdf(self, pdf_path):
        """Carica un PDF per l'anteprima, evitando riaperture inutili."""
        try:
            if self.pdf_doc is None or self.pdf_path != pdf_path:
                self.pdf_doc = fitz.open(pdf_path)
                self.pdf_path = pdf_path
                self.current_page = 0
            self.render_page()
            return True
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile caricare il PDF: {e}")
            return False
    
    def render_page(self):
        """Renderizza la pagina corrente con il watermark."""
        if not self.pdf_doc:
            return
        
        try:
            # Ottieni la pagina
            page = self.pdf_doc[self.current_page]
            
            # Calcola il fattore di scala per adattare alla canvas
            canvas_width = self.winfo_width()
            canvas_height = self.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Handle different PyMuPDF versions and ensure we have a proper Page object
            try:
                page_rect = page.rect  # type: ignore
            except AttributeError:
                # Fallback for different PyMuPDF versions
                page_rect = page.bound()  # type: ignore
            scale_x = (canvas_width - 20) / page_rect.width
            scale_y = (canvas_height - 20) / page_rect.height
            self.scale_factor = min(scale_x, scale_y, 1.0)            # Renderizza la pagina
            mat = fitz.Matrix(self.scale_factor, self.scale_factor)
            
            # Handle different PyMuPDF versions
            # Note: PyMuPDF method names have changed across versions
            try:
                # Modern PyMuPDF (1.23+)
                pix = page.get_pixmap(matrix=mat)  # type: ignore
            except AttributeError:
                try:
                    # Older PyMuPDF
                    pix = page.getPixmap(matrix=mat)  # type: ignore
                except AttributeError:
                    # Very old PyMuPDF
                    pix = page.getPixmap(mat)  # type: ignore
            
            # Convert to PIL Image
            try:
                # Try new method first
                img_data = pix.pil_tobytes(format="PNG")  # type: ignore
                from io import BytesIO
                self.page_image = Image.open(BytesIO(img_data))
            except AttributeError:
                # Fallback for older versions
                img_data = pix.tobytes("ppm")  # type: ignore
                from io import BytesIO
                self.page_image = Image.open(BytesIO(img_data))
            
            # Aggiungi il watermark se presente
            if self.watermark_image:
                self.add_watermark_to_preview()
            
            # Converti per Tkinter
            self.photo = ImageTk.PhotoImage(self.page_image)
              # Pulisci e mostra
            self.delete("all")
            x = (canvas_width - self.page_image.width) // 2
            y = (canvas_height - self.page_image.height) // 2
            self.create_image(x, y, anchor='nw', image=self.photo)
            
        except Exception as e:            print(f"Errore nel rendering: {e}")
    
    def set_watermark(self, watermark_path, scale, position, opacity=0.8):
        """Imposta il watermark per l'anteprima."""
        try:
            if not watermark_path or not os.path.exists(watermark_path):
                self.watermark_image = None
                return
            
            # Usa la stessa logica di dimensionamento del PDF per coerenza
            width_points, height_points, img_width_px, img_height_px = calculate_watermark_size_points(
                watermark_path, scale
            )
            
            # Converti punti PDF in pixel per il display tenendo conto del scale_factor della pagina
            # Nel PDF: 1 punto PDF = 1/72 pollici
            # Nella preview: le dimensioni devono essere scalate come la pagina
            if hasattr(self, 'scale_factor') and self.scale_factor:
                # Usa il fattore di scala della pagina per mantenere le proporzioni corrette
                display_width = int(width_points * self.scale_factor)
                display_height = int(height_points * self.scale_factor)
            else:
                # Fallback se scale_factor non è ancora disponibile
                display_width = int(width_points)
                display_height = int(height_points)
            
            # Carica e ridimensiona l'immagine watermark
            img = Image.open(watermark_path)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Ridimensiona usando le dimensioni calcolate in modo coerente
            new_size = (display_width, display_height)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Applica opacità
            if opacity < 1.0:
                alpha = img.split()[-1]
                alpha = alpha.point(lambda p: int(p * opacity))
                img.putalpha(alpha)
            
            self.watermark_image = img
            self.watermark_size = new_size
            
            # Calcola posizione iniziale
            if self.page_image:
                self.calculate_watermark_position(position)
                self.render_page()
            
        except Exception as e:
            print(f"Errore nel watermark: {e}")
            self.watermark_image = None
    
    def calculate_watermark_position(self, position):
        """Calcola la posizione del watermark in base alla stringa posizione."""
        if not self.page_image:
            return
        
        page_width, page_height = self.page_image.size
        wm_width, wm_height = self.watermark_size
        margin = 20
        
        positions = {
            "bottom-right": (page_width - wm_width - margin, page_height - wm_height - margin),
            "bottom-left": (margin, page_height - wm_height - margin),
            "top-right": (page_width - wm_width - margin, margin),
            "top-left": (margin, margin)
        }
        
        self.watermark_position = positions.get(position, positions["bottom-right"])
    
    def add_watermark_to_preview(self):
        """Aggiunge il watermark all'immagine di anteprima."""
        if not self.watermark_image or not self.page_image:
            return
        
        try:
            # Crea una copia dell'immagine pagina
            preview_img = self.page_image.copy()
            
            # Sovrapponi il watermark
            preview_img.paste(self.watermark_image, self.watermark_position, self.watermark_image)
            
            self.page_image = preview_img
            
        except Exception as e:
            print(f"Errore nell'aggiunta watermark: {e}")
    
    def on_click(self, event):
        """Gestisce il click del mouse."""
        if self.watermark_image and self.page_image:
            # Controlla se il click è sul watermark
            canvas_width = self.winfo_width()
            canvas_height = self.winfo_height()
            
            img_x = (canvas_width - self.page_image.width) // 2
            img_y = (canvas_height - self.page_image.height) // 2
            
            rel_x = event.x - img_x
            rel_y = event.y - img_y
            
            wm_x, wm_y = self.watermark_position
            wm_w, wm_h = self.watermark_size
            
            if (wm_x <= rel_x <= wm_x + wm_w and 
                wm_y <= rel_y <= wm_y + wm_h):
                self.dragging = True
                self.drag_start = (rel_x - wm_x, rel_y - wm_y)
    
    def on_drag(self, event):
        """Gestisce il trascinamento del watermark."""
        if self.dragging and self.watermark_image and self.page_image:
            canvas_width = self.winfo_width()
            canvas_height = self.winfo_height()
            
            img_x = (canvas_width - self.page_image.width) // 2
            img_y = (canvas_height - self.page_image.height) // 2
            
            rel_x = event.x - img_x
            rel_y = event.y - img_y
            
            # Calcola nuova posizione
            new_x = rel_x - self.drag_start[0]
            new_y = rel_y - self.drag_start[1]
            
            # Limita ai bordi dell'immagine
            max_x = self.page_image.width - self.watermark_size[0]
            max_y = self.page_image.height - self.watermark_size[1]
            
            new_x = max(0, min(new_x, max_x))
            new_y = max(0, min(new_y, max_y))
            
            self.watermark_position = (new_x, new_y)
            self.render_page()
            
            # Notifica il callback
            if self.preview_callback:
                self.preview_callback()
    
    def on_release(self, event):
        """Gestisce il rilascio del mouse."""
        self.dragging = False
    
    def on_resize(self, event):
        """Gestisce il ridimensionamento della canvas."""
        if self.pdf_doc:
            self.after(100, self.render_page)  # Ritardo per evitare troppi refresh
    
    def next_page(self):
        """Vai alla pagina successiva."""
        if self.pdf_doc and self.current_page < len(self.pdf_doc) - 1:
            self.current_page += 1
            self.render_page()
    
    def prev_page(self):
        """Vai alla pagina precedente."""        
        if self.pdf_doc and self.current_page > 0:
            self.current_page -= 1
            self.render_page()
    
    def get_relative_watermark_position(self):
        """Restituisce la posizione relativa del watermark (0-1)."""
        if not self.page_image:
            return (0.8, 0.1)  # Default bottom-right
        
        rel_x = self.watermark_position[0] / self.page_image.width
        # Inverti Y per il sistema di coordinate PDF (origine in basso a sinistra)
        rel_y = 1.0 - (self.watermark_position[1] + self.watermark_size[1]) / self.page_image.height
        
        return (rel_x, rel_y)


class PDFSignerGUI:
    """Classe principale per l'interfaccia grafica del PDF Signer."""
    
    def __init__(self, root):
        self.root = root
        self.config_manager = ConfigManager()
        self.setup_window()
        self.setup_variables()
        self.create_widgets()
        self.load_settings()
        
        # Queue per threading
        self.processing_queue = queue.Queue()
        self.root.after(100, self.check_queue)
    
    def setup_window(self):
        """Configura la finestra principale."""
        self.root.title("PDF Signer - Firma Digitale Avanzata")
        self.root.geometry(self.config_manager.config.get('window_geometry', '1200x800'))
        self.root.minsize(1000, 600)
        
        # Icona (se disponibile)
        try:
            if os.path.exists("icon.ico"):
                self.root.iconbitmap("icon.ico")
        except:
            pass        
        # Stile
        style = ttk.Style()
        style.theme_use('clam')
    
    def setup_variables(self):
        """Inizializza le variabili Tkinter."""
        # Variabili base
        self.pdf_path = tk.StringVar()
        self.watermark_path = tk.StringVar(value=self.config_manager.config.get('last_watermark_path', 'sign.png'))
        self.output_path = tk.StringVar()
        self.scale_var = tk.DoubleVar(value=self.config_manager.config.get('default_scale', 1.0))
        self.position_var = tk.StringVar(value=self.config_manager.config.get('default_position', 'bottom-right'))
        self.opacity_var = tk.DoubleVar(value=self.config_manager.config.get('default_opacity', 0.8))
        self.selected_profile = tk.StringVar(value="Nessun profilo")
        self.processing = False
        
        # Variabili avanzate - Selezione pagine
        self.pages_var = tk.StringVar(value="all")
        self.pages_range_var = tk.StringVar(value="1-")
        
        # Variabili avanzate - Effetti
        self.border_width_var = tk.IntVar(value=0)
        self.border_color_var = tk.StringVar(value="#000000")
        self.shadow_enabled_var = tk.BooleanVar(value=False)
        self.shadow_offset_x_var = tk.IntVar(value=5)
        self.shadow_offset_y_var = tk.IntVar(value=5)
        
        # Variabili avanzate - Timestamp
        self.timestamp_enabled_var = tk.BooleanVar(value=False)
        self.timestamp_format_var = tk.StringVar(value="short")
        self.timestamp_position_var = tk.StringVar(value="bottom-left")
        
        # Variabili avanzate - Metadati
        self.add_metadata_var = tk.BooleanVar(value=False)
        self.metadata_author_var = tk.StringVar(value="")
        self.metadata_title_var = tk.StringVar(value="")
        self.metadata_subject_var = tk.StringVar(value="")
        
        # Variabili avanzate - Email
        self.email_enabled_var = tk.BooleanVar(value=False)
        self.email_to_var = tk.StringVar(value="")
        self.email_cc_var = tk.StringVar(value="")
        self.email_subject_var = tk.StringVar(value="PDF Firmato")
        self.email_template_var = tk.StringVar(value="")
    
    def create_widgets(self):
        """Crea tutti i widget dell'interfaccia."""
        # Frame principale
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Pannello superiore - File e profili
        self.create_file_panel(main_frame)
        
        # Pannello centrale - Anteprima e controlli
        self.create_main_panel(main_frame)
        
        # Pannello inferiore - Azioni
        self.create_action_panel(main_frame)
        
        # Menu
        self.create_menu()
    
    def create_file_panel(self, parent):
        """Crea il pannello per la selezione file e profili."""
        file_frame = ttk.LabelFrame(parent, text="File e Profili", padding=10)
        file_frame.pack(fill='x', pady=(0, 10))
        
        # Prima riga - PDF
        pdf_frame = ttk.Frame(file_frame)
        pdf_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(pdf_frame, text="PDF:").pack(side='left')
        pdf_entry = ttk.Entry(pdf_frame, textvariable=self.pdf_path, width=50)
        pdf_entry.pack(side='left', padx=(10, 5), fill='x', expand=True)
        ttk.Button(pdf_frame, text="Sfoglia", command=self.browse_pdf).pack(side='right', padx=(5, 0))
          # Drag and drop per PDF
        pdf_entry.drop_target_register(DND_FILES)  # type: ignore
        pdf_entry.dnd_bind('<<Drop>>', self.on_pdf_drop)  # type: ignore
        
        # Seconda riga - Watermark
        wm_frame = ttk.Frame(file_frame)
        wm_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(wm_frame, text="Firma:").pack(side='left')
        wm_entry = ttk.Entry(wm_frame, textvariable=self.watermark_path, width=50)
        wm_entry.pack(side='left', padx=(10, 5), fill='x', expand=True)
        ttk.Button(wm_frame, text="Sfoglia", command=self.browse_watermark).pack(side='right', padx=(5, 0))
          # Drag and drop per watermark
        wm_entry.drop_target_register(DND_FILES)  # type: ignore
        wm_entry.dnd_bind('<<Drop>>', self.on_watermark_drop)  # type: ignore
        
        # Terza riga - Output
        out_frame = ttk.Frame(file_frame)
        out_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(out_frame, text="Output:").pack(side='left')
        ttk.Entry(out_frame, textvariable=self.output_path, width=50).pack(side='left', padx=(10, 5), fill='x', expand=True)
        ttk.Button(out_frame, text="Sfoglia", command=self.browse_output).pack(side='right', padx=(5, 0))
        
        # Profili
        profile_frame = ttk.Frame(file_frame)
        profile_frame.pack(fill='x')
        
        ttk.Label(profile_frame, text="Profilo:").pack(side='left')
        self.profile_combo = ttk.Combobox(profile_frame, textvariable=self.selected_profile, 
                                         values=list(self.config_manager.profiles.keys()),
                                         state='readonly', width=20)
        self.profile_combo.pack(side='left', padx=(10, 5))
        self.profile_combo.bind('<<ComboboxSelected>>', self.on_profile_selected)
        
        ttk.Button(profile_frame, text="Carica", command=self.load_profile).pack(side='left', padx=(5, 5))
        ttk.Button(profile_frame, text="Salva", command=self.save_profile_dialog).pack(side='left', padx=(0, 5))
        ttk.Button(profile_frame, text="Elimina", command=self.delete_profile).pack(side='left')
    
    def create_main_panel(self, parent):
        """Crea il pannello principale con anteprima e controlli."""
        main_paned = ttk.PanedWindow(parent, orient='horizontal')
        main_paned.pack(fill='both', expand=True, pady=(0, 10))
        
        # Pannello anteprima (sinistra)
        preview_frame = ttk.LabelFrame(main_paned, text="Anteprima", padding=5)
        main_paned.add(preview_frame, weight=2)
        
        # Canvas per anteprima PDF
        self.preview_canvas = PDFPreviewCanvas(preview_frame, self.on_preview_change)
        self.preview_canvas.pack(fill='both', expand=True)
        
        # Controlli pagina
        page_frame = ttk.Frame(preview_frame)
        page_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Button(page_frame, text="◀ Precedente", command=self.preview_canvas.prev_page).pack(side='left')
        self.page_label = ttk.Label(page_frame, text="Pagina: -")
        self.page_label.pack(side='left', padx=(10, 10))
        ttk.Button(page_frame, text="Successiva ▶", command=self.preview_canvas.next_page).pack(side='left')
        
        # Pannello controlli (destra)
        controls_frame = ttk.LabelFrame(main_paned, text="Controlli Firma", padding=10)
        main_paned.add(controls_frame, weight=1)
        
        self.create_controls(controls_frame)
    def create_controls(self, parent):
        """Crea i controlli per la personalizzazione della firma."""
        # Notebook per organizzare i controlli in tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True)
        
        # Tab 1: Controlli Base
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Base")
        self.create_basic_controls(basic_frame)
        
        # Tab 2: Pagine
        pages_frame = ttk.Frame(notebook)
        notebook.add(pages_frame, text="Pagine")
        self.create_pages_controls(pages_frame)
        
        # Tab 3: Effetti
        effects_frame = ttk.Frame(notebook)
        notebook.add(effects_frame, text="Effetti")
        self.create_effects_controls(effects_frame)
        
        # Tab 4: Timestamp
        timestamp_frame = ttk.Frame(notebook)
        notebook.add(timestamp_frame, text="Timestamp")
        self.create_timestamp_controls(timestamp_frame)
        
        # Tab 5: Metadati
        metadata_frame = ttk.Frame(notebook)
        notebook.add(metadata_frame, text="Metadati")
        self.create_metadata_controls(metadata_frame)
        
        # Tab 6: Email
        email_frame = ttk.Frame(notebook)
        notebook.add(email_frame, text="Email")
        self.create_email_controls(email_frame)
    
    def create_basic_controls(self, parent):
        """Crea i controlli base."""
        # Scroll frame per i controlli base
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Scala
        scale_frame = ttk.LabelFrame(scrollable_frame, text="Dimensione", padding=5)
        scale_frame.pack(fill='x', pady=(0, 10), padx=5)        
        scale_scale = ttk.Scale(scale_frame, from_=0.05, to=5.0, variable=self.scale_var, 
                                orient='horizontal', command=self.on_settings_change)
        scale_scale.pack(fill='x')
        
        scale_label = ttk.Label(scale_frame, text="")
        scale_label.pack()
        
        def update_scale_label(*args):
            scale_label.config(text=f"{self.scale_var.get():.2f}")
        
        self.scale_var.trace('w', update_scale_label)
        update_scale_label()
        
        # Posizione
        pos_frame = ttk.LabelFrame(scrollable_frame, text="Posizione", padding=5)
        pos_frame.pack(fill='x', pady=(0, 10), padx=5)
        
        positions = [
            ("Alto Sinistra", "top-left"),
            ("Alto Destra", "top-right"), 
            ("Basso Sinistra", "bottom-left"),
            ("Basso Destra", "bottom-right")
        ]
        
        for text, value in positions:
            ttk.Radiobutton(pos_frame, text=text, variable=self.position_var, 
                           value=value, command=self.on_settings_change).pack(anchor='w')
        
        # Opacità
        opacity_frame = ttk.LabelFrame(scrollable_frame, text="Opacità", padding=5)
        opacity_frame.pack(fill='x', pady=(0, 10), padx=5)
        
        opacity_scale = ttk.Scale(opacity_frame, from_=0.1, to=1.0, variable=self.opacity_var,
                                 orient='horizontal', command=self.on_settings_change)
        opacity_scale.pack(fill='x')
        
        opacity_label = ttk.Label(opacity_frame, text="")
        opacity_label.pack()
        
        def update_opacity_label(*args):
            opacity_label.config(text=f"{self.opacity_var.get():.1f}")
        
        self.opacity_var.trace('w', update_opacity_label)
        update_opacity_label()
        
        # Anteprima watermark
        wm_preview_frame = ttk.LabelFrame(scrollable_frame, text="Anteprima Firma", padding=5)
        wm_preview_frame.pack(fill='x', pady=(0, 10), padx=5)
        
        self.wm_preview_label = ttk.Label(wm_preview_frame, text="Nessuna firma caricata")
        self.wm_preview_label.pack()
        
        # Pulsante aggiorna anteprima
        ttk.Button(scrollable_frame, text="Aggiorna Anteprima", 
                  command=self.update_preview).pack(fill='x', pady=(10, 0), padx=5)
    
    def create_pages_controls(self, parent):
        """Crea i controlli per la selezione delle pagine."""
        # Scroll frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Selezione pagine
        pages_frame = ttk.LabelFrame(scrollable_frame, text="Seleziona Pagine", padding=5)
        pages_frame.pack(fill='x', pady=(0, 10), padx=5)
        
        # Radio buttons per selezione pagine
        ttk.Radiobutton(pages_frame, text="Tutte le pagine", variable=self.pages_var, 
                       value="all", command=self.on_pages_change).pack(anchor='w')
        ttk.Radiobutton(pages_frame, text="Solo prima pagina", variable=self.pages_var, 
                       value="first", command=self.on_pages_change).pack(anchor='w')
        ttk.Radiobutton(pages_frame, text="Solo ultima pagina", variable=self.pages_var, 
                       value="last", command=self.on_pages_change).pack(anchor='w')
        
        # Range personalizzato
        range_frame = ttk.Frame(pages_frame)
        range_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Radiobutton(range_frame, text="Range personalizzato:", variable=self.pages_var, 
                       value="range", command=self.on_pages_change).pack(side='left')
        
        self.pages_range_entry = ttk.Entry(range_frame, textvariable=self.pages_range_var, width=15)
        self.pages_range_entry.pack(side='left', padx=(5, 0))
        
        # Descrizione del formato
        desc_label = ttk.Label(pages_frame, text="Formato: 1-5, 7, 10-12", font=('TkDefaultFont', 8))
        desc_label.pack(anchor='w', pady=(5, 0))
    
    def create_effects_controls(self, parent):
        """Crea i controlli per gli effetti."""
        # Scroll frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bordo
        border_frame = ttk.LabelFrame(scrollable_frame, text="Bordo", padding=5)
        border_frame.pack(fill='x', pady=(0, 10), padx=5)
        
        # Larghezza bordo
        border_width_frame = ttk.Frame(border_frame)
        border_width_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(border_width_frame, text="Larghezza:").pack(side='left')
        border_width_scale = ttk.Scale(border_width_frame, from_=0, to=10, variable=self.border_width_var,
                                      orient='horizontal', command=self.on_settings_change)
        border_width_scale.pack(side='left', fill='x', expand=True, padx=(5, 5))
        
        self.border_width_label = ttk.Label(border_width_frame, text="0")
        self.border_width_label.pack(side='right')
        
        def update_border_width_label(*args):
            self.border_width_label.config(text=str(self.border_width_var.get()))
        
        self.border_width_var.trace('w', update_border_width_label)
        
        # Colore bordo
        border_color_frame = ttk.Frame(border_frame)
        border_color_frame.pack(fill='x')
        
        ttk.Label(border_color_frame, text="Colore:").pack(side='left')
        ttk.Button(border_color_frame, text="Scegli Colore", 
                  command=self.choose_border_color).pack(side='left', padx=(5, 0))
        
        self.border_color_preview = tk.Label(border_color_frame, text="  ", bg="#000000", relief="solid")
        self.border_color_preview.pack(side='left', padx=(5, 0))
        
        # Ombra
        shadow_frame = ttk.LabelFrame(scrollable_frame, text="Ombra", padding=5)
        shadow_frame.pack(fill='x', pady=(0, 10), padx=5)
        
        ttk.Checkbutton(shadow_frame, text="Abilita ombra", variable=self.shadow_enabled_var,
                       command=self.on_settings_change).pack(anchor='w')
        
        # Offset ombra X
        shadow_x_frame = ttk.Frame(shadow_frame)
        shadow_x_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(shadow_x_frame, text="Offset X:").pack(side='left')
        shadow_x_scale = ttk.Scale(shadow_x_frame, from_=-20, to=20, variable=self.shadow_offset_x_var,
                                  orient='horizontal', command=self.on_settings_change)
        shadow_x_scale.pack(side='left', fill='x', expand=True, padx=(5, 5))
        
        self.shadow_x_label = ttk.Label(shadow_x_frame, text="5")
        self.shadow_x_label.pack(side='right')
        
        def update_shadow_x_label(*args):
            self.shadow_x_label.config(text=str(self.shadow_offset_x_var.get()))
        
        self.shadow_offset_x_var.trace('w', update_shadow_x_label)
        
        # Offset ombra Y
        shadow_y_frame = ttk.Frame(shadow_frame)
        shadow_y_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(shadow_y_frame, text="Offset Y:").pack(side='left')
        shadow_y_scale = ttk.Scale(shadow_y_frame, from_=-20, to=20, variable=self.shadow_offset_y_var,
                                  orient='horizontal', command=self.on_settings_change)
        shadow_y_scale.pack(side='left', fill='x', expand=True, padx=(5, 5))
        
        self.shadow_y_label = ttk.Label(shadow_y_frame, text="5")
        self.shadow_y_label.pack(side='right')
        
        def update_shadow_y_label(*args):
            self.shadow_y_label.config(text=str(self.shadow_offset_y_var.get()))
        
        self.shadow_offset_y_var.trace('w', update_shadow_y_label)
    
    def create_timestamp_controls(self, parent):
        """Crea i controlli per il timestamp."""
        # Scroll frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Timestamp
        timestamp_frame = ttk.LabelFrame(scrollable_frame, text="Timestamp", padding=5)
        timestamp_frame.pack(fill='x', pady=(0, 10), padx=5)
        
        ttk.Checkbutton(timestamp_frame, text="Aggiungi timestamp", variable=self.timestamp_enabled_var,
                       command=self.on_settings_change).pack(anchor='w')
        
        # Formato timestamp
        format_frame = ttk.Frame(timestamp_frame)
        format_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(format_frame, text="Formato:").pack(side='left')
        format_combo = ttk.Combobox(format_frame, textvariable=self.timestamp_format_var,
                                   values=["short", "long", "full"], state="readonly", width=10)
        format_combo.pack(side='left', padx=(5, 0))
        format_combo.bind('<<ComboboxSelected>>', self.on_settings_change)
        
        # Posizione timestamp
        pos_frame = ttk.Frame(timestamp_frame)
        pos_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(pos_frame, text="Posizione:").pack(side='left')
        pos_combo = ttk.Combobox(pos_frame, textvariable=self.timestamp_position_var,
                                values=["top-left", "top-right", "bottom-left", "bottom-right"], 
                                state="readonly", width=12)
        pos_combo.pack(side='left', padx=(5, 0))
        pos_combo.bind('<<ComboboxSelected>>', self.on_settings_change)
        
        # Anteprima formato
        preview_frame = ttk.Frame(timestamp_frame)
        preview_frame.pack(fill='x', pady=(10, 0))
        
        ttk.Label(preview_frame, text="Anteprima:").pack(anchor='w')
        self.timestamp_preview_label = ttk.Label(preview_frame, text="", font=('TkDefaultFont', 8))
        self.timestamp_preview_label.pack(anchor='w')
        
        self.update_timestamp_preview()
        self.timestamp_format_var.trace('w', lambda *args: self.update_timestamp_preview())
    
    def create_metadata_controls(self, parent):
        """Crea i controlli per i metadati."""
        # Scroll frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Metadati
        metadata_frame = ttk.LabelFrame(scrollable_frame, text="Metadati PDF", padding=5)
        metadata_frame.pack(fill='x', pady=(0, 10), padx=5)
        
        ttk.Checkbutton(metadata_frame, text="Aggiungi metadati personalizzati", 
                       variable=self.add_metadata_var).pack(anchor='w')
        
        # Autore
        author_frame = ttk.Frame(metadata_frame)
        author_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(author_frame, text="Autore:").pack(side='left')
        ttk.Entry(author_frame, textvariable=self.metadata_author_var, width=30).pack(side='left', padx=(5, 0), fill='x', expand=True)
        
        # Titolo
        title_frame = ttk.Frame(metadata_frame)
        title_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(title_frame, text="Titolo:").pack(side='left')
        ttk.Entry(title_frame, textvariable=self.metadata_title_var, width=30).pack(side='left', padx=(5, 0), fill='x', expand=True)
        
        # Soggetto
        subject_frame = ttk.Frame(metadata_frame)
        subject_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(subject_frame, text="Soggetto:").pack(side='left')
        ttk.Entry(subject_frame, textvariable=self.metadata_subject_var, width=30).pack(side='left', padx=(5, 0), fill='x', expand=True)
    
    def create_email_controls(self, parent):
        """Crea i controlli per l'email."""
        # Scroll frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Email
        email_frame = ttk.LabelFrame(scrollable_frame, text="Invio Email", padding=5)
        email_frame.pack(fill='x', pady=(0, 10), padx=5)
        
        ttk.Checkbutton(email_frame, text="Invia PDF firmato via email", 
                       variable=self.email_enabled_var).pack(anchor='w')
        
        # Destinatario
        to_frame = ttk.Frame(email_frame)
        to_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(to_frame, text="A:").pack(side='left')
        ttk.Entry(to_frame, textvariable=self.email_to_var, width=40).pack(side='left', padx=(5, 0), fill='x', expand=True)
        
        # CC
        cc_frame = ttk.Frame(email_frame)
        cc_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(cc_frame, text="CC:").pack(side='left')
        ttk.Entry(cc_frame, textvariable=self.email_cc_var, width=40).pack(side='left', padx=(5, 0), fill='x', expand=True)
        
        # Oggetto
        subject_frame = ttk.Frame(email_frame)
        subject_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(subject_frame, text="Oggetto:").pack(side='left')
        ttk.Entry(subject_frame, textvariable=self.email_subject_var, width=40).pack(side='left', padx=(5, 0), fill='x', expand=True)
        
        # Template
        template_frame = ttk.Frame(email_frame)
        template_frame.pack(fill='x', pady=(5, 0))
        
        ttk.Label(template_frame, text="Template:").pack(anchor='w')
        ttk.Entry(template_frame, textvariable=self.email_template_var, width=50).pack(fill='x', pady=(2, 0))
        ttk.Button(template_frame, text="Sfoglia", command=self.browse_email_template).pack(pady=(2, 0))
    
    def create_action_panel(self, parent):
        """Crea il pannello delle azioni principali."""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill='x')
        
        # Progress bar
        self.progress = ttk.Progressbar(action_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=(0, 10))
        
        # Pulsanti
        button_frame = ttk.Frame(action_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Pulisci", command=self.clear_all).pack(side='left', padx=(0, 10))
        ttk.Button(button_frame, text="Anteprima", command=self.update_preview).pack(side='left', padx=(0, 10))
        
        self.process_button = ttk.Button(button_frame, text="Firma PDF", 
                                        command=self.process_pdf, style='Accent.TButton')
        self.process_button.pack(side='right', padx=(10, 0))
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(action_frame, textvariable=self.status_var, relief='sunken', anchor='w')
        status_bar.pack(fill='x', pady=(10, 0))
    
    def create_menu(self):
        """Crea il menu dell'applicazione."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Nuovo", command=self.clear_all, accelerator="Ctrl+N")
        file_menu.add_separator()
        file_menu.add_command(label="Apri PDF...", command=self.browse_pdf, accelerator="Ctrl+O")
        file_menu.add_command(label="Carica Firma...", command=self.browse_watermark)
        file_menu.add_separator()
        file_menu.add_command(label="Esci", command=self.on_closing, accelerator="Ctrl+Q")
        
        # Menu Profili
        profile_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Profili", menu=profile_menu)
        profile_menu.add_command(label="Nuovo Profilo...", command=self.save_profile_dialog)
        profile_menu.add_command(label="Gestisci Profili...", command=self.manage_profiles_dialog)
        profile_menu.add_separator()
        profile_menu.add_command(label="Ripristina Predefiniti", command=self.reset_to_defaults)
        
        # Menu Aiuto
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aiuto", menu=help_menu)
        help_menu.add_command(label="Guida", command=self.show_help)
        help_menu.add_command(label="Informazioni", command=self.show_about)
        
        # Shortcuts
        self.root.bind('<Control-n>', lambda e: self.clear_all())
        self.root.bind('<Control-o>', lambda e: self.browse_pdf())
        self.root.bind('<Control-q>', lambda e: self.on_closing())
    
    # Event handlers
    def on_pdf_drop(self, event):
        """Gestisce il drop di file PDF."""
        files = event.data.split()
        if files:
            file_path = files[0].replace('{', '').replace('}', '')
            if file_path.lower().endswith('.pdf'):
                self.pdf_path.set(file_path)
                self.update_output_path()
                self.update_preview()
    
    def on_watermark_drop(self, event):
        """Gestisce il drop di file immagine per watermark."""
        files = event.data.split()
        if files:
            file_path = files[0].replace('{', '').replace('}', '')
            if any(file_path.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']):
                self.watermark_path.set(file_path)
                self.update_preview()
    
    def on_profile_selected(self, event=None):
        """Gestisce la selezione di un profilo."""
        # Viene gestito dal pulsante Carica per evitare cambi involontari
        pass
    
    def on_settings_change(self, *args):
        """Gestisce i cambiamenti nelle impostazioni."""
        if hasattr(self, 'preview_canvas'):
            self.root.after(100, self.update_preview)  # Ritardo per evitare troppi aggiornamenti
    
    def on_preview_change(self):
        """Callback chiamato quando l'anteprima cambia (es. trascinamento)."""
        self.status_var.set("Posizione firma aggiornata - Trascina per spostare")
    
    def on_pages_change(self, *args):
        """Gestisce i cambiamenti nella selezione delle pagine."""
        self.on_settings_change()
    
    def choose_border_color(self):
        """Apre il dialog per selezionare il colore del bordo."""
        color = colorchooser.askcolor(color=self.border_color_var.get())
        if color[1]:  # Se un colore è stato selezionato
            self.border_color_var.set(color[1])
            self.border_color_preview.config(bg=color[1])
            self.on_settings_change()
    
    def browse_email_template(self):
        """Apre il dialog per selezionare il template email."""
        file_path = filedialog.askopenfilename(
            title="Seleziona template email",
            filetypes=[
                ("Text files", "*.txt"),
                ("HTML files", "*.html"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.email_template_var.set(file_path)
    
    def update_timestamp_preview(self):
        """Aggiorna l'anteprima del timestamp."""
        if hasattr(self, 'timestamp_preview_label'):
            timestamp_format = self.timestamp_format_var.get()
            current_time = datetime.now()
            
            if timestamp_format == "short":
                preview = current_time.strftime("%d/%m/%Y")
            elif timestamp_format == "long":
                preview = current_time.strftime("%d/%m/%Y %H:%M")
            elif timestamp_format == "full":
                preview = current_time.strftime("%d/%m/%Y %H:%M:%S")
            else:
                preview = current_time.strftime("%d/%m/%Y")
            
            self.timestamp_preview_label.config(text=preview)
    
    # File operations
    def browse_pdf(self):
        """Apre il dialog per selezionare il PDF."""
        file_path = filedialog.askopenfilename(
            title="Seleziona PDF da firmare",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.pdf_path.set(file_path)
            self.update_output_path()
            self.update_preview()
    
    def browse_watermark(self):
        """Apre il dialog per selezionare l'immagine watermark."""
        file_path = filedialog.askopenfilename(
            title="Seleziona immagine firma",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.watermark_path.set(file_path)
            self.update_preview()
    
    def browse_output(self):
        """Apre il dialog per selezionare il file di output."""
        file_path = filedialog.asksaveasfilename(
            title="Salva PDF firmato come",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if file_path:
            self.output_path.set(file_path)
    
    def update_output_path(self):
        """Aggiorna automaticamente il percorso di output."""
        if self.pdf_path.get():
            input_path = Path(self.pdf_path.get())
            output_path = input_path.parent / f"{input_path.stem}_signed{input_path.suffix}"
            self.output_path.set(str(output_path))
    
    # Preview operations
    def update_preview(self):
        """Aggiorna l'anteprima PDF con il watermark."""
        if not self.pdf_path.get() or not os.path.exists(self.pdf_path.get()):
            self.status_var.set("Seleziona un PDF valido")
            return

        benchmark = self.config_manager.config.get('benchmark_preview', False)
        start_time = time.perf_counter() if benchmark else None

        self.status_var.set("Caricamento anteprima...")

        # Carica PDF (verrà riaperto solo se il percorso cambia)
        if self.preview_canvas.load_pdf(self.pdf_path.get()):
            # Imposta watermark
            if self.watermark_path.get() and os.path.exists(self.watermark_path.get()):
                self.preview_canvas.set_watermark(
                    self.watermark_path.get(),
                    self.scale_var.get(),
                    self.position_var.get(),
                    self.opacity_var.get()
                )
                self.status_var.set("Anteprima aggiornata - Trascina la firma per riposizionarla")
            else:
                self.status_var.set("Anteprima PDF caricata - Seleziona un'immagine firma")
            
            # Aggiorna info pagina
            if self.preview_canvas.pdf_doc:
                total_pages = len(self.preview_canvas.pdf_doc)
                current_page = self.preview_canvas.current_page + 1
                self.page_label.config(text=f"Pagina: {current_page}/{total_pages}")
        
        self.update_watermark_preview()

        if benchmark and start_time is not None:
            elapsed = time.perf_counter() - start_time
            print(f"Tempo aggiornamento anteprima: {elapsed:.4f}s")
    
    def update_watermark_preview(self):
        """Aggiorna l'anteprima del watermark nei controlli."""
        if self.watermark_path.get() and os.path.exists(self.watermark_path.get()):
            try:
                # Carica e ridimensiona per anteprima
                img = Image.open(self.watermark_path.get())
                img.thumbnail((100, 100), Image.Resampling.LANCZOS)
                  # Converti per Tkinter
                photo = ImageTk.PhotoImage(img)
                self.wm_preview_label.config(image=photo, text="")
                self.wm_preview_label.image = photo  # type: ignore # Mantieni riferimento
                
            except Exception as e:
                self.wm_preview_label.config(image="", text=f"Errore: {e}")
        else:
            self.wm_preview_label.config(image="", text="Nessuna firma caricata")
    
    # Profile operations
    def load_profile(self):
        """Carica il profilo selezionato."""
        profile_name = self.selected_profile.get()
        if profile_name in self.config_manager.profiles:
            profile = self.config_manager.profiles[profile_name]
            
            # Carica parametri base
            self.scale_var.set(profile.get('scale', 0.2))
            self.position_var.set(profile.get('position', 'bottom-right'))
            self.opacity_var.set(profile.get('opacity', 0.8))
            
            # Carica parametri avanzati - Pagine
            self.pages_var.set(profile.get('pages', 'all'))
            self.pages_range_var.set(profile.get('pages_range', '1-'))
            
            # Carica parametri avanzati - Effetti
            self.border_width_var.set(profile.get('border_width', 0))
            border_color = profile.get('border_color', (0, 0, 0))
            if isinstance(border_color, tuple):
                border_color_hex = f"#{border_color[0]:02x}{border_color[1]:02x}{border_color[2]:02x}"
            else:
                border_color_hex = border_color
            self.border_color_var.set(border_color_hex)
            if hasattr(self, 'border_color_preview'):
                self.border_color_preview.config(bg=border_color_hex)
            
            self.shadow_enabled_var.set(profile.get('shadow_enabled', False))
            shadow_offset = profile.get('shadow_offset', (5, 5))
            self.shadow_offset_x_var.set(shadow_offset[0])
            self.shadow_offset_y_var.set(shadow_offset[1])
            
            # Carica parametri avanzati - Timestamp
            self.timestamp_enabled_var.set(profile.get('timestamp_enabled', False))
            self.timestamp_format_var.set(profile.get('timestamp_format', 'short'))
            self.timestamp_position_var.set(profile.get('timestamp_position', 'bottom-left'))
            
            # Carica parametri avanzati - Metadati
            self.add_metadata_var.set(profile.get('add_metadata', False))
            self.metadata_author_var.set(profile.get('metadata_author', ''))
            self.metadata_title_var.set(profile.get('metadata_title', ''))
            self.metadata_subject_var.set(profile.get('metadata_subject', ''))
            
            # Carica parametri avanzati - Email
            self.email_enabled_var.set(profile.get('email_enabled', False))
            self.email_to_var.set(profile.get('email_to', ''))
            self.email_cc_var.set(profile.get('email_cc', ''))
            self.email_subject_var.set(profile.get('email_subject', 'PDF Firmato'))
            self.email_template_var.set(profile.get('email_template', ''))
            
            watermark_path = profile.get('watermark_path', '')
            if watermark_path and os.path.exists(watermark_path):
                self.watermark_path.set(watermark_path)
            
            self.update_preview()
            self.update_timestamp_preview()
            self.status_var.set(f"Profilo '{profile_name}' caricato")
    def save_profile_dialog(self):
        """Apre il dialog per salvare un nuovo profilo."""
        dialog = ProfileSaveDialog(self.root, self.config_manager)
        if dialog.result:
            name, description = dialog.result
            
            # Salva il profilo con tutti i parametri
            border_color = self.border_color_var.get()
            # Converti colore hex in tupla RGB per compatibilità
            border_color_rgb = tuple(int(border_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            
            profile_data = {
                # Parametri base
                'scale': self.scale_var.get(),
                'position': self.position_var.get(),
                'opacity': self.opacity_var.get(),
                'watermark_path': self.watermark_path.get(),
                'description': description,
                
                # Parametri avanzati - Pagine
                'pages': self.pages_var.get(),
                'pages_range': self.pages_range_var.get(),
                
                # Parametri avanzati - Effetti
                'border_width': self.border_width_var.get(),
                'border_color': border_color_rgb,
                'shadow_enabled': self.shadow_enabled_var.get(),
                'shadow_offset': (self.shadow_offset_x_var.get(), self.shadow_offset_y_var.get()),
                
                # Parametri avanzati - Timestamp
                'timestamp_enabled': self.timestamp_enabled_var.get(),
                'timestamp_format': self.timestamp_format_var.get(),
                'timestamp_position': self.timestamp_position_var.get(),
                
                # Parametri avanzati - Metadati
                'add_metadata': self.add_metadata_var.get(),
                'metadata_author': self.metadata_author_var.get(),
                'metadata_title': self.metadata_title_var.get(),
                'metadata_subject': self.metadata_subject_var.get(),
                
                # Parametri avanzati - Email
                'email_enabled': self.email_enabled_var.get(),
                'email_to': self.email_to_var.get(),
                'email_cc': self.email_cc_var.get(),
                'email_subject': self.email_subject_var.get(),
                'email_template': self.email_template_var.get()
            }
            
            self.config_manager.profiles[name] = profile_data
            self.config_manager.save_profiles()
            
            # Aggiorna la combobox
            self.profile_combo['values'] = list(self.config_manager.profiles.keys())
            self.selected_profile.set(name)
            
            self.status_var.set(f"Profilo '{name}' salvato")
    
    def delete_profile(self):
        """Elimina il profilo selezionato."""
        profile_name = self.selected_profile.get()
        if profile_name in self.config_manager.profiles:
            if messagebox.askyesno("Conferma", f"Eliminare il profilo '{profile_name}'?"):
                del self.config_manager.profiles[profile_name]
                self.config_manager.save_profiles()
                
                # Aggiorna la combobox
                self.profile_combo['values'] = list(self.config_manager.profiles.keys())
                self.selected_profile.set("Nessun profilo")
                
                self.status_var.set(f"Profilo '{profile_name}' eliminato")
    
    def manage_profiles_dialog(self):
        """Apre il dialog per gestire i profili."""
        ProfileManagerDialog(self.root, self.config_manager, self)
    
    def reset_to_defaults(self):
        """Ripristina le impostazioni predefinite."""
        if messagebox.askyesno("Conferma", "Ripristinare tutte le impostazioni ai valori predefiniti?"):
            self.scale_var.set(0.2)
            self.position_var.set('bottom-right')
            self.opacity_var.set(0.8)
            self.watermark_path.set('sign.png')
            self.selected_profile.set("Nessun profilo")
            self.update_preview()
            self.status_var.set("Impostazioni ripristinate")
    
    # Processing
    def process_pdf(self):
        """Avvia l'elaborazione del PDF."""
        if self.processing:
            return
        
        # Validazione input
        if not self.pdf_path.get() or not os.path.exists(self.pdf_path.get()):
            messagebox.showerror("Errore", "Seleziona un file PDF valido")
            return
        
        if not self.watermark_path.get() or not os.path.exists(self.watermark_path.get()):
            messagebox.showerror("Errore", "Seleziona un'immagine firma valida")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Errore", "Specifica il percorso di output")
            return
        
        # Avvia elaborazione in thread separato
        self.processing = True
        self.process_button.config(state='disabled', text='Elaborazione...')
        self.progress.start()
        self.status_var.set("Elaborazione in corso...")
        
        thread = threading.Thread(target=self._process_pdf_thread)
        thread.daemon = True
        thread.start()
    def _process_pdf_thread(self):
        """Thread di elaborazione PDF."""
        try:
            # Ottieni posizione custom dal trascinamento se necessario
            if hasattr(self.preview_canvas, 'watermark_position'):
                rel_pos = self.preview_canvas.get_relative_watermark_position()
                position = f"custom:{rel_pos[0]:.3f},{rel_pos[1]:.3f}"
            else:
                position = self.position_var.get()
            
            # Prepara tutti i parametri avanzati
            
            # Parametri selezione pagine
            pages = self.pages_var.get()
            if pages == "range":
                pages = self.pages_range_var.get()
            
            # Parametri effetti
            border_width = self.border_width_var.get()
            border_color_hex = self.border_color_var.get()
            border_color_rgb = tuple(int(border_color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
              # Parametri timestamp
            timestamp_enabled = self.timestamp_enabled_var.get()
            timestamp_format = self.timestamp_format_var.get()
            timestamp_position = self.timestamp_position_var.get()
            
            print(f"⏰ Debug: Timestamp abilitato: {timestamp_enabled}")
            if timestamp_enabled:
                print(f"⏰ Debug: Formato timestamp: {timestamp_format}, Posizione: {timestamp_position}")
            # Parametri metadati
            metadata = {}
            if self.add_metadata_var.get():
                if self.metadata_author_var.get():
                    metadata['author'] = self.metadata_author_var.get()
                if self.metadata_title_var.get():
                    metadata['title'] = self.metadata_title_var.get()
                if self.metadata_subject_var.get():
                    metadata['subject'] = self.metadata_subject_var.get()
            
            # Parametri email
            email_config = None
            if self.email_enabled_var.get() and self.email_to_var.get():
                email_config = {
                    'to': self.email_to_var.get(),
                    'cc': self.email_cc_var.get() if self.email_cc_var.get() else None,
                    'subject': self.email_subject_var.get(),
                    'template_path': self.email_template_var.get() if self.email_template_var.get() else None
                }            # Prepara parametri per email se abilitata
            kwargs = {
                'opacity': self.opacity_var.get(),
                'pages': pages,
                'border_width': border_width,
                'border_color': border_color_rgb,
                'shadow_enabled': self.shadow_enabled_var.get(),
                'shadow_offset': (self.shadow_offset_x_var.get(), self.shadow_offset_y_var.get()),
                'timestamp': timestamp_enabled,
                'timestamp_format': timestamp_format,
                'timestamp_position': timestamp_position,
                'add_metadata': bool(metadata),
                'author': metadata.get('author'),
                'title': metadata.get('title'),
                'subject': metadata.get('subject')
            }            # Aggiungi parametri email se abilitata
            if email_config and email_config.get('to'):
                print(f"🔧 Debug: Email config ricevuta: {email_config}")
                
                # Crea configurazione email temporanea
                email_recipients = [addr.strip() for addr in email_config['to'].split(',') if addr.strip()]
                if email_config.get('cc'):
                    email_recipients.extend([addr.strip() for addr in email_config['cc'].split(',') if addr.strip()])
                
                print(f"📧 Debug: Email recipients: {email_recipients}")
                
                # Cerca il file di configurazione email
                config_files = [
                    'email_config.yaml',
                    'email_config_example.yaml', 
                    'email_config_default.yaml'
                ]
                
                email_config_path = None
                for config_file in config_files:
                    if os.path.exists(config_file):
                        email_config_path = config_file
                        print(f"✅ Trovato file configurazione email: {config_file}")
                        break
                
                if email_config_path:
                    kwargs.update({
                        'email_recipients': email_recipients,
                        'email_subject': email_config.get('subject', 'PDF Firmato'),
                        'email_template': email_config.get('template_path'),
                        'email_config': email_config_path
                    })
                    print(f"📧 Email abilitata con config: {email_config_path}")
                else:
                    print("⚠️ Nessun file di configurazione email trovato. Funzionalità email disabilitata.")
            else:
                print("📧 Debug: Email non abilitata o configurazione mancante")
            
            # Elabora il PDF con parametri avanzati
            add_watermark_to_pdf(
                input_pdf_path=self.pdf_path.get(),
                watermark_image_path=self.watermark_path.get(),
                output_pdf_path=self.output_path.get(),
                scale_factor=self.scale_var.get(),
                position=position,
                **kwargs
            )
            
            message = f"PDF firmato salvato: {self.output_path.get()}"
            if email_config:
                message += f"\nEmail inviata a: {email_config['to']}"
            
            self.processing_queue.put(("success", message))
            
        except Exception as e:
            self.processing_queue.put(("error", f"Errore durante l'elaborazione: {str(e)}"))
    
    def check_queue(self):
        """Controlla la queue dei risultati di elaborazione."""
        try:
            while True:
                msg_type, message = self.processing_queue.get_nowait()
                
                if msg_type == "success":
                    messagebox.showinfo("Successo", message)
                    self.status_var.set("Elaborazione completata")
                elif msg_type == "error":
                    messagebox.showerror("Errore", message)
                    self.status_var.set("Errore durante l'elaborazione")
                
                self.processing = False
                self.process_button.config(state='normal', text='Firma PDF')
                self.progress.stop()
                
        except queue.Empty:
            pass
        
        self.root.after(100, self.check_queue)
    
    # Utility methods
    def clear_all(self):
        """Pulisce tutti i campi."""
        self.pdf_path.set("")
        self.output_path.set("")
        self.selected_profile.set("Nessun profilo")
        self.preview_canvas.pdf_doc = None
        self.preview_canvas.delete("all")
        self.page_label.config(text="Pagina: -")
        self.wm_preview_label.config(image="", text="Nessuna firma caricata")
        self.status_var.set("Campi puliti")
    
    def load_settings(self):
        """Carica le impostazioni salvate."""
        config = self.config_manager.config
        
        if config.get('last_watermark_path') and os.path.exists(config['last_watermark_path']):
            self.watermark_path.set(config['last_watermark_path'])
            self.update_watermark_preview()
    
    def save_settings(self):
        """Salva le impostazioni correnti."""
        self.config_manager.config.update({
            'last_watermark_path': self.watermark_path.get(),
            'default_scale': self.scale_var.get(),
            'default_position': self.position_var.get(),
            'default_opacity': self.opacity_var.get(),
            'window_geometry': self.root.geometry()
        })
        self.config_manager.save_config()
    def show_help(self):
        """Mostra la finestra di aiuto."""
        help_text = """
PDF Signer v2.0 - Guida Completa

FUNZIONALITÀ PRINCIPALI:
• Trascina file PDF e immagini firma direttamente nell'applicazione
• Anteprima in tempo reale con posizionamento interattivo
• Trascina la firma nell'anteprima per riposizionarla
• Profili salvabili per diverse configurazioni
• Funzionalità avanzate organizzate in schede

UTILIZZO BASE:
1. Seleziona o trascina un file PDF
2. Seleziona o trascina un'immagine per la firma
3. Regola dimensione, posizione e opacità nella scheda "Base"
4. Usa l'anteprima per vedere il risultato
5. Trascina la firma per riposizionarla
6. Clicca "Firma PDF" per salvare

FUNZIONALITÀ AVANZATE:

SCHEDA PAGINE:
• Firma tutte le pagine, solo la prima, solo l'ultima
• Range personalizzato (es: 1-5, 7, 10-12)

SCHEDA EFFETTI:
• Bordo personalizzabile (larghezza e colore)
• Ombra con offset regolabile
• Effetti visivi per rendere la firma più professionale

SCHEDA TIMESTAMP:
• Aggiungi automaticamente data e ora
• Formati: breve (DD/MM/YYYY), lungo (DD/MM/YYYY HH:MM), completo
• Posizionamento indipendente dalla firma

SCHEDA METADATI:
• Aggiungi metadati personalizzati al PDF
• Autore, titolo, soggetto
• Migliora la gestione documentale

SCHEDA EMAIL:
• Invio automatico del PDF firmato
• Destinatari multipli (TO, CC)
• Template personalizzabili per email
• Oggetto personalizzabile

PROFILI:
• Salva tutte le configurazioni avanzate
• Carica rapidamente impostazioni complete
• Gestisci e organizza i tuoi profili
• Profili predefiniti per diversi scenari

FORMATI SUPPORTATI:
• PDF: Tutti i tipi di PDF
• Immagini: PNG, JPG, JPEG, GIF, BMP, SVG
• Conversione automatica tra formati immagine

CONSIGLI:
• Usa profili predefiniti per iniziare rapidamente
• Sperimenta con gli effetti per personalizzare l'aspetto
• Il timestamp è utile per documenti legali
• L'invio email automatizza la distribuzione
"""
        
        HelpDialog(self.root, "Guida PDF Signer", help_text)
    def show_about(self):
        """Mostra le informazioni sull'applicazione."""
        about_text = """
PDF Signer v2.0
Firma Digitale Avanzata per PDF

Sviluppato con Python e Tkinter
Librerie utilizzate:
• PyPDF2 - Manipolazione PDF
• Pillow - Elaborazione immagini  
• ReportLab - Generazione PDF
• PyMuPDF - Anteprima PDF
• TkinterDnD2 - Drag and Drop
• YAML - Configurazioni
• smtplib - Invio email

Funzionalità Principali:
✓ Interfaccia drag-and-drop intuitiva
✓ Anteprima in tempo reale
✓ Posizionamento interattivo
✓ Selezione pagine avanzata
✓ Effetti visivi (bordi, ombre)
✓ Timestamp automatico
✓ Metadati personalizzati
✓ Invio email automatico
✓ Profili personalizzabili
✓ Supporto formati multipli

Nuove Funzionalità v2.0:
• Selezione pagine specifica
• Effetti grafici avanzati
• Timestamp con formati multipli
• Gestione metadati PDF
• Sistema di invio email integrato
• Interfaccia a schede organizzata
• Profili con parametri completi

© 2025 - PDF Signer Advanced
"""
        
        HelpDialog(self.root, "Informazioni", about_text)
    
    def on_closing(self):
        """Gestisce la chiusura dell'applicazione."""
        self.save_settings()
        self.root.quit()


# Dialog classes
class ProfileSaveDialog:
    """Dialog per salvare un nuovo profilo."""
    
    def __init__(self, parent, config_manager):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Salva Profilo")
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centra la finestra
        self.dialog.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")
        
        # Variabili
        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        
        # Widget
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        ttk.Label(main_frame, text="Nome Profilo:").pack(anchor='w')
        name_entry = ttk.Entry(main_frame, textvariable=self.name_var, width=40)
        name_entry.pack(fill='x', pady=(5, 10))
        name_entry.focus()
        
        ttk.Label(main_frame, text="Descrizione:").pack(anchor='w')
        desc_entry = ttk.Entry(main_frame, textvariable=self.desc_var, width=40)
        desc_entry.pack(fill='x', pady=(5, 20))
        
        # Pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Annulla", command=self.cancel).pack(side='right', padx=(10, 0))
        ttk.Button(button_frame, text="Salva", command=self.save).pack(side='right')
        
        # Bind Enter
        self.dialog.bind('<Return>', lambda e: self.save())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
        # Attendi risultato
        self.dialog.wait_window()
    
    def save(self):
        """Salva il profilo."""
        name = self.name_var.get().strip()
        desc = self.desc_var.get().strip()
        
        if not name:
            messagebox.showerror("Errore", "Inserisci un nome per il profilo")
            return
        
        self.result = (name, desc)
        self.dialog.destroy()
    
    def cancel(self):
        """Annulla il dialog."""
        self.dialog.destroy()


class ProfileManagerDialog:
    """Dialog per gestire i profili esistenti."""
    
    def __init__(self, parent, config_manager, main_app):
        self.config_manager = config_manager
        self.main_app = main_app
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Gestione Profili")
        self.dialog.geometry("600x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Centra la finestra
        self.dialog.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")
        
        self.create_widgets()
        self.load_profiles()
    
    def create_widgets(self):
        """Crea i widget del dialog."""
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        # Lista profili
        list_frame = ttk.LabelFrame(main_frame, text="Profili Salvati", padding=5)
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Treeview per profili
        columns = ('Nome', 'Scala', 'Posizione', 'Opacità', 'Descrizione')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Pulsanti
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')
        
        ttk.Button(button_frame, text="Carica", command=self.load_selected).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="Elimina", command=self.delete_selected).pack(side='left', padx=(0, 5))
        ttk.Button(button_frame, text="Duplica", command=self.duplicate_selected).pack(side='left', padx=(0, 20))
        
        ttk.Button(button_frame, text="Chiudi", command=self.dialog.destroy).pack(side='right')
    
    def load_profiles(self):
        """Carica i profili nella lista."""
        # Pulisci lista esistente
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Aggiungi profili
        for name, profile in self.config_manager.profiles.items():
            values = (
                name,
                f"{profile.get('scale', 0):.2f}",
                profile.get('position', ''),
                f"{profile.get('opacity', 0):.1f}",
                profile.get('description', '')
            )
            self.tree.insert('', 'end', values=values)
    
    def load_selected(self):
        """Carica il profilo selezionato nell'applicazione principale."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Avviso", "Seleziona un profilo da caricare")
            return
        
        item = self.tree.item(selection[0])
        profile_name = item['values'][0]
        
        # Imposta il profilo nell'app principale
        self.main_app.selected_profile.set(profile_name)
        self.main_app.load_profile()
        
        messagebox.showinfo("Successo", f"Profilo '{profile_name}' caricato")
    
    def delete_selected(self):
        """Elimina il profilo selezionato."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Avviso", "Seleziona un profilo da eliminare")
            return
        
        item = self.tree.item(selection[0])
        profile_name = item['values'][0]
        
        if messagebox.askyesno("Conferma", f"Eliminare il profilo '{profile_name}'?"):
            if profile_name in self.config_manager.profiles:
                del self.config_manager.profiles[profile_name]
                self.config_manager.save_profiles()
                self.load_profiles()
                
                # Aggiorna l'app principale
                self.main_app.profile_combo['values'] = list(self.config_manager.profiles.keys())
                
                messagebox.showinfo("Successo", f"Profilo '{profile_name}' eliminato")
    
    def duplicate_selected(self):
        """Duplica il profilo selezionato."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Avviso", "Seleziona un profilo da duplicare")
            return
        
        item = self.tree.item(selection[0])
        profile_name = item['values'][0]
        
        if profile_name in self.config_manager.profiles:            # Chiedi nuovo nome
            new_name = simpledialog.askstring("Duplica Profilo", 
                                               f"Nome per la copia di '{profile_name}':",
                                               initialvalue=f"{profile_name} - Copia")
            
            if new_name and new_name not in self.config_manager.profiles:
                # Copia il profilo
                self.config_manager.profiles[new_name] = self.config_manager.profiles[profile_name].copy()
                self.config_manager.profiles[new_name]['description'] = f"Copia di {profile_name}"
                self.config_manager.save_profiles()
                self.load_profiles()
                
                # Aggiorna l'app principale
                self.main_app.profile_combo['values'] = list(self.config_manager.profiles.keys())
                
                messagebox.showinfo("Successo", f"Profilo duplicato come '{new_name}'")


class HelpDialog:
    """Dialog per mostrare testo di aiuto o informazioni."""
    
    def __init__(self, parent, title, text):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        
        # Centra la finestra
        self.dialog.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")
        
        # Text widget con scrollbar
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill='both', expand=True)
        
        text_widget = tk.Text(main_frame, wrap='word', padx=10, pady=10)
        scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        text_widget.insert('1.0', text)
        text_widget.config(state='disabled')
        
        # Pulsante chiudi
        ttk.Button(main_frame, text="Chiudi", command=self.dialog.destroy).pack(pady=(10, 0))


def main():
    """Funzione principale per avviare la GUI."""
    try:
        # Prova a importare PyMuPDF
        import fitz
    except ImportError:
        print(
            "Dipendenza mancante: PyMuPDF. "
            "Installa manualmente con 'pip install PyMuPDF'."
        )
        return
    
    try:
        # Prova a importare tkinterdnd2
        from tkinterdnd2 import TkinterDnD
    except ImportError:
        print(
            "Dipendenza mancante: tkinterdnd2. "
            "Installa manualmente con 'pip install tkinterdnd2'."
        )
        return
    
    # Crea l'applicazione
    root = TkinterDnD.Tk()
    app = PDFSignerGUI(root)
    
    # Gestisce la chiusura
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Avvia il loop principale
    root.mainloop()


if __name__ == "__main__":
    main()
