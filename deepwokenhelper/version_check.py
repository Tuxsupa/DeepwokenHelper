import re
import os
import sys
import toml
import requests
import webbrowser
from packaging import version

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

import deepwokenhelper


class UpdateChecker:
    def __init__(self, parent=None):
        self.parent = parent
        self.github = None
        
        self.settings = QSettings("Tuxsuper", "DeepwokenHelper")
        self.last_check_time = self.settings.value("last_check_time")
        self.current_version = version.parse(deepwokenhelper.__version__)

    def check_for_updates(self):
        current_time = QDateTime.currentDateTime()
        if self.last_check_time:
            elapsed_time = self.last_check_time.secsTo(current_time)

        if not self.last_check_time or elapsed_time >= 24 * 3600:
            response = requests.get("https://api.github.com/repos/Tuxsupa/DeepwokenHelper/releases/latest", timeout=10)
            latest_release = response.json()

            if latest_release:
                self.settings.setValue("last_check_time", current_time)

                new_version = latest_release.get("name", "v1.0")
                new_version = version.parse(new_version)
                if new_version > self.current_version:
                    if self.github is None:
                        self.github = UpdateWindow(self.parent)
                    self.github.show()
                    
                    # github = UpdateWindow(self.parent)
                    # github.exec()
    

class UpdateWindow(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.settings = QSettings("Tuxsuper", "DeepwokenHelper")
        
        self.setWindowTitle("New Release")
        self.setText("A new update is available. Do you want to update?")

        pixmap = QIcon("./assets/gui/github-black.png")
        self.setIconPixmap(pixmap.pixmap(QSize(30, 30)))

        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        self.accepted.connect(self.accept)
        self.rejected.connect(self.reject)

    def accept(self):
        url = "https://github.com/Tuxsupa/DeepwokenHelper/releases/latest"
        webbrowser.open(url)
        self.close()

    def reject(self):
        self.close()


class VersionChanger():
    def __init__(self):
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            return
        
        if self.same_version():
            return
        
        self.update_pyproject()
        self.update_iss()

    def same_version(self):
        if not os.path.exists('pyproject.toml'):
            return
        
        with open("pyproject.toml", 'r') as f:
            pyproject_data = toml.load(f)

        return pyproject_data['tool']['poetry']['version'] == deepwokenhelper.__version__
    
    def update_pyproject(self):
        if not os.path.exists('pyproject.toml'):
            return
        
        with open("pyproject.toml", 'r') as f:
            pyproject_data = toml.load(f)

        pyproject_data['tool']['poetry']['version'] = deepwokenhelper.__version__

        with open("pyproject.toml", 'w') as f:
            toml.dump(pyproject_data, f)
    
    def update_iss(self):
        if not os.path.exists('setup.iss'):
            return
        
        current_version = r'#define MyAppVersion\s+"[^"]+"'
        new_version = f'#define MyAppVersion "{deepwokenhelper.__version__}"'

        with open('setup.iss', 'r') as file:
            filedata = file.read()

        filedata = re.sub(current_version, new_version, filedata)

        with open('setup.iss', 'w') as file:
            file.write(filedata)
