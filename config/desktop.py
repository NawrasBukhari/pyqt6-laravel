"""
DEBUG: Whether the application should be in debug mode or not.
DESKTOP_APP_NAME: The name of the application.
ANIMATED: Whether the application should be animated or not.
PHP_BIN_DIRECTORY_NAME: The name of the PHP binary directory.
PHP_EXECUTABLE_NAME: The name of the PHP executable.
LARAVEL_PROJECT_DIRECTORY_NAME: The name of the Laravel project directory.
LARAVEL_PUBLIC_DIRECTORY_NAME: The name of the Laravel public directory.
FALLBACK_FILE_NAME: The name of the fallback file.
"""
DEBUG = True
DESKTOP_APP_NAME = "Laravel Desktop"
ANIMATED = True
PHP_BIN_DIRECTORY_NAME = "php"
PHP_EXECUTABLE_NAME = "php.exe"
LARAVEL_PROJECT_DIRECTORY_NAME = "www"
LARAVEL_PUBLIC_DIRECTORY_NAME = "public"
COMPOSER_EXECUTABLE_NAME = "composer.phar"
FALLBACK_FILE_NAME = "default.php"

"""
ICON: The icon of the application.
PRERENDER_SCRIPT: The script that will be executed before the page is loaded.
STYLESHEET: The stylesheet of the application.
LOGS: The logs of the application.
SPLASH_SCREEN: The splash screen of the application.
"""

ICON = {
    "folder_name": "assets\\icons",
    "icon_name": "icon.ico",
}

PRERENDER_SCRIPT = {
    "folder_name": "assets\\js",
    "script_name": "prerender.js"
}

STYLESHEET = {
    "folder_name": "assets\\css",
    "stylesheet_name": "style.css",
}

LOGS = {
    "folder_name": "logs",
    "log_file_name": "laravel-desktop.log",
}

SPLASH_SCREEN = {
    "folder_name": "assets\\splash",
    "splash_name": "splash.png",
    "splash_loader_name": "loader.gif",
    "splash_time": 2.5
}

CACERT_PEM = {
    "folder_name": "assets\\ssl",
    "cacert_pem_name": "cacert.pem",
}

# ---------------------------------------------------------------------------

"""
X_COORDINATE: The x-coordinate of the window.
Y_COORDINATE: The y-coordinate of the window.
WIDTH: The width of the window.
HEIGHT: The height of the window.
MIN_WIDTH: The minimum width of the window.
MIN_HEIGHT: The minimum height of the window.
MAX_WIDTH: The maximum width of the window.
MAX_HEIGHT: The maximum height of the window.
SET_MAXIMIZED: Whether the window should be maximized or not.
ZOOM_FACTOR: The zoom factor of the window.
"""
X_COORDINATE = 100
Y_COORDINATE = 100
WIDTH = 800
HEIGHT = 600
MIN_WIDTH = 800
MIN_HEIGHT = 600
MAX_WIDTH = 1000
MAX_HEIGHT = 800
ZOOM_FACTOR = 1.0
SET_MAXIMIZED = True
# ---------------------------------------------------------------------------

"""
LEFT_MARGIN: The left margin of the window.
TOP_MARGIN: The top margin of the window.
RIGHT_MARGIN: The right margin of the window.
BOTTOM_MARGIN: The bottom margin of the window.
"""
LEFT_MARGIN = 0
TOP_MARGIN = 0
RIGHT_MARGIN = 0
BOTTOM_MARGIN = 0
# ---------------------------------------------------------------------------
"""
PHP_DOWNLOAD_URL_64: The download URL of the PHP 64-bit version.
PHP_DOWNLOAD_URL_32: The download URL of the PHP 32-bit version.
PHP_INI_STUB: The stub of the PHP ini file.
PHP_INI_FILENAME: The name of the PHP ini file.
PHP_INI_FILENAME_FRESH_INSTALL: The name of the newly downloaded PHP ini file.
TEMP: The temporary folder.
"""
PHP_DOWNLOAD_URL_64 = {
    "7.4": "https://windows.php.net/downloads/releases/php-7.4.33-nts-Win32-vc15-x64.zip",
    "8.0": "https://windows.php.net/downloads/releases/php-8.0.30-nts-Win32-vs16-x64.zip",
    "8.1": "https://windows.php.net/downloads/releases/php-8.1.23-nts-Win32-vs16-x86.zip",
    "8.2": "https://windows.php.net/downloads/releases/php-8.2.10-nts-Win32-vs16-x64.zip",
}

PHP_DOWNLOAD_URL_32 = {
    "7.4": "https://windows.php.net/downloads/releases/php-7.4.33-nts-Win32-vc15-x86.zip",
    "8.0": "https://windows.php.net/downloads/releases/php-8.0.30-Win32-vs16-x86.zip",
    "8.1": "https://windows.php.net/downloads/releases/php-8.1.23-nts-Win32-vs16-x86.zip",
    "8.2": "https://windows.php.net/downloads/releases/php-8.2.10-nts-Win32-vs16-x86.zip",
}

COMPOSER_DOWNLOAD_URL = "https://getcomposer.org/installer"
COMPOSER_SETUP_FILE = "composer-setup.php"

PHP_INI_STUB = {
    "folder_name": "assets\\stubs",
    "stub_name": "php.ini.stub",
}

PHP_INI_FILENAME = "php.ini"
PHP_INI_FILENAME_FRESH_INSTALL = "php.ini-development"

TEMP = {
    "folder_name": "assets\\temp",
}

