from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from deepwokenhelper.gui.cards_area import Card
from deepwokenhelper.gui.control_panel import ControlPanel

from deepwokenhelper.ocr import DeepwokenOCR
from deepwokenhelper.data import DeepwokenData
from deepwokenhelper.version_check import *


class DeepwokenHelper(QMainWindow):
    loadingSignal = pyqtSignal(bool)
    errorSignal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.data: DeepwokenData = None
        self.active_tasks = 0
        self.mutex = QMutex()
        
        self.loadingSignal.connect(self.loading)
        self.errorSignal.connect(self.error_message)
        
        self.settings = QSettings("Tuxsuper", "DeepwokenHelper")
        self.read_settings()
        
        self.ocrThread = QThread()
        self.ocr = DeepwokenOCR(self)
        self.ocr.moveToThread(self.ocrThread)
        self.ocr.addCardsSignal.connect(self.add_cards)
        self.ocrThread.started.connect(self.ocr.start)
        self.ocrThread.start()
        
        self.updateChecker = UpdateChecker(self)
        self.updateChecker.update_available_signal.connect(self.show_update_window)
        self.updateChecker.start()
        
        self.main()
        
        self.stats.load_list_builds()

    def show_update_window(self):
        if self.updateChecker.github is None:
            self.updateChecker.github = UpdateWindow(self)
        self.updateChecker.github.show()
    
    
    class DataWorker(QThread):
        data_ready = pyqtSignal(object)
        
        def __init__(self, helper, buildId):
            super().__init__()
            self.helper = helper
            self.buildId = buildId

        def run(self):
            data = DeepwokenData(self.helper, self.buildId)
            self.data_ready.emit(data)


    def main(self):
        self.setWindowTitle("Deepwoken Helper")
        self.setWindowIcon(QIcon('./assets/icons/favicon.png'))
        
        self.setObjectName("MainWindow")
        self.setStyleSheet("#MainWindow { background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.8, fx:0.5, fy:0.5, stop:0 rgba(24, 34, 26, 255), stop:1 rgba(4, 16, 13, 255)); }")


        main = QWidget()
        self.setCentralWidget(main)

        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        cards = QWidget()
        cards.setObjectName("Cards")
        cards.setStyleSheet("#Cards { border-image: url(./assets/gui/border.png); border-width: 15px; border-style: outset; background-image: url(./assets/gui/background.png) repeat; background-origin: border-box; }")

        self.cards_layout = QVBoxLayout(cards)
        self.cards_layout.setContentsMargins(0, 0, 0, 0)

        self.stats = ControlPanel(self)
        self.stats.setObjectName("ControlPanel")
        self.stats.setStyleSheet("#ControlPanel { background-color: rgb(216, 215, 202); border-image: url(./assets/gui/border.png); border-width: 15px; }")
        self.stats.setAttribute(Qt.WidgetAttribute.WA_StyledBackground)
        
        main_layout.addWidget(cards, 15)
        main_layout.addWidget(self.stats, 5)

    def write_settings(self):
        self.settings.setValue("geometry", self.saveGeometry())

    def read_settings(self):
        self.restoreGeometry(self.settings.value("geometry", QByteArray()))

    def closeEvent(self, event):
        self.write_settings()
        
        super().closeEvent(event)

    def clear_layout(self, layout: QBoxLayout):
        for i in reversed(range(layout.count())):
            layout.itemAt(i).widget().deleteLater()

    @pyqtSlot(list)
    def add_cards(self, cards):
        self.clear_layout(self.cards_layout)

        for data in cards:
            label_widget = Card(self.ocr, data)
            self.cards_layout.addWidget(label_widget, 1)
    
    @pyqtSlot(bool)
    def loading(self, isStart):
        self.mutex.lock()
        
        if isStart:
            self.active_tasks += 1
            if self.active_tasks == 1:
                self.stats.spinner.start()
        else:
            self.active_tasks -= 1
            if self.active_tasks == 0:
                self.stats.spinner.stop()
                
        self.mutex.unlock()

    @pyqtSlot(str)
    def error_message(self, message):
        QMessageBox.warning(
            self,
            "Error",
            message,
            buttons=QMessageBox.StandardButton.Close,
            defaultButton=QMessageBox.StandardButton.Close,
        )
