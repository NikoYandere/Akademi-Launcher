import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os
import sys
import subprocess

def load_language(lang_code):
    languages = {
        "en": {
            "play": "Play",
            "settings": "Settings",
            "select_exe": "Select .EXE",
            "no_exe": "Please select a .EXE first.",
            "change_lang": "Change Language"
        },
        "es": {
            "play": "Jugar",
            "settings": "Configuraciones",
            "select_exe": "Seleccionar .EXE",
            "no_exe": "Por favor, seleccione un .EXE primero.",
            "change_lang": "Cambiar idioma"
        },
        "pt": {
            "play": "Jogar",
            "settings": "Configurações",
            "select_exe": "Selecionar .EXE",
            "no_exe": "Por favor, selecione um .EXE primeiro.",
            "change_lang": "Mudar idioma"
        }
    }
    return languages.get(lang_code, languages["en"])

def save_config():
    with open(os.path.join(script_dir, "config.json"), "w") as f:
        json.dump({"exe": selected_exe, "lang": current_lang}, f)

def load_config():
    config_path = os.path.join(script_dir, "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {"exe": None, "lang": "en"}

def play_game():
    if selected_exe and os.path.exists(selected_exe):
        subprocess.Popen(selected_exe, shell=True)
        root.quit()  # Fecha a janela após executar o jogo
    else:
        messagebox.showerror("Error", lang["no_exe"])

def select_exe():
    global selected_exe
    file = filedialog.askopenfilename(filetypes=[("Executables", "*.exe")])
    if file:
        selected_exe = file
        save_config()

def open_settings():
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("300x200")
    settings_window.resizable(False, False)

    lang_label = tk.Label(settings_window, text="Select Language:")
    lang_label.pack(pady=10)

    lang_combobox = ttk.Combobox(settings_window, values=["en", "es", "pt"])
    lang_combobox.set(current_lang)
    lang_combobox.pack(pady=10)

    def save_settings():
        global current_lang, lang
        current_lang = lang_combobox.get()
        lang = load_language(current_lang)
        save_config()
        settings_window.destroy()

    save_button = tk.Button(settings_window, text="Save", command=save_settings)
    save_button.pack(pady=10)

def resource_path(relative_path):
    """Obter o caminho absoluto do arquivo quando empacotado com PyInstaller"""
    try:
        # PyInstaller cria uma pasta temporária para os arquivos
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

script_dir = os.path.dirname(os.path.abspath(__file__))

config = load_config()
selected_exe = config["exe"]
current_lang = config["lang"]
lang = load_language(current_lang)

root = tk.Tk()
root.title("Akademi Launcher")
root.geometry("400x600")
root.resizable(False, False)

bg_path = resource_path("background.png")  # Usando o método resource_path
bg_image = Image.open(bg_path)
bg_image = bg_image.resize((400, 600), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

canvas = tk.Canvas(root, width=400, height=600)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

btn_play = tk.Button(root, text=lang["play"], font=("Helvetica", 20), command=play_game)
canvas.create_window(200, 200, window=btn_play)

btn_settings = tk.Button(root, text=lang["settings"], font=("Helvetica", 14), command=open_settings)
canvas.create_window(200, 250, window=btn_settings)

btn_select = tk.Button(root, text=lang["select_exe"], font=("Helvetica", 14), command=select_exe)
canvas.create_window(200, 300, window=btn_select)

root.mainloop()

