from enum import StrEnum

_default_mini: dict = {
    0: "F3",
    1: "F4",
    2: "C3",
    3: "C4",
    4: "P3",
    5: "P4",
    6: "O1",
    7: "O2",
}

_dummy_smr_theta: dict = {
    3: "C4",  # Active
}

_dummy_beta_theta: dict = {
    2: "C3",  # Active
}


class CapType(StrEnum):
    UNKNOWN = "UNKNOWN"
    BA_HALLO = "BA HALO"
    BA_MINI = "BA MINI"
    BA_MIDI = "BA MIDI"
    BA_MAXI = "BA MAXI"


class Cap:
    def __init__(self, cap_map: dict, cap_type: StrEnum, config_name: str):
        self.mapping = cap_map
        self.cap_type = cap_type
        self.config_name = config_name

    def get_electrode_list(self):
        return list(self.mapping.values())


eeg_caps = [
    Cap(_default_mini, CapType.BA_MINI, "BA MINI - All electrodes"),
    Cap(_dummy_smr_theta, CapType.BA_MINI, "BA MINI - SMR/Theta"),
    Cap(_dummy_beta_theta, CapType.BA_MINI, "BA MINI - Beta/Theta"),
    Cap(_default_mini, CapType.UNKNOWN, "OpenBci - Gamma"),
]
