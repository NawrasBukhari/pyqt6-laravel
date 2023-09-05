# PyQt6-Laravel

PyQt6-Laravel is a simple application that allows you to create a laravel project with a simple click. It is written in
python and uses PyQt6 for the GUI.

## Installation

You can install PyQt6-Laravel latest release
from [here](https://github.com/NawrasBukhari/pyqt6-laravel/releases/download/v0.2/pyqt6-laravel.rar).
you should have the following directory structure:

```
project
│   assets
│   config
│   logs
│   php
│   www
│   .gitignore
│   laravel-desktop.exe
│   main.py
│   README.md
|   requirements.txt
```

## Usage

You can run the application by double clicking on the `laravel-desktop.exe` file. It will ask for an admin permission to
run the application. After that, you will see the following window, at this point your are being asked to allow the
program to download PHP for you (recommended). If you choose to download PHP, you will be asked to choose a PHP version.
After that, you will be asked to choose a laravel version. Finally, you will be asked to choose a project name and a
project path. After that, the application will start downloading the required files and installing the dependencies.
After that, you will see the following window:
![image](https://github.com/NawrasBukhari/pyqt6-laravel/assets/63796900/fbd560dd-1087-4cfe-b22f-27e653e790b3)


At this point, you need to choose a PHP version which will be used later in your Laravel project.
![image](https://github.com/NawrasBukhari/pyqt6-laravel/assets/63796900/16c9a289-78ec-459b-9ba1-b46a84f9289d)


It will download it and replace the php.ini-development file with the custom php.ini file. which is located in
the `assets/stubs/php.ini.stub` directory.
![image](https://github.com/NawrasBukhari/pyqt6-laravel/assets/63796900/f71c0d11-349f-40d8-b9c0-d133c5c724f0)


Finally just rerun the application and it will start the server for you.

