import threading
import time
from typing import Callable, Union

from brainaccess import core
from brainaccess.core import eeg_channel
from brainaccess.core.eeg_manager import EEGManager
from brainaccess.core.gain_mode import GainMode
from brainaccess.utils.exceptions import BrainAccessException

from eeg.battery_status import BatteryStatus
from eeg.caps import Cap
from eeg.device_features import DeviceFeatures
from eeg.device_info import DeviceInfo
from eeg.device_version import DeviceVersion
from eeg.eeg_data_recorder import EEGDataRecorder


class EEGDeviceInterfaceError(Exception):
    def __init__(self, message: str):
        super().__init__(f"EEGDeviceInterfaceError: {message}")


class EEGDeviceInterface:
    def __init__(self, device_name: str, adapter_number: int):
        core.init()
        core.config_set_adapter_index(adapter_number)

        self._manager = EEGManager()
        self._device_name = device_name
        self._adapter_number = adapter_number
        self._device_features = DeviceFeatures()
        self._eeg_data_recorder = EEGDataRecorder()
        self._eeg_data_ready = False
        self._lock = threading.Lock()
        self._scanned_devices = []

    def close(self):
        print("Device will be disconnect")
        self.disconnect()
        time.sleep(1)  # TODO: Nasty workaround to allow BLE callbacks to finish before shutdown
        core.close()

    def connect(self):
        with self._lock:
            self._scan_for_devices()

            if not any(self._device_name in dev.name for dev in self._scanned_devices):
                raise EEGDeviceInterfaceError("Device not found")

            status = self._manager.connect(self._device_name)
            if status == 1:
                raise EEGDeviceInterfaceError("Connection failed")
            if status == 2:
                raise EEGDeviceInterfaceError("Stream is incompatible. Update the firmware.")

    def is_connected(self) -> bool:
        with self._lock:
            return self._manager.is_connected()

    def disconnect(self):
        with self._lock:
            self._manager.disconnect()

    """ Device status and hardware information """

    def get_sample_frequency(self) -> int:
        with self._lock:
            if self._manager.is_connected():
                return self._manager.get_sample_frequency()
            raise EEGDeviceInterfaceError("Device was not connected yet")

    def get_device_info(self) -> DeviceInfo:
        with self._lock:
            if self._manager.is_connected():
                info = self._manager.get_device_info()
                device_model = info.device_model
                hw_version = DeviceVersion(
                    major=info.hardware_version.major,
                    minor=info.hardware_version.minor,
                    patch=info.hardware_version.patch,
                )
                sw_version = DeviceVersion(
                    major=info.firmware_version.major,
                    minor=info.firmware_version.minor,
                    patch=info.firmware_version.patch,
                )
                serial_number = info.serial_number

                return DeviceInfo(
                    device_model=device_model,
                    hardware_version=hw_version,
                    software_version=sw_version,
                    serial_number=serial_number,
                )
            raise EEGDeviceInterfaceError("Device was not connected yet")

    def get_device_name(self) -> str:
        with self._lock:
            if self._manager.is_connected():
                return self._device_name
            return ""

    def get_device_mac(self) -> str:
        with self._lock:
            if self._manager.is_connected():
                for dev in self._scanned_devices:
                    if self._device_name in dev.name:
                        return dev.mac_address
            return ""

    def get_battery_status(self) -> BatteryStatus:
        with self._lock:
            if self._manager.is_connected():
                info = self._manager.get_battery_info()
                return BatteryStatus(
                    level=info.level,
                    is_charging=info.is_charging,
                    is_charger_connected=info.is_charger_connected,
                )
            raise EEGDeviceInterfaceError("Device was not connected yet")

    """ Cap-related utilities and validation functions """

    def electrode_count_matches_cap(self, cap: Cap) -> bool:
        with self._lock:
            self._update_device_features()
            return len(cap.mapping) == self._device_features.electrode_count

    """ EEG data streaming """

    def start_stream(self) -> None:
        self._eeg_data_ready = False
        if not self._manager.is_streaming():
            self._disable_all_channels()
            self._enable_all_channels()
            print("Manager not started, so it will be.")
            self._eeg_data_recorder.set_sampling_rate(self.get_sample_frequency())
            print("Sampling rate was set")
            self._manager.set_callback_chunk(self._eeg_data_recorder.process_chunk)

            # SDK has a problem with calling callback passed to the start/stop stream functions
            if self._manager.start_stream():
                print("Stream was successfully started")
            else:
                print("There was a problem with starting stream")

    def stop_stream(self) -> None:
        if self._manager.is_streaming():
            # SDK has a problem with calling callback passed to the start/stop stream functions
            if self._manager.stop_stream():
                self._on_stream_stopped()
            else:
                self._disable_all_channels()
        else:
            print("Manager is not streaming yet")

    def save_stream_to_file(self, path: str) -> None:
        if self._eeg_data_ready:
            print(f"Stream will be saved to the: {path}")
            self._eeg_data_recorder.save_to_csv(path)
        else:
            print("EEG data not ready yet.")

    def is_stream_data_ready(self):
        return self._eeg_data_ready

    def _enable_all_channels(self):
        for ch in range(self._device_features.electrode_count):
            ch_id = eeg_channel.ELECTRODE_MEASUREMENT + ch
            self._manager.set_channel_enabled(ch_id, True)
            self._manager.set_channel_gain(ch_id, GainMode.X12)

        self._manager.set_channel_enabled(eeg_channel.SAMPLE_NUMBER, True)
        self._manager.set_channel_enabled(eeg_channel.STREAMING, True)

    def _disable_all_channels(self):
        for ch in range(self._device_features.electrode_count):
            ch_id = eeg_channel.ELECTRODE_MEASUREMENT + ch
            self._manager.set_channel_enabled(ch_id, False)

        self._manager.set_channel_enabled(eeg_channel.SAMPLE_NUMBER, False)
        self._manager.set_channel_enabled(eeg_channel.STREAMING, False)

    """ Callbacks """

    def _on_stream_stopped(self):
        print("Stream stopped")
        self._disable_all_channels()
        self._eeg_data_ready = True

    """ Device connection """

    def _scan_for_devices(self) -> None:
        try:
            self._scanned_devices = core.scan()
        except BrainAccessException as e:
            raise EEGDeviceInterfaceError(f"Device scan failed due to SDK error: {e}") from e

    """ Utils """

    def _update_device_features(self) -> None:
        features = self._manager.get_device_features()
        self._device_features.has_gyro = features.has_gyro()
        self._device_features.has_accel = features.has_accel()
        self._device_features.is_bipolar = features.is_bipolar()
        self._device_features.electrode_count = features.electrode_count()

    def set_callback_battery(self, callback: Union[Callable, None] = None) -> None:
        if callback is not None:
            self._manager.set_callback_battery(callback)
