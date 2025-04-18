import re
import subprocess
from enum import StrEnum


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
        # Verify blueutil is available
        try:
            subprocess.run(["blueutil", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "blueutil is not installed. Please install it using 'brew install blueutil'"
            )

    def __str__(self):
        output = ""
        for device in self._devices:
            output += f"{device.mac}    {device.description}    {device.connection_state}\n"
        return output

    def to_str(self):
        return self.__str__()

    def get_devices_info(self) -> list[DeviceState]:
        self._get_all_available_device_descriptions()
        self._get_connection_states()
        return self._devices

    def run_scan(self) -> None:
        # blueutil inquiry with 10 second timeout (default)
        subprocess.run(["blueutil", "--inquiry"], capture_output=True, text=True)

    def connect_device(self, mac: str) -> None:
        result = subprocess.run(
            ["blueutil", "--connect", self._format_mac(mac)], capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to connect to device {mac}: {result.stderr}")

    def disconnect_device(self, mac: str) -> None:
        result = subprocess.run(
            ["blueutil", "--disconnect", self._format_mac(mac)], capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to disconnect device {mac}: {result.stderr}")

    def _get_all_available_device_descriptions(self) -> None:
        self._devices.clear()

        # Get paired devices
        result = subprocess.run(
            ["blueutil", "--paired", "--format", "json"], capture_output=True, text=True
        )

        if result.returncode != 0:
            print("Cannot get paired bluetooth devices")
            return

        try:
            import json

            devices = json.loads(result.stdout)
            for device in devices:
                if self._is_it_eeg_device(device.get("name", "")):
                    self._devices.append(
                        DeviceState(
                            mac=device["address"],
                            description=device.get("name", "Unknown"),
                            connection_state=ConnectionState.UNKNOWN,
                        )
                    )
        except json.JSONDecodeError:
            print("Error parsing device information")

    def _format_mac(self, mac: str) -> str:
        """Convert MAC address to format expected by blueutil (colon-separated)"""
        # Remove any existing separators
        mac = mac.replace("-", "").replace(":", "")
        # Insert colons
        return ":".join(mac[i : i + 2] for i in range(0, len(mac), 2))

    def _is_valid_mac_address(self, mac: str) -> bool:
        mac_regex = re.compile(r"^(?:[0-9A-Fa-f]{2}([:-]))(?:[0-9A-Fa-f]{2}\1){4}[0-9A-Fa-f]{2}$")
        return bool(mac_regex.match(mac))

    def _is_device_connected(self, mac: str) -> bool:
        result = subprocess.run(
            ["blueutil", "--is-connected", self._format_mac(mac)], capture_output=True, text=True
        )
        return result.stdout.strip() == "1"

    def _is_it_eeg_device(self, name: str) -> bool:
        target_names = ["BA MINI"]
        return name in target_names or any(sub in name for sub in target_names)

    def _get_connection_states(self) -> None:
        for device in self._devices:
            if self._is_device_connected(device.mac):
                device.connection_state = ConnectionState.CONNECTED
            else:
                device.connection_state = ConnectionState.DISCONNECTED
