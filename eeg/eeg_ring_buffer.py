import numpy as np


class EegRingBuffer:
    """
    Fixed-size ring buffer for EEG samples stored in samples x channels format.

    The buffer keeps the most recent data up to:
        sampling_rate * capacity_seconds

    When capacity is exceeded, the oldest samples are overwritten.

    Internal storage shape:
        (samples_capacity, no_of_channels)

    Public read methods return data in chronological order
    from oldest to newest within the requested range.
    """

    def __init__(self, sampling_rate: int, capacity_seconds: int, no_of_channels: int):
        """
        Initialize EEG ring buffer.

        Args:
            sampling_rate: Sampling frequency in Hz.
            capacity_seconds: Buffer capacity expressed in seconds.
            no_of_channels: Number of signal channels stored per sample.
        """
        self._sampling_rate = sampling_rate
        self._capacity_seconds = capacity_seconds
        self._no_of_channels = no_of_channels
        self._samples_capacity = self._sampling_rate * self._capacity_seconds
        self._no_of_valid_samples = 0
        self._write_pos = 0
        self._buffer = np.zeros((self._samples_capacity, self._no_of_channels), dtype=np.float32)

    def add_samples(self, samples: np.ndarray) -> None:
        """
        Add a chunk of samples to the ring buffer.

        Input must use samples x channels layout.

        Args:
            samples: 2D NumPy array of shape (n_samples, no_of_channels).
        """

        if samples.size == 0:
            return

        if samples.ndim != 2:
            raise ValueError("samples must be a 2D array in samples x channels format")

        if samples.shape[1] != self._no_of_channels:
            raise ValueError(f"Expected {self._no_of_channels} channels, got {samples.shape[1]}")

        if self._write_pos == self._samples_capacity:
            self._write_pos = 0

        samples_till_buffer_ends = self._samples_capacity - self._write_pos
        no_of_samples = samples.shape[0]

        if no_of_samples <= samples_till_buffer_ends:
            self._buffer[self._write_pos : self._write_pos + no_of_samples] = samples
            self._write_pos += no_of_samples
            self._no_of_valid_samples += no_of_samples
            if self._no_of_valid_samples > self._samples_capacity:
                self._no_of_valid_samples = self._samples_capacity

            if self._write_pos == self._samples_capacity:
                self._write_pos = 0
        else:
            head = samples[:samples_till_buffer_ends]
            tail = samples[samples_till_buffer_ends:]
            self.add_samples(head)
            self.add_samples(tail)

    def get_last_n_samples(self, no_of_samples: int) -> np.ndarray:
        """
        Return the most recent N samples.

        Returned data is ordered chronologically from oldest to newest
        within the selected range.

        Args:
            no_of_samples: Number of latest samples to return.

        Returns:
            NumPy array of shape (n, no_of_channels), where
            n = min(no_of_samples, current_number_of_valid_samples).
        """
        if no_of_samples <= 0:
            raise ValueError("No of samples must be positive intiger")

        n = min(no_of_samples, self._no_of_valid_samples)
        start = (self._write_pos - n) % self._samples_capacity
        idx = (start + np.arange(n)) % self._samples_capacity

        return self._buffer[idx]

    def get_last_n_seconds(self, no_of_seconds: int) -> np.ndarray:
        """
        Return the most recent data window expressed in seconds.

        Returned data is ordered chronologically from oldest to newest
        within the selected range.

        Args:
            no_of_seconds: Length of requested window in seconds.

        Returns:
            NumPy array of shape (n, no_of_channels), where
            n = min(no_of_seconds * sampling_rate, current_number_of_valid_samples).
        """
        if no_of_seconds <= 0:
            raise ValueError("No of seconds must be positive intiger")

        return self.get_last_n_samples(no_of_seconds * self._sampling_rate)

    def get_samples_no(self) -> int:
        """
        Return the current number of valid samples stored in the buffer.

        Args:
            None

        Returns:
            Number of valid samples currently available for reading.
        """
        return self._no_of_valid_samples

    def clear(self) -> None:
        """
        Clear buffer logical content.

        Buffer memory is not reallocated. Only logical state is reset,
        so the buffer becomes empty and the next write starts from index 0.

        Args:
            None

        Returns:
            None
        """
        self._no_of_valid_samples = 0
        self._write_pos = 0

    def is_full(self) -> bool:
        """
        Check whether the buffer is filled to capacity.

        Args:
            None

        Returns:
            True if the buffer currently contains `samples_capacity` valid samples,
            otherwise False.
        """
        return self._samples_capacity == self._no_of_valid_samples
