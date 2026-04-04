import eeg_ring_buffer as rb
import numpy as np


class EEGDataRecorder:
    def __init__(self, sampling_rate: int = 250, channels: int = 8):
        self._ring_buffer = rb.EegRingBuffer(
            sampling_rate=sampling_rate, capacity_seconds=60, no_of_channels=channels
        )
        self._overall_buffer = []

    def process_chunk(self, chunk_arrays, size) -> None:
        samples = np.array(chunk_arrays).T

        if samples.shape[0] != size:
            raise ValueError("Incorrect sample size")

        self._overall_buffer += samples
        self._ring_buffer.add_samples(samples)

    def save_to_edf(self, output_path: str):
        pass

    def save_to_csv(self, output_path: str) -> None:
        with open(output_path, "w") as file:
            for row in self._overall_buffer:
                file.write(",".join(map(str, row)) + "\n")

    def get_last_n_samples(self, no_of_samples: int) -> np.ndarray:
        return self._ring_buffer.get_last_n_samples(no_of_samples)

    def get_last_n_seconds(self, no_of_seconds: int) -> np.ndarray:
        return self._ring_buffer.get_last_n_seconds(no_of_seconds)

    def reset_recording(self) -> None:
        self._overall_buffer.clear()

    def clear_buffer(self) -> None:
        self._ring_buffer.clear()
