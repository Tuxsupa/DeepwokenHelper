import logging
import sys
from multiprocessing import freeze_support

from PyQt6.QtWidgets import QApplication

import deepwokenhelper
from deepwokenhelper.gui.application import DeepwokenHelper
from deepwokenhelper.logging import cleanup_logs, init_logging

logger = logging.getLogger("helper")


freeze_support()

init_logging()
cleanup_logs()


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


logger.info(f"DeepwokenHelper - Version {deepwokenhelper.__version__} - Starting...")

app = QApplication(sys.argv)
# app.setStyle("Fusion")
mainWindow = DeepwokenHelper()
mainWindow.show()
sys.exit(app.exec())
