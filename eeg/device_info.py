from eeg.device_model import DeviceModel
from eeg.device_version import DeviceVersion


class DeviceInfo:
    def __init__(
        self,
        device_model=DeviceModel.UNKNOWN,
        hardware_version=None,
        software_version=None,
        serial_number=0,
    ):
        # Device model (enum)
        self.device_model = device_model
        # Hardware version (Version object)
        self.hardware_version = hardware_version or DeviceVersion()
        # Firmware version (Version object)
        self.software_version = software_version or DeviceVersion()
        # Device serial number
        self.serial_number = serial_number
