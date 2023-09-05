import os
import re
import sys
import time
import easygui
import zipfile
import requests
import pymsgbox
import platform
import threading
import subprocess
from config.server import *
from config.desktop import *
from config.styles import STYLES
from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplashScreen, QSizePolicy

SCRIPT_DIRECTORY = os.path.abspath(os.getcwd())
splash_screen = None

# Define the path to the bundled PHP executable
PHP_EXECUTABLE = os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME, PHP_EXECUTABLE_NAME)

# Global variables
PHP_BINARIES = os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME)
LARAVEL_ROOT = os.path.join(SCRIPT_DIRECTORY, LARAVEL_PROJECT_DIRECTORY_NAME)
LARAVEL_PUBLIC = os.path.join(LARAVEL_ROOT, LARAVEL_PUBLIC_DIRECTORY_NAME)

# PHP server
PHP_SERVER = None
PHP_SERVER_THREAD = None
PHP_SERVER_RUNNING = False


def log(message):
    with open(os.path.join(SCRIPT_DIRECTORY, LOGS['folder_name'], LOGS['log_file_name']), "a") as log_file:
        log_file.write(time.strftime("%Y-%m-%d %H:%M:%S") + " - " + message + "\n")


def splash():
    splash_start_time = time.time()
    splash_pixmap = QPixmap(os.path.join(SCRIPT_DIRECTORY, SPLASH_SCREEN["folder_name"], SPLASH_SCREEN["splash_name"]))
    splash_screen_content = QSplashScreen(splash_pixmap)
    splash_screen_content.show()
    time.sleep(SPLASH_SCREEN["splash_time"])
    splash_end_time = time.time()
    splash_time = (splash_end_time - splash_start_time) * 1000
    if splash_time > 1000:
        log("Splash screen displayed for " + str("[" + str(splash_time / 1000) + "]") + " s")
    else:
        log("Splash screen displayed for " + str("[" + str(splash_time) + "]") + " ms")

    return splash_screen_content


def create_fallback_php_file():
    with open(os.path.join(SCRIPT_DIRECTORY, FALLBACK_FILE_NAME), "w") as default_file:
        default_file.write("<?php echo phpinfo(); ?>")


def check_user_bitNess():
    bitNess = platform.architecture()[0]
    if bitNess == "64bit":
        return True
    else:
        return False


def rewrite_php_ini():
    pattern = re.compile(r'%pyqt6_laravel_(.*?)%')

    VARIABLES_TO_BE_REPLACED = {
        "error_log": os.path.join(SCRIPT_DIRECTORY, LOGS['folder_name']),
        "upload_tmp_dir": os.path.join(SCRIPT_DIRECTORY, TEMP['folder_name']),
        "session_save_path": os.path.join(SCRIPT_DIRECTORY, TEMP['folder_name']),
        "soap_wsdl_cache_dir": os.path.join(SCRIPT_DIRECTORY, TEMP['folder_name']),
        "extension_dir": os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME, "ext"),
        "php_opcache_dll": os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME, "ext", "php_opcache.dll"),
    }

    # search for PHP_INI_FILENAME_FRESH_INSTALL in the php folder then rename it with PHP_INI_FILENAME
    if os.path.exists(os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME, PHP_INI_FILENAME_FRESH_INSTALL)):
        os.rename(os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME, PHP_INI_FILENAME_FRESH_INSTALL),
                  os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME, PHP_INI_FILENAME))
        log("PHP ini file renamed successfully from " + PHP_INI_FILENAME_FRESH_INSTALL + " to " + PHP_INI_FILENAME)

    # Read the content from the PHP ini stub file
    with open(
            os.path.join(
                SCRIPT_DIRECTORY, PHP_INI_STUB['folder_name'], PHP_INI_STUB['stub_name']), "r") as php_ini_stub_file:
        php_ini_content = php_ini_stub_file.read()

    log("PHP ini stub file content read successfully from " + PHP_INI_STUB['stub_name'] + " file")

    # Replace the variables using the pattern and dictionary
    php_ini_content = pattern.sub(lambda match: VARIABLES_TO_BE_REPLACED.get(match.group(1), match.group(0)),
                                  php_ini_content)

    # Write the updated content to the PHP ini file
    with open(os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME, PHP_INI_FILENAME), "w") as php_ini_file:
        php_ini_file.write(php_ini_content)

    log("PHP ini file updated successfully with the new variables")


def download_php(version):
    current_platform = platform.system()
    bitNess = "64bit" if check_user_bitNess() else "32bit"
    if current_platform == "Windows" and bitNess == "64bit":
        URL = PHP_DOWNLOAD_URL_64.get(version)
    elif current_platform == "Windows" and bitNess == "32bit":
        URL = PHP_DOWNLOAD_URL_32.get(version)
    else:
        URL = None

    if URL:
        try:
            log("Downloading PHP from " + URL)
            response = requests.get(URL, allow_redirects=True)
            # get the downloaded file name
            PHP_ZIP_FILE_NAME = URL.split("/")[-1]

            # Ensure the PHP directory exists
            php_dir = os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME)
            os.makedirs(php_dir, exist_ok=True)

            # Save the ZIP file
            with open(os.path.join(php_dir, PHP_ZIP_FILE_NAME), "wb") as php_zip_file:
                php_zip_file.write(response.content)
            log("PHP downloaded successfully")

            # Unzip the file
            with zipfile.ZipFile(os.path.join(php_dir, PHP_ZIP_FILE_NAME), "r") as zip_ref:
                zip_ref.extractall(php_dir)

            log("PHP unzipped successfully")

            # Delete the ZIP file
            os.remove(os.path.join(php_dir, PHP_ZIP_FILE_NAME))
            log("PHP ZIP file deleted successfully")

        except Exception as PHPDownloadError:
            log("Error downloading PHP:" + str(PHPDownloadError))
    else:
        log("PHP version not found or unsupported for your platform")


def create_php_server():
    global PHP_SERVER
    global PHP_SERVER_THREAD
    global PHP_SERVER_RUNNING

    start_time = time.time()

    try:
        if not os.path.exists(PHP_EXECUTABLE) or not os.listdir(PHP_BINARIES):
            log("PHP executable not found so it will be downloaded automatically")
            response = pymsgbox.confirm(
                "PHP executable was not found. Do you want to install PHP automatically?",
                "PHP Not Found",
                buttons=[pymsgbox.YES_TEXT, pymsgbox.NO_TEXT],
            )
            log("User response:" + str(response))
            if response == pymsgbox.YES_TEXT:
                log("PHP executable will be installed automatically")
                user_bitNess = check_user_bitNess()
                log("User bitNess:" + str(user_bitNess))
                if user_bitNess:
                    log("64bit detected so we will download the 64bit version")
                    choices = []
                    for key in PHP_DOWNLOAD_URL_64:
                        choices.append(key)

                    selected_option = easygui.choicebox("Select an option:", "Select PHP version to download",
                                                        choices=choices)
                    log("User selected option:" + str(selected_option))
                    splash_screen = splash()
                    download_php(selected_option)
                    rewrite_php_ini()
                    splash_screen.close()
                else:
                    log("32bit detected so we will download the 32bit version")
                    choices = []
                    for key in PHP_DOWNLOAD_URL_32:
                        choices.append(key)
                    selected_option = easygui.choicebox("Select an option:", "Select PHP version to download",
                                                        choices=choices)
                    log("User selected option:" + str(selected_option))
                    splash_screen = splash()
                    download_php(selected_option)
                    rewrite_php_ini()
                    splash_screen.close()

            else:
                log("User cancelled the installation of PHP")
                sys.exit(1)

        elif not os.path.exists(LARAVEL_ROOT) or not os.path.exists(LARAVEL_PUBLIC):
            log(f"Laravel root and public folders not found so we will redirect to the {FALLBACK_FILE_NAME} file")
            create_fallback_php_file()
            PHP_SERVER = subprocess.Popen(
                [PHP_EXECUTABLE, "-S", SERVER_HOST, "-t", SCRIPT_DIRECTORY, FALLBACK_FILE_NAME],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW)
            PHP_SERVER_RUNNING = True

        elif os.path.exists(LARAVEL_ROOT) and not os.listdir(LARAVEL_ROOT):
            log(f"Laravel root folder is empty so we will redirect to the {FALLBACK_FILE_NAME} file")
            create_fallback_php_file()
            PHP_SERVER = subprocess.Popen(
                [PHP_EXECUTABLE, "-S", SERVER_HOST, "-t", SCRIPT_DIRECTORY, FALLBACK_FILE_NAME],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW)
            PHP_SERVER_RUNNING = True

        else:
            PHP_SERVER = subprocess.Popen([PHP_EXECUTABLE, "-S", SERVER_HOST, "-t", LARAVEL_PUBLIC],
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          creationflags=subprocess.CREATE_NO_WINDOW)
            PHP_SERVER_RUNNING = True

    except Exception as ServerStartingError:
        log("Error starting PHP server:" + str(ServerStartingError))
        PHP_SERVER_RUNNING = False

    end_time = time.time()

    PHP_SERVER_THREAD = threading.Thread(target=PHP_SERVER.communicate)
    PHP_SERVER_THREAD.start()
    final_time = (end_time - start_time) * 1000

    if final_time > 1000:
        log("PHP server started at " + "[" + SERVER_URL + "]" + " in " + str("[" + str(final_time / 1000) + "]") + " s")
    else:
        log("PHP server started at " + "[" + SERVER_URL + "]" + " in " + str("[" + str(final_time) + "]") + " ms")

    App = QApplication(sys.argv)
    window = MyApp(SERVER_URL)
    window.show()
    sys.exit(App.exec())


def stop_php_server():
    global PHP_SERVER
    global PHP_SERVER_THREAD
    global PHP_SERVER_RUNNING

    if PHP_SERVER_RUNNING:
        PHP_SERVER.terminate()
        PHP_SERVER_THREAD.join()
        PHP_SERVER_RUNNING = False
        log("PHP server stopped at " + "[" + SERVER_URL + "] " + "in " + str("[" + str(time.time()) + "]") + " ms")


class MyWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # This method will be called when there's a message in the JavaScript console
        if level == QWebEnginePage.InfoMessageLevel:
            log(message + " (Line " + str(lineNumber) + " in " + sourceID + ")" + "\n")
        elif level == QWebEnginePage.WarningMessageLevel:
            log(message + " (Line " + str(lineNumber) + " in " + sourceID + ")" + "\n")
        elif level == QWebEnginePage.ErrorMessageLevel:
            log(message + " (Line " + str(lineNumber) + " in " + sourceID + ")" + "\n")


class MyApp(QMainWindow):
    cleanup_signal = pyqtSignal()

    def __init__(self, server_url):
        super().__init__()

        # global variables
        self.settings = QWebEngineSettings
        self.server_url = server_url
        self.webview = QWebEngineView(self)
        self.setCentralWidget(self.webview)

        # Connect the window's close event to the cleanup signal
        self.closing = False
        self.cleanup_signal.connect(self.perform_cleanup)

        # initialize the UI
        splash_screen = splash()
        self.initUI()

    def initUI(self):

        self.setWindowTitle(DESKTOP_APP_NAME)
        self.setWindowIcon(QIcon(os.path.join(ICON["folder_name"], ICON["icon_name"])))
        self.setAnimated(ANIMATED)
        self.setStyleSheet(STYLES)

        if SET_MAXIMIZED:
            self.webview.showMaximized()

        else:
            self.setGeometry(X_COORDINATE, Y_COORDINATE, WIDTH, HEIGHT)
            self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
            self.setMaximumSize(MAX_WIDTH, MAX_HEIGHT)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(LEFT_MARGIN, TOP_MARGIN, RIGHT_MARGIN, BOTTOM_MARGIN)

        self.webview = QWebEngineView()

        self.webview.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.layout.addWidget(self.webview)

        self.webview.setZoomFactor(ZOOM_FACTOR)

        menubar = self.menuBar()
        self.setMenuBar(menubar)
        self.menuBar().setStyleSheet(
            open(os.path.join(SCRIPT_DIRECTORY, STYLESHEET['folder_name'], STYLESHEET['stylesheet_name']), "r").read())

        # Create a File menu
        file_menu = menubar.addMenu('Application')

        # Create an Edit menu
        edit_menu = menubar.addMenu('Edit')

        # Create a "Reload" action under the File menu
        reload_action = QAction('Reload', self)
        reload_action.triggered.connect(self.reloadWebPage)
        file_menu.addAction(reload_action)

        # Create a "Copy" action under the Edit menu
        copy_action = QAction('Copy', self)
        copy_action.triggered.connect(self.copyText)
        edit_menu.addAction(copy_action)

        # Create a "Paste" action under the Edit menu
        paste_action = QAction('Paste', self)
        paste_action.triggered.connect(self.pasteText)
        edit_menu.addAction(paste_action)

        # Create a "Save Page As" action under the File menu
        save_as_action = QAction('Save Page As', self)
        save_as_action.triggered.connect(self.savePageAs)
        file_menu.addAction(save_as_action)

        # Create an "Exit" action under the File menu
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.exitApp)
        file_menu.addAction(exit_action)

        self.webview.page().runJavaScript(
            open(os.path.join(SCRIPT_DIRECTORY, PRERENDER_SCRIPT["folder_name"], PRERENDER_SCRIPT["script_name"]),
                 "r").read())

        self.loadWebPage()

    def loadWebPage(self):
        self.webview.setUrl(QUrl(self.server_url))

    def reloadWebPage(self):
        self.webview.reload()

    def copyText(self):
        self.javascript("document.execCommand('copy');")

    def pasteText(self):
        self.javascript("document.execCommand('paste');")

    def savePageAs(self):
        self.javascript("window.print();")

    def exitApp(self):
        self.closing = True
        self.close()
        stop_php_server()

    def closeEvent(self, event):
        if not self.closing:
            self.closing = True
            self.cleanup_signal.emit()
            event.ignore()
        else:
            event.accept()

    def perform_cleanup(self):
        stop_php_server()
        self.close()

    def javascript(self, command):
        self.webview.page().runJavaScript(command)


if __name__ == "__main__":

    try:
        app = QApplication(sys.argv)
        create_php_server()
        splash_screen.close()
        sys.exit(app.exec())

    except Exception as error:
        log("Error starting application:" + str(error))
        sys.exit(1)
