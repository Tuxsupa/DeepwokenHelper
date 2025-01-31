import requests
import webbrowser
from packaging import version

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

import deepwokenhelper

import logging
logger = logging.getLogger("helper")


class UpdateChecker(QThread):
    update_available_signal = pyqtSignal()
    
    def __init__(self, helper=None):
        super().__init__()
        from deepwokenhelper.gui.application import DeepwokenHelper
        self.helper: DeepwokenHelper = helper
        self.github = None
        
        self.settings = self.helper.settings
        self.last_check_time = self.settings.value("last_check_time")
        self.current_version = version.parse(deepwokenhelper.__version__)

    def run(self):
        logger.info("Checking for new updates...")
        self.helper.loadingSignal.emit(True)
        
        current_time = QDateTime.currentDateTime()
        if self.last_check_time:
            elapsed_time = self.last_check_time.secsTo(current_time)

        if not self.last_check_time or elapsed_time >= 24 * 3600:
            try:
                response = requests.get("https://api.github.com/repos/Tuxsupa/DeepwokenHelper/releases/latest", timeout=10)
                latest_release = response.json()

                if latest_release:
                    self.settings.setValue("last_check_time", current_time)

                    new_version = latest_release.get("name", "v1.0")
                    new_version = version.parse(new_version)

                    if new_version > self.current_version:
                        logger.info("New version available")
                        self.update_available_signal.emit()

            except requests.exceptions.RequestException as e:
                logger.error(f"Error checking for updates: {e}")
                self.helper.errorSignal.emit("Error checking for updates.\nPlease check your internet connection")
    
        self.helper.loadingSignal.emit(False)


class UpdateWindow(QMessageBox):
    def __init__(self, helper=None):
        super().__init__(helper)
        
        self.setWindowTitle("New Release")
        self.setText("A new update is available. Do you want to update?")

        pixmap = QIcon("./assets/gui/github-black.png")
        self.setIconPixmap(pixmap.pixmap(QSize(30, 30)))

        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        self.accepted.connect(self.accept)
        self.rejected.connect(self.reject)

    def accept(self):
        logger.info("Opening github update link...")
        url = "https://github.com/Tuxsupa/DeepwokenHelper/releases/latest"
        webbrowser.open(url)
        self.close()

    def reject(self):
        self.close()
