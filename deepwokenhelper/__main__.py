import sys
from multiprocessing import freeze_support

from PyQt6.QtWidgets import QApplication

from deepwokenhelper.gui.application import DeepwokenHelper

freeze_support()
app = QApplication(sys.argv)
mainWindow = DeepwokenHelper()
mainWindow.show()
sys.exit(app.exec())