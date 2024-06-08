from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from deepwokenhelper.ocr import DeepwokenOCR


class Tooltip(QFrame):
    def __init__(self, data: dict):
        super().__init__()
        
        self.data = data
        self.has_tooltip = False
        
        self.setFixedWidth(200)
        
        self.setObjectName("Tooltip")
        self.setStyleSheet("#Tooltip { background-color: rgb(229, 224, 203); border-image: url(./assets/gui/border.png); border-width: 15px; }") #padding: 15px 5px 5px 5px; 
        self.setWindowFlags(Qt.WindowType.ToolTip)
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        
        self.hide()
        
    def card_tooltip(self):
        self.has_tooltip = True
        
        tags = QWidget()
        tags_layout = QGridLayout(tags)
        tags_layout.setContentsMargins(0, 0, 0, 0)
        
        if self.data.get('reqs'):
            if int(self.data["reqs"]["power"]) > 0:
                label = QLabel(f"<b>Power</b>: {self.data['reqs']['power']}")
                tags_layout.addWidget(label)
                
            for statName, statAmount in self.data["reqs"]["base"].items():
                if statAmount != 0:
                    label = QLabel(f"<b>{statName}</b>: {statAmount}")
                    tags_layout.addWidget(label)
            
            if self.data["reqs"]["weapon"]:
                for statName, statAmount in self.data["reqs"]["weapon"].items():
                    if statAmount != 0:
                        label = QLabel(f"<b>{statName}</b>: {statAmount}")
                        tags_layout.addWidget(label)
            
            for statName, statAmount in self.data["reqs"]["attunement"].items():
                if statAmount != 0:
                    label = QLabel(f"<b>{statName}</b>: {statAmount}")
                    tags_layout.addWidget(label)

        if self.data.get('diffReqs'):
            for idx, (statName, statAmount)in enumerate(self.data["diffReqs"].items()):
                    if statAmount != 0:
                        suffix = " <b>OR</b> " if idx+1 < len(self.data["diffReqs"]) else ""
                        label = QLabel(f"<b>{statName}</b>: {statAmount}{suffix}")
                        tags_layout.addWidget(label)

        self.main_layout.addWidget(tags)
        tags.setFixedWidth(200 - 36)
        
        desc_label = QLabel(self.data.get("desc"))
        desc_label.setWordWrap(True)
        desc_label.adjustSize()
        self.main_layout.addWidget(desc_label)
        
        desc_label.setFixedWidth(200 - 36)

    def exclusive_tooltip(self, ocr: DeepwokenOCR):
        self.has_tooltip = True

        type_cards = ocr.get_type_card()

        for exclusive in self.data["exclusiveWith"]:
            if not exclusive:
                continue

            data_exclusive = type_cards[exclusive.lower()]

            locked = QWidget()
            locked_layout = QHBoxLayout(locked)
            locked_layout.setContentsMargins(0, 0, 0, 0)

            icon_name = "locked_important" if data_exclusive["taken"] else "locked"
            lock_taken_icon = QLabel()
            lock_taken_icon.setMouseTracking(True)

            pixmap = QPixmap(f"./assets/gui/{icon_name}.png")
            pixmap = pixmap.scaledToWidth(20)
            lock_taken_icon.setPixmap(pixmap)
            locked_layout.addWidget(lock_taken_icon)

            lock_taken_label = QLabel(f"<b>{data_exclusive['name']}</b>:")
            lock_taken_label.setMouseTracking(True)

            locked_layout.addWidget(lock_taken_label, 1)

            self.main_layout.addWidget(locked)
            locked.setFixedWidth(200 - 36)

            desc_label = QLabel(data_exclusive.get("desc"))
            desc_label.setWordWrap(True)
            desc_label.adjustSize()

            self.main_layout.addWidget(desc_label)
            desc_label.setFixedWidth(200 - 36)
    
    def for_tooltip(self, ocr: DeepwokenOCR):
        self.has_tooltip = True

        type_cards = ocr.get_type_card()

        for forTaken in self.data["forTaken"]:
            data_forTaken = type_cards[forTaken.lower()]

            titles = QWidget()
            titles_layout = QHBoxLayout(titles)
            titles_layout.setContentsMargins(0, 0, 0, 0)

            icon_name = "important_shrine" if data_forTaken["shrine"] else "important"
            icon = QLabel()
            icon.setMouseTracking(True)
            pixmap = QPixmap(f"./assets/gui/{icon_name}.png")
            pixmap = pixmap.scaledToWidth(20)
            icon.setPixmap(pixmap)
            titles_layout.addWidget(icon)

            title_label = QLabel(f"<b>{forTaken}</b>:")
            titles_layout.addWidget(title_label, 1)
            self.main_layout.addWidget(titles)
            titles.setFixedWidth(200 - 36)

            desc_label = QLabel(data_forTaken.get("desc"))
            desc_label.setWordWrap(True)
            desc_label.adjustSize()
            self.main_layout.addWidget(desc_label)
            desc_label.setFixedWidth(200 - 36)
            

    def show_tooltip(self, x, y):
        self.move(x, y)
        self.show()

    def hide_tooltip(self):
        self.hide()

    def move_tooltip(self, x, y):
        self.move(x, y)


class Card(QWidget):
    def __init__(self, ocr: DeepwokenOCR, data: dict):
        super().__init__()

        card_tooltip = Tooltip(data)
        card_tooltip.card_tooltip()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)


        label = QLabel(data.get("name", "???"))
        label.setMouseTracking(True)
        
        
        color = "255, 165, 0" if data.get("taken") else "255, 255, 255"
        label.setStyleSheet(f"color: rgb({color});")
        
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("Segoe UI", 12))
        label.setWordWrap(True)
        layout.addWidget(label, 7)

        label.enterEvent = lambda event: self.show_custom_tooltip(event, card_tooltip)
        label.mouseMoveEvent = lambda event: self.move_custom_tooltip(event, card_tooltip)
        label.leaveEvent = lambda event: self.hide_custom_tooltip(card_tooltip)


        icons = QWidget()
        icons.setMouseTracking(True)

        icons_layout = QVBoxLayout(icons)
        icons_layout.setContentsMargins(0, 0, 0, 0)
        
        icons_tooltip = Tooltip(data)
        
        icons_layout.addItem(QSpacerItem(0, 0, vPolicy=QSizePolicy.Policy.Expanding))

        if data.get("exclusiveWith") and any(data["exclusiveWith"]):
            icons_tooltip.exclusive_tooltip(ocr)
            
            locked_taken = False
            type_cards = ocr.get_type_card()

            for exclusive in data["exclusiveWith"]:
                if not exclusive:
                    continue
                
                data_exclusive = type_cards[exclusive.lower()]
                
                if data_exclusive["taken"]:
                    locked_taken = True
                    break


            locked_layout = QHBoxLayout()
            locked_layout.setContentsMargins(0, 0, 0, 0)
            
            exclusive_label = QLabel()
            exclusive_label.setMouseTracking(True)

            pixmap = QPixmap("./assets/gui/locked.png")
            pixmap = pixmap.scaledToWidth(20)
            exclusive_label.setPixmap(pixmap)
            locked_layout.addWidget(exclusive_label)
                
            if locked_taken:
                lock_new_label = QLabel()
                lock_new_label.setMouseTracking(True)

                pixmap = QPixmap("./assets/gui/locked_important.png")
                pixmap = pixmap.scaledToWidth(20)
                lock_new_label.setPixmap(pixmap)
                locked_layout.addWidget(lock_new_label, 1)
                
            icons_layout.addLayout(locked_layout)


        if data.get("shrine"):
            shrine_label = QLabel()
            shrine_label.setMouseTracking(True)

            pixmap = QPixmap("./assets/gui/shrine.png")
            pixmap = pixmap.scaledToWidth(20)
            shrine_label.setPixmap(pixmap)
            icons_layout.addWidget(shrine_label)

        if data.get("forTaken"):
            icons_tooltip.for_tooltip(ocr)
            
            forTaken_layout = QHBoxLayout()
            forTaken_layout.setContentsMargins(0, 0, 0, 0)
            
            forTaken_label = QLabel()
            forTaken_label.setMouseTracking(True)

            pixmap = QPixmap("./assets/gui/important.png")
            pixmap = pixmap.scaledToWidth(20)
            forTaken_label.setPixmap(pixmap)
            forTaken_layout.addWidget(forTaken_label)

            if data.get("shrineTaken"):
                shrineTaken_label = QLabel()
                shrineTaken_label.setMouseTracking(True)

                pixmap = QPixmap("./assets/gui/important_shrine.png")
                pixmap = pixmap.scaledToWidth(20)
                shrineTaken_label.setPixmap(pixmap)
                forTaken_layout.addWidget(shrineTaken_label, 1)
            
            icons_layout.addLayout(forTaken_layout)


        if icons_tooltip.has_tooltip:
            icons.enterEvent = lambda event: self.show_custom_tooltip(event, icons_tooltip)
            icons.mouseMoveEvent = lambda event: self.move_custom_tooltip(event, icons_tooltip)
            icons.leaveEvent = lambda event: self.hide_custom_tooltip(icons_tooltip)


        icons_layout.addItem(QSpacerItem(0, 0, vPolicy=QSizePolicy.Policy.Expanding))

        layout.addWidget(icons, 3)
        self.setLayout(layout)

    def show_custom_tooltip(self, event: QEnterEvent, tooltip: Tooltip):
        tooltip.show_tooltip(event.globalPosition().toPoint().x() + 15, event.globalPosition().toPoint().y())

    def move_custom_tooltip(self, event: QMouseEvent, tooltip: Tooltip):
        tooltip.move_tooltip(event.globalPosition().toPoint().x() + 15, event.globalPosition().toPoint().y())

    def hide_custom_tooltip(self, tooltip: Tooltip):
        tooltip.hide_tooltip()
