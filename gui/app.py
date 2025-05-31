import logging
import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)
from status_bar.ui_status_bar import UiStatusBar

from eeg.caps_manager import CapManager
from eeg.eeg_device_interface import EEGDeviceInterface
from gui.gui_utils import get_centered_geometry
from scripts.bluetooth_utils import ConnectionState, DevicesManager

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = None
        logging.basicConfig(level=logging.DEBUG)

        self.status_bar = UiStatusBar()
        self.setStatusBar(self.status_bar)

        self.bt_devices_manager = DevicesManager()
        self.eeg_cap_manager = CapManager()
        self.bt_devices_info = []

        # Window general properties
        title = "🧠 P300 / EEG"
        win_width = 800
        win_height = 300
        centre = get_centered_geometry(width=win_width, height=win_height)

        self.setWindowTitle(title)
        self.setGeometry(centre)
        self.setMinimumSize(QSize(win_width, win_height))

        # Icon
        self.setWindowIcon(QIcon("resources/icon.png"))

        # Widgets - Detection
        self.button_detect_devices: QPushButton = QPushButton("Detect bt devices")
        self.button_clear_devices_list: QPushButton = QPushButton("Clear")

        # Widgets - Choose and maintain device connection
        self.devices_radio_groupbox = QGroupBox("Chosen device")

        self.devices_radio_children_layout = QVBoxLayout()
        self.devices_radio_groupbox.setLayout(self.devices_radio_children_layout)

        self.devices_radio_buttons_group = QButtonGroup(self)
        self.devices_radio_buttons_group.setExclusive(True)
        self.devices_radio_buttons_group.buttonClicked.connect(self.device_radio_selected)

        self.devices_list_label = QLabel("Detected devices: ")
        self.devices_list = QListWidget()

        # Widgets - Caps
        self.cap_label = QLabel("Cap type: ")
        self.cap_label.setMaximumWidth(60)
        self.cap_list = QComboBox()

        # Signals
        self.button_detect_devices.clicked.connect(self.detect_devices)
        self.button_clear_devices_list.clicked.connect(self.clear_devices_list)
        self.devices_list.itemDoubleClicked.connect(self.toggle_device_connection)

        # Layout - General
        general_layout = QVBoxLayout()

        # Layouts - Detection
        detection_buttons_layout = QHBoxLayout()
        detection_buttons_layout.addWidget(self.button_detect_devices)
        detection_buttons_layout.addWidget(self.button_clear_devices_list)

        # Layouts - Choose and maintain device connection
        detection_device_section_layout = QHBoxLayout()
        detection_device_section_layout.addWidget(self.devices_radio_groupbox)

        detection_layout = QVBoxLayout()
        detection_layout.addWidget(self.devices_list_label)
        detection_layout.addWidget(self.devices_list)

        detection_device_section_layout.addLayout(detection_layout)

        # Layout - Caps
        cap_layout = QHBoxLayout()
        cap_layout.addWidget(self.cap_label)
        cap_layout.addWidget(self.cap_list)

        # Aggregate all layouts
        general_layout.addLayout(detection_buttons_layout)
        general_layout.addLayout(detection_device_section_layout)
        general_layout.addLayout(cap_layout)

        content_panel = QWidget()
        content_panel.setLayout(general_layout)

        self.setCentralWidget(content_panel)

    def detect_devices(self):
        self.bt_devices_manager.run_scan()
        self.update_devices_list()

    def remove_radio_options(self):
        layout = self.devices_radio_groupbox.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

    def update_devices_radio_options_number(self):
        self.remove_radio_options()
        layout = self.devices_radio_groupbox.layout()

        for button in self.devices_radio_buttons_group.buttons():
            self.devices_radio_buttons_group.removeButton(button)

        for metadata in self.bt_devices_info:
            radio = QRadioButton(metadata["description"])
            radio.setObjectName(metadata["mac"])
            layout.addWidget(radio, alignment=Qt.AlignmentFlag.AlignTop)
            self.devices_radio_buttons_group.addButton(radio)

    def update_devices_list(self):
        self.bt_devices_info.clear()
        self.devices_list.clear()
        devices = self.bt_devices_manager.get_devices_info()
        logger.debug("GUI: update_devices_list - refresh controllers")

        for device in devices:
            logger.debug("GUI: device add %s", device.description)

            item = QListWidgetItem(
                f"{device.mac}    {device.description}    {device.connection_state}"
            )
            item.setData(
                Qt.ItemDataRole.UserRole,
                {
                    "mac": device.mac,
                    "status": device.connection_state,
                    "description": device.description,
                },
            )
            self.bt_devices_info.append(
                {
                    "mac": device.mac,
                    "description": device.description,
                    "status": device.connection_state,
                }
            )
            self.devices_list.addItem(item)
            self.update_devices_radio_options_number()

    def clear_devices_list(self):
        self.devices_list.clear()

    def toggle_device_connection(self, item):
        metadata = item.data(Qt.ItemDataRole.UserRole)
        if metadata:
            status = metadata.get("status")
            description = metadata.get("description")
            if status == ConnectionState.CONNECTED:
                self.manager.disconnect()
                self.status_bar.set_connection_status(False, self.manager)
            else:
                self.manager = EEGDeviceInterface(description, 0)
                self.manager.connect()
                self.status_bar.set_connection_status(True, self.manager)

        self.update_devices_list()

    def device_radio_selected(self, button):
        self.cap_list.clear()
        caps = self.eeg_cap_manager.get_caps_available_for_device(button.text())
        self.cap_list.addItems([cap.name for cap in caps])


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
