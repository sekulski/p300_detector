from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
)
import time

import sys
from gui.gui_utils import get_centered_geometry
from scripts.bluetooth_utils import DevicesManager, ConnectionState

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window general properties
        title = "🧠 P300 / EEG"
        win_width = 800
        win_height = 600
        centre = get_centered_geometry(width=win_width, height=win_height)

        self.setWindowTitle(title)
        self.setGeometry(centre)
        self.setMinimumSize(QSize(win_width, win_height))

        # Icon
        self.setWindowIcon(QIcon("resources/icon.png"))

        # Widgets
        self.button_detect_devices: QPushButton = QPushButton("Detect bt devices")
        self.button_clear_devices_list: QPushButton = QPushButton("Clear")
        self.devices_list = QListWidget()

        # Signals
        self.button_detect_devices.clicked.connect(self.detect_devices)
        self.button_clear_devices_list.clicked.connect(self.clear_devices_list)

        self.devices_list.itemDoubleClicked.connect(self.toggle_device_connection)

        # Layout
        detection_layout = QVBoxLayout()
        detection_layout.addWidget(self.button_detect_devices)
        detection_layout.addWidget(self.button_clear_devices_list)
        detection_layout.addWidget(self.devices_list)

        # Aggregate all layouts
        content_panel = QWidget()
        content_panel.setLayout(detection_layout)

        self.setCentralWidget(content_panel)
        self.bt_devices_manager = DevicesManager()
        self.bt_devices_info = []

    def detect_devices(self):
        self.bt_devices_manager.run_scan()
        self.update_devices_list()

    def update_devices_list(self):
        self.devices_list.clear()
        devices = self.bt_devices_manager.get_devices_info()

        for device in devices:
            item = QListWidgetItem(f"{device.mac}    {device.description}    {device.connection_state}")
            item.setData(Qt.ItemDataRole.UserRole, {"mac": device.mac, "status": device.connection_state})
            self.bt_devices_info.append(item)
            self.devices_list.addItem(item)

    def clear_devices_list(self):
        self.devices_list.clear()

    def toggle_device_connection(self, item):
        metadata = item.data(Qt.ItemDataRole.UserRole)
        if metadata:
            mac = metadata.get("mac")
            status = metadata.get("status")
            if (status == ConnectionState.CONNECTED):
                self.bt_devices_manager.disconnect_device(mac)
            else:
                self.bt_devices_manager.connect_device(mac)
        self.update_devices_list()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
