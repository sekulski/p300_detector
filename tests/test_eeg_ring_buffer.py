import numpy as np
import pytest

from eeg.eeg_ring_buffer import EegRingBuffer


def make_chunk(samples: int, channels: int = 8, start: int = 0) -> np.ndarray:
    return np.arange(start, start + samples * channels, dtype=np.float32).reshape(samples, channels)


@pytest.fixture
def ring_buffer():
    return EegRingBuffer(sampling_rate=250, capacity_seconds=2, no_of_channels=8)


def test_buffer_should_have_no_samples_at_beginning(ring_buffer):
    assert ring_buffer.get_samples_no() == 0
    assert ring_buffer.get_last_n_samples(10).shape[0] == 0
    assert ring_buffer.get_last_n_seconds(10).shape[0] == 0
    assert ring_buffer.is_full() is False


def test_count_samples(ring_buffer):
    ring_buffer.add_samples(make_chunk(123))

    assert ring_buffer.get_samples_no() == 123


def test_clear_samples(ring_buffer):
    ring_buffer.add_samples(make_chunk(421))
    ring_buffer.clear()

    assert ring_buffer.get_samples_no() == 0
    assert ring_buffer.get_last_n_samples(10).shape[0] == 0
    assert ring_buffer.get_last_n_seconds(10).shape[0] == 0
    assert ring_buffer.is_full() is False


def test_samples_getter_should_be_restrained(ring_buffer):
    ring_buffer.add_samples(make_chunk(500))

    assert ring_buffer.get_last_n_samples(750).shape[0] == 500


def test_samples_get_by_time_should_be_restrained(ring_buffer):
    ring_buffer.add_samples(make_chunk(500))

    assert ring_buffer.get_last_n_seconds(3).shape[0] == 500


def test_buffer_should_hold_exactly_capacity_samples(ring_buffer):
    chunk = make_chunk(500)
    ring_buffer.add_samples(chunk)

    result = ring_buffer.get_last_n_samples(500)

    assert ring_buffer.get_samples_no() == 500
    assert ring_buffer.is_full() is True
    np.testing.assert_array_equal(result, chunk)


def test_should_return_last_samples_without_wrap(ring_buffer):
    chunk = make_chunk(100)
    ring_buffer.add_samples(chunk)

    result = ring_buffer.get_last_n_samples(50)

    np.testing.assert_array_equal(result, chunk[-50:])


def test_should_return_last_samples_after_wrap(ring_buffer):
    chunk1 = make_chunk(300, start=0)
    chunk2 = make_chunk(300, start=300 * 8)

    ring_buffer.add_samples(chunk1)
    ring_buffer.add_samples(chunk2)

    expected = np.vstack([chunk1, chunk2])[-500:]
    result = ring_buffer.get_last_n_samples(500)

    assert ring_buffer.get_samples_no() == 500
    assert ring_buffer.is_full() is True
    np.testing.assert_array_equal(result, expected)


def test_buffer_should_be_trimmed_when_exceeded(ring_buffer):
    chunk1 = make_chunk(250, start=0)
    chunk2 = make_chunk(250, start=250 * 8)
    chunk3 = make_chunk(666, start=500 * 8)

    ring_buffer.add_samples(chunk1)
    ring_buffer.add_samples(chunk2)
    ring_buffer.add_samples(chunk3)

    expected = np.vstack([chunk1, chunk2, chunk3])[-500:]

    assert ring_buffer.get_last_n_samples(2500).shape[0] == 500
    assert ring_buffer.get_last_n_seconds(3).shape[0] == 500
    np.testing.assert_array_equal(ring_buffer.get_last_n_samples(500), expected)


def test_add_samples_should_raise_for_non_2d_input(ring_buffer):
    with pytest.raises(ValueError):
        ring_buffer.add_samples(np.arange(10, dtype=np.float32))


def test_add_samples_should_raise_for_invalid_channel_count(ring_buffer):
    with pytest.raises(ValueError):
        ring_buffer.add_samples(np.zeros((10, 7), dtype=np.float32))


def test_get_last_n_samples_should_raise_for_zero(ring_buffer):
    with pytest.raises(ValueError):
        ring_buffer.get_last_n_samples(0)


def test_get_last_n_samples_should_raise_for_negative_value(ring_buffer):
    with pytest.raises(ValueError):
        ring_buffer.get_last_n_samples(-1)


def test_get_last_n_seconds_should_raise_for_zero(ring_buffer):
    with pytest.raises(ValueError):
        ring_buffer.get_last_n_seconds(0)


def test_get_last_n_seconds_should_raise_for_negative_value(ring_buffer):
    with pytest.raises(ValueError):
        ring_buffer.get_last_n_seconds(-1)
