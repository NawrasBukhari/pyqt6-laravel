"""
DESKTOP_APP_NAME: The name of the application.
ANIMATED: Whether the application should be animated or not.
DEBUG: Whether the application should be in debug mode or not.
PHP_BIN_DIRECTORY_NAME: The name of the PHP binary directory.
PHP_EXECUTABLE_NAME: The name of the PHP executable.
LARAVEL_PROJECT_DIRECTORY_NAME: The name of the Laravel project directory.
LARAVEL_PUBLIC_DIRECTORY_NAME: The name of the Laravel public directory.
FALLBACK_FILE_NAME: The name of the fallback file.
"""

DESKTOP_APP_NAME = "Laravel Desktop"
ANIMATED = True
DEBUG = True
PHP_BIN_DIRECTORY_NAME = "php"
PHP_EXECUTABLE_NAME = "php.exe"
LARAVEL_PROJECT_DIRECTORY_NAME = "www"
LARAVEL_PUBLIC_DIRECTORY_NAME = "public"
FALLBACK_FILE_NAME = "default.php"

"""
ICON: The icon of the application.
PRERENDER_SCRIPT: The script that will be executed before the page is loaded.
STYLESHEET: The stylesheet of the application.
LOGS: The logs of the application.
SPLASH_SCREEN: The splash screen of the application.
"""

ICON = {
    "folder_name": "assets/icons",
    "icon_name": "icon.ico",
}

PRERENDER_SCRIPT = {
    "folder_name": "assets/js",
    "script_name": "prerender.js"
}

STYLESHEET = {
    "folder_name": "assets/css",
    "stylesheet_name": "style.css",
}

LOGS = {
    "folder_name": "logs",
    "log_file_name": "laravel-desktop.log",
}

SPLASH_SCREEN = {
    "folder_name": "assets/splash",
    "splash_name": "splash.png",
    'splash_time': 2.5
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
