from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QApplication,
    QListWidget,
    QMainWindow,
    QPushButton,
    QWidget,
    QVBoxLayout,
)
import sys
from gui.gui_utils import get_centered_geometry
from scripts.bluetooth_utils import DevicesManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window general properties
        title = "🧠 P300 / EEG GUI – PoC"
        win_width = 800
        win_height = 600
        centre = get_centered_geometry(width=win_width, height=win_height)

        self.setWindowTitle(title)
        self.setGeometry(centre)
        self.setMinimumSize(QSize(win_width, win_height))

        # Widgets
        self.button_detect_devices: QPushButton = QPushButton("Detect connected devices")
        self.button_clear_devices_list: QPushButton = QPushButton("Clear")
        self.devices_list = QListWidget()

        # Signals
        self.button_detect_devices.clicked.connect(self.detect_devices)
        self.button_clear_devices_list.clicked.connect(self.clear_devices_list)

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
        #self.bt_devices_info = []

    def detect_devices(self):
        self.bt_devices_manager.run()
        devices = self.bt_devices_manager.get_devices_info()

        for device in devices:


        # I teraz ma być mapowanie. Każda pozycja z listy (descriptionów) ma być powiązana z określonym MAC-adressem


        self.devices_list.addItems()



    def clear_devices_list(self):
        self.devices_list.clear()

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
