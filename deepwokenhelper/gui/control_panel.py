import re
import webbrowser

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from waitingspinnerwidget import QtWaitingSpinner

import deepwokenhelper
from deepwokenhelper.data import DeepwokenData

import logging
logger = logging.getLogger("helper")


class ControlPanel(QWidget):
    def __init__(self, helper):
        super().__init__()
        
        from deepwokenhelper.gui.application import DeepwokenHelper
        self.helper: DeepwokenHelper = helper
        self.info = None
        self.settings = None
        self.isAdding = False
        
        main_layout = QVBoxLayout(self)
        
        layout = QHBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)

        self.traits_widget = self.traits()
        layout.addWidget(self.traits_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.builds_widget = self.builds()
        layout.addWidget(self.builds_widget, 5)
        
        buttons_widget = self.buttons()
        layout.addWidget(buttons_widget, 1)
        
        main_layout.addLayout(layout, 1)
        
        
        layout = QHBoxLayout()
        
        spinner = QtWaitingSpinner(self, False)
        spinner.setRoundness(0.0)
        spinner.setMinimumTrailOpacity(0.0)
        spinner.setTrailFadePercentage(70.0)
        spinner.setNumberOfLines(100)
        spinner.setLineLength(4)
        spinner.setLineWidth(5)
        spinner.setInnerRadius(6)
        spinner.setRevolutionsPerSecond(1)
        self.spinner = spinner
        
        spinner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout.addWidget(spinner, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        
        # layout.addItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Policy.Expanding))
        
        tag = QLabel(f"<b>v{deepwokenhelper.__version__} @Tuxsuper</b>")
        tag.setStyleSheet("color: #000000; font-size: 12px;")
        tag.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout.addWidget(tag, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        
        main_layout.addLayout(layout)
    
    def traits(self):
        self.trait_values = {}
        
        traits_widget = QWidget()
        traits_layout = QVBoxLayout(traits_widget)
        traits_layout.setContentsMargins(10, 0, 20, 0)
        
        traits = {
            "Vitality": 0,
            "Erudition": 0,
            "Proficiency": 0,
            "Songchant": 0
        }
        
        for name, value in traits.items():
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 3, 0, 3)
            
            nameLabel = QLabel(name)
            nameLabel.setFixedWidth(100)
            nameLabel.setStyleSheet("font-size: 15px; font-weight: 600;")
            layout.addWidget(nameLabel)
            
            valueLabel = QLabel(str(value))
            valueLabel.setFixedWidth(40)
            valueLabel.setStyleSheet("background-color: transparent; border-radius: 5px; border: 1px solid rgba(0, 0, 0, .25); padding: 2px;")
            layout.addWidget(valueLabel)
            
            self.trait_values[name] = valueLabel
            traits_layout.addWidget(widget)
            
        return traits_widget

    def update_trait_value(self, new_traits=None):
        traits = {
            "Vitality": 0,
            "Erudition": 0,
            "Proficiency": 0,
            "Songchant": 0
        }
        if new_traits:
            traits.update(new_traits)
        
        for traitName, traitValue in traits.items():
            self.trait_values[traitName].setText(str(traitValue))

    def builds(self):
        build_widget = QWidget()
        build_layout = QVBoxLayout(build_widget)
        build_layout.setContentsMargins(0, 0, 10, 0)


        #Builds
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
    
        title = QLabel("Builds")
        title.setFixedWidth(80)
        title.setStyleSheet("font-size: 15px; font-weight: 600;")
        layout.addWidget(title, 1)
        
        self.comboBox = QComboBox()
        self.comboBox.setMinimumWidth(40)
        self.comboBox.setMaximumHeight(30)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setStyleSheet("""#comboBox { background-color: rgb(216, 215, 202);
                                border-radius: 5px;
                                border: 1px solid rgba(0, 0, 0, .25);
                                }

                                #comboBox QListView { background-color: rgb(216, 215, 202);
                                border-radius: 5px;
                                border: 1px solid rgba(0, 0, 0, .25);
                                }

                                #comboBox::drop-down {
                                    border: 0px;
                                }

                                #comboBox::down-arrow {
                                    image: url(./assets/gui/down-arrow.png);
                                    width: 12px;
                                    height: 12px;
                                }

                                #comboBox QListView {
                                    min-width: 250px;
                                }""")
        self.comboBox.setSizeAdjustPolicy(self.comboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        layout.addWidget(self.comboBox, 5)
        
        build_layout.addLayout(layout)


        #Build Name
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Build Name")
        title.setFixedWidth(80)
        title.setStyleSheet("font-size: 15px; font-weight: 600;")
        layout.addWidget(title, 1)

        self.buildName = QLabel()
        self.buildName.setMinimumWidth(40)
        self.buildName.setMaximumHeight(30)
        self.buildName.setStyleSheet("""background-color: transparent;
                                border-radius: 5px;
                                border: 1px solid rgba(0, 0, 0, .25);
                                padding: 2px;""")
        layout.addWidget(self.buildName, 5)

        build_layout.addLayout(layout)


        #Author
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
    
        title = QLabel("Author")
        title.setFixedWidth(80)
        title.setStyleSheet("font-size: 15px; font-weight: 600;")
        layout.addWidget(title, 1)
                
        self.buildAuthor = QLabel()
        self.buildAuthor.setMinimumWidth(40)
        self.buildAuthor.setMaximumHeight(30)
        self.buildAuthor.setStyleSheet("""background-color: transparent;
                                border-radius: 5px;
                                border: 1px solid rgba(0, 0, 0, .25);
                                padding: 2px;""")
        layout.addWidget(self.buildAuthor, 5)
        
        build_layout.addLayout(layout)
        
        return build_widget

    def on_combobox_changed(self, index):
        self.helper.loadingSignal.emit(True)
        self.traits_widget.setEnabled(False)
        self.builds_widget.setEnabled(False)
        
        selectedId = self.comboBox.currentData()
        self.helper.settings.setValue("currentBuild", selectedId)
        
        if not selectedId:
            self.update_data(None)
            return
        
        self.worker = self.helper.DataWorker(self.helper, selectedId)
        self.worker.data_ready.connect(self.update_data)
        self.worker.start()
    
    def update_data(self, data: DeepwokenData):
        self.helper.data = data
        traits = getattr(data, "traits", None)

        self.update_trait_value(traits)
        self.update_build_values()
        self.helper.clear_layout(self.helper.cards_layout)
        
        self.isAdding = False
        self.traits_widget.setEnabled(True)
        self.builds_widget.setEnabled(True)
        self.helper.loadingSignal.emit(False)

    def get_name_author(self):
        name = ""
        author = ""
        
        if not self.helper.data:
            return name, author

        stats_data = getattr(self.helper.data, "stats", {})
        author_data = getattr(self.helper.data, "author", {})

        name = stats_data.get("buildName", "")
        author = stats_data.get("buildAuthor") or author_data.get("name", "")
        
        return name, author

    def update_build_values(self):
        name, author = self.get_name_author()
        self.buildName.setText(str(name))
        self.buildAuthor.setText(str(author))

    def save_builds(self):
        builds_values = [(self.comboBox.itemText(i), self.comboBox.itemData(i)) for i in range(self.comboBox.count())]
        self.helper.settings.setValue("builds", builds_values)

    def load_list_builds(self):
        self.isAdding = True
        
        build_values = self.helper.settings.value("builds", [])
        currentBuild = self.helper.settings.value("currentBuild", None)
        currentIdx = 0

        for idx, (buildName, buildId) in enumerate(build_values):
            self.comboBox.addItem(buildName, buildId)
            
            if currentBuild == buildId:
                currentIdx = idx
        
        self.comboBox.setCurrentIndex(currentIdx)
        self.on_combobox_changed(currentIdx)
        self.comboBox.currentIndexChanged.connect(self.on_combobox_changed)
        
        return currentIdx

    def buttons(self):
        buttons_widget = QWidget()
        buttons_widget.setMaximumWidth(150)
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        #Add and Delete buttons
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        addButton = QPushButton()
        addButton.setStyleSheet("background: #04100d; border-image: url(./assets/gui/border.png); border-width: 15px; padding: -10px; color: #ffffff;")
        addButton.setIcon(QIcon("./assets/gui/add.png"))
        addButton.setIconSize(QSize(20, 20))
        addButton.clicked.connect(self.add_clicked)
        layout.addWidget(addButton)
        
        deleteButton = QPushButton()
        deleteButton.setStyleSheet("background: #04100d; border-image: url(./assets/gui/border.png); border-width: 15px; padding: -10px; color: #ffffff;")
        deleteButton.setIcon(QIcon("./assets/gui/trash.png"))
        deleteButton.setIconSize(QSize(20, 20))
        deleteButton.clicked.connect(self.delete_clicked)
        layout.addWidget(deleteButton)
        
        buttons_layout.addLayout(layout)


        #Github Button
        githubButton = QPushButton("GitHub")
        githubButton.setStyleSheet("background: #04100d; border-image: url(./assets/gui/border.png); border-width: 15px; padding: -10px; color: #ffffff;")
        githubButton.setIcon(QIcon("./assets/gui/github.png"))
        githubButton.setIconSize(QSize(20, 20))
        githubButton.clicked.connect(self.github_clicked)
        buttons_layout.addWidget(githubButton)


        #Info Button
        infoButton = QPushButton("Info")
        infoButton.setStyleSheet("background: #04100d; border-image: url(./assets/gui/border.png); border-width: 15px; padding: -10px; color: #ffffff;")
        infoButton.setIcon(QIcon("./assets/gui/info.png"))
        infoButton.setIconSize(QSize(20, 20))
        infoButton.clicked.connect(self.info_clicked)
        buttons_layout.addWidget(infoButton)


        #Settings Button
        settingsButton = QPushButton("Settings")
        settingsButton.setStyleSheet("background: #04100d; border-image: url(./assets/gui/border.png); border-width: 15px; padding: -10px; color: #ffffff;")
        settingsButton.setIcon(QIcon("./assets/gui/cog.png"))
        settingsButton.setIconSize(QSize(20, 20))
        settingsButton.clicked.connect(self.settings_clicked)
        buttons_layout.addWidget(settingsButton)


        return buttons_widget

    def add_clicked(self):
        logger.info("Adding Build")

        dlg = AddDialog(self)
        dlg.exec()

    def delete_clicked(self):
        if self.isAdding:
            logger.info("Cannot delete while adding a build. Please wait.")
            return
        
        logger.info("Deleting Build")
        
        index = self.comboBox.currentIndex()
        if index == -1:
            return
        
        self.comboBox.currentIndexChanged.disconnect(self.on_combobox_changed)
        self.comboBox.removeItem(index)
        self.comboBox.currentIndexChanged.connect(self.on_combobox_changed)
        
        self.on_combobox_changed(index)
        self.save_builds()

    def github_clicked(self):
        github = GithubWindow(self)
        github.exec()
    
    def info_clicked(self):
        if self.info is None:
            self.info = InfoWindow(self)
        self.info.show()

    def settings_clicked(self):
        if not self.helper.ocr.hotkeys:
            return
        
        if self.settings is None:
            self.settings = SettingsWindow(self)
        else:
            self.settings.load_settings()
        self.settings.show()


class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(325, 100)
        # self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.stats: ControlPanel = parent

        self.setWindowTitle("New Build")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        build_layout = QHBoxLayout()
        build_layout.setContentsMargins(9, 9, 9, 9)
        
        label = QLabel("Build Link:")
        build_layout.addWidget(label)
        
        self.lineEdit = QLineEdit()
        build_layout.addWidget(self.lineEdit)
        
        layout.addLayout(build_layout, 1)
        
        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        buttonBox.setCenterButtons(True)
        buttonBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout.addWidget(buttonBox, 1)
        
        self.info = QWidget()
        self.info.setMinimumHeight(16)
        
        bottom_layout = QHBoxLayout(self.info)
        bottom_layout.setContentsMargins(3, 0, 0, 0)
        
        self.icon = QLabel()
        pixmap = QMessageBox.standardIcon(QMessageBox.Icon.Warning)
        pixmap = pixmap.scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio)
        self.icon.setPixmap(pixmap)
        self.icon.hide()
        
        bottom_layout.addWidget(self.icon)
        
        self.error_label = QLabel()
        self.error_label.setStyleSheet("font-size: 12px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.error_label.hide()
        
        bottom_layout.addWidget(self.error_label, 1)
        
        layout.addWidget(self.info)

    def accept(self):
        self.stats.isAdding = True
        self.stats.helper.loadingSignal.emit(True)
        
        self.worker = self.AddData(self)
        self.worker.buildProcessed.connect(self.on_build_processed)
        self.worker.errorOccurred.connect(self.on_error)
        self.worker.start()

    def on_build_processed(self, build_name, build_id):
        self.stats.comboBox.currentIndexChanged.disconnect(self.stats.on_combobox_changed)
        self.stats.comboBox.insertItem(0, build_name, build_id)
        self.stats.comboBox.setCurrentIndex(0)
        self.stats.comboBox.currentIndexChanged.connect(self.stats.on_combobox_changed)

        self.stats.on_combobox_changed(0)
        self.stats.save_builds()

        self.stats.helper.loadingSignal.emit(False)
        self.done(0)

    def on_error(self, message):
        self.stats.isAdding = False
        logger.warning(f"Error: {message}")
        
        self.lineEdit.clear()
        self.stats.helper.loadingSignal.emit(False)
        
        self.error_label.setText(f"Error: {message}")
        self.error_label.show()
        self.icon.show()


    class AddData(QThread):
        buildProcessed = pyqtSignal(str, str)
        errorOccurred = pyqtSignal(str)
        
        def __init__(self, parent):
            super().__init__()
            self.parent: AddDialog = parent
            self.stats = self.parent.stats
            self.helper = self.stats.helper
        
        def run(self):
            try:
                buildIdMatch = re.findall(r"[a-zA-Z0-9]{8}$", self.parent.lineEdit.text())
                if not buildIdMatch:
                    self.errorOccurred.emit("Invalid Build ID")
                    return

                buildId = buildIdMatch[0]
                if buildId in [self.stats.comboBox.itemData(i) for i in range(self.stats.comboBox.count())]:
                    self.errorOccurred.emit("Build already loaded")
                    return
                
                buildLink = f"https://api.deepwoken.co/build?id={buildId}"
                build = self.helper.getData(buildLink, True)

                if not build or isinstance(build, str):
                    self.errorOccurred.emit("Build not found or invalid")
                    return

                buildName = f"{buildId} - {build.get('stats', {}).get('buildName', '')}"

                self.buildProcessed.emit(buildName, buildId)
                
            except Exception as e:
                logger.exception(e)
                raise e


class GithubWindow(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setWindowFlag(Qt.WindowType.Popup)
        self.setWindowTitle("GitHub")
        
        self.setText("Open link?")

        pixmap = QIcon("./assets/gui/github-black.png")
        self.setIconPixmap(pixmap.pixmap(QSize(30, 30)))

        self.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        self.accepted.connect(self.accept)
        self.rejected.connect(self.reject)

    def accept(self):
        logger.info("Opening github...")
        url = "https://github.com/Tuxsupa/DeepwokenHelper"
        webbrowser.open(url)
        self.close()

    def reject(self):
        self.close()


class InfoWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        
        # self.resize(1235, 1050)
        self.resize(615, 525)
        
        self.fontText = QFont()
        self.fontText.setPointSize(12)
        
        self.setWindowTitle("Info")
        self.setWindowIcon(QIcon('./assets/icons/favicon.png'))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        main_widget = QWidget()
        main_widget.setObjectName("Info")
        main_widget.setStyleSheet("#Info { background-image: url(./assets/gui/background.png); } ")
        
        main_layout = QVBoxLayout(main_widget)
        layout.addWidget(main_widget)

        icon_group = self.set_icon_group()
        main_layout.addWidget(icon_group)
        
        tutorial_group = self.set_tutorial_group()
        main_layout.addWidget(tutorial_group)
        
        main_layout.addItem(QSpacerItem(0, 0, vPolicy=QSizePolicy.Policy.Expanding))

    def set_icon_group(self):
        icon_group = QGroupBox("Icons")
        icon_group.setFont(self.fontText)
        icon_group.setStyleSheet("color: rgb(255, 255, 255);")
        icon_layout = QVBoxLayout(icon_group)


        layout = QHBoxLayout()
        
        icon = QLabel()
        pixmap = QPixmap("./assets/gui/locked.png")
        pixmap = pixmap.scaledToWidth(20)
        icon.setPixmap(pixmap)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedWidth(64)
        layout.addWidget(icon)
        
        text = QLabel("""<b>Locked:</b> This talent is mutually exclusive with another. The tooltip will show which talent is mutually exclusive.""")
        text.setFont(self.fontText)
        text.setWordWrap(True)
        layout.addWidget(text, 1)

        icon_layout.addLayout(layout)
        
        
        layout = QHBoxLayout()
        widget = QWidget()
        widget_layout = QHBoxLayout(widget)

        icon = QLabel()
        pixmap = QPixmap("./assets/gui/locked.png")
        pixmap = pixmap.scaledToWidth(20)
        icon.setPixmap(pixmap)
        widget_layout.addWidget(icon)

        icon = QLabel()
        pixmap = QPixmap("./assets/gui/locked_important.png")
        pixmap = pixmap.scaledToWidth(20)
        icon.setPixmap(pixmap)
        widget_layout.addWidget(icon)
        layout.addWidget(widget)
        
        text = QLabel("""<b>Locked Important:</b> This talent is mutually exclusive with another talent that is needed for the build. Be careful with this talent because it's going to lock you out of a needed talent. The tooltip will show which talent needed for this build will get locked out if you pick this talent.""")
        text.setFont(self.fontText)
        text.setWordWrap(True)
        layout.addWidget(text, 1)
        
        icon_layout.addLayout(layout)


        layout = QHBoxLayout()
        icon = QLabel()
        pixmap = QPixmap("./assets/gui/important.png")
        pixmap = pixmap.scaledToWidth(20)
        icon.setPixmap(pixmap)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedWidth(64)
        layout.addWidget(icon)

        text = QLabel("""<b>Important:</b> This talent is needed to get a different talent from the build. The tooltip will show which build talent wants this talent.""")
        text.setFont(self.fontText)
        text.setWordWrap(True)
        layout.addWidget(text, 1)

        icon_layout.addLayout(layout)
        
        
        layout = QHBoxLayout()
        widget = QWidget()
        widget_layout = QHBoxLayout(widget)
        
        icon = QLabel()
        pixmap = QPixmap("./assets/gui/important.png")
        pixmap = pixmap.scaledToWidth(20)
        icon.setPixmap(pixmap)
        widget_layout.addWidget(icon)

        icon = QLabel()
        pixmap = QPixmap("./assets/gui/important_shrine.png")
        pixmap = pixmap.scaledToWidth(20)
        icon.setPixmap(pixmap)
        widget_layout.addWidget(icon)
        layout.addWidget(widget)
        
        text = QLabel("""<b>Important Shrine:</b> This talent is needed to get a shrine talent from the build. The tooltip will show which shrine build talent wants this talent.""")
        text.setFont(self.fontText)
        text.setWordWrap(True)
        layout.addWidget(text, 1)
        
        icon_layout.addLayout(layout)
        
        
        layout = QHBoxLayout()
        icon = QLabel()
        pixmap = QPixmap("./assets/gui/shrine.png")
        pixmap = pixmap.scaledToWidth(20)
        icon.setPixmap(pixmap)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedWidth(64)
        layout.addWidget(icon)

        text = QLabel("""<b>Shrine:</b> This talent can only be obtained pre-shrine meaning that you can only get it before Shrine of Order. You might want to prioritize them if they are needed for the build.""")
        text.setFont(self.fontText)
        text.setWordWrap(True)
        layout.addWidget(text, 1)

        icon_layout.addLayout(layout)
        
        return icon_group

    def set_tutorial_group(self):
        tutorial_group = QGroupBox("Tutorial")
        tutorial_group.setFont(self.fontText)
        tutorial_group.setStyleSheet("color: rgb(255, 255, 255);")
        layout = QVBoxLayout(tutorial_group)

        text = QLabel("""First add a New Build with the <b>Add Button</b>. While having <b>Roblox - Deepwoken</b> open, have the cards on screen/open and press the hotkey from <b>Settings</b>. This will take a screenshot of the game, extract the location of the title with AI and then will use OCR to detect the text. Finally it will show the card data on the Helper. <b>The cards in orange are needed for the selected build</b>""")
        text.setFont(self.fontText)
        text.setWordWrap(True)
        layout.addWidget(text)

        return tutorial_group


class SettingsWindow(QWidget):
    def __init__(self, stats: ControlPanel):
        super().__init__()
        
        self.stats = stats
        self.hotkeys = stats.helper.ocr.hotkeys
        self.settings = stats.helper.settings
        
        self.fontText = QFont()
        self.fontText.setPointSize(12)
        
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon('./assets/icons/favicon.png'))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        main_widget = QWidget()
        main_widget.setObjectName("Settings")
        main_widget.setStyleSheet("#Settings { background-image: url(./assets/gui/background.png); } ")
        
        main_layout = QVBoxLayout(main_widget)
        layout.addWidget(main_widget)
        
        
        self.checkBox = QCheckBox("Give focus after taking screenshot")
        self.checkBox.setStyleSheet("color: rgb(255, 255, 255);")
        self.checkBox.setFont(self.fontText)
        checked = self.settings.value("giveFocus", False, bool)
        self.checkBox.setChecked(checked)
        main_layout.addWidget(self.checkBox)
        
        hotkey_group = QGroupBox("Screenshot Hotkey")
        hotkey_group.setFont(self.fontText)
        hotkey_group.setStyleSheet("QGroupBox::title { color: rgb(255, 255, 255); }")
        hotkey_layout = QVBoxLayout(hotkey_group)
        
        layout = QHBoxLayout()
        label = QLabel("1:")
        label.setFont(self.fontText)
        label.setStyleSheet("color: rgb(255, 255, 255);")
        layout.addWidget(label)
        
        key_sequence = self.settings.value("screenshotHotkey1", QKeySequence("J"))
        self.keySequence1 = QKeySequenceEdit(key_sequence)
        self.keySequence1.setMaximumSequenceLength(1)
        self.keySequence1.setClearButtonEnabled(True)
        layout.addWidget(self.keySequence1)
        hotkey_layout.addLayout(layout)
        
        layout = QHBoxLayout()
        label = QLabel("2:")
        label.setFont(self.fontText)
        label.setStyleSheet("color: rgb(255, 255, 255);")
        layout.addWidget(label)
        
        key_sequence = self.settings.value("screenshotHotkey2", None)
        self.keySequence2 = QKeySequenceEdit(key_sequence)
        self.keySequence2.setMaximumSequenceLength(1)
        self.keySequence2.setClearButtonEnabled(True)
        layout.addWidget(self.keySequence2)
        
        hotkey_layout.addLayout(layout)
        
        main_layout.addWidget(hotkey_group)
        
        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        
        main_layout.addWidget(buttonBox)

    def load_settings(self):
        logger.info("Loading settings")
        
        checked = self.settings.value("giveFocus", False, bool)
        self.checkBox.setChecked(checked)
        
        key_sequence = self.settings.value("screenshotHotkey1", QKeySequence("J"), QKeySequence)
        self.keySequence1.setKeySequence(key_sequence)
        
        key_sequence = self.settings.value("screenshotHotkey2", QKeySequence())
        self.keySequence2.setKeySequence(key_sequence)

    def accept(self):
        if self.keySequence1.keySequence().isEmpty():
            self.keySequence1.setKeySequence(QKeySequence("J"))
        
        self.hotkeys.giveFocus = self.checkBox.isChecked()
        hotkey1 = self.keySequence1.keySequence()
        hotkey2 = self.keySequence2.keySequence()
        
        self.hotkeys.start_listener(hotkey1, hotkey2)
        
        self.settings.setValue("giveFocus", self.checkBox.isChecked())
        self.settings.setValue("screenshotHotkey1", self.keySequence1.keySequence())
        self.settings.setValue("screenshotHotkey2", self.keySequence2.keySequence())
        logger.info("Settings changes saved.")
        
        self.hide()

    def reject(self):
        self.hide()
