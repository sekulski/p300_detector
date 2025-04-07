from brainaccess import core
from brainaccess.core.eeg_manager import EEGManager
from brainaccess.utils.exceptions import BrainAccessException

from eeg.battery_status import BatteryStatus
from eeg.caps import Cap
from eeg.device_features import DeviceFeatures


class EEGDeviceInterfaceError(Exception):
    def __init__(self, message: str):
        super().__init__(f"EEGDeviceInterfaceError: {message}")


class EEGDeviceInterface:
    def __init__(self, device_name: str, adapter_number: int):
        core.init()
        self.manager = EEGManager()
        self.device_name = device_name
        self.adapter_number = adapter_number
        self.device_features = DeviceFeatures()

    def __del__(self):
        self.disconnect()

    def connect(self):
        self._scan_for_devices()
        status = self.manager.connect(self._get_device_index())
        if status == 1:
            raise EEGDeviceInterfaceError("Connection failed")
        if status == 2:
            raise EEGDeviceInterfaceError("Stream is incompatible. Update the firmware.")

    def disconnect(self):
        self.manager.disconnect()

    """ Cap-related utilities and validation functions """

    def electrode_count_matches_cap(self, cap: Cap) -> bool:
        self._update_device_features()
        return len(cap.mapping) == self.device_features.electrode_count

    """ Battery management """

    def get_battery_status(self) -> BatteryStatus:
        # ToDo: Check if there is a connection do the device
        info = self.manager.get_battery_info()
        return BatteryStatus(
            level=info.level,
            is_charging=info.is_charging,
            is_charger_connected=info.is_charger_connected,
        )

    """ Device connection """

    def _scan_for_devices(self) -> None:
        try:
            core.scan(self.adapter_number)
        except BrainAccessException as e:
            raise EEGDeviceInterfaceError(f"Device scan failed due to SDK error: {e}") from e

    def _get_device_index(self) -> int:
        for device_index in range(core.get_device_count()):
            if self.device_name in core.get_device_name(device_index):
                return device_index

        raise EEGDeviceInterfaceError("Device not found")

    """ Utils """

    def _update_device_features(self) -> None:
        features = self.manager.get_device_features()
        self.device_features.has_gyro = features.has_gyro()
        self.device_features.has_accel = features.has_accel()
        self.device_features.is_bipolar = features.is_bipolar()
        self.device_features.electrode_count = features.electrode_count()
