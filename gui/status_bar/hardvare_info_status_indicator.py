from device_info import DeviceInfo
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class HardwareStatusIndicator(QLabel):
    def __init__(self, font: QFont):
        super().__init__()
        self.connected = False
        self.name = ""
        self.mac = ""
        self.setFont(font)
        self.setText("\uf2db")  # chip
        #   tooltip frame
        self.tooltip = QFrame()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 6, 8, 6)  # padding
        layout.setSpacing(4)

        self.tooltip.setLayout(layout)
        self.tooltip.setAutoFillBackground(True)
        self.tooltip.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        # Add labels
        self.label_status_label = QLabel(
            "Status: Connected" if self.connected else "Status: Disconnected"
        )

        self.mac_label = QLabel("MAC: ")
        self.name_label = QLabel("Name: ")
        self.model_label = QLabel("Model: ")
        self.sw_label = QLabel("SW: ")
        self.hw_label = QLabel("HW: ")
        self.serial_label = QLabel("Serial: ")
        layout.addWidget(self.mac_label)
        layout.addWidget(self.name_label)
        layout.addWidget(self.model_label)
        layout.addWidget(self.sw_label)
        layout.addWidget(self.hw_label)
        layout.addWidget(self.serial_label)
        layout.addWidget(self.label_status_label)
        self.setMouseTracking(True)
        self.mouseMoveEvent = self._show_hardware_tooltip
        self.leaveEvent = lambda event: self.tooltip.hide()

    def _show_hardware_tooltip(self, event):
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self.tooltip.move(pos + QPoint(0, 8))
        self.tooltip.show()

    def updated_data(self, info: DeviceInfo, connected: bool):
        self.label_status_label.setText(
            "Status: Connected" if self.connected else "Status: Disconnected"
        )
        self.mac_label.setText("MAC: " + self.mac)
        self.name_label.setText("Name: " + self.name)
        self.model_label.setText("Model: " + str(info.device_model))
        self.sw_label.setText("SW: " + str(info.software_version))
        self.hw_label.setText("HW: " + str(info.hardware_version))
        self.serial_label.setText("Serial: " + str(info.serial_number))
