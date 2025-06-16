#!/usr/bin/env python3
"""
GUI completa per PDF Signer con drag-and-drop, preview in tempo reale,
editor visuale per posizionamento e gestione profili.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser, simpledialog
import tkinter.font as tkFont
from tkinterdnd2 import DND_FILES, TkinterDnD
import json
import yaml
import os
from pathlib import Path
from PIL import Image, ImageTk, ImageDraw
import threading
import queue
from datetime import datetime
import tempfile
import fitz  # PyMuPDF per anteprima PDF
import subprocess
import sys

# Import delle funzioni dal modulo originale
from pdf_signer import add_watermark_to_pdf, create_watermark_pdf

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
            'default_scale': 0.2,
            'default_position': 'bottom-right',
            'default_opacity': 0.8,
            'window_geometry': '1200x800',
            'preview_quality': 'medium'
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
        """Restituisce i profili predefiniti."""
        return {
            "Firma Standard": {
                "scale": 0.2,
                "position": "bottom-right",
                "opacity": 0.8,
                "watermark_path": "sign.png",
                "description": "Firma standard in basso a destra"
            },
            "Firma Piccola": {
                "scale": 0.1,
                "position": "bottom-right",
                "opacity": 0.6,
                "watermark_path": "sign.png", 
                "description": "Firma piccola e discreta"
            },
            "Firma Ufficiale": {
                "scale": 0.3,
                "position": "bottom-left",
                "opacity": 1.0,
                "watermark_path": "signAL.png",
                "description": "Firma grande per documenti ufficiali"
            }
        }


class PDFPreviewCanvas(tk.Canvas):
    """Canvas personalizzato per l'anteprima PDF con posizionamento interattivo."""
    
    def __init__(self, parent, preview_callback=None):
        super().__init__(parent, bg='white', relief='sunken', bd=2)
        self.preview_callback = preview_callback
        self.pdf_doc = None
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
        """Carica un PDF per l'anteprima."""
        try:
            self.pdf_doc = fitz.open(pdf_path)
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
            
            page_rect = page.rect
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
            
        except Exception as e:
            print(f"Errore nel rendering: {e}")
    
    def set_watermark(self, watermark_path, scale, position, opacity=0.8):
        """Imposta il watermark per l'anteprima."""
        try:
            if not watermark_path or not os.path.exists(watermark_path):
                self.watermark_image = None
                return
            
            # Carica e ridimensiona l'immagine watermark
            img = Image.open(watermark_path)
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Applica scala
            new_size = (int(img.width * scale), int(img.height * scale))
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
        self.pdf_path = tk.StringVar()
        self.watermark_path = tk.StringVar(value=self.config_manager.config.get('last_watermark_path', 'sign.png'))
        self.output_path = tk.StringVar()
        self.scale_var = tk.DoubleVar(value=self.config_manager.config.get('default_scale', 0.2))
        self.position_var = tk.StringVar(value=self.config_manager.config.get('default_position', 'bottom-right'))
        self.opacity_var = tk.DoubleVar(value=self.config_manager.config.get('default_opacity', 0.8))
        self.selected_profile = tk.StringVar(value="Nessun profilo")
        self.processing = False
    
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
        # Scala
        scale_frame = ttk.LabelFrame(parent, text="Dimensione", padding=5)
        scale_frame.pack(fill='x', pady=(0, 10))
        
        scale_scale = ttk.Scale(scale_frame, from_=0.05, to=1.0, variable=self.scale_var, 
                               orient='horizontal', command=self.on_settings_change)
        scale_scale.pack(fill='x')
        
        scale_label = ttk.Label(scale_frame, text="")
        scale_label.pack()
        
        def update_scale_label(*args):
            scale_label.config(text=f"{self.scale_var.get():.2f}")
        
        self.scale_var.trace('w', update_scale_label)
        update_scale_label()
        
        # Posizione
        pos_frame = ttk.LabelFrame(parent, text="Posizione", padding=5)
        pos_frame.pack(fill='x', pady=(0, 10))
        
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
        opacity_frame = ttk.LabelFrame(parent, text="Opacità", padding=5)
        opacity_frame.pack(fill='x', pady=(0, 10))
        
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
        wm_preview_frame = ttk.LabelFrame(parent, text="Anteprima Firma", padding=5)
        wm_preview_frame.pack(fill='x', pady=(0, 10))
        
        self.wm_preview_label = ttk.Label(wm_preview_frame, text="Nessuna firma caricata")
        self.wm_preview_label.pack()
        
        # Pulsante aggiorna anteprima
        ttk.Button(parent, text="Aggiorna Anteprima", 
                  command=self.update_preview).pack(fill='x', pady=(10, 0))
    
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
        
        self.status_var.set("Caricamento anteprima...")
        
        # Carica PDF
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
            
            self.scale_var.set(profile.get('scale', 0.2))
            self.position_var.set(profile.get('position', 'bottom-right'))
            self.opacity_var.set(profile.get('opacity', 0.8))
            
            watermark_path = profile.get('watermark_path', '')
            if watermark_path and os.path.exists(watermark_path):
                self.watermark_path.set(watermark_path)
            
            self.update_preview()
            self.status_var.set(f"Profilo '{profile_name}' caricato")
    
    def save_profile_dialog(self):
        """Apre il dialog per salvare un nuovo profilo."""
        dialog = ProfileSaveDialog(self.root, self.config_manager)
        if dialog.result:
            name, description = dialog.result
            
            # Salva il profilo
            profile_data = {
                'scale': self.scale_var.get(),
                'position': self.position_var.get(),
                'opacity': self.opacity_var.get(),
                'watermark_path': self.watermark_path.get(),
                'description': description
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
            
            # Elabora il PDF
            add_watermark_to_pdf(
                self.pdf_path.get(),
                self.watermark_path.get(),
                self.output_path.get(),
                self.scale_var.get(),
                position
            )
            
            self.processing_queue.put(("success", f"PDF firmato salvato: {self.output_path.get()}"))
            
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
PDF Signer - Guida Rapida

FUNZIONALITÀ PRINCIPALI:
• Trascina file PDF e immagini firma direttamente nell'applicazione
• Anteprima in tempo reale con posizionamento interattivo
• Trascina la firma nell'anteprima per riposizionarla
• Profili salvabili per diverse configurazioni

UTILIZZO:
1. Seleziona o trascina un file PDF
2. Seleziona o trascina un'immagine per la firma
3. Regola dimensione, posizione e opacità
4. Usa l'anteprima per vedere il risultato
5. Trascina la firma per riposizionarla
6. Clicca "Firma PDF" per salvare

PROFILI:
• Salva le tue configurazioni preferite
• Carica rapidamente impostazioni predefinite
• Gestisci e organizza i tuoi profili

FORMATI SUPPORTATI:
• PDF: Tutti i tipi di PDF
• Immagini: PNG, JPG, JPEG, GIF, BMP
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

Funzionalità:
✓ Interfaccia drag-and-drop
✓ Anteprima in tempo reale
✓ Posizionamento interattivo
✓ Profili personalizzabili
✓ Configurazione avanzata

© 2025 - PDF Signer
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
        print("Installazione di PyMuPDF in corso...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyMuPDF"])
        import fitz
    
    try:
        # Prova a importare tkinterdnd2
        from tkinterdnd2 import TkinterDnD
    except ImportError:
        print("Installazione di tkinterdnd2 in corso...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tkinterdnd2"])
        from tkinterdnd2 import TkinterDnD
    
    # Crea l'applicazione
    root = TkinterDnD.Tk()
    app = PDFSignerGUI(root)
    
    # Gestisce la chiusura
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Avvia il loop principale
    root.mainloop()


if __name__ == "__main__":
    main()
