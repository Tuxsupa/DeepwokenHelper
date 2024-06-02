import requests
import webbrowser
from packaging import version

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class UpdateChecker:
    def __init__(self, parent=None):
        self.parent = parent
        self.github = None
        
        self.settings = QSettings("Tuxsuper", "DeepwokenHelper")
        self.last_check_time = self.settings.value("last_check_time")
        
        with open("./assets/version.txt", 'r') as file:
            current_version = file.read() or "1.0"
        self.current_version = version.parse(current_version)

    def check_for_updates(self):
        current_time = QDateTime.currentDateTime()
        if self.last_check_time:
            elapsed_time = self.last_check_time.secsTo(current_time)

        if not self.last_check_time or elapsed_time >= 24 * 3600:
            response = requests.get("https://api.github.com/repos/Tuxsupa/DeepwokenHelper/releases/latest")
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
