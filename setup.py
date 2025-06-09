from setuptools import setup
import os
import sys

os.environ['CODESIGNING_ALLOWED'] = "NO"

APP = ['habitTracker.py']
ICON_FILE = 'habitTrackerIcon.icns'

DATA_FILES = [ICON_FILE]

OPTIONS = {
    'argv_emulation': False,
    'iconfile': ICON_FILE,
    'plist': {
        'CFBundleName': 'Habit Tracker',
        'CFBundleDisplayName': 'Habit Tracker',
        'CFBundleIdentifier': 'com.yourcompany.habittracker',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': '© 2025 Your Name',
        'LSApplicationCategoryType': 'public.app-category.utilities',
    },
    'packages': ['PyQt6'],
    'includes': [
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'sys',
        'os',
        'json',
    ],
    'qt_plugins': [
        'platforms',
        'imageformats',
        'styles',
    ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)