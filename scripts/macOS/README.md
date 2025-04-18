# macOS Bluetooth Utilities

## Overview
On macOS, the `bluetoothctl` command-line tool is not available. Instead, we use `blueutil`, a CLI tool for managing Bluetooth on macOS that provides similar functionality.

## Requirements

1. Install `blueutil` using Homebrew:
```bash
brew install blueutil
```

## Implementation
The macOS-specific implementation is provided in two files:

1. `bluetooth_utils_macOS.py` - Core implementation using `blueutil`
2. `bluetooth_cli.py` - Command-line interface for testing and manual device management

## Testing the Implementation
You can use the CLI tool to test Bluetooth functionality:

```bash
# List all paired EEG devices
poetry run python bluetooth_cli.py list

# List only connected devices
poetry run python bluetooth_cli.py list --connected-only

# Scan for new devices
poetry run python bluetooth_cli.py scan

# Scan and list devices immediately after
poetry run python bluetooth_cli.py scan --list

# Connect to a specific device
poetry run python bluetooth_cli.py connect "00:11:22:33:44:55"

# Disconnect from a device
poetry run python bluetooth_cli.py disconnect "00:11:22:33:44:55"

# Check device status
poetry run python bluetooth_cli.py status "00:11:22:33:44:55"

# Show help and available commands
poetry run python bluetooth_cli.py --help
```

## Troubleshooting
If you encounter any issues:

1. Ensure `blueutil` is installed:
```bash
blueutil --version
```

2. Make sure Bluetooth is enabled on your Mac
3. Verify that your EEG device is in pairing mode
4. Check if the device appears in macOS Bluetooth preferences

## References
- [blueutil GitHub repository](https://github.com/toy/blueutil)


## TODO
- [ ] Add tests for bluetooth_utils_macOS.py
- [ ] consider defining adapters for different OSs
- [ ] adjsut main README.md
