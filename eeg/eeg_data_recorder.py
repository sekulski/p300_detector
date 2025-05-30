import numpy as np

# ToDo: Few things. It should have an option to propagate data to GUI
# ToDo: At next stage, it should be propagated in real time


class EEGDataRecorder:
    def __init__(self, sampling_rate: int = 250):
        self._buffer = []
        self._sampling_rate = sampling_rate

    def set_sampling_rate(self, sampling_rate: int):
        self._sampling_rate = sampling_rate

    def process_chunk(self, chunk_arrays, size):
        samples = np.array(chunk_arrays).T
        self._buffer.extend(samples)

    def save_to_edf(self, output_path: str):
        pass

    def save_to_csv(self, output_path: str):
        with open(output_path, "w") as file:
            for row in self._buffer:
                file.write(",".join(map(str, row)) + "\n")

    def clear(self):
        self._buffer.clear()
