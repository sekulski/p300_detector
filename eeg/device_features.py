class DeviceFeatures:
    def __init__(self, has_gyro=False, has_accel=False, is_bipolar=False, electrode_count=0):
        # True if the device has a gyroscope, False otherwise.
        # Indicates whether the device can capture gyroscope data.
        self.has_gyro = has_gyro

        # True if the device has an accelerometer, False otherwise.
        # Indicates whether the device can capture accelerometer data.
        self.has_accel = has_accel

        # True if electrodes are bipolar, False otherwise.
        # Bipolar electrodes have separate positive (P) and negative (N) contacts.
        self.is_bipolar = is_bipolar

        # Number of EEG/EMG electrodes supported by the device.
        self.electrode_count = electrode_count
