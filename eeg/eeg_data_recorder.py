import numpy as np

from eeg.caps import Cap
from eeg.edf_exporter import EdfExporter
from eeg.edf_utils import (
    EdfRecordingMetadata,
    EegSessionData,
    build_uniform_channel_configs,
)
from eeg.eeg_ring_buffer import EegRingBuffer


class EEGDataRecorder:
    def __init__(self, sampling_rate: int, seconds: int, channels: int, cap: Cap):
        self._sampling_rate = sampling_rate
        self._channels = channels
        self._cap = cap
        self._ring_buffer = EegRingBuffer(
            sampling_rate=sampling_rate, capacity_seconds=seconds, no_of_channels=channels
        )
        self._overall_buffer = []

    def process_chunk(self, chunk_arrays, size) -> None:
        expected_eeg_channels = len(self._cap.get_electrode_list())
        samples = np.array(chunk_arrays, dtype=np.float32).T

        if samples.shape[0] != size:
            raise ValueError("Incorrect sample size")

        if samples.ndim != 2:
            raise ValueError(f"Chunk must be 2D, got shape {samples.shape}")

        if samples.shape[1] < expected_eeg_channels:
            raise ValueError(
                f"Chunk has too few channels: got {samples.shape[1]}, expected at least {expected_eeg_channels}"
            )

        samples = samples[:, :expected_eeg_channels]

        self._overall_buffer.append(samples.copy())
        self._ring_buffer.add_samples(samples)

    def save_to_edf(self, output_path: str) -> None:
        EdfExporter.export(session=self._build_session_data(), output_path=output_path)

    def _build_session_data(self) -> EegSessionData:
        electrode_labels = self._cap.get_electrode_list()

        if not self._overall_buffer:
            raise ValueError("No samples recorded")

        samples = np.vstack(self._overall_buffer).astype(np.float32)

        if samples.size == 0:
            raise ValueError("No samples recorded")

        if samples.ndim != 2:
            raise ValueError("Recorded samples must have shape (n_samples, n_channels)")

        if len(electrode_labels) != self._channels:
            raise ValueError(
                f"Cap electrode count ({len(electrode_labels)})"
                " does not match recorder channel count ({self._channels})"
            )

        if samples.shape[1] != self._channels:
            raise ValueError(
                f"Recorded data channel count ({samples.shape[1]})"
                " does not match recorder channel count ({self._channels})"
            )

        channel_configs = build_uniform_channel_configs(electrode_labels)
        metadata = EdfRecordingMetadata(equipment=self._cap.cap_type)

        return EegSessionData(
            samples=samples,
            sampling_rate=self._sampling_rate,
            channels=channel_configs,
            metadata=metadata,
        )

    def save_to_csv(self, output_path: str) -> None:
        if not self._overall_buffer:
            raise ValueError("No samples recorded")

        samples = np.vstack(self._overall_buffer).astype(np.float32)

        with open(output_path, "w") as file:
            for row in samples:
                file.write(",".join(map(str, row)) + "\n")

    def get_last_n_samples(self, no_of_samples: int) -> np.ndarray:
        return self._ring_buffer.get_last_n_samples(no_of_samples)

    def get_last_n_seconds(self, no_of_seconds: int) -> np.ndarray:
        return self._ring_buffer.get_last_n_seconds(no_of_seconds)

    def reset_recording(self) -> None:
        self._overall_buffer.clear()

    def clear_buffer(self) -> None:
        self._ring_buffer.clear()
