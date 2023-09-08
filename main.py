import os
import re
import sys
import time
import easygui
import zipfile
import requests
import pymsgbox
import platform
import subprocess
from config.server import *
from config.desktop import *
from config.styles import STYLES
from config.localization import LANG
from PyQt6.QtCore import QUrl, pyqtSignal, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtGui import QAction, QIcon, QPixmap, QCloseEvent
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings, QWebEngineProfile
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSplashScreen, QSizePolicy

# Global variables
SCRIPT_DIRECTORY = os.path.abspath(os.getcwd())
SPLASH_SCREEN_VISIBLE = None

# PHP
PHP_EXECUTABLE = os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME, PHP_EXECUTABLE_NAME)
COMPOSER_EXECUTABLE_NAME = "composer.phar"
splash_screen = None

# PHP binaries
PHP_BINARIES = os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME)
LARAVEL_ROOT = os.path.join(SCRIPT_DIRECTORY, LARAVEL_PROJECT_DIRECTORY_NAME)
LARAVEL_PUBLIC = os.path.join(LARAVEL_ROOT, LARAVEL_PUBLIC_DIRECTORY_NAME)

# PHP server
PHP_SERVER = None
PHP_SERVER_THREAD = None
PHP_SERVER_RUNNING = False

# Make sure the user has entered a correct application name
DESKTOP_APP_NAME = DESKTOP_APP_NAME.strip()
if not DESKTOP_APP_NAME:
    pymsgbox.alert(
        LANG["Please enter a correct application name"],
        LANG["Application Name Error"],
        button=pymsgbox.OK_TEXT)
    sys.exit(1)


def log(message):
    line_number = sys._getframe(1).f_lineno.__str__()
    with open(os.path.join(SCRIPT_DIRECTORY,
                           LOGS['folder_name'],
                           LOGS['log_file_name']), "a") as log_file:
        log_file.write(time.strftime("%Y-%m-%d %H:%M:%S") +
                       " - " + message + " (Line " +
                       str(line_number) + ")" + "\n")


def space(string, left=False, right=False, both=False):
    if left:
        return " " + string
    elif right:
        return string + " "
    elif both:
        return " " + string + " "
    else:
        return string


def splash(splash_file):
    splash_start_time = time.time()

    splash_pixmap = QPixmap(os.path.join(SCRIPT_DIRECTORY,
                                         SPLASH_SCREEN["folder_name"],
                                         splash_file))

    splash_screen_content = QSplashScreen(splash_pixmap)
    splash_screen_content.show()
    splash_end_time = time.time()
    splash_time = (splash_end_time - splash_start_time) * 1000
    if splash_time > 1000:
        log(space(LANG["Splash screen displayed for"], right=True) +
            str("[" + str(splash_time / 1000) + "]") +
            space(LANG["seconds"], left=True))

    else:
        log(space(LANG["Splash screen displayed for"], right=True) +
            str("[" + str(splash_time) + "]") +
            space(LANG["milliseconds"], left=True))

    return splash_screen_content


def create_fallback_php_file():
    with open(os.path.join(SCRIPT_DIRECTORY,
                           FALLBACK_FILE_NAME), "w") as default_file:
        default_file.write("<?php echo phpinfo(); ?>")


def check_user_bitNess():
    bitNess = platform.architecture()[0]
    if bitNess == "64bit":
        return True
    else:
        return False


def check_internet_connection():
    check_connection = requests.get("https://google.com")
    if check_connection.status_code == 200:
        log(LANG["Internet connection detected successfully"])
        return True
    else:
        pymsgbox.alert(
            LANG["Internet connection not detected. Please check your internet connection and try again."],
            LANG["Internet Connection Error"],
            button=pymsgbox.OK_TEXT)

        return False


def create_laravel_project():
    try:
        if check_internet_connection():
            download_start_at = time.time()
            if not os.path.exists(LARAVEL_ROOT) or not os.listdir(LARAVEL_ROOT):
                os.makedirs(LARAVEL_ROOT, exist_ok=True)
                log(space(LANG["Creating Laravel project in"], right=True) + LARAVEL_PROJECT_DIRECTORY_NAME)

            download_composer_file = requests.get(COMPOSER_DOWNLOAD_URL)
            with open(os.path.join(SCRIPT_DIRECTORY, COMPOSER_SETUP_FILE), "wb") as composer_file:
                composer_file.write(download_composer_file.content)
            log(LANG["Composer file downloaded successfully"])

            composer_setup = subprocess.Popen(
                [os.path.join(PHP_EXECUTABLE),
                 os.path.join(SCRIPT_DIRECTORY, COMPOSER_SETUP_FILE)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            composer_setup.communicate()
            log(LANG["Composer setup file executed successfully"])

            os.remove(os.path.join(SCRIPT_DIRECTORY, COMPOSER_SETUP_FILE))
            log(LANG["Composer setup file deleted successfully"])

            # if the file already exists in the Laravel project directory then stop else move it
            if not os.path.exists(os.path.join(LARAVEL_ROOT, COMPOSER_EXECUTABLE_NAME)):
                os.rename(os.path.join(SCRIPT_DIRECTORY, COMPOSER_EXECUTABLE_NAME),
                          os.path.join(LARAVEL_ROOT, COMPOSER_EXECUTABLE_NAME))
                log(LANG["Composer phar file moved successfully to the Laravel project directory"])
            else:
                log(LANG["Composer phar file already exists in the Laravel project directory"])

            composerDotPhar = os.path.join(LARAVEL_ROOT, COMPOSER_EXECUTABLE_NAME)

            laravel_project = subprocess.Popen(
                [os.path.join(PHP_EXECUTABLE),
                 composerDotPhar,
                 "create-project",
                 "laravel/laravel",
                 DESKTOP_APP_NAME],
                cwd=LARAVEL_ROOT,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW)

            laravel_project.communicate()
            log(LANG["Laravel project created successfully"])

            # make sure that Laravel was installed successfully
            if not os.path.exists(os.path.join(LARAVEL_ROOT, DESKTOP_APP_NAME, "vendor")):
                # download the vendor folder
                composer_install_vendor = subprocess.Popen(
                    [os.path.join(PHP_EXECUTABLE),
                     composerDotPhar,
                     "install"],
                    cwd=os.path.join(LARAVEL_ROOT, DESKTOP_APP_NAME),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW)

                composer_install_vendor.communicate()
                log(LANG["Vendor downloaded successfully"])

                # check if the .env file exists
                if not os.path.exists(os.path.join(LARAVEL_ROOT, DESKTOP_APP_NAME, ".env")):
                    os.rename(os.path.join(LARAVEL_ROOT, DESKTOP_APP_NAME, ".env.example"),
                              os.path.join(LARAVEL_ROOT, DESKTOP_APP_NAME, ".env"))

                    log(LANG[".env file renamed successfully"])

                # generate the key
                generate_key = subprocess.Popen(
                    [os.path.join(PHP_EXECUTABLE),
                     os.path.join(LARAVEL_ROOT, DESKTOP_APP_NAME, "artisan"),
                     "key:generate"],
                    cwd=os.path.join(LARAVEL_ROOT, DESKTOP_APP_NAME),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW)

                generate_key.communicate()
                log(LANG["Key generated successfully"])

            for item in os.listdir(os.path.join(LARAVEL_ROOT, DESKTOP_APP_NAME)):
                os.rename(os.path.join(LARAVEL_ROOT, DESKTOP_APP_NAME, item),
                          os.path.join(LARAVEL_ROOT, item))
            os.rmdir(os.path.join(LARAVEL_ROOT, DESKTOP_APP_NAME))
            log(LANG["Laravel project moved successfully to the Laravel project directory"])
            download_ended_at = time.time()
            download_time = (download_ended_at - download_start_at) * 1000
            if download_time > 1000:
                log(space(LANG["Laravel project created successfully in"], right=True) +
                    str("[" + str(download_time / 1000) + "]") +
                    space(LANG["seconds"], left=True))

            else:
                log(space(LANG["Laravel project created successfully in"], right=True) +
                    str("[" + str(download_time) + "]") +
                    space(LANG["milliseconds"], left=True))

        else:
            log(LANG["Internet connection not detected"])
            log(LANG["Laravel project downloaded successfully in"] + LARAVEL_PROJECT_DIRECTORY_NAME)
            pymsgbox.alert(
                LANG["Internet connection not detected. Please check your internet connection and try again."],
                LANG["Internet Connection Error"],
                button=pymsgbox.OK_TEXT)
            sys.exit(1)

    except Exception as LaravelProjectCreationError:
        log(space(LANG["Error creating Laravel project because of:"], right=True) + str(LaravelProjectCreationError))


def rewrite_php_ini():
    pattern = re.compile(r'%pyqt6_laravel_(.*?)%')

    VARIABLES_TO_BE_REPLACED = {
        "error_log": os.path.join(SCRIPT_DIRECTORY, LOGS['folder_name']),
        "upload_tmp_dir": os.path.join(SCRIPT_DIRECTORY, TEMP['folder_name']),
        "session_save_path": os.path.join(SCRIPT_DIRECTORY, TEMP['folder_name']),
        "soap_wsdl_cache_dir": os.path.join(SCRIPT_DIRECTORY, TEMP['folder_name']),
        "extension_dir": os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME, "ext"),
        "php_opcache_dll": os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME, "ext", "php_opcache.dll"),
        "cainfo": os.path.join(SCRIPT_DIRECTORY, CACERT_PEM["folder_name"], CACERT_PEM["cacert_pem_name"]),
        "openssl_cainfo": os.path.join(SCRIPT_DIRECTORY, CACERT_PEM["folder_name"], CACERT_PEM["cacert_pem_name"]),
    }

    if os.path.exists(os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME, PHP_INI_FILENAME_FRESH_INSTALL)):
        os.rename(os.path.join(SCRIPT_DIRECTORY,
                               PHP_BIN_DIRECTORY_NAME,
                               PHP_INI_FILENAME_FRESH_INSTALL),
                  os.path.join(
                      SCRIPT_DIRECTORY,
                      PHP_BIN_DIRECTORY_NAME,
                      PHP_INI_FILENAME))

        log(space(LANG["PHP ini file renamed successfully from"], right=True) +
            PHP_INI_FILENAME_FRESH_INSTALL +
            space(LANG["to"], both=True) +
            PHP_INI_FILENAME)

    # Read the content from the PHP ini stub file
    with open(
            os.path.join(
                SCRIPT_DIRECTORY,
                PHP_INI_STUB['folder_name'],
                PHP_INI_STUB['stub_name']), "r") as php_ini_stub_file:
        php_ini_content = php_ini_stub_file.read()

    log(space(LANG["PHP ini stub file content read successfully from"], right=True) +
        PHP_INI_STUB['stub_name'] + space(LANG["file"], left=True))

    # Replace the variables using the pattern and dictionary
    php_ini_content = pattern.sub(
        lambda match: VARIABLES_TO_BE_REPLACED
        .get(match.group(1), match.group(0)),
        php_ini_content)

    # Write the updated content to the PHP ini file
    with open(os.path.join(SCRIPT_DIRECTORY,
                           PHP_BIN_DIRECTORY_NAME,
                           PHP_INI_FILENAME), "w") as php_ini_file:
        php_ini_file.write(php_ini_content)

    log(LANG["PHP ini file updated successfully with the new variables"])


def download_php(version):
    if check_internet_connection():

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
                log(space(LANG["Downloading PHP from"], right=True) + URL)
                response = requests.get(URL, allow_redirects=True)
                # get the downloaded file name
                PHP_ZIP_FILE_NAME = URL.split("/")[-1]

                # Ensure the PHP directory exists
                php_dir = os.path.join(SCRIPT_DIRECTORY, PHP_BIN_DIRECTORY_NAME)
                os.makedirs(php_dir, exist_ok=True)

                # Save the ZIP file
                with open(os.path.join(php_dir, PHP_ZIP_FILE_NAME), "wb") as php_zip_file:
                    php_zip_file.write(response.content)
                log(LANG["PHP downloaded successfully"])

                # Unzip the file
                with zipfile.ZipFile(os.path.join(php_dir, PHP_ZIP_FILE_NAME), "r") as zip_ref:
                    zip_ref.extractall(php_dir)

                log(LANG["PHP unzipped successfully"])

                # Delete the ZIP file
                os.remove(os.path.join(php_dir, PHP_ZIP_FILE_NAME))
                log(LANG["PHP ZIP file deleted successfully"])

            except Exception as PHPDownloadError:
                log(space(LANG["Error downloading PHP because of:"], right=True) + str(PHPDownloadError))
        else:
            log(LANG["PHP version not found or unsupported for your platform"])


def create_php_server():
    try:
        global PHP_SERVER
        global PHP_SERVER_THREAD
        global PHP_SERVER_RUNNING

        start_time = time.time()

        try:
            if not os.path.exists(PHP_EXECUTABLE) or not os.listdir(PHP_BINARIES):
                log(LANG["PHP executable not found so it will be downloaded automatically"])
                response = pymsgbox.confirm(
                    LANG["PHP executable was not found. Do you want to install PHP automatically?"],
                    LANG["PHP Not Found"],
                    buttons=[pymsgbox.YES_TEXT, pymsgbox.NO_TEXT]
                )
                log(space(LANG["User response:"], right=True) + str(response))
                if response == pymsgbox.YES_TEXT:
                    log(LANG["User selected to install PHP automatically"])
                    user_bitNess = check_user_bitNess()
                    log(space(LANG["User bitNess:"], right=True) + str(user_bitNess))
                    if user_bitNess:
                        log(LANG["64bit detected so we will download the 64bit version of PHP"])
                        choices = []
                        for key in PHP_DOWNLOAD_URL_64:
                            choices.append(key)

                        selected_option = easygui.choicebox(LANG["Select an option:"],
                                                            LANG["Select PHP version to download"],
                                                            choices=choices)
                        log(LANG["User selected option:"] + str(selected_option))
                        splash_screen = splash(SPLASH_SCREEN["splash_loader_name"])
                        download_php(selected_option)
                        rewrite_php_ini()
                        splash_screen.close()
                        if not os.path.exists(LARAVEL_ROOT) or not os.path.exists(LARAVEL_PUBLIC):
                            log(LANG[
                                    "Currently there is no Laravel project in the current directory, we will ask the user to create one"])
                            ask_to_create_laravel_project = pymsgbox.confirm(
                                LANG[
                                    "Current directory does not contain a Laravel project. Do you want to create one?"],
                                LANG["Laravel Project Not Found"],
                                buttons=[pymsgbox.YES_TEXT, pymsgbox.NO_TEXT]
                            )
                            if ask_to_create_laravel_project == pymsgbox.YES_TEXT:
                                splash_screen = splash(SPLASH_SCREEN["splash_loader_name"])
                                create_laravel_project()
                                splash_screen.close()
                                PHP_SERVER = subprocess.Popen([PHP_EXECUTABLE, "-S", SERVER_HOST,
                                                               "-t", LARAVEL_PUBLIC],
                                                              stdout=subprocess.PIPE,
                                                              stderr=subprocess.PIPE,
                                                              creationflags=subprocess.CREATE_NO_WINDOW)
                                PHP_SERVER_RUNNING = True
                            else:
                                log(LANG["User cancelled the creation of Laravel project"])
                                create_fallback_php_file()
                                PHP_SERVER = subprocess.Popen(
                                    [PHP_EXECUTABLE, "-S", SERVER_HOST,
                                     "-t", SCRIPT_DIRECTORY, FALLBACK_FILE_NAME],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
                                PHP_SERVER_RUNNING = True

                        else:
                            PHP_SERVER = subprocess.Popen([PHP_EXECUTABLE, "-S", SERVER_HOST,
                                                           "-t", LARAVEL_PUBLIC],
                                                          stdout=subprocess.PIPE,
                                                          stderr=subprocess.PIPE,
                                                          creationflags=subprocess.CREATE_NO_WINDOW)
                            PHP_SERVER_RUNNING = True
                    else:
                        log(LANG["32bit detected so we will download the 32bit version of PHP"])
                        choices = []
                        for key in PHP_DOWNLOAD_URL_32:
                            choices.append(key)
                        selected_option = easygui.choicebox(LANG["Select an option:"],
                                                            LANG["Select PHP version to download"],
                                                            choices=choices)
                        log(LANG["User selected option:"] + str(selected_option))
                        splash_screen = splash(SPLASH_SCREEN["splash_loader_name"])
                        download_php(selected_option)
                        rewrite_php_ini()
                        splash_screen.close()
                        if not os.path.exists(LARAVEL_ROOT) or not os.path.exists(LARAVEL_PUBLIC):
                            log(LANG[
                                    "Currently there is no Laravel project in the current directory, we will ask the user to create one"])
                            ask_to_create_laravel_project = pymsgbox.confirm(
                                LANG[
                                    "Current directory does not contain a Laravel project. Do you want to create one?"],
                                LANG["Laravel Project Not Found"],
                                buttons=[pymsgbox.YES_TEXT, pymsgbox.NO_TEXT]
                            )
                            if ask_to_create_laravel_project == pymsgbox.YES_TEXT:
                                splash_screen = splash(SPLASH_SCREEN["splash_loader_name"])
                                create_laravel_project()
                                splash_screen.close()
                                PHP_SERVER = subprocess.Popen([PHP_EXECUTABLE, "-S", SERVER_HOST,
                                                               "-t", LARAVEL_PUBLIC],
                                                              stdout=subprocess.PIPE,
                                                              stderr=subprocess.PIPE,
                                                              creationflags=subprocess.CREATE_NO_WINDOW)
                                PHP_SERVER_RUNNING = True
                            else:
                                log(LANG["User cancelled the creation of Laravel project"])
                                create_fallback_php_file()
                                PHP_SERVER = subprocess.Popen(
                                    [PHP_EXECUTABLE, "-S", SERVER_HOST,
                                     "-t", SCRIPT_DIRECTORY, FALLBACK_FILE_NAME],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    creationflags=subprocess.CREATE_NO_WINDOW)
                                PHP_SERVER_RUNNING = True

                        else:
                            PHP_SERVER = subprocess.Popen([PHP_EXECUTABLE, "-S", SERVER_HOST,
                                                           "-t", LARAVEL_PUBLIC],
                                                          stdout=subprocess.PIPE,
                                                          stderr=subprocess.PIPE,
                                                          creationflags=subprocess.CREATE_NO_WINDOW)
                            PHP_SERVER_RUNNING = True

                else:
                    log(LANG["User cancelled the installation of PHP"])
                    sys.exit(1)

            elif not os.path.exists(LARAVEL_ROOT) or not os.path.exists(LARAVEL_PUBLIC):
                log(LANG[
                        "Currently there is no Laravel project in the current directory, we will ask the user to create one"])
                ask_to_create_laravel_project = pymsgbox.confirm(
                    LANG["Current directory does not contain a Laravel project. Do you want to create one?"],
                    LANG["Laravel Project Not Found"],
                    buttons=[pymsgbox.YES_TEXT, pymsgbox.NO_TEXT]
                )
                if ask_to_create_laravel_project == pymsgbox.YES_TEXT:
                    splash_screen = splash(SPLASH_SCREEN["splash_loader_name"])
                    create_laravel_project()
                    splash_screen.close()
                    PHP_SERVER = subprocess.Popen([PHP_EXECUTABLE, "-S", SERVER_HOST,
                                                   "-t", LARAVEL_PUBLIC],
                                                  stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE,
                                                  creationflags=subprocess.CREATE_NO_WINDOW)
                    PHP_SERVER_RUNNING = True
                else:
                    log(LANG["User cancelled the creation of Laravel project"])
                    create_fallback_php_file()
                    PHP_SERVER = subprocess.Popen(
                        [PHP_EXECUTABLE, "-S", SERVER_HOST,
                         "-t", SCRIPT_DIRECTORY, FALLBACK_FILE_NAME],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        creationflags=subprocess.CREATE_NO_WINDOW)
                    PHP_SERVER_RUNNING = True

            else:
                PHP_SERVER = subprocess.Popen([PHP_EXECUTABLE, "-S", SERVER_HOST,
                                               "-t", LARAVEL_PUBLIC],
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              creationflags=subprocess.CREATE_NO_WINDOW)
                PHP_SERVER_RUNNING = True

        except Exception as ServerStartingError:
            log(LANG["Error starting PHP server:"] + str(ServerStartingError))
            PHP_SERVER_RUNNING = False

        end_time = time.time()

        final_time = (end_time - start_time) * 1000

        if final_time > 1000:
            log(space(LANG["PHP server started at"], right=True) +
                "[" + SERVER_URL + "]" + space(LANG["in"], both=True) +
                str("[" + str(final_time / 1000) + "]") +
                space(LANG["seconds"], left=True))
        else:
            log(space(LANG["PHP server started at"], right=True) +
                "[" + SERVER_URL + "]" + space(LANG["in"], both=True) +
                str("[" + str(final_time) + "]") +
                space(LANG["milliseconds"], left=True))

        App = QApplication(sys.argv + ['--webEngineArgs', '--remote-debugging-port=0.0.0.0'])
        window = MyApp(SERVER_URL)
        window.show()
        sys.exit(App.exec())

    except Exception as ApplicationStartingError:
        log(space(LANG["Error starting application:"], right=True) + str(ApplicationStartingError))


def stop_php_server():
    try:
        global PHP_SERVER
        global PHP_SERVER_THREAD
        global PHP_SERVER_RUNNING

        if PHP_SERVER_RUNNING:
            PHP_SERVER.terminate()
            PHP_SERVER_THREAD.join()
            PHP_SERVER_RUNNING = False

            log(space(LANG["PHP server stopped at"], right=True) + "[" + SERVER_URL + "] " + "in " + str(
                "[" + str(time.time()) + "]") + space(LANG["seconds"], left=True))

    except Exception as ServerStoppingError:
        log(space(LANG["Error stopping PHP server:"], right=True) + str(ServerStoppingError))


class DeveloperTools(QWebEngineView):
    def __init__(self, parent=None):
        super(DeveloperTools, self).__init__(parent)
        self.setPage(MyWebEnginePage(self))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setUrl(QUrl(""))

    def contextMenuEvent(self, event):
        pass


class MyWebEnginePage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if level == QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel:
            log(message + " (Line " + str(lineNumber) + " in " + sourceID + ")" + "\n")
        elif level == QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel:
            log(message + " (Line " + str(lineNumber) + " in " + sourceID + ")" + "\n")
        elif level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            log(message + " (Line " + str(lineNumber) + " in " + sourceID + ")" + "\n")


def closeCGI():
    try:
        check_cgi = subprocess.Popen(["tasklist", "/FI", "IMAGENAME eq php-cgi.exe"],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     creationflags=subprocess.CREATE_NO_WINDOW
                                     )
        check_cgi.communicate()

        if check_cgi.returncode == 0:
            log(LANG["PHP CGI process found so we will kill it"])
            kill_cgi = subprocess.Popen(["taskkill", "/F", "/IM", "php-cgi.exe"],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        creationflags=subprocess.CREATE_NO_WINDOW
                                        )
            kill_cgi.communicate()
            log(LANG["PHP CGI process killed successfully"])

        else:
            log(LANG["PHP CGI process not found"])

    except Exception as CGIProcessError:
        log(space(LANG["Error killing PHP CGI process:"], right=True) + str(CGIProcessError))


class MyApp(QMainWindow):
    cleanup_signal = pyqtSignal()

    def __init__(self, server_url):
        super().__init__()

        # global variables
        self.settings = QWebEngineSettings
        self.server_url = server_url
        self.webview = QWebEngineView(self)

        self.webview.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

        self.setCentralWidget(self.webview)

        # Connect the window's close event to the cleanup signal
        self.closing = False
        self.cleanup_signal.connect(self.perform_cleanup)

        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies)

        self.profileSettings = self.profile.settings()
        self.profileSettings.setAttribute(self.settings.WebAttribute.JavascriptCanOpenWindows, True)
        self.profileSettings.setAttribute(self.settings.WebAttribute.JavascriptCanAccessClipboard, True)
        self.profileSettings.setAttribute(self.settings.WebAttribute.LocalStorageEnabled, True)
        self.profileSettings.setAttribute(self.settings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.profileSettings.setAttribute(self.settings.WebAttribute.LocalContentCanAccessFileUrls, True)
        self.profileSettings.setAttribute(self.settings.WebAttribute.FullScreenSupportEnabled, True)
        self.profileSettings.setAttribute(self.settings.WebAttribute.AllowRunningInsecureContent, True)
        self.profileSettings.setAttribute(self.settings.WebAttribute.AllowWindowActivationFromJavaScript, True)
        self.profileSettings.setAttribute(self.settings.WebAttribute.AllowGeolocationOnInsecureOrigins, True)

        # initialize the UI
        splash_screen = splash(SPLASH_SCREEN["splash_name"])
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
            open(
                os.path.join(SCRIPT_DIRECTORY,
                             STYLESHEET['folder_name'],
                             STYLESHEET['stylesheet_name']), "r")
            .read())

        # Create a File menu
        file_menu = menubar.addMenu('Application')

        # Create an Edit menu
        edit_menu = menubar.addMenu('Edit')

        # Create a "Reload" action under the File menu
        reload_action = QAction('Reload', self)
        reload_action.setShortcut('Ctrl+R')

        reload_action.triggered.connect(self.reloadWebPage)
        file_menu.addAction(reload_action)

        # Create a "Copy" action under the Edit menu
        copy_action = QAction('Copy', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.copyText)
        edit_menu.addAction(copy_action)

        # Create a "Paste" action under the Edit menu
        paste_action = QAction('Paste', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.pasteText)
        edit_menu.addAction(paste_action)

        # Create a "Save Page As" action under the File menu
        save_as_action = QAction('Save Page As', self)
        save_as_action.setShortcut('Ctrl+S')
        save_as_action.triggered.connect(self.savePageAs)
        file_menu.addAction(save_as_action)

        # Create an "Exit" action under the File menu
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.exitApp)
        file_menu.addAction(exit_action)

        self.webview.page().runJavaScript(
            open(os.path.join(
                SCRIPT_DIRECTORY,
                PRERENDER_SCRIPT["folder_name"],
                PRERENDER_SCRIPT["script_name"]), "r")
            .read())

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
        stop_php_server()
        self.closing = True
        self.close()
        closeCGI()

    def closeEvent(self, event: QCloseEvent):
        result = pymsgbox.confirm(LANG["Are you sure you want to exit?"],
                                  LANG["Exit Application"],
                                  buttons=[pymsgbox.YES_TEXT, pymsgbox.NO_TEXT])
        if result == "Yes":
            self.exitApp()
            self.cleanup_signal.emit()
            event.accept()
            log(LANG["Application closed successfully by the user"])
        else:
            event.ignore()
            log(LANG["Application close cancelled by the user"])

    def perform_cleanup(self):
        stop_php_server()
        self.close()

    def javascript(self, command):
        self.webview.page().runJavaScript(command)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv + ['--webEngineArgs', '--remote-debugging-port=0.0.0.0'])
        create_php_server()
        SPLASH_SCREEN_VISIBLE.close()
        sys.exit(app.exec())

    except Exception as error:
        log(space(LANG["Error starting application:"], right=True) + str(error))
        sys.exit(1)
