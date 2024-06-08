import re
import webbrowser

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from waitingspinnerwidget import QtWaitingSpinner

import deepwokenhelper
from deepwokenhelper.data import DeepwokenData


class ControlPanel(QWidget):
    def __init__(self, helper):
        super().__init__()
        
        from deepwokenhelper.gui.application import DeepwokenHelper
        self.helper: DeepwokenHelper = helper
        self.info = None
        self.settings = None
        
        main_layout = QVBoxLayout(self)
        
        layout = QHBoxLayout()
        # layout.setContentsMargins(0, 0, 0, 0)

        traits_widget = self.traits()
        layout.addWidget(traits_widget, alignment=Qt.AlignmentFlag.AlignLeft)
        
        builds_layout = self.builds()
        layout.addLayout(builds_layout, 5)
        
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
        spinner.start()
        
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
        if self.helper.data:
            traits.update(self.helper.data.traits)
        
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
        build_layout = QVBoxLayout()
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
        
        self.load_builds()
        
        build_layout.addLayout(layout)


        #Build Name
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Build Name")
        title.setFixedWidth(80)
        title.setStyleSheet("font-size: 15px; font-weight: 600;")
        layout.addWidget(title, 1)

        stats_data = self.helper.data.stats if self.helper.data else None
        self.buildName = QLabel(stats_data["buildName"] if stats_data else None)
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
        
        self.buildAuthor = QLabel(stats_data["buildAuthor"] if stats_data else None)
        self.buildAuthor.setMinimumWidth(40)
        self.buildAuthor.setMaximumHeight(30)
        self.buildAuthor.setStyleSheet("""background-color: transparent;
                                border-radius: 5px;
                                border: 1px solid rgba(0, 0, 0, .25);
                                padding: 2px;""")
        layout.addWidget(self.buildAuthor, 5)
        
        build_layout.addLayout(layout)
        
        return build_layout

    def on_combobox_changed(self, index):
        selectedId = self.comboBox.currentData()
        self.helper.settings.setValue("currentBuild", selectedId)
        
        data = DeepwokenData(selectedId) 
        self.helper.data = data

        self.update_trait_value(data.traits)
        self.update_build_values(data.stats['buildName'], data.stats['buildAuthor'])
        self.helper.clear_layout(self.helper.cards_layout)

    def update_build_values(self, buildName, buildAuthor):
        self.buildName.setText(str(buildName))
        self.buildAuthor.setText(str(buildAuthor))

    def save_builds(self):
        builds_values = [(self.comboBox.itemText(i), self.comboBox.itemData(i)) for i in range(self.comboBox.count())]
        self.helper.settings.setValue("builds", builds_values)

    def load_builds(self):
        build_values = self.helper.settings.value("builds", [])
        currentBuild = self.helper.settings.value("currentBuild", None)
        currentIdx = 0

        for idx, (value, data) in enumerate(build_values):
            self.comboBox.addItem(value, data)
            
            if currentBuild == data:
                currentIdx = idx
        
        self.comboBox.setCurrentIndex(currentIdx)
        self.comboBox.currentIndexChanged.connect(self.on_combobox_changed)

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
        print("Adding Build")

        dlg = AddDialog(self)
        dlg.exec()

    def delete_clicked(self):
        print("Deleting Build")
        
        index = self.comboBox.currentIndex()
        if index == -1:
            return
        
        self.comboBox.currentIndexChanged.disconnect(self.on_combobox_changed)
        self.comboBox.removeItem(index)
        self.comboBox.currentIndexChanged.connect(self.on_combobox_changed)

        currentData = self.comboBox.currentData()
        self.helper.settings.setValue("currentBuild", currentData)
        data = DeepwokenData(currentData) if currentData else None

        self.helper.data = data
        traits = data.traits if data else None
        self.update_trait_value(traits)

        stats = data.stats if data else None
        buildName = stats['buildName'] if stats else ''
        buildAuthor = stats['buildAuthor'] if stats else ''
        self.update_build_values(buildName, buildAuthor)
        
        self.helper.clear_layout(self.helper.cards_layout)

        self.save_builds()
    
    def github_clicked(self):
        github = GithubWindow(self)
        github.exec()
    
    def info_clicked(self):
        if self.info is None:
            self.info = InfoWindow(self)
        self.info.show()

    def settings_clicked(self):
        if self.settings is None:
            self.settings = SettingsWindow(self)
        else:
            self.settings.load_settings()
        self.settings.show()


class AddDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(325, 75)
        # self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.stats: ControlPanel = parent

        self.setWindowTitle("New Build")
        
        layout = QVBoxLayout(self)
        
        build_layout = QHBoxLayout()
        
        label = QLabel("Build Link:")
        build_layout.addWidget(label)
        
        self.lineEdit = QLineEdit()
        build_layout.addWidget(self.lineEdit)
        
        layout.addLayout(build_layout)
        
        QBtn = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        buttonBox.setCenterButtons(True)
        
        layout.addWidget(buttonBox)
    
    def accept(self):
        buildId = re.findall(r"[a-zA-Z0-9]{8}$", self.lineEdit.text())
        if not buildId:
            self.lineEdit.clear()
            return

        buildId = buildId[0]
        buildLink = f"https://api.deepwoken.co/build?id={buildId}"
        build = DeepwokenData.getData(buildLink)

        if isinstance(build, str):
            self.lineEdit.clear()
            return

        buildName = f"{buildId} - {build['stats']['buildName'] if build.get('stats') and build['stats'].get('buildName') else ''}"

        if buildId not in [self.stats.comboBox.itemData(i) for i in range(self.stats.comboBox.count())]:
            self.stats.comboBox.currentIndexChanged.disconnect(self.stats.on_combobox_changed)
            self.stats.comboBox.insertItem(0, buildName, buildId)
            self.stats.comboBox.setCurrentIndex(0)
            self.stats.comboBox.currentIndexChanged.connect(self.stats.on_combobox_changed)

            self.stats.on_combobox_changed(0)
            self.stats.helper.clear_layout(self.stats.helper.cards_layout)

            self.stats.save_builds()

        self.done(0)


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
        self.settings = QSettings("Tuxsuper", "DeepwokenHelper")
        
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
        checked = self.settings.value("giveFocus", False, bool)
        self.checkBox.setChecked(checked)
        
        key_sequence = self.settings.value("screenshotHotkey1", QKeySequence("J"), QKeySequence)
        self.keySequence1.setKeySequence(key_sequence)
        
        key_sequence = self.settings.value("screenshotHotkey2")
        self.keySequence2.setKeySequence(key_sequence)

    def accept(self):
        if self.keySequence1.keySequence().isEmpty():
            self.keySequence1.setKeySequence(QKeySequence("J"))
        
        self.stats.helper.ocr.listener.giveFocus = self.checkBox.isChecked()
        self.stats.helper.ocr.listener.hotkey1 = self.keySequence1.keySequence().toString(QKeySequence.SequenceFormat.NativeText)
        self.stats.helper.ocr.listener.hotkey2 = self.keySequence2.keySequence().toString(QKeySequence.SequenceFormat.NativeText)
        
        self.settings.setValue("giveFocus", self.checkBox.isChecked())
        self.settings.setValue("screenshotHotkey1", self.keySequence1.keySequence())
        self.settings.setValue("screenshotHotkey2", self.keySequence2.keySequence())
        print("Changes saved.")
        
        self.hide()

    def reject(self):
        self.hide()
