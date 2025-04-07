class BatteryStatus:
    def __init__(self, level=0, is_charging=False, is_charger_connected=False):
        # Battery charge percentage, from 0 to 100.
        self.level = level

        # True if the battery is currently charging, False otherwise.
        self.is_charging = is_charging

        # True if a charger is connected to the device, False otherwise.
        self.is_charger_connected = is_charger_connected
