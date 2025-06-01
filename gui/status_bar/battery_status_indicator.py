import enum

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget

from eeg.battery_status import BatteryStatus
from eeg.eeg_device_interface import EEGDeviceInterface


class BatteryLevel(enum.Enum):
    UNKNOWN = ("\u003f", "Unknown")
    L100 = ("\uf240", "100%")
    L75 = ("\uf241", "75%")
    L50 = ("\uf242", "50%")
    L25 = ("\uf243", "25%")
    L0 = ("\uf244", "0%")


class ChargingStatus(enum.Enum):
    DISCONNECTED = ("\ue55e", "Disconnected")
    CONNECTED = ("\ue55b", "Connected, not charging")
    CHARGING = ("\ue55b", "Charging")


def _get_battery_level(value: int) -> BatteryLevel:
    if value < 10:
        return BatteryLevel.L0
    elif value < 30:
        return BatteryLevel.L25
    elif value < 55:
        return BatteryLevel.L50
    elif value < 80:
        return BatteryLevel.L75
    return BatteryLevel.L100


def _get_charger_status(is_charging, is_charger_connected) -> ChargingStatus:
    if not is_charger_connected:
        return ChargingStatus.DISCONNECTED
    elif is_charging:
        return ChargingStatus.CHARGING
    else:
        return ChargingStatus.CONNECTED


class BatteryStatusUi(QWidget):
    def __init__(self, font: QFont):
        super().__init__()
        self.timer = None
        self.manager = None
        self.battery_level_value = -1

        self.label_charger = QLabel()
        self.label_battery = QLabel()
        self.label_charger.setFont(font)
        self.label_battery.setFont(font)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(self.label_charger)
        layout.addWidget(self.label_battery)

        self.setLayout(layout)

    def start_measurement(self, manager: EEGDeviceInterface):
        self.manager = manager
        self.timer = QTimer()
        self.timer.timeout.connect(self._update)
        self.timer.start(10000)  # co 10s

        self._update()

    def stop_measurement(self):
        self._set_charger_status(ChargingStatus.DISCONNECTED)
        self._set_battery_level(BatteryLevel.UNKNOWN)
        if self.timer:
            self.timer.stop()

    def _update(self):
        status: BatteryStatus = self.manager.get_battery_status()
        self._set_battery_level(_get_battery_level(status.level))
        self._set_charger_status(
            _get_charger_status(status.is_charging, status.is_charger_connected)
        )

    def _set_charger_status(self, status: ChargingStatus):
        self.label_charger.setText(status.value[0])
        self.label_charger.setToolTip(f"Charger: {status.value[1]}")

    def _set_battery_level(self, level: BatteryLevel):
        self.label_battery.setText(level.value[0])
        self.label_battery.setToolTip(f"Battery: {level.value[1]}")
