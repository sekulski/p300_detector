import argparse

from scripts.macOS.bluetooth_utils_macOS import DevicesManager


def main():
    parser = argparse.ArgumentParser(description="Bluetooth Device Management")
    parser.add_argument("--list", action="store_true", help="List all EEG devices")
    parser.add_argument("--scan", action="store_true", help="Scan for devices")
    parser.add_argument("--connect", metavar="MAC", help="Connect to a device")
    parser.add_argument("--disconnect", metavar="MAC", help="Disconnect from a device")

    args = parser.parse_args()
    manager = DevicesManager()

    if args.scan:
        print("Scanning for devices...")
        manager.run_scan()

    if args.list:
        devices = manager.get_devices_info()
        if devices:
            print("Found devices:")
            print(manager)
        else:
            print("No devices found")

    if args.connect:
        manager.connect_device(args.connect)
        print(f"Connected to {args.connect}")

    if args.disconnect:
        manager.disconnect_device(args.disconnect)
        print(f"Disconnected from {args.disconnect}")


if __name__ == "__main__":
    main()
