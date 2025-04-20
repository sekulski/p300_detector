import enum

from battery_status import BatteryStatus
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QLabel


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


def _get_battery_level(value: int):
    if value < 10:
        return BatteryLevel.L0
    elif value < 30:
        return BatteryLevel.L25
    elif value < 55:
        return BatteryLevel.L50
    elif value < 80:
        return BatteryLevel.L75
    return BatteryLevel.L100


def _get_charger_status(is_charging, is_charger_connected):
    if not is_charger_connected:
        return ChargingStatus.DISCONNECTED
    elif is_charging:
        return ChargingStatus.CHARGING
    else:
        return ChargingStatus.CONNECTED


class BatteryStatusUi(QLabel):
    def __init__(self, font: QFont):
        super().__init__()
        self.timer = None
        self.manager = None
        self.battery_level_value = -1
        self.setFont(font)

    def set_value(self, status: BatteryStatus):
        self.battery_level_value = status.level
        self._set_icons(
            _get_battery_level(status.level),
            _get_charger_status(status.is_charging, status.is_charger_connected),
        )

    def _set_icons(self, level: BatteryLevel, charging_status: ChargingStatus):
        self.setText(charging_status.value[0] + " " + level.value[0])
        self.setToolTip(charging_status.value[1] + "\n" + level.value[1])

    def stop_measurement(self):
        self._set_icons(BatteryLevel.UNKNOWN, ChargingStatus.DISCONNECTED)
        if self.timer:
            self.timer.stop()

    def start_measurement(self, manager):
        self.manager = manager
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.set_value(self.manager.get_battery_status()))
        self.timer.start(10000)  # 10 sec
