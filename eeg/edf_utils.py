from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import numpy as np


@dataclass(slots=True)
class EdfChannelConfig:
    label: str
    unit: str = "uV"
    physical_min: float = -500.0
    physical_max: float = 500.0
    digital_min: int = -32768
    digital_max: int = 32767
    prefilter: str = "None"
    transducer_type: str = "EEG electrode"


@dataclass(slots=True)
class EdfRecordingMetadata:
    patient_id: str = ""
    recording_id: str = ""
    start_datetime: Optional[datetime] = None
    equipment: str = ""


@dataclass(slots=True)
class EegSessionData:
    samples: np.ndarray
    sampling_rate: int
    channels: list[EdfChannelConfig]
    metadata: EdfRecordingMetadata = field(default_factory=EdfRecordingMetadata)

    def validate(self) -> None:
        if not isinstance(self.samples, np.ndarray):
            raise TypeError("samples must be a NumPy array")

        if self.samples.ndim != 2:
            raise ValueError("samples must have shape (n_samples, n_channels)")

        if self.samples.shape[0] == 0:
            raise ValueError("samples cannot be empty")

        if self.samples.shape[1] == 0:
            raise ValueError("samples must contain at least one channel")

        if self.sampling_rate <= 0:
            raise ValueError("sampling_rate must be positive")

        if len(self.channels) != self.samples.shape[1]:
            raise ValueError(
                f"Number of channel configs ({len(self.channels)}) "
                f"does not match samples channel count ({self.samples.shape[1]})"
            )


def build_uniform_channel_configs(
    channel_labels: list[str],
    unit: str = "uV",
    physical_min: float = -500.0,
    physical_max: float = 500.0,
    digital_min: int = -32768,
    digital_max: int = 32767,
    prefilter: str = "",
    transducer_type: str = "",
) -> list[EdfChannelConfig]:
    return [
        EdfChannelConfig(
            label=label,
            unit=unit,
            physical_min=physical_min,
            physical_max=physical_max,
            digital_min=digital_min,
            digital_max=digital_max,
            prefilter=prefilter,
            transducer_type=transducer_type,
        )
        for label in channel_labels
    ]
