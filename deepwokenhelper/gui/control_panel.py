import re
import os
import sys
import subprocess
import logging
import webbrowser
from enum import Enum


from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from waitingspinnerwidget import QtWaitingSpinner


import deepwokenhelper
from deepwokenhelper.data import DeepwokenData


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

        # spinner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout.addWidget(
            spinner,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
            stretch=0,
        )

        self.loading_text = QLabel()
        self.loading_text.setStyleSheet("color: #000000; font-size: 12px;")
        # self.loading_text.setSizePolicy(
        #     QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed
        # )
        self.loading_text.hide()

        layout.addWidget(
            self.loading_text,
            alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom,
            stretch=0,
        )

        layout.addStretch(1)
        # layout.addItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Policy.Expanding))

        tag = QLabel(f"<b>v{deepwokenhelper.__version__} @Tuxsuper</b>")
        tag.setStyleSheet("color: #000000; font-size: 12px;")
        tag.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        layout.addWidget(
            tag, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom
        )

        main_layout.addLayout(layout)

    def set_color(self, widget: QWidget, color_role: QPalette.ColorRole):
        palette = widget.palette()

        palette.setColor(
            QPalette.ColorGroup.Active,
            color_role,
            QColor(0, 0, 0),
        )
        palette.setColor(
            QPalette.ColorGroup.Inactive,
            color_role,
            QColor(0, 0, 0),
        )
        widget.setPalette(palette)

    def traits(self):
        self.trait_values = {}

        traits_widget = QWidget()
        traits_layout = QVBoxLayout(traits_widget)
        traits_layout.setContentsMargins(10, 0, 20, 0)

        traits = {"Vitality": 0, "Erudition": 0, "Proficiency": 0, "Songchant": 0}

        for name, value in traits.items():
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 3, 0, 3)

            nameLabel = QLabel(name)
            nameLabel.setFixedWidth(100)
            self.set_color(nameLabel, QPalette.ColorRole.WindowText)
            nameLabel.setStyleSheet("font-size: 15px; font-weight: 600;")
            layout.addWidget(nameLabel)

            valueLabel = QLabel(str(value))
            valueLabel.setFixedWidth(40)
            self.set_color(valueLabel, QPalette.ColorRole.WindowText)
            valueLabel.setStyleSheet(
                "background-color: transparent; border-radius: 5px; border: 1px solid rgba(0, 0, 0, .25); padding: 2px;"
            )
            layout.addWidget(valueLabel)

            self.trait_values[name] = valueLabel
            traits_layout.addWidget(widget)

        return traits_widget

    def update_trait_value(self, new_traits=None):
        traits = {"Vitality": 0, "Erudition": 0, "Proficiency": 0, "Songchant": 0}
        if new_traits:
            traits.update(new_traits)

        for traitName, traitValue in traits.items():
            self.trait_values[traitName].setText(str(traitValue))

    def builds(self):
        build_widget = QWidget()
        build_layout = QVBoxLayout(build_widget)
        build_layout.setContentsMargins(0, 0, 10, 0)

        # Builds
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Builds")
        self.set_color(title, QPalette.ColorRole.WindowText)
        title.setFixedWidth(80)
        title.setStyleSheet("font-size: 15px; font-weight: 600;")
        layout.addWidget(title, 1)

        self.comboBox = QComboBox()
        self.set_color(self.comboBox, QPalette.ColorRole.Text)
        self.comboBox.setMinimumWidth(40)
        self.comboBox.setMaximumHeight(30)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.setStyleSheet("""#comboBox { background-color: rgb(216, 215, 202);
                                border-radius: 5px;
                                border: 1px solid rgba(0, 0, 0, .25);
                                padding-left: 5px;
                                }

                                #comboBox QListView { background-color: rgb(216, 215, 202);
                                border-radius: 5px;
                                border: 1px solid rgba(0, 0, 0, .25);
                                color: rgb(0, 0, 0);
                                selection-color: rgb(0, 0, 0);
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
        self.comboBox.setSizeAdjustPolicy(
            self.comboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        layout.addWidget(self.comboBox, 5)

        copy_button = QPushButton()
        copy_button.setStyleSheet(
            "background: #04100d; border-image: url(./assets/gui/border.png); border-width: 15px; padding: -10px; color: #ffffff;"
        )
        copy_button.setIcon(QIcon("./assets/gui/copy.png"))
        copy_button.setIconSize(QSize(20, 20))
        copy_button.clicked.connect(self.copy_build)
        layout.addWidget(copy_button)

        open_button = QPushButton()
        open_button.setStyleSheet(
            "background: #04100d; border-image: url(./assets/gui/border.png); border-width: 15px; padding: -10px; color: #ffffff;"
        )
        open_button.setIcon(QIcon("./assets/gui/open.png"))
        open_button.setIconSize(QSize(20, 20))
        open_button.clicked.connect(self.open_build)
        layout.addWidget(open_button)

        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide_message)

        build_layout.addLayout(layout)

        # Build Name
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Build Name")
        self.set_color(title, QPalette.ColorRole.WindowText)
        title.setFixedWidth(80)
        title.setStyleSheet("font-size: 15px; font-weight: 600;")
        layout.addWidget(title, 1)

        self.buildName = QLabel()
        self.set_color(self.buildName, QPalette.ColorRole.WindowText)
        self.buildName.setMinimumWidth(40)
        self.buildName.setMaximumHeight(30)
        self.buildName.setStyleSheet("""background-color: transparent;
                                border-radius: 5px;
                                border: 1px solid rgba(0, 0, 0, .25);
                                padding: 2px;""")
        layout.addWidget(self.buildName, 5)

        build_layout.addLayout(layout)

        # Author
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Author")
        self.set_color(title, QPalette.ColorRole.WindowText)
        title.setFixedWidth(80)
        title.setStyleSheet("font-size: 15px; font-weight: 600;")
        layout.addWidget(title, 1)

        self.buildAuthor = QLabel()
        self.set_color(self.buildAuthor, QPalette.ColorRole.WindowText)
        self.buildAuthor.setMinimumWidth(40)
        self.buildAuthor.setMaximumHeight(30)
        self.buildAuthor.setStyleSheet("""background-color: transparent;
                                border-radius: 5px;
                                border: 1px solid rgba(0, 0, 0, .25);
                                padding: 2px;""")
        layout.addWidget(self.buildAuthor, 5)

        build_layout.addLayout(layout)

        return build_widget

    def change_combobox(self, index):
        self.helper.start_loading_signal.emit("Changing Build...")
        self.on_combobox_changed(index)
        self.helper.stop_loading_signal.emit()

    def on_combobox_changed(self, index):
        self.helper.start_loading_signal.emit(None)
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

        self.helper.stop_loading_signal.emit()

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
        builds_values = [
            (self.comboBox.itemText(i), self.comboBox.itemData(i))
            for i in range(self.comboBox.count())
        ]
        self.helper.settings.setValue("builds", builds_values)

    def load_list_builds(self):
        self.helper.start_loading_signal.emit("Loading Builds...")
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
        self.comboBox.currentIndexChanged.connect(self.change_combobox)

        self.helper.stop_loading_signal.emit()

        return currentIdx

    def copy_build(self):
        current_id = self.comboBox.currentData()
        if not current_id:
            return

        current_link = f"https://deepwoken.co/builder?id={current_id}"
        logger.info(f"Copying build link: {current_link}")

        clipboard = QApplication.clipboard()
        clipboard.setText(current_link)

        self.show_message("Copied build!")

    def open_build(self):
        current_id = self.comboBox.currentData()
        if not current_id:
            return

        current_link = f"https://deepwoken.co/builder?id={current_id}"
        logger.info(f"Opening build link: {current_link}")

        QDesktopServices.openUrl(QUrl(current_link))

        self.show_message("Opened build!")

    def show_message(self, message):
        self.loading_text.setText(f"<b>{message}</b>")
        self.loading_text.show()

        self.timer.start(5000)

    def hide_message(self):
        self.loading_text.hide()

    def buttons(self):
        buttons_widget = QWidget()
        buttons_widget.setMaximumWidth(150)
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        # Add and Delete buttons
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        addButton = QPushButton()
        addButton.setStyleSheet(
            "background: #04100d; border-image: url(./assets/gui/border.png); border-width: 15px; padding: -10px; color: #ffffff;"
        )
        addButton.setIcon(QIcon("./assets/gui/add.png"))
        addButton.setIconSize(QSize(20, 20))
        addButton.clicked.connect(self.add_clicked)
        layout.addWidget(addButton)

        deleteButton = QPushButton()
        deleteButton.setStyleSheet(
            "background: #04100d; border-image: url(./assets/gui/border.png); border-width: 15px; padding: -10px; color: #ffffff;"
        )
        deleteButton.setIcon(QIcon("./assets/gui/trash.png"))
        deleteButton.setIconSize(QSize(20, 20))
        deleteButton.clicked.connect(self.delete_clicked)
        layout.addWidget(deleteButton)

        buttons_layout.addLayout(layout)

        # Github Button
        githubButton = QPushButton("GitHub")
        githubButton.setStyleSheet(
            "background: #04100d; border-image: url(./assets/gui/border.png); border-width: 15px; padding: -10px; color: #ffffff;"
        )
        githubButton.setIcon(QIcon("./assets/gui/github.png"))
        githubButton.setIconSize(QSize(20, 20))
        githubButton.clicked.connect(self.github_clicked)
        buttons_layout.addWidget(githubButton)

        # Info Button
        infoButton = QPushButton("Info")
        infoButton.setStyleSheet(
            "background: #04100d; border-image: url(./assets/gui/border.png); border-width: 15px; padding: -10px; color: #ffffff;"
        )
        infoButton.setIcon(QIcon("./assets/gui/info.png"))
        infoButton.setIconSize(QSize(20, 20))
        infoButton.clicked.connect(self.info_clicked)
        buttons_layout.addWidget(infoButton)

        # Settings Button
        settingsButton = QPushButton("Settings")
        settingsButton.setStyleSheet(
            "background: #04100d; border-image: url(./assets/gui/border.png); border-width: 15px; padding: -10px; color: #ffffff;"
        )
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
        self.helper.start_loading_signal.emit("Deleting Build...")

        index = self.comboBox.currentIndex()
        if index == -1:
            return

        self.comboBox.currentIndexChanged.disconnect(self.change_combobox)
        self.comboBox.removeItem(index)
        self.comboBox.currentIndexChanged.connect(self.change_combobox)

        self.on_combobox_changed(index)
        self.save_builds()

        self.helper.stop_loading_signal.emit()

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

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        buttonBox.setCenterButtons(True)
        buttonBox.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

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
        self.error_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
        )
        self.error_label.hide()

        bottom_layout.addWidget(self.error_label, 1)

        layout.addWidget(self.info)

    def accept(self):
        self.stats.isAdding = True
        self.stats.helper.start_loading_signal.emit("Adding Build...")

        self.worker = self.AddData(self)
        self.worker.buildProcessed.connect(self.on_build_processed)
        self.worker.errorOccurred.connect(self.on_error)
        self.worker.start()

    def on_build_processed(self, build_name, build_id):
        self.stats.comboBox.currentIndexChanged.disconnect(self.stats.change_combobox)
        self.stats.comboBox.insertItem(0, build_name, build_id)
        self.stats.comboBox.setCurrentIndex(0)
        self.stats.comboBox.currentIndexChanged.connect(self.stats.change_combobox)

        self.stats.on_combobox_changed(0)
        self.stats.save_builds()

        self.stats.helper.stop_loading_signal.emit()
        self.done(0)

    def on_error(self, message):
        self.stats.isAdding = False
        logger.warning(f"Error: {message}")

        self.lineEdit.clear()
        self.stats.helper.stop_loading_signal.emit()

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
                buildIdMatch = re.findall(
                    r"[a-zA-Z0-9]{8}$", self.parent.lineEdit.text()
                )
                if not buildIdMatch:
                    self.errorOccurred.emit("Invalid Build ID")
                    return

                buildId = buildIdMatch[0]
                if buildId in [
                    self.stats.comboBox.itemData(i)
                    for i in range(self.stats.comboBox.count())
                ]:
                    self.errorOccurred.emit("Build already loaded")
                    return

                # buildLink = f"https://deepwoken.co/builder?id={buildId}"
                buildLink = f'https://deepwoken.co/api/proxy?url=https://api.deepwoken.co/build?id={buildId}&options={{"signal":{{}}}}'
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
        self.stats: ControlPanel = parent

        # self.setWindowFlag(Qt.WindowType.Popup)
        self.setWindowTitle("GitHub")
        bg_color = self.palette().color(QPalette.ColorRole.Window)
        use_dark_icon = bg_color.value() > 128

        self.setText("Open link?")

        if use_dark_icon:
            pixmap = QIcon("./assets/gui/github-black.png")
        else:
            pixmap = QIcon("./assets/gui/github.png")

        self.setIconPixmap(pixmap.pixmap(QSize(30, 30)))

        self.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        self.accepted.connect(self.accept)
        self.rejected.connect(self.reject)

    def accept(self):
        logger.info("Opening github...")

        url = "https://github.com/Tuxsupa/DeepwokenHelper"
        webbrowser.open(url)
        self.close()

        self.stats.show_message("Opened GitHub link!")

    def reject(self):
        self.close()


class InfoWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__()

        self.resize(615, 575)

        self.fontText = QFont()
        self.fontText.setPointSize(12)

        self.setWindowTitle("Info")
        self.setWindowIcon(QIcon("./assets/icons/favicon.png"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        main_widget = QWidget()
        main_widget.setObjectName("Info")
        main_widget.setStyleSheet(
            "#Info { background-image: url(./assets/gui/background.png); } "
        )

        main_layout = QVBoxLayout(main_widget)
        layout.addWidget(main_widget)

        icon_group = self.set_icon_group()
        main_layout.addWidget(icon_group)

        tutorial_group = self.set_tutorial_group()
        main_layout.addWidget(tutorial_group)

        main_layout.addItem(QSpacerItem(0, 0, vPolicy=QSizePolicy.Policy.Expanding))

        bottom_layout = QHBoxLayout()
        bottom_layout.addItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Policy.Expanding))

        open_logs_button = QPushButton("Open Logs Folder")
        open_logs_button.setFixedSize(170, 30)
        open_logs_button.clicked.connect(self.open_logs_folder)
        bottom_layout.addWidget(open_logs_button)

        main_layout.addLayout(bottom_layout)

    def set_icon_group(self):
        icon_group = QGroupBox("Icons")

        icon_font = QFont(self.fontText)
        icon_font.setBold(True)
        icon_font.setPointSize(14)
        icon_group.setFont(icon_font)

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

        text = QLabel(
            """<b>Locked:</b> This talent is mutually exclusive with another. The tooltip will show which talent is mutually exclusive."""
        )
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

        text = QLabel(
            """<b>Locked Important:</b> This talent is mutually exclusive with another talent that is needed for the build. Be careful with this talent because it's going to lock you out of a needed talent. The tooltip will show which talent needed for this build will get locked out if you pick this talent."""
        )
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

        text = QLabel(
            """<b>Important:</b> This talent is needed to get a different talent from the build. The tooltip will show which build talent wants this talent."""
        )
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

        text = QLabel(
            """<b>Important Shrine:</b> This talent is needed to get a shrine talent from the build. The tooltip will show which shrine build talent wants this talent."""
        )
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

        text = QLabel(
            """<b>Shrine:</b> This talent can only be obtained pre-shrine meaning that you can only get it before Shrine of Order. You might want to prioritize them if they are needed for the build."""
        )
        text.setFont(self.fontText)
        text.setWordWrap(True)
        layout.addWidget(text, 1)

        icon_layout.addLayout(layout)

        return icon_group

    def set_tutorial_group(self):
        tutorial_group = QGroupBox("Tutorial")

        tutorial_font = QFont(self.fontText)
        tutorial_font.setBold(True)
        tutorial_font.setPointSize(14)
        tutorial_group.setFont(tutorial_font)

        tutorial_group.setStyleSheet("color: rgb(255, 255, 255);")
        layout = QVBoxLayout(tutorial_group)

        text = QLabel(
            """First add a New Build with the <b>Add Button</b>. While having <b>Roblox - Deepwoken</b> open, have the cards on screen/open and press the hotkey from <b>Settings</b>. This will take a screenshot of the game, extract the location of the title with AI and then will use OCR to detect the text. Finally it will show the card data on the Helper. <b>The cards in orange are needed for the selected build</b>"""
        )
        text.setFont(self.fontText)
        text.setWordWrap(True)
        layout.addWidget(text)

        return tutorial_group

    def open_logs_folder(self):
        from deepwokenhelper.logging import LOG_FOLDER

        if os.path.exists(LOG_FOLDER):
            try:
                if sys.platform == "win32":
                    os.startfile(LOG_FOLDER)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", LOG_FOLDER])
                else:
                    subprocess.Popen(["xdg-open", LOG_FOLDER])
            except Exception as e:
                logger.error(f"Failed to open logs folder: {e}")
        else:
            logger.warning("Logs folder does not exist.")


class ScreenshotMethod(Enum):
    AUTOMATIC = 0
    BITBLT = 1
    WGC = 2


class SettingsWindow(QWidget):
    def __init__(self, stats: ControlPanel):
        super().__init__()

        self.stats = stats
        self.hotkeys = stats.helper.ocr.hotkeys
        self.settings = stats.helper.settings

        self.fontText = QFont()
        self.fontText.setPointSize(12)

        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon("./assets/icons/favicon.png"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        main_widget = QWidget()
        main_widget.setObjectName("Settings")
        main_widget.setStyleSheet(
            "#Settings { background-image: url(./assets/gui/background.png); } "
        )

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
        hotkey_group.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
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

        layout = QHBoxLayout()
        label = QLabel("Screenshot Method:")
        label.setFont(self.fontText)
        label.setStyleSheet("color: rgb(255, 255, 255);")
        layout.addWidget(label, 0)

        self.comboBox = QComboBox()
        self.comboBox.addItem("Automatic", ScreenshotMethod.AUTOMATIC)
        self.comboBox.addItem("BitBlt (Windows 7+)", ScreenshotMethod.BITBLT)
        self.comboBox.addItem("WGC (Windows 10+ | Yellow Bars)", ScreenshotMethod.WGC)

        screenshotMethod = self.settings.value(
            "screenshotMethod", ScreenshotMethod.AUTOMATIC, ScreenshotMethod
        )
        self.comboBox.setCurrentIndex(screenshotMethod.value)

        stylesheet = f"""
            QComboBox {{
                font-size: {self.fontText.pointSize()}px;
                padding: 0px 0px 0px 0px;
                padding-left: 3px;
            }}
        """

        self.comboBox.setStyleSheet(stylesheet)
        layout.addWidget(self.comboBox, 1)

        main_layout.addLayout(layout)
        main_layout.addStretch()

        main_layout.addItem(QSpacerItem(0, 0, vPolicy=QSizePolicy.Policy.Expanding))

        QBtn = (
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

        buttonBox = QDialogButtonBox(QBtn)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        main_layout.addWidget(buttonBox)

    def load_settings(self):
        logger.info("Loading settings")

        checked = self.settings.value("giveFocus", False, bool)
        self.checkBox.setChecked(checked)

        key_sequence = self.settings.value(
            "screenshotHotkey1", QKeySequence("J"), QKeySequence
        )
        self.keySequence1.setKeySequence(key_sequence)

        key_sequence = self.settings.value("screenshotHotkey2", QKeySequence())
        self.keySequence2.setKeySequence(key_sequence)

        screenshotMethod = self.settings.value(
            "screenshotMethod", ScreenshotMethod.AUTOMATIC, ScreenshotMethod
        )
        self.comboBox.setCurrentIndex(screenshotMethod.value)

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
        self.settings.setValue("screenshotMethod", self.comboBox.currentData())
        logger.info("Settings changes saved.")

        self.hide()

    def reject(self):
        self.hide()
