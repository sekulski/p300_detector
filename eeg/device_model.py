import enum


class DeviceModel(enum.Enum):
    MINI = 0  # BrainAccess MINI V2 (8 Channels)
    MIDI = 1  # BrainAccess MIDI (16 Channels)
    MAXI = 2  # BrainAccess MAXI (32 Channels)
    EMG = 3  # BrainAccess EMG
    HALO1 = 4  # BrainAccess Halo v1 (4 Channels)
    HALO = 5  # BrainAccess Halo v2 (4 Channels)
    UNKNOWN = 0xFF  # Unknown device
