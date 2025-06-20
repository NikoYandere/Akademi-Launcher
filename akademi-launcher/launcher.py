import os
import subprocess
import webbrowser
import shutil
import time
import threading
import requests
import zipfile
import sys
import socket

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout,
    QWidget, QLabel, QMessageBox, QComboBox, QDialog, QHBoxLayout,
    QSplashScreen
)
from PyQt5.QtGui import QFont, QPalette, QLinearGradient, QColor, QBrush, QIcon, QPainter, QPixmap
from PyQt5.QtCore import Qt, QUrl, QRect, QTimer, QCoreApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView


try:
    from pypresence import Presence
    presence_enabled = True
except ImportError:
    presence_enabled = False
    print("pypresence library not found. Discord Rich Presence will be disabled.")
    print("Install it with: pip install pypresence")


CLIENT_ID = '1383809366460989490'

# Use the directory where the script is located for data files
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
AKADEMI_PATH = SCRIPT_DIR
DATA_DOWNLOAD_URL = "https://nikoyandere.github.io/data.zip"
TEMP_ZIP_PATH = os.path.join(AKADEMI_PATH, "data.zip")

CONFIG_PATH = os.path.join(AKADEMI_PATH, "data/game_path.txt")
LANG_PATH = os.path.join(AKADEMI_PATH, "data/multilang.txt")
VERSION_PATH = os.path.join(AKADEMI_PATH, "data/version.txt")
BACKGROUND_PATH = os.path.join(AKADEMI_PATH, "data/background.txt")
ICON_PATH = os.path.join(AKADEMI_PATH, "data/Yanix-Launcher.png")

os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)


LANGUAGES = {
    "en": {"welcome": "Welcome to Akademi Launcher", "loading": "Loading", "play": "Play", "github": "GitHub", "settings": "Settings", "download": "Download Game", "select_language": "Select Language", "select_exe": "Select .exe for Game", "support": "Support", "discord": "Discord", "lang_changed": "Language changed!", "exit": "Exit", "missing_path": "Uh oh, try extracting to the launcher's folder", "select_background": "Select Background Image", "winetricks": "Winetricks (Linux Only)", "no_internet": "No internet connection. Please check your network and try again.", "downloading_data": "Downloading Data File....", "extracting_data": "Extracting Files....", "download_failed": "Failed to download data.", "extract_failed": "Failed to extract data.", "download_success": "Data downloaded and extracted successfully!"},
    "es": {"welcome": "Bienvenido a Akademi Launcher", "loading": "Cargando", "play": "Jugar", "github": "GitHub", "settings": "Configuración", "download": "Descargar Juego", "select_language": "Seleccionar Idioma", "select_exe": "Seleccionar .exe para Juego", "support": "Soporte", "discord": "Discord", "lang_changed": "¡Idioma cambiado!", "exit": "Salir", "missing_path": "Uh oh, intenta extraerlo en la carpeta del lanzador", "select_background": "Seleccionar Imagen de Fondo", "winetricks": "Winetricks (Solo Linux)", "no_internet": "Sin conexión de internet. Por favor, revisa tu red e inténtalo de nuevo.", "downloading_data": "Descargando archivo de datos....", "extracting_data": "Extrayendo archivos....", "download_failed": "Fallo al descargar datos.", "extract_failed": "Fallo al extraer datos.", "download_success": "Datos descargados y extraídos exitosamente!"},
    "pt": {"welcome": "Bem-vindo ao Akademi Launcher", "loading": "Carregando", "play": "Jogar", "github": "GitHub", "settings": "Configurações", "download": "Baixar Jogo", "select_language": "Selecionar Idioma", "select_exe": "Selecionar .exe pro Jogo", "support": "Suporte", "discord": "Discord", "lang_changed": "Idioma alterado!", "exit": "Sair", "missing_path": "Uh oh... tente extrai-lo na pasta do lançador.", "select_background": "Selecionar Imagem de Fundo", "winetricks": "Winetricks (Somente Linux)", "no_internet": "Sem conexão com a internet. Por favor, verifique sua rede e tente novamente.", "downloading_data": "Baixando arquivo de dados....", "extracting_data": "Extraindo arquivos....", "download_failed": "Falha ao baixar dados.", "extract_failed": "Falha ao extrair dados.", "download_success": "Dados baixados e extraídos com sucesso!"},
    "ru": {"welcome": "Добро пожаловать в Akademi Launcher", "loading": "Загрузка", "play": "Играть", "github": "GitHub", "settings": "Настройки", "download": "Скачать игру", "select_language": "Выбрать язык", "select_exe": "Выбрать .exe для игры", "support": "Поддержка", "discord": "Discord", "lang_changed": "Язык изменен!", "exit": "Выход", "missing_path": "Упс, попробуйте извлечь в папку лаунчера", "select_background": "Выбрать изображение фона", "winetricks": "Winetricks (Только Linux)", "no_internet": "Нет подключения к интернету. Пожалуйста, проверьте свою сеть и повторите попытку.", "downloading_data": "Загрузка файла данных....", "extracting_data": "Извлечение файлов....", "download_failed": "Не удалось загрузить данные.", "extract_failed": "Не удалось извлечь данные.", "download_success": "Данные успешно загружены и извлечены!"},
    "ja": {"welcome": "Akademi Launcherへようこそ", "loading": "読み込み中", "play": "プレイ", "github": "GitHub", "settings": "設定", "download": "ゲームをダウンロード", "select_language": "言語を選択", "select_exe": "ゲーム用の.exeを選択", "support": "サポート", "discord": "Discord", "lang_changed": "言語が変更されました！", "exit": "終了", "missing_path": "うーん、ランチャーのフォルダに抽出してみてください", "select_background": "背景画像を選択", "winetricks": "Winetricks (Linuxのみ)", "no_internet": "インターネット接続がありません。ネットワークを確認してもう一度お試しください。", "downloading_data": "データファイルをダウンロード中....", "extracting_data": "ファイルを展開中....", "download_failed": "データのダウンロードに失敗しました。", "extract_failed": "データの抽出に失敗しました。", "download_success": "データが正常にダウンロードされ、抽出されました！"},
    "zh": {"welcome": "欢迎使用 Akademi Launcher", "loading": "加载中", "play": "游戏", "github": "GitHub", "settings": "设置", "download": "下载游戏", "select_language": "选择语言", "select_exe": "选择游戏的.exe文件", "support": "支持", "discord": "Discord", "lang_changed": "语言已更改！", "exit": "退出", "missing_path": "哎呀，请尝试将其解压到启动器文件夹", "select_background": "选择背景图片", "winetricks": "Winetricks (仅限Linux)", "no_internet": "无网络连接。请检查您的网络并重试。", "downloading_data": "正在下载数据文件....", "extracting_data": "正在解压文件....", "download_failed": "下载数据失败。", "extract_failed": "解压数据失败。", "download_success": "数据已成功下载和解压！"},
    "fr": {"welcome": "Bienvenue sur Akademi Launcher", "loading": "Chargement", "play": "Jouer", "github": "GitHub", "settings": "Paramètres", "download": "Télécharger le jeu", "select_language": "Sélectionner la langue", "select_exe": "Sélectionner .exe pour le jeu", "support": "Support", "discord": "Discord", "lang_changed": "Langue changée !", "exit": "Quitter", "missing_path": "Oups, essayez de l'extraire dans le dossier du lanceur", "select_background": "Sélectionner l'image de fond", "winetricks": "Winetricks (Linux seulement)", "no_internet": "Pas de connexion internet. Veuillez vérifier votre réseau et réessayer.", "downloading_data": "Téléchargement du fichier de données....", "extracting_data": "Extraction des fichiers....", "download_failed": "Échec du téléchargement des données.", "extract_failed": "Échec de l'extraction des données.", "download_success": "Données téléchargées et extraites avec succès !"},
    "ar": {"welcome": "مرحبًا بك في Akademi Launcher", "loading": "جار التحميل", "play": "تشغيل", "github": "GitHub", "settings": "الإعدادات", "download": "تنزيل اللعبة", "select_language": "اختر اللغة", "select_exe": "حدد ملف .exe للعبة", "support": "الدعم", "discord": "Discord", "lang_changed": "تم تغيير اللغة!", "exit": "خروج", "missing_path": "أوه، حاول استخراجها في مجلد المشغل", "select_background": "اختيار صورة الخلفية", "winetricks": "Winetricks (لينكس فقط)", "no_internet": "لا يوجد اتصال بالإنترنت. يرجى التحقق من شبكتك والمحاولة مرة أخرى.", "downloading_data": " جارٍ تنزيل ملف البيانات....", "extracting_data": " جارٍ استخراج الملفات....", "download_failed": "فشل تنزيل البيانات.", "extract_failed": "فشل استخراج البيانات.", "download_success": "تم تنزيل البيانات واستخراجها بنجاح!"},
    "ko": {"welcome": "Akademi Launcher에 오신 것을 환영합니다", "loading": "로딩 중", "play": "플레이", "github": "GitHub", "settings": "설정", "download": "게임 다운로드", "select_language": "언어 선택", "select_exe": "게임용 .exe 선택", "support": "지원", "discord": "Discord", "lang_changed": "언어가 변경되었습니다!", "exit": "종료", "missing_path": "오류, 런처 폴더에 압축을 풀어 보세요", "select_background": "배경 이미지 선택", "winetricks": "Winetricks (Linux 전용)", "no_internet": "인터넷 연결이 없습니다. 네트워크를 확인하고 다시 시도하십시오.", "downloading_data": "데이터 파일 다운로드 중....", "extracting_data": "파일 압축 해제 중....", "download_failed": "데이터 다운로드 실패.", "extract_failed": "데이터 추출 실패.", "download_success": "데이터가 성공적으로 다운로드 및 추출되었습니다!"},
    "ndk": {"welcome": "niko Niko-Launcher!", "loading": "You Activated the Nikodorito Easter-egg!", "play": "Niko", "github": "GitHub", "settings": "Meow", "download": "Dalad Gaem", "select_language": "niko to to ni", "select_exe": "niko to to ni Game", "support": "niko to to ni", "discord": "Discorda", "lang_changed": "Niko DOrito! Niko dorito kimegasu", "exit": "nikotorito", "missing_path": "Uh oh,}try extract in home foldar,stupid", "select_background": "Niko dorito... select the back.", "winetricks": "manage the fucking winetricks", "no_internet": "no internet. check your network, stupid.", "downloading_data": "downloading daka file....", "extracting_data": "extracting files....", "download_failed": "fail to download daka.", "extract_failed": "fail to extract daka.", "download_success": "daka downloaded and extracted successfully!"},
    "he": {"welcome": "ברוכים הבאים ל-Akademi Launcher", "loading": "טוען", "play": "שחק", "github": "גיטהאב", "settings": "הגדרות", "download": "הורד משחק", "select_language": "בחר שפה", "select_exe": "בחר קובץ .exe עבור המשחק", "support": "תמיכה", "discord": "דיסקורד", "lang_changed": "השפה שונתה!", "exit": "יציאה", "missing_path": "אופס, נסה לחלץ לתיקיית המשגר", "select_background": "בחר תמונת רקע", "winetricks": "ווינטריקס (לינוקס בלבד)", "no_internet": "אין חיבור לאינטרנט. אנא בדוק את הרשת שלך ונסה שוב.", "downloading_data": "מוריד קובץ נתונים....", "extracting_data": "מחזיר קבצים....", "download_failed": "הורדת הנתונים נכשלה.", "extract_failed": "חילוץ הנתונים נכשל.", "download_success": "הנתונים הורדו וחולצו בהצלחה!"}
}

def get_language():
    try:
        if os.path.exists(LANG_PATH):
            with open(LANG_PATH, "r") as f:
                return f.read().strip()
    except IOError:
        pass
    return "en"


def check_internet_connection():
    try:
        socket.create_connection(("www.google.com", 80), timeout=0.1)
        return True
    except OSError:
        return False


class AkademiSplashScreen(QSplashScreen):
    def __init__(self, current_lang_data):
        super().__init__()
        self.current_lang = current_lang_data
        self.setFixedSize(600, 300)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.message = ""
        self.progress_text = ""

        self.update_splash_content(self.current_lang["downloading_data"])

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()

        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, QColor("#ff4da6"))
        gradient.setColorAt(1, QColor("#6666ff"))
        painter.fillRect(rect, gradient)

        painter.setPen(QColor(0, 0, 0))
        painter.drawRect(rect.adjusted(20, 20, -20, -20))

        text_rect = QRect(rect.width() // 2 - 200, rect.height() // 2 - 50, 400, 100)

        font_title = QFont("Futura", 32, QFont.Bold)
        painter.setFont(font_title)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(text_rect, Qt.AlignCenter, "Akademi Launcher")

        font_message = QFont("Futura", 16)
        painter.setFont(font_message)
        painter.setPen(QColor(0, 0, 0))
        message_rect = QRect(rect.width() // 2 - 200, rect.height() // 2 + 10, 400, 50)
        painter.drawText(message_rect, Qt.AlignCenter, self.message)

        font_progress = QFont("Futura", 12)
        painter.setFont(font_progress)
        painter.setPen(QColor(0, 0, 0))
        progress_rect = QRect(rect.width() - 150, rect.height() - 50, 100, 30)
        painter.drawText(progress_rect, Qt.AlignRight | Qt.AlignBottom, self.progress_text)

    def update_splash_content(self, message, progress=""):
        self.message = message
        self.progress_text = progress
        self.repaint()


def download_and_extract_data(splash_screen, current_lang_data):
    target_data_folder = os.path.join(AKADEMI_PATH, "data")

    if os.path.exists(target_data_folder) and os.listdir(target_data_folder):
        splash_screen.update_splash_content(current_lang_data["download_success"])
        return

    if not check_internet_connection():
        if os.path.exists(target_data_folder):
            splash_screen.update_splash_content(current_lang_data["download_success"])
            return
        else:
            QMessageBox.critical(None, current_lang_data["no_internet"], current_lang_data["no_internet"])
            splash_screen.hide()
            sys.exit(1)

    splash_screen.update_splash_content(current_lang_data["downloading_data"])
    try:
        response = requests.get(DATA_DOWNLOAD_URL, stream=True, timeout=10)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        with open(TEMP_ZIP_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded_size += len(chunk)
                progress = f"{downloaded_size / (1024 * 1024):.1f}MB / {total_size / (1024 * 1024):.1f}MB" if total_size > 0 else "..."
                splash_screen.update_splash_content(current_lang_data["downloading_data"], progress)
                QApplication.processEvents()

    except requests.exceptions.Timeout:
        QMessageBox.critical(None, current_lang_data["download_failed"], f"{current_lang_data['download_failed']} (Connection Timeout).")
        if os.path.exists(TEMP_ZIP_PATH):
            os.remove(TEMP_ZIP_PATH)
        splash_screen.hide()
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        QMessageBox.critical(None, current_lang_data["download_failed"], f"{current_lang_data['download_failed']} (Connection Error. Check URL or internet).")
        if os.path.exists(TEMP_ZIP_PATH):
            os.remove(TEMP_ZIP_PATH)
        splash_screen.hide()
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        QMessageBox.critical(None, current_lang_data["download_failed"], f"{current_lang_data['download_failed']} (Error: {e}).")
        if os.path.exists(TEMP_ZIP_PATH):
            os.remove(TEMP_ZIP_PATH)
        splash_screen.hide()
        sys.exit(1)
    except Exception as e:
        QMessageBox.critical(None, current_lang_data["download_failed"], f"{current_lang_data['download_failed']} (Unexpected error during download: {e}).")
        if os.path.exists(TEMP_ZIP_PATH):
            os.remove(TEMP_ZIP_PATH)
        splash_screen.hide()
        sys.exit(1)


    splash_screen.update_splash_content(current_lang_data["extracting_data"])
    QApplication.processEvents()
    try:
        os.makedirs(target_data_folder, exist_ok=True)
        with zipfile.ZipFile(TEMP_ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(target_data_folder)
    except zipfile.BadZipFile as e:
        QMessageBox.critical(None, current_lang_data["extract_failed"], f"{current_lang_data['extract_failed']} (Corrupted or invalid ZIP file: {e}).")
        if os.path.exists(TEMP_ZIP_PATH):
            os.remove(TEMP_ZIP_PATH)
        shutil.rmtree(target_data_folder, ignore_errors=True)
        splash_screen.hide()
        sys.exit(1)
    except Exception as e:
        QMessageBox.critical(None, current_lang_data["extract_failed"], f"{current_lang_data['extract_failed']} (Unexpected error during extraction: {e}).")
        if os.path.exists(TEMP_ZIP_PATH):
            os.remove(TEMP_ZIP_PATH)
        shutil.rmtree(target_data_folder, ignore_errors=True)
        splash_screen.hide()
        sys.exit(1)
    finally:
        if os.path.exists(TEMP_ZIP_PATH):
            os.remove(TEMP_ZIP_PATH)


class SettingsDialog(QDialog):
    def __init__(self, lang_code, lang_data, parent=None):
        super().__init__(parent)
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
        try:
            with open(LANG_PATH, "w") as f:
                f.write(lang)

            message = LANGUAGES[lang]["lang_changed"]
            if lang not in ["en", "pt", "ndk"]:
                message += "\n\nThis language is 100% AI and may have malfunctions."

            QMessageBox.information(self, "Info", message)

            if self.parent():
                self.parent().retranslate_ui()

            self.accept()
        except IOError as e:
            QMessageBox.critical(self, "Error", f"Could not save language setting: {e}")


class AkademiLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang_code = get_language()
        self.lang = LANGUAGES.get(self.lang_code, LANGUAGES["en"])

        self.setWindowTitle("Akademi Launcher")
        self.setFixedSize(1100, 600)

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.setup_ui()

        self.rpc = None
        self.start_time = int(time.time())
        if presence_enabled:
            self.init_rpc()

    def init_rpc(self):
        try:
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.update_rpc(details="In the launcher", state="Browse...")
        except Exception:
            self.rpc = None

    def update_rpc(self, details, state=None):
        if not self.rpc:
            return
        try:
            self.rpc.update(
                details=details,
                state=state,
                start=self.start_time,
                large_image="yanix_logo",
                large_text="Akademi Launcher"
            )
        except Exception:
            self.rpc.close()
            self.rpc = None

    def setup_ui(self):
        main_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.left_layout.setAlignment(Qt.AlignTop)

        font = QFont("Futura", 16)
        version_font = QFont("Futura", 10)

        button_style = """
            QPushButton {
                color: black;
                background-color: white;
                padding: 8px;
                border-radius: 6px;
                border: 1px solid #ccc;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """

        self.play_button = QPushButton()
        self.play_button.setFont(font)
        self.play_button.setStyleSheet(button_style)
        self.play_button.clicked.connect(self.launch_game)
        self.left_layout.addWidget(self.play_button)

        self.settings_button = QPushButton()
        self.settings_button.setFont(font)
        self.settings_button.setStyleSheet(button_style)
        self.settings_button.clicked.connect(self.open_settings)
        self.left_layout.addWidget(self.settings_button)

        self.select_exe_button = QPushButton()
        self.select_exe_button.setFont(font)
        self.select_exe_button.setStyleSheet(button_style)
        self.select_exe_button.clicked.connect(self.select_exe)
        self.left_layout.addWidget(self.select_exe_button)

        self.download_button = QPushButton()
        self.download_button.setFont(font)
        self.download_button.setStyleSheet(button_style)
        self.download_button.clicked.connect(self.download_game)
        self.left_layout.addWidget(self.download_button)

        self.winetricks_button = QPushButton()
        self.winetricks_button.setFont(font)
        self.winetricks_button.setStyleSheet(button_style)
        self.winetricks_button.clicked.connect(self.manage_winetricks)
        self.left_layout.addWidget(self.winetricks_button)

        self.support_button = QPushButton()
        self.support_button.setFont(font)
        self.support_button.setStyleSheet(button_style)
        self.support_button.clicked.connect(lambda: webbrowser.open("https://github.com/NikoYandere/Yanix-Launcher/issues"))
        self.left_layout.addWidget(self.support_button)

        self.discord_button = QPushButton()
        self.discord_button.setFont(font)
        self.discord_button.setStyleSheet(button_style)
        self.discord_button.clicked.connect(lambda: webbrowser.open("https://discord.gg/7JC4FGn69U"))
        self.left_layout.addWidget(self.discord_button)

        self.version_label = QLabel()
        self.version_label.setFont(version_font)
        self.version_label.setStyleSheet("color: white; margin-top: 20px;")
        self.left_layout.addWidget(self.version_label)

        blog_view = QWebEngineView()
        blog_view.load(QUrl("https://yanix-launcher.blogspot.com"))

        main_layout.addLayout(self.left_layout, 1)
        main_layout.addWidget(blog_view, 2)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.retranslate_ui()

    def retranslate_ui(self):
        self.lang_code = get_language()
        self.lang = LANGUAGES.get(self.lang_code, LANGUAGES["en"])

        self.play_button.setText(self.lang["play"])
        self.settings_button.setText(self.lang["settings"])
       
        self.select_exe_button.setText(self.lang["select_exe"])
        self.download_button.setText(self.lang["download"])
        
        self.winetricks_button.setText(self.lang["winetricks"])
        self.winetricks_button.setEnabled(False)  
        self.support_button.setText(self.lang["support"])
        self.discord_button.setText(self.lang["discord"])
        self.version_label.setText(f"{self.lang['welcome']} V 0.7")

        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#ff4da6"))
        gradient.setColorAt(1, QColor("#6666ff"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)


    def open_settings(self):
        dlg = SettingsDialog(self.lang_code, self.lang, self)
        dlg.exec_()

    def _wait_for_game_exit(self, process):
        process.wait()
        self.update_rpc(details="In the launcher", state="Browse...")

    def launch_game(self):
        if not os.path.exists(CONFIG_PATH):
            QMessageBox.critical(self, "Error", "Game executable path not defined. Please select the .exe file in Settings.")
            return

        with open(CONFIG_PATH) as f:
            path = f.read().strip()

        if os.path.exists(path):
            try:
                self.update_rpc(details="Playing Yandere Simulator", state="In-Game")
                
                game_process = subprocess.Popen([path])

                monitor_thread = threading.Thread(
                    target=self._wait_for_game_exit,
                    args=(game_process,),
                    daemon=True
                )
                monitor_thread.start()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred while starting the game: {e}")
                self.update_rpc(details="In the launcher", state="Browse...")
        else:
            QMessageBox.critical(self, "Error", "The saved game path is invalid. Please re-select the executable.")

    def select_exe(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select Game Executable", "", "Executable Files (*.exe)")
        if file:
            try:
                with open(CONFIG_PATH, "w") as f:
                    f.write(file)
                QMessageBox.information(self, "Success", "Executable path saved successfully.")
            except IOError as e:
                QMessageBox.critical(self, "Error", f"Could not save executable path: {e}")

    def download_game(self):
        webbrowser.open("https://yanderesimulator.com/dl/latest.zip")

    def manage_winetricks(self):
        QMessageBox.information(self, "Winetricks", self.lang["winetricks"])
       
    def closeEvent(self, event):
        if self.rpc:
            self.rpc.close()
        event.accept()


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)

    lang_code = get_language()
    current_lang_data = LANGUAGES.get(lang_code, LANGUAGES["en"])

    splash = AkademiSplashScreen(current_lang_data)
    splash.show()

    QApplication.processEvents()

    download_and_extract_data(splash, current_lang_data)

    launcher = AkademiLauncher()
    launcher.show()
    splash.finish(launcher)

    sys.exit(app.exec_())
