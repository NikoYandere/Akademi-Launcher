#!/usr/bin/env python3
import os
import subprocess
import webbrowser
import shutil
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout,
    QWidget, QLabel, QMessageBox, QComboBox, QDialog, QHBoxLayout
)
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush, QIcon
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

def find_akademi_launcher():
    home_dir = os.path.expanduser("~")
    for root, dirs, files in os.walk(home_dir):
        if "akademi-launcher" in dirs:
            return os.path.join(root, "akademi-launcher")
    return None

AKADEMI_PATH = find_akademi_launcher()
if not AKADEMI_PATH:
    raise Exception("akademi-launcher folder not found!")

CONFIG_PATH = os.path.join(AKADEMI_PATH, "binary/data/game_path.txt")
LANG_PATH = os.path.join(AKADEMI_PATH, "binary/data/multilang.txt")
VERSION_PATH = os.path.join(AKADEMI_PATH, "binary/data/version.txt")
BACKGROUND_PATH = os.path.join(AKADEMI_PATH, "binary/data/background.txt")
ICON_PATH = os.path.join(AKADEMI_PATH, "binary/data/Akademi-Launcher.png")

LANGUAGES = {
    "en": {"welcome": "Welcome to Akademi Launcher", "loading": "Loading", "play": "Play", "github": "GitHub", "settings": "Settings", "download": "Download Game", "select_language": "Select Language", "select_exe": "Select .exe", "support": "Support", "discord": "Discord", "lang_changed": "Language changed! Restart the launcher.", "exit": "Exit", "missing_path": "Uh oh, try extract in your user folder", "select_background": "Select Background Image", "winetricks": "Winetricks", "winetricks_missing": "Winetricks is not installed."},
    "es": {"welcome": "Bienvenido a Akademi Launcher", "loading": "Cargando", "play": "Jugar", "github": "GitHub", "settings": "Configuración", "download": "Descargar Juego", "select_language": "Seleccionar Idioma", "select_exe": "Seleccionar .exe", "support": "Soporte", "discord": "Discord", "lang_changed": "¡Idioma cambiado! Reinicie el lanzador.", "exit": "Salir", "missing_path": "Uh oh, intenta extraerlo en tu carpeta de usuario", "select_background": "Seleccionar Imagen de Fondo", "winetricks": "Winetricks", "winetricks_missing": "Winetricks no está instalado."},
    "pt": {"welcome": "Bem-vindo ao Akademi Launcher", "loading": "Carregando", "play": "Jogar", "github": "GitHub", "settings": "Configurações", "download": "Baixar Jogo", "select_language": "Selecionar Idioma", "select_exe": "Selecionar .exe", "support": "Suporte", "discord": "Discord", "lang_changed": "Idioma alterado! Reinicie o lançador.", "exit": "Sair", "missing_path": "Uh oh, tente extrair na sua pasta de usuário", "select_background": "Selecionar Imagem de Fundo", "winetricks": "Winetricks", "winetricks_missing": "Winetricks não está instalado."},
}

def get_language():
    if os.path.exists(LANG_PATH):
        return open(LANG_PATH, encoding="utf-8").read().strip()
    return "en"

class SettingsDialog(QDialog):
    def __init__(self, lang_code, lang_data):
        super().__init__()
        self.setWindowTitle(lang_data["settings"])
        self.setFixedSize(300, 180)
        layout = QVBoxLayout()
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(LANGUAGES.keys())
        self.lang_selector.setCurrentText(lang_code)
        lang_label = QLabel(lang_data["select_language"])
        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.apply_settings)
        apply_btn.setStyleSheet("color: black")
        layout.addWidget(lang_label)
        layout.addWidget(self.lang_selector)
        layout.addWidget(apply_btn)
        self.setLayout(layout)

    def apply_settings(self):
        lang = self.lang_selector.currentText()
        with open(LANG_PATH, "w", encoding="utf-8") as f:
            f.write(lang)
        QMessageBox.information(self, "Info", LANGUAGES[lang]["lang_changed"])
        self.accept()

class AkademiLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang_code = get_language()
        self.lang = LANGUAGES.get(self.lang_code, LANGUAGES["en"])
        self.setWindowTitle("Akademi Launcher")
        self.setFixedSize(1100, 600)
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
        self.set_gradient_background()
        self.setup_ui()

    def set_gradient_background(self):
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#4da6ff"))
        gradient.setColorAt(1, QColor("#6666ff"))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)

    def setup_ui(self):
        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        left_layout.setAlignment(Qt.AlignTop)
        font = QFont("Segoe UI", 16)
        version_font = QFont("Segoe UI", 10)

        def add_button(label, handler):
            btn = QPushButton(label)
            btn.setFont(font)
            btn.setStyleSheet("color: black; background-color: white; padding: 8px; border-radius: 6px;")
            btn.clicked.connect(handler)
            left_layout.addWidget(btn)

        add_button(self.lang["play"], self.launch_game)
        add_button(self.lang["settings"], self.open_settings)
        add_button(self.lang["select_exe"], self.select_exe)
        add_button(self.lang["download"], self.download_game)
        add_button(self.lang["support"], lambda: webbrowser.open("https://github.com/NikoYandere/Akademi-Launcher/issues"))
        add_button(self.lang["discord"], lambda: webbrowser.open("https://discord.gg/7JC4FGn69U"))

        version = QLabel(f"{self.lang['welcome']} - experimental version")
        version.setFont(version_font)
        version.setStyleSheet("color: white; margin-top: 20px;")
        left_layout.addWidget(version)

        blog_view = QWebEngineView()
        blog_view.load(QUrl("https://akademi-launcher.blogspot.com"))

        main_layout.addLayout(left_layout, 1)
        main_layout.addWidget(blog_view, 2)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_settings(self):
        dlg = SettingsDialog(self.lang_code, self.lang)
        dlg.exec_()

    def launch_game(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, encoding="utf-8") as f:
                path = f.read().strip()
            if os.path.exists(path):
                try:
              
                    subprocess.Popen([path], shell=True)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Game failed to launch!\n{e}")
                return
        QMessageBox.critical(self, "Error", "Game path not set or file does not exist.")

    def select_exe(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select .exe", "", "Executable Files (*.exe)")
        if file:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                f.write(file)
            QMessageBox.information(self, "Saved", "Executable path saved.")

    def download_game(self):
        webbrowser.open("https://yanderesimulator.com/dl/latest.zip")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    launcher = AkademiLauncher()
    launcher.show()
    sys.exit(app.exec_())
