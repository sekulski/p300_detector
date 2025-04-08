from eeg.caps import Cap, eeg_caps


class CapManager:
    def __init__(self):
        self.caps=eeg_caps

    def get_caps_available_for_device(self, device_name: str) -> list[Cap]:
        result = []
        for cap in self.caps:
            if cap.cap_type in device_name:
                result.append(cap)

        return result

