from pathlib import Path
from typing import Optional

from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QLabel, QStatusBar
from status_bar.battery_status_indicator import BatteryStatusUi
from status_bar.hardvare_info_status_indicator import HardwareStatusIndicator

from eeg.device_info import DeviceInfo
from eeg.eeg_device_interface import EEGDeviceInterface


class UiStatusBar(QStatusBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.name = None
        self.mac = None
        self.connected = False
        self.device_info = DeviceInfo()
        self.setContentsMargins(10, 5, 10, 5)

        # Load FA font
        font_path = Path(__file__).resolve().parent / "../../resources/fa-solid-900.ttf"
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.fa_font = QFont(font_family)
        self.fa_font.setPointSize(16)

        self._setUpConnectionIndicator()
        self.battery_status = BatteryStatusUi(self.fa_font)
        self.addPermanentWidget(self.battery_status)
        self.hardware_icon = HardwareStatusIndicator(self.fa_font)
        self.addPermanentWidget(self.hardware_icon)

        self.set_connection_status(False, None)

    def set_connection_status(self, connected: bool, manager: Optional[EEGDeviceInterface]):
        self.connected = connected
        if not connected:
            self.battery_status.stop_measurement()
            self.device_info = DeviceInfo()

        else:
            self.battery_status.start_measurement(manager)
            self.device_info = manager.get_device_info()

        self.hardware_icon.updated_data(self.device_info, connected)
        icon_unicode = "\uf1eb" if connected else "\uf127"  # WiFi or Ban
        tooltip = "Connected" if connected else "Disconnected"
        self.conn_icon.setText(icon_unicode)
        self.conn_icon.setToolTip(tooltip)

    def _setUpConnectionIndicator(self):
        self.conn_icon = QLabel()
        self.conn_icon.setFont(self.fa_font)
        self.addPermanentWidget(self.conn_icon)
