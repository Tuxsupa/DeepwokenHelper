import os
import sys
from datetime import datetime, timezone
from multiprocessing import freeze_support

import logging
from logging import FileHandler

from PyQt6.QtWidgets import QApplication

import deepwokenhelper
from deepwokenhelper.gui.application import DeepwokenHelper


freeze_support()

LOG_FOLDER = "logs"
MAX_FOLDER_SIZE_MB = 50
MAX_LOG_FILES = 25

os.makedirs(LOG_FOLDER, exist_ok=True)
log_filename = os.path.join(LOG_FOLDER, f"DeepwokenHelper-{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H_%M_%S_%fZ")}.log")

logger = logging.getLogger("helper")
logger.setLevel(logging.DEBUG)

file_handler = FileHandler(log_filename, mode="w")
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(console_handler)

def get_folder_size(folder):
    """Get the total size of a folder in bytes."""
    return sum(os.path.getsize(os.path.join(folder, f)) for f in os.listdir(folder))

def cleanup_logs():
    """Delete oldest log files until constraints are met."""
    log_files = sorted(
        [os.path.join(LOG_FOLDER, f) for f in os.listdir(LOG_FOLDER) if f.endswith(".log")],
        key=os.path.getctime
    )

    while len(log_files) > MAX_LOG_FILES:
        os.remove(log_files.pop(0))

    while (get_folder_size(LOG_FOLDER) / (1024 * 1024)) > MAX_FOLDER_SIZE_MB and log_files:
        os.remove(log_files.pop(0))

cleanup_logs()

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception


logger.info(f"DeepwokenHelper - Version {deepwokenhelper.__version__} - Starting...")

app = QApplication(sys.argv)
mainWindow = DeepwokenHelper()
mainWindow.show()
sys.exit(app.exec())