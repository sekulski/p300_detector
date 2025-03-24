from enum import StrEnum
import subprocess
import time


class ConnectionState(StrEnum):
    UNKNOWN = "unknown"
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class DeviceState:
    def __init__(self, mac: str, description: str, connection_state: ConnectionState):
        self.mac = mac
        self.description = description
        self.connection_state = connection_state


class DevicesManager:
    def __init__(self):
        self._devices: list[DeviceState] = []

    def __str__(self):
        output = ""

        for device in self._devices:
            output+=f"{device.mac}    {device.description}    {device.connection_state}\n"

        return output

    def to_str(self):
        return self.__str__()

    def get_devices_info(self) -> list[DeviceState]:
        return self._devices

    def run(self):
        self._scan_devices()
        self._get_all_available_device_descriptions()
        self._get_connection_states()

    def connect_device(self, mac: str) -> None:
        # ToDo: Check whether succeed. Update connection info
        result = subprocess.run(
            ["bluetoothctl", "connect", mac],
            capture_output=True,
            text=True
        )

    def disconnect_device(self, mac: str) -> None:
        # ToDo: Check whether succeed. Update connection info
        result = subprocess.run(
            ["bluetoothctl", "disconnect", mac],
            capture_output=True,
            text=True
        )


    def _get_all_available_device_descriptions(self) -> None:
        result = subprocess.run(
            ["bluetoothctl", "devices"],
            capture_output=True,
            text=True
        )

        if result.returncode:
            print("Cannot scan bluetooth devices")

        for description in result.stdout.strip().split('\n'):
            detected_mac = self._extract_mac(text=description)
            device_name = self._extract_device_name(text=description)
            # ToDo: Add MAC validation
            self._devices.append(DeviceState(detected_mac, device_name, ConnectionState.UNKNOWN))

    def _extract_mac(self, text: str) -> str:
        mac_pos = 1
        parts = text.split(" ")
        if len(parts) >= 2 and parts[0] == "Device":
            return parts[mac_pos]

        return ""

    def _extract_device_name(self, text: str) -> str:
        device_name_pos = 2
        parts = text.split(" ")
        if len(parts) >= 2 and parts[0] == "Device":
            return " ".join(parts[device_name_pos:len(parts)])

        return ""

    def _is_device_connected(self, mac: str) -> bool:
        result = subprocess.run(
            ["bluetoothctl", "info", mac],
            capture_output=True,
            text=True
        )
        return "Connected: yes" in result.stdout

    def _get_connection_states(self) -> None:
        for device in self._devices:
            if self._is_device_connected(device.mac):
                device.connection_state = ConnectionState.CONNECTED
            else:
                device.connection_state = ConnectionState.DISCONNECTED

    def _scan_devices(self) -> None:
        subprocess.run(["bluetoothctl", "scan", "on"])
        time.sleep(5)
        subprocess.run(["bluetoothctl", "scan", "off"])
