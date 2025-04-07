from brainaccess import core
from brainaccess.core.eeg_manager import EEGManager

from eeg.battery_status import BatteryStatus


class EEGDeviceInterface:
    def __init__(self):
        core.init()
        self.manager = EEGManager()

    """ Battery management """

    def get_battery_status(self) -> BatteryStatus:
        info = self.manager.get_battery_info()
        return BatteryStatus(
            level=info.level,
            is_charging=info.is_charging,
            is_charger_connected=info.is_charger_connected,
        )
