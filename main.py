import os
import sys
import json
import uuid
import math
import requests
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


# configuration des correspondances de types imposer par LawinServer

FIXED_BACKEND_VALUES = {
    "AthenaEmoji": "AthenaDance",
    "AthenaSpray": "AthenaDance",
    "AthenaToy": "AthenaDance",
    "AthenaPetCarrier": "AthenaBackpack",
    "AthenaPet": "AthenaBackpack",
    "SparksDrum": "SparksDrums",
    "SparksMic": "SparksMicrophone",
    "CosmeticCompanion": "CosmeticMimosa"
}

COSMETIC_TYPES_TO_HAVE_UUID = ["CosmeticMimosa"]


# dictionnaire Français, Anglais

LANGUAGES = {
    "Français": {
        "welcome": "Générateur de profil Athena OGFN V1.1",
        "title": "Générateur de Profil Athena - Jinx On Reboot",
        "tab_official": "1. Cosmétiques Officiels",
        "tab_custom": "2. Cosmétiques Moddés",
        "btn_generate": "GÉNÉRER LE PROFIL ATHENA",
        "lbl_lang": "Langue :",
        "lbl_path": "Destination :",
        "btn_browse": "Parcourir...",
        "lbl_mode": "Mode de saisie :",
        "mode_uasset": "Fichiers .uasset",
        "mode_exact_id": "IDs Exacts (virgules)",
        "info_uasset": "MODE UASSET :\n\n1. Choisissez une catégorie.\n2. Collez vos noms de fichiers .uasset (un par ligne).\n3. L'outil ajoutera le bon préfixe automatiquement.",
        "info_exact": "MODE IDs EXACTS :\n\n1. Choisissez une catégorie.\n2. Collez vos IDs.\n3. Séparez-les par des virgules.\n\nExemple : LSID_Cosmic, EID_Dance01",
        "lbl_cat": "Catégorie :",
        "btn_save_cat": "Sauvegarder les modifications",
        "msg_cat_saved": "{} item(s) enregistrés pour la catégorie '{}' !",
        "msg_exact_saved": "{} ID(s) exact(s) enregistré(s) pour la catégorie '{}' !",
        "api_connect": "Connexion à fortnite-api.com...",
        "api_err": "Impossible de récupérer les cosmétiques officiels : {}",
        "success": "Profil généré avec succès !\n\nFichier : {}\nTaille : {}",
        "note_default": "\n\n(Note : Aucun cosmétique moddé n'a été ajouté. Un profil Athena par défaut a été créé.)",
        "err_template": "Le fichier 'athena_template.json' est introuvable dans le dossier.",
        "categories": {
            "Skins": "Skins", "Danses": "Danses", "Emojis": "Emojis", "Pioches": "Pioches",
            "Sacs": "Sacs", "Planeurs": "Planeurs", "Revêtements": "Revêtements",
            "Musiques": "Musiques", "Écrans": "Écrans de chargement"
        }
    },
    "English": {
        "welcome": "Athena Profile Generator OGFN V1.1",
        "title": "Athena Profile Generator - Jinx On Reboot",
        "tab_official": "1. Official Cosmetics",
        "tab_custom": "2. Modded Cosmetics",
        "btn_generate": "GENERATE ATHENA PROFILE",
        "lbl_lang": "Language:",
        "lbl_path": "Destination:",
        "btn_browse": "Browse...",
        "lbl_mode": "Input Mode:",
        "mode_uasset": ".uasset Files",
        "mode_exact_id": "Exact IDs (commas)",
        "info_uasset": "UASSET MODE:\n\n1. Choose a category.\n2. Paste your .uasset filenames (one per line).\n3. The tool automatically adds the prefix.",
        "info_exact": "EXACT IDs MODE:\n\n1. Choose a category.\n2. Paste your IDs.\n3. Separate them with commas.\n\nExample: LSID_Cosmic, EID_Dance01",
        "lbl_cat": "Category:",
        "btn_save_cat": "Save modifications",
        "msg_cat_saved": "{} item(s) saved for category '{}' !",
        "msg_exact_saved": "{} exact ID(s) saved for category '{}' !",
        "api_connect": "Connecting to fortnite-api.com...",
        "api_err": "Unable to fetch official cosmetics: {}",
        "success": "Profile successfully generated!\n\nFile: {}\nSize: {}",
        "note_default": "\n\n(Note: No modded cosmetics were added. A default profile was created.)",
        "err_template": "The file 'athena_template.json' could not be found.",
        "categories": {
            "Skins": "Skins", "Danses": "Dances", "Emojis": "Emojis", "Pioches": "Pickaxes",
            "Sacs": "Backpacks", "Planeurs": "Gliders", "Revêtements": "Wraps",
            "Musiques": "Music Packs", "Écrans": "Loading Screens"
        }
    }
}

CUSTOM_CATEGORIES = [
    {"key": "Skins",      "backend": "AthenaCharacter"},
    {"key": "Danses",     "backend": "AthenaDance"},
    {"key": "Emojis",     "backend": "AthenaDance"},
    {"key": "Pioches",    "backend": "AthenaPickaxe"},
    {"key": "Sacs",       "backend": "AthenaBackpack"},
    {"key": "Planeurs",   "backend": "AthenaGlider"},
    {"key": "Revêtements","backend": "AthenaItemWrap"},
    {"key": "Musiques",   "backend": "AthenaMusicPack"},
    {"key": "Écrans",     "backend": "AthenaLoadingScreen"}
]


def resource_path(*parts):
    """Retourne le chemin absolu vers une ressource, compatible .exe PyInstaller."""
    try:
        base = sys._MEIPASS         
    except AttributeError:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, *parts)


C_BG      = "#0d1117"   
C_SURFACE = "#161b22"   
C_INPUT   = "#21262d"   
C_ACCENT  = "#1f6feb"  
C_ACCT_H  = "#388bfd"   
C_TEXT    = "#e6edf3"   
C_MUTED   = "#8b949e"   
C_BORDER  = "#30363d"   
C_SUCCESS = "#3fb950"   


class AthenaApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = "Français"

        self.stored_uassets = {cat["key"]: [] for cat in CUSTOM_CATEGORIES}
        self.stored_exacts  = {cat["key"]: [] for cat in CUSTOM_CATEGORIES}
        self.input_mode     = tk.StringVar(value="uasset")

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.output_directory = os.path.join(desktop_path, "Athena Created")

        self.root.geometry("840x660")
        self.root.configure(bg=C_BG)
        self.root.resizable(True, True)
        self.root.minsize(720, 580)

        self.imported_athena_path = None

        self._configure_styles()
        self.create_header()
        self.create_top_bar()
        self.create_import_bar()

        self.notebook = ttk.Notebook(self.root, style="App.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=14, pady=(6, 0))

        self.create_official_tab()
        self.create_custom_tab()
        self.create_footer_credits()

        self.update_ui_language()

  # interface

    def _configure_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

       
        self.style.configure(".",
            background=C_BG, foreground=C_TEXT,
            fieldbackground=C_INPUT, font=("Segoe UI", 9))

        # zone de texte
        self.style.configure("App.TNotebook",
            background=C_BG, borderwidth=0)
        self.style.configure("App.TNotebook.Tab",
            background=C_SURFACE, foreground=C_MUTED,
            padding=[22, 9], font=("Segoe UI", 9, "bold"),
            borderwidth=0)
        self.style.map("App.TNotebook.Tab",
            background=[("selected", C_INPUT),  ("active", C_BORDER)],
            foreground=[("selected", C_TEXT),   ("active", C_TEXT)])

        # bouton principal
        self.style.configure("Primary.TButton",
            background=C_ACCENT, foreground="#ffffff",
            borderwidth=0, padding=[14, 9],
            font=("Segoe UI", 10, "bold"), relief="flat")
        self.style.map("Primary.TButton",
            background=[("active", C_ACCT_H), ("pressed", "#1558b0")])

        # bouton secondaire
        self.style.configure("Secondary.TButton",
            background=C_INPUT, foreground=C_TEXT,
            borderwidth=0, padding=[8, 6],
            font=("Segoe UI", 9), relief="flat")
        self.style.map("Secondary.TButton",
            background=[("active", C_BORDER)])

        # bouton info
        self.style.configure("Info.TButton",
            background=C_INPUT, foreground=C_MUTED,
            padding=[6, 4], font=("Segoe UI", 8, "bold"),
            borderwidth=0, relief="flat")
        self.style.map("Info.TButton",
            background=[("active", C_BORDER)])

       
        self.style.configure("TRadiobutton",
            background=C_SURFACE, foreground=C_TEXT,
            font=("Segoe UI", 9))
        self.style.map("TRadiobutton",
            background=[("active", C_SURFACE)])

        
        self.style.configure("TCombobox",
            fieldbackground=C_INPUT, background=C_INPUT,
            foreground=C_TEXT, selectbackground=C_ACCENT,
            borderwidth=0, relief="flat")
        self.style.map("TCombobox",
            fieldbackground=[("readonly", C_INPUT)],
            foreground=[("readonly", C_TEXT)])

  
    # interface et en tete

    def create_header(self):
        
        tk.Frame(self.root, bg=C_ACCENT, height=3).pack(fill="x")

        header = tk.Frame(self.root, bg=C_SURFACE, height=52)
        header.pack(fill="x")
        header.pack_propagate(False)

        inner = tk.Frame(header, bg=C_SURFACE)
        inner.pack(fill="both", expand=True, padx=16, pady=10)

        tk.Label(inner, text="JINX", bg=C_SURFACE, fg=C_TEXT,
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(inner, text=" ON REBOOT", bg=C_SURFACE, fg=C_ACCENT,
                 font=("Segoe UI", 14, "bold")).pack(side="left")
        tk.Label(inner, text="  v1.1", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8)).pack(side="left", pady=(5, 0))

        
        tk.Frame(self.root, bg=C_BORDER, height=1).pack(fill="x")

    # interface barre des langue + Chemin

    def create_top_bar(self):
        bar = tk.Frame(self.root, bg=C_BG, pady=9)
        bar.pack(fill="x", padx=14)

        # langue
        self.lbl_lang = tk.Label(bar, text="", bg=C_BG, fg=C_MUTED,
                                  font=("Segoe UI", 8, "bold"))
        self.lbl_lang.pack(side="left", padx=(0, 4))

        self.lang_combo = ttk.Combobox(bar, values=list(LANGUAGES.keys()),
                                        state="readonly", width=10,
                                        font=("Segoe UI", 9))
        self.lang_combo.set(self.current_lang)
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>", self.on_language_change)


        tk.Frame(bar, bg=C_BORDER, width=1, height=20).pack(side="left", padx=12, pady=2)

       
        self.lbl_path = tk.Label(bar, text="", bg=C_BG, fg=C_MUTED,
                                  font=("Segoe UI", 8, "bold"))
        self.lbl_path.pack(side="left", padx=(0, 4))

       
        path_box = tk.Frame(bar, bg=C_BORDER, padx=1, pady=1)
        path_box.pack(side="left", fill="x", expand=True, padx=(0, 6))

        path_inner = tk.Frame(path_box, bg=C_INPUT)
        path_inner.pack(fill="x")

        self.ent_path = tk.Entry(
            path_inner, bg=C_INPUT, fg=C_MUTED,
            insertbackground=C_TEXT, relief="flat",
            width=36, font=("Segoe UI", 8),
            readonlybackground=C_INPUT)
        self.ent_path.insert(0, self.output_directory)
        self.ent_path.config(state="readonly")
        self.ent_path.pack(fill="x", padx=6, pady=4)

        self.btn_browse = ttk.Button(bar, text="", command=self.browse_folder,
                                      style="Secondary.TButton")
        self.btn_browse.pack(side="left")

# interface et barre d'import athena
  

    def create_import_bar(self):
     
        tk.Frame(self.root, bg=C_BORDER, height=1).pack(fill="x", padx=14)

        bar = tk.Frame(self.root, bg=C_SURFACE, pady=8)
        bar.pack(fill="x", padx=14, pady=(4, 2))

        tk.Label(bar, text="⬡", bg=C_SURFACE, fg=C_ACCENT,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=(4, 4))
        tk.Label(bar, text="Source Athena :", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(0, 6))

        import_box = tk.Frame(bar, bg=C_BORDER, padx=1, pady=1)
        import_box.pack(side="left", fill="x", expand=True, padx=(0, 6))

        import_inner = tk.Frame(import_box, bg=C_INPUT)
        import_inner.pack(fill="x")

        self.ent_import = tk.Entry(
            import_inner, bg=C_INPUT, fg=C_MUTED,
            insertbackground=C_TEXT, relief="flat",
            width=36, font=("Segoe UI", 8),
            readonlybackground=C_INPUT)
        self.ent_import.insert(0, "Aucun fichier — utilise athena_template.json par défaut")
        self.ent_import.config(state="readonly")
        self.ent_import.pack(fill="x", padx=6, pady=4)

        # bouton importer
        ttk.Button(bar, text="Importer...", command=self.import_athena_file,
                   style="Secondary.TButton").pack(side="left", padx=(0, 4))

        # bouton effacer 
        self.btn_clear_import = ttk.Button(bar, text="✕", command=self.clear_imported_file,
                                            style="Info.TButton", width=3)
        self.btn_clear_import.pack(side="left")
        self.btn_clear_import.config(state="disabled")

    def import_athena_file(self):
        path = filedialog.askopenfilename(
            title="Importer un fichier Athena",
            filetypes=[("Fichiers JSON", "*.json"), ("Tous les fichiers", "*.*")])
        if path:
            self.imported_athena_path = os.path.normpath(path)
            self.ent_import.config(state="normal")
            self.ent_import.delete(0, tk.END)
            self.ent_import.insert(0, self.imported_athena_path)
            self.ent_import.config(fg=C_SUCCESS, state="readonly")
            self.btn_clear_import.config(state="normal")

    def clear_imported_file(self):
        self.imported_athena_path = None
        self.ent_import.config(state="normal")
        self.ent_import.delete(0, tk.END)
        self.ent_import.insert(0, "Aucun fichier — utilise athena_template.json par défaut")
        self.ent_import.config(fg=C_MUTED, state="readonly")
        self.btn_clear_import.config(state="disabled")

# interface avec les cosmetics fortnite officiel

    def create_official_tab(self):
        self.tab_off = tk.Frame(self.notebook, bg=C_INPUT)
        self.notebook.add(self.tab_off, text="")

        center = tk.Frame(self.tab_off, bg=C_INPUT)
        center.place(relx=0.5, rely=0.46, anchor="center")

        
        card = tk.Frame(center, bg=C_SURFACE, padx=55, pady=35)
        card.pack()

        
        tk.Frame(card, bg=C_ACCENT, height=3, width=130).pack(pady=(0, 18))

        
        tk.Label(card, text="ATHENA", bg=C_SURFACE, fg=C_ACCENT,
                 font=("Impact", 52)).pack()
        tk.Label(card, text="PROFILE  GENERATOR", bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 9, "bold")).pack(pady=(2, 18))

       
        self.lbl_welcome = tk.Label(card, text="", bg=C_SURFACE, fg=C_MUTED,
                                     font=("Segoe UI", 9, "italic"),
                                     wraplength=420)
        self.lbl_welcome.pack(pady=(0, 22))

        # bouton pour generer
        self.btn_generate = ttk.Button(card, text="", command=self.generate_profile,
                                        style="Primary.TButton", width=30)
        self.btn_generate.pack(pady=4)

        # astuce sous le bouton
        tk.Label(card, text="↳ Récupère les données depuis fortnite-api.com",
                 bg=C_SURFACE, fg=C_MUTED, font=("Segoe UI", 8)).pack(pady=(10, 0))

 # cosmetics moddés

    def create_custom_tab(self):
        self.tab_cust = tk.Frame(self.notebook, bg=C_INPUT)
        self.notebook.add(self.tab_cust, text="")

        # mode de saisie
        mode_card = tk.Frame(self.tab_cust, bg=C_SURFACE, padx=14, pady=10)
        mode_card.pack(fill="x", padx=14, pady=(13, 6))

        self.mode_frame = tk.Frame(mode_card, bg=C_SURFACE)
        self.mode_frame.pack(fill="x")

        self.lbl_mode = tk.Label(self.mode_frame, text="", bg=C_SURFACE, fg=C_MUTED,
                                  font=("Segoe UI", 8, "bold"))
        self.lbl_mode.pack(side="left", padx=(0, 10))

        self.rb_uasset = ttk.Radiobutton(self.mode_frame, text="",
                                          variable=self.input_mode, value="uasset",
                                          command=self.toggle_input_mode)
        self.rb_uasset.pack(side="left", padx=5)

        self.rb_exact = ttk.Radiobutton(self.mode_frame, text="",
                                         variable=self.input_mode, value="exact_id",
                                         command=self.toggle_input_mode)
        self.rb_exact.pack(side="left", padx=5)

        self.btn_info = ttk.Button(self.mode_frame, text="[ ? ] Info",
                                    style="Info.TButton", command=self.show_info)
        self.btn_info.pack(side="right")

        # categorie
        cat_card = tk.Frame(self.tab_cust, bg=C_SURFACE, padx=14, pady=9)
        cat_card.pack(fill="x", padx=14, pady=(0, 6))

        self.cat_frame = tk.Frame(cat_card, bg=C_SURFACE)
        self.cat_frame.pack(fill="x")

        self.lbl_cat = tk.Label(self.cat_frame, text="", bg=C_SURFACE, fg=C_TEXT,
                                 font=("Segoe UI", 9, "bold"))
        self.lbl_cat.pack(side="left", padx=(0, 8))

        self.cat_combo = ttk.Combobox(self.cat_frame, state="readonly", width=22,
                                       font=("Segoe UI", 9))
        self.cat_combo.pack(side="left")
        self.cat_combo.bind("<<ComboboxSelected>>", self.on_category_change)

        # zone de texte
        tk.Label(self.tab_cust, text="  Item IDs / Noms .uasset",
                 bg=C_INPUT, fg=C_MUTED,
                 font=("Segoe UI", 8, "bold"),
                 anchor="w").pack(fill="x", padx=14, pady=(4, 2))

        # texte ou on met les cosmetics (encadrée)
        txt_border = tk.Frame(self.tab_cust, bg=C_BORDER, padx=1, pady=1)
        txt_border.pack(fill="both", expand=True, padx=14, pady=(0, 8))

        self.txt_input = scrolledtext.ScrolledText(
            txt_border,
            bg=C_INPUT, fg=C_TEXT,
            insertbackground=C_TEXT,
            relief="flat", bd=0,
            font=("Consolas", 9),
            padx=10, pady=8,
            selectbackground=C_ACCENT,
            selectforeground="#ffffff"
        )
        self.txt_input.pack(fill="both", expand=True)

        # Bouton sauvegarder
        btn_row = tk.Frame(self.tab_cust, bg=C_INPUT)
        btn_row.pack(fill="x", padx=14, pady=(0, 10))

        self.btn_save_cat = ttk.Button(btn_row, text="", command=self.save_current_data,
                                        style="Primary.TButton")
        self.btn_save_cat.pack(side="right")

    #
    # interface de fin
    # 

    def create_footer_credits(self):
        footer = tk.Frame(self.root, bg=C_SURFACE, height=34)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        tk.Frame(self.root, bg=C_BORDER, height=1).pack(fill="x", side="bottom")

        inner = tk.Frame(footer, bg=C_SURFACE)
        inner.pack(fill="both", expand=True, padx=14)

        # Point vert (style "en ligne")
        tk.Label(inner, text="●", bg=C_SURFACE, fg=C_SUCCESS,
                 font=("Segoe UI", 8)).pack(side="left", padx=(0, 6))

        tk.Label(inner,
                 text="Modded Athena System by Jinx On Reboot  •  discord.gg/rebootxjinx",
                 bg=C_SURFACE, fg=C_MUTED,
                 font=("Segoe UI", 8)).pack(side="left")



    def browse_folder(self):
        selected_dir = filedialog.askdirectory(initialdir=self.output_directory)
        if selected_dir:
            self.output_directory = os.path.normpath(selected_dir)
            self.ent_path.config(state="normal")
            self.ent_path.delete(0, tk.END)
            self.ent_path.insert(0, self.output_directory)
            self.ent_path.config(state="readonly")

    def show_info(self):
        txt = LANGUAGES[self.current_lang]
        mode = self.input_mode.get()
        messagebox.showinfo("Information", txt["info_uasset"] if mode == "uasset" else txt["info_exact"])

    def toggle_input_mode(self):
        self.on_category_change(None)

    def on_language_change(self, event):
        self.current_lang = self.lang_combo.get()
        self.update_ui_language()

    def on_category_change(self, event):
        selected_display = self.cat_combo.get()
        txt_data = LANGUAGES[self.current_lang]["categories"]

        cat_key = "Skins"
        for k, v in txt_data.items():
            if v == selected_display:
                cat_key = k
                break

        self.txt_input.delete("1.0", tk.END)
        mode = self.input_mode.get()

        if mode == "uasset":
            lines = self.stored_uassets.get(cat_key, [])
            if lines: self.txt_input.insert(tk.END, "\n".join(lines))
        else:
            lines = self.stored_exacts.get(cat_key, [])
            if lines: self.txt_input.insert(tk.END, ", ".join(lines))

    def save_current_data(self):
        txt = LANGUAGES[self.current_lang]
        mode = self.input_mode.get()
        selected_display = self.cat_combo.get()
        txt_data = txt["categories"]
        cat_key = next((k for k, v in txt_data.items() if v == selected_display), "Skins")

        raw_text = self.txt_input.get("1.0", tk.END)
        cleaned_ids = []

        if mode == "uasset":
            for line in raw_text.split("\n"):
                cleaned = line.strip()
                if cleaned.lower().endswith(".uasset"): cleaned = cleaned[:-7]
                if cleaned: cleaned_ids.append(cleaned)
            self.stored_uassets[cat_key] = cleaned_ids
            messagebox.showinfo("Success", txt["msg_cat_saved"].format(len(cleaned_ids), selected_display))
        else:
            raw_text = raw_text.replace("\n", ",")
            for item in raw_text.split(","):
                cleaned = item.strip()
                if cleaned: cleaned_ids.append(cleaned)
            self.stored_exacts[cat_key] = cleaned_ids
            messagebox.showinfo("Success", txt["msg_exact_saved"].format(len(cleaned_ids), selected_display))

    def update_ui_language(self):
        txt = LANGUAGES[self.current_lang]
        self.root.title(txt["title"])
        self.lbl_lang.config(text=txt["lbl_lang"])
        self.lbl_path.config(text=txt["lbl_path"])
        self.btn_browse.config(text=txt["btn_browse"])
        self.lbl_welcome.config(text=txt["welcome"])
        self.btn_generate.config(text=txt["btn_generate"])
        self.lbl_mode.config(text=txt["lbl_mode"])
        self.rb_uasset.config(text=txt["mode_uasset"])
        self.rb_exact.config(text=txt["mode_exact_id"])
        self.lbl_cat.config(text=txt["lbl_cat"])
        self.btn_save_cat.config(text=txt["btn_save_cat"])

        self.notebook.tab(0, text=txt["tab_official"])
        self.notebook.tab(1, text=txt["tab_custom"])

        cat_translations = [txt["categories"][cat["key"]] for cat in CUSTOM_CATEGORIES]
        self.cat_combo.config(values=cat_translations)
        if cat_translations:
            if not self.cat_combo.get():
                self.cat_combo.set(cat_translations[0])
            self.on_category_change(None)

    def generate_profile(self):
        txt = LANGUAGES[self.current_lang]
        has_customs = False

        # fichier importé ou creation par défaut ?
        if self.imported_athena_path:
            source_path = self.imported_athena_path
            if not os.path.exists(source_path):
                messagebox.showerror("Error", f"Fichier importé introuvable :\n{source_path}")
                return
            use_api = False
        else:
            source_path = resource_path("athena_template.json")
            if not os.path.exists(source_path):
                messagebox.showerror("Error", txt["err_template"])
                return
            use_api = True

        with open(source_path, "r", encoding="utf-8") as f:
            athena = json.load(f)

        custom_guids = set()

        for cat in CUSTOM_CATEGORIES:
            cat_key = cat["key"]
            backend_value = cat["backend"]

            all_ids = self.stored_uassets.get(cat_key, []) + self.stored_exacts.get(cat_key, [])
            all_ids = list(set(all_ids))

            if all_ids:
                has_customs = True
                for item_id in all_ids:
                    full_id = f"{backend_value}:{item_id}"
                    guid = str(uuid.uuid4()) if backend_value in COSMETIC_TYPES_TO_HAVE_UUID else full_id
                    custom_guids.add(guid)
                    athena["items"][guid] = {
                        "templateId": full_id,
                        "attributes": {"max_level_bonus": 0, "level": 1, "item_seen": True, "xp": 0, "variants": [], "favorite": False},
                        "quantity": 1
                    }

        # API de fortnite seulement si ce n'est pas un fichier importé
        if use_api:
            try:
                resp = requests.get("https://fortnite-api.com/v2/cosmetics")
                resp.raise_for_status()
                data = resp.json()["data"]
            except Exception as e:
                messagebox.showerror("API Error", txt["api_err"].format(e))
                return

            for mode in data.keys():
                if mode in ["lego", "beans"]: continue

                for item in data[mode]:
                    if "type" not in item or "random" in item["id"].lower(): continue
                    if mode == "tracks": item["type"] = {"backendValue": "SparksSong"}

                    backend_value = item["type"]["backendValue"]
                    if backend_value in FIXED_BACKEND_VALUES:
                        backend_value = FIXED_BACKEND_VALUES[backend_value]

                    full_id = f"{backend_value}:{item['id']}"
                    guid = str(uuid.uuid4()) if backend_value in COSMETIC_TYPES_TO_HAVE_UUID else full_id

                    if guid in custom_guids: continue

                    variants = []
                    if "variants" in item and item["variants"]:
                        for obj in item["variants"]:
                            if "channel" in obj and obj["channel"].lower() == "pettemperament": continue
                            active_tag = obj["options"][0].get("tag", "") if "options" in obj and obj["options"] else ""
                            owned_tags = [opt.get("tag", "") for opt in obj["options"] if opt] if "options" in obj and obj["options"] else []
                            variants.append({"channel": obj.get("channel", ""), "active": active_tag, "owned": owned_tags})

                    athena["items"][guid] = {
                        "templateId": full_id,
                        "attributes": {"max_level_bonus": 0, "level": 1, "item_seen": True, "xp": 0, "variants": variants, "favorite": False},
                        "quantity": 1
                    }

        if not os.path.exists(self.output_directory):
            try: os.makedirs(self.output_directory)
            except Exception as e:
                messagebox.showerror("Error", f"Impossible de créer le dossier :\n{e}")
                return

        athena["_jor"] = "JinxOnReboot"

        output_path = os.path.join(self.output_directory, "athena.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(athena, f, indent=2, ensure_ascii=False)

        def format_size(bytes_size):
            if bytes_size == 0: return "N/A"
            sizes = ["Bytes", "KB", "MB", "GB"]
            i = int(math.floor(math.log(bytes_size) / math.log(1024)))
            return f"{(bytes_size / math.pow(1024, i)):.1f} {sizes[i]}"

        msg = txt["success"].format(output_path, format_size(os.path.getsize(output_path)))
        if not has_customs:
            msg += txt["note_default"]

        messagebox.showinfo("Success", msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = AthenaApp(root)
    root.mainloop()