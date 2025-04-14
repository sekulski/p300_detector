class DeviceVersion:
    def __init__(self, major=0, minor=0, patch=0):
        # API-breaking changes
        self.major = major
        # Feature updates
        self.minor = minor
        # Bugfixes
        self.patch = patch

    def __repr__(self):
        return f"{self.major}.{self.minor}.{self.patch}"
