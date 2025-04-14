from eeg.caps import Cap, CapType
from eeg.eeg_device_interface import EEGDeviceInterface

# Electrode mapping for BA MINI
default_mini: dict = {
    0: "F3",
    1: "F4",
    2: "C3",
    3: "C4",
    4: "P3",
    5: "P4",
    6: "O1",
    7: "O2",
}

# Initialize device interface
manager = EEGDeviceInterface("BA MINI 002", 0)

try:
    print("Connecting to device...\n")
    manager.connect()

    # Get sample frequency
    sample_freq = manager.get_sample_frequency()
    print(f"Sample frequency: {sample_freq}\n")

    # Get device info
    device_info = manager.get_device_info()
    print("Device info:")
    print(f"\tModel: {device_info.device_model}")
    print(f"\tSoftware Version: {device_info.software_version}")
    print(f"\tHardware Version: {device_info.hardware_version}")
    print(f"\tSerial Number: {device_info.serial_number}\n")

    # Get battery status
    battery = manager.get_battery_status()
    print("Battery status:")
    print(f"\tLevel: {battery.level}")
    print(f"\tIs Charging: {battery.is_charging}")
    print(f"\tIs Charger Connected: {battery.is_charger_connected}\n")

    # Check cap compatibility
    default_cap = Cap(default_mini, CapType.BA_MINI, "BA MINI - All electrodes")
    print(f"Electrode cap compatibility: {manager.electrode_count_matches_cap(default_cap)}\n")

finally:
    # Ensure proper disconnection and cleanup
    print("Closing connection...")
    manager.close()
    print("Done.")
