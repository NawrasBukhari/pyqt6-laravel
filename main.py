import os
import sys
import time
import threading
import subprocess
import webbrowser
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


def splash():
    splash_pixmap = QPixmap(os.path.join(SCRIPT_DIRECTORY, SPLASH_SCREEN["folder_name"], SPLASH_SCREEN["splash_name"]))
    splash_screen_content = QSplashScreen(splash_pixmap)
    splash_screen_content.show()
    time.sleep(SPLASH_SCREEN["splash_time"])
    return splash_screen_content


def log(message):
    with open(os.path.join(SCRIPT_DIRECTORY, LOGS['folder_name'], LOGS['log_file_name']), "a") as log_file:
        log_file.write(time.strftime("%Y-%m-%d %H:%M:%S") + " - " + message + "\n")


def create_fallback_php_file():
    with open(os.path.join(SCRIPT_DIRECTORY, FALLBACK_FILE_NAME), "w") as default_file:
        default_file.write("<?php echo phpinfo(); ?>")


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


def create_php_server():
    global PHP_SERVER
    global PHP_SERVER_THREAD
    global PHP_SERVER_RUNNING

    start_time = time.time()

    try:
        if not os.path.exists(PHP_EXECUTABLE) or not os.listdir(PHP_BINARIES):
            log("PHP executable not found")
            webbrowser.open("https://windows.php.net/download/")
            PHP_SERVER_RUNNING = False

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
