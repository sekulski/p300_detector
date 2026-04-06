from datetime import datetime

import numpy as np
import pytest

from eeg.edf_exporter import EdfExporter
from eeg.edf_utils import EdfChannelConfig, EdfRecordingMetadata, EegSessionData


def _build_channels(count: int) -> list[EdfChannelConfig]:
    return [
        EdfChannelConfig(
            label=f"Ch{i}",
            unit="uV",
            physical_min=-500.0,
            physical_max=500.0,
            digital_min=-32768,
            digital_max=32767,
            prefilter="",
            transducer_type="",
        )
        for i in range(count)
    ]


def _build_session(
    n_samples: int = 500,
    n_channels: int = 2,
    sampling_rate: int = 250,
) -> EegSessionData:
    samples = np.zeros((n_samples, n_channels), dtype=np.float32)
    channels = _build_channels(n_channels)
    metadata = EdfRecordingMetadata(
        patient_id="patient-1",
        recording_id="recording-1",
        start_datetime=datetime(2026, 4, 6, 12, 34, 56),
        equipment="brainaccess",
    )
    return EegSessionData(
        samples=samples,
        sampling_rate=sampling_rate,
        channels=channels,
        metadata=metadata,
    )


def test_validate_session_accepts_valid_session():
    session = _build_session()

    EdfExporter._validate_session(session)


def test_validate_session_raises_for_non_ndarray_samples():
    session = _build_session()
    session.samples = [[1.0, 2.0], [3.0, 4.0]]

    with pytest.raises(TypeError, match="NumPy array"):
        EdfExporter._validate_session(session)


def test_validate_session_raises_for_1d_samples():
    session = _build_session()
    session.samples = np.array([1.0, 2.0, 3.0], dtype=np.float32)

    with pytest.raises(ValueError, match="shape"):
        EdfExporter._validate_session(session)


def test_validate_session_raises_for_empty_samples():
    session = _build_session()
    session.samples = np.empty((0, 2), dtype=np.float32)

    with pytest.raises(ValueError, match="cannot be empty"):
        EdfExporter._validate_session(session)


def test_validate_session_raises_for_zero_channels():
    session = _build_session()
    session.samples = np.empty((10, 0), dtype=np.float32)

    with pytest.raises(ValueError, match="at least one channel"):
        EdfExporter._validate_session(session)


def test_validate_session_raises_for_non_positive_sampling_rate():
    session = _build_session(sampling_rate=0)

    with pytest.raises(ValueError, match="sampling_rate must be positive"):
        EdfExporter._validate_session(session)


def test_validate_session_raises_for_channel_count_mismatch():
    session = _build_session(n_channels=2)
    session.channels = _build_channels(3)

    with pytest.raises(ValueError, match="does not match"):
        EdfExporter._validate_session(session)


def test_validate_session_raises_for_invalid_digital_range():
    session = _build_session()
    session.channels[0].digital_min = 100
    session.channels[0].digital_max = 100

    with pytest.raises(ValueError, match="Invalid digital range"):
        EdfExporter._validate_session(session)


def test_validate_session_raises_for_invalid_physical_range():
    session = _build_session()
    session.channels[0].physical_min = 5.0
    session.channels[0].physical_max = 5.0

    with pytest.raises(ValueError, match="Invalid physical range"):
        EdfExporter._validate_session(session)


def test_build_samples_per_record_returns_same_value_for_all_channels():
    session = _build_session(n_channels=3, sampling_rate=250)

    result = EdfExporter._build_samples_per_record(session, 1.0)

    assert result == [250, 250, 250]


def test_build_samples_per_record_raises_for_non_positive_result():
    session = _build_session(n_channels=2, sampling_rate=1)

    with pytest.raises(ValueError, match="must be positive"):
        EdfExporter._build_samples_per_record(session, 0.0)


def test_align_samples_to_full_records_trims_tail():
    samples = np.zeros((520, 2), dtype=np.float32)
    samples_per_record = [250, 250]

    n_records, trimmed = EdfExporter._align_samples_to_full_records(samples, samples_per_record)

    assert n_records == 2
    assert trimmed.shape == (500, 2)


def test_align_samples_to_full_records_raises_when_not_enough_samples():
    samples = np.zeros((100, 2), dtype=np.float32)
    samples_per_record = [250, 250]

    with pytest.raises(ValueError, match="Not enough samples"):
        EdfExporter._align_samples_to_full_records(samples, samples_per_record)


def test_build_main_header_returns_expected_basic_fields():
    session = _build_session(n_samples=500, n_channels=2, sampling_rate=250)

    header = EdfExporter._build_main_header(session, n_records=2, record_duration_sec=1.0)

    assert header["version"] == "0"
    assert header["patient_id"] == "patient-1"
    assert header["recording_id"] == "recording-1"
    assert header["startdate"] == "06.04.26"
    assert header["starttime"] == "12.34.56"
    assert header["header_bytes"] == str(256 + 2 * 256)
    assert header["n_records"] == "2"
    assert header["record_duration"] == "1"
    assert header["ns"] == "2"


def test_build_signal_headers_maps_channel_fields_correctly():
    session = _build_session(n_channels=2)
    samples_per_record = [250, 250]

    headers = EdfExporter._build_signal_headers(session, samples_per_record)

    assert len(headers) == 2
    assert headers[0]["label"] == "Ch0"
    assert headers[0]["physical_dimension"] == "uV"
    assert headers[0]["physical_min"] == "-500"
    assert headers[0]["physical_max"] == "500"
    assert headers[0]["digital_min"] == "-32768"
    assert headers[0]["digital_max"] == "32767"
    assert headers[0]["samples_per_record"] == "250"


def test_ascii_field_pads_to_requested_width():
    result = EdfExporter._ascii_field("abc", 5)

    assert result == b"abc  "
    assert len(result) == 5


def test_ascii_field_truncates_to_requested_width():
    result = EdfExporter._ascii_field("abcdef", 4)

    assert result == b"abcd"
    assert len(result) == 4


def test_format_date_dd_mm_yy():
    dt = datetime(2026, 4, 6, 12, 34, 56)

    assert EdfExporter._format_date_dd_mm_yy(dt) == "06.04.26"


def test_format_time_hh_mm_ss():
    dt = datetime(2026, 4, 6, 12, 34, 56)

    assert EdfExporter._format_time_hh_mm_ss(dt) == "12.34.56"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (1.0, "1"),
        (1.5, "1.5"),
        (-500.0, "-500"),
        (0.125, "0.125"),
    ],
)
def test_format_number(value, expected):
    assert EdfExporter._format_number(value) == expected


def test_scale_one_channel_maps_extremes_and_zero():
    cfg = EdfChannelConfig(
        label="Ch0",
        unit="uV",
        physical_min=-500.0,
        physical_max=500.0,
        digital_min=-32768,
        digital_max=32767,
    )
    channel_samples = np.array([-500.0, 0.0, 500.0], dtype=np.float32)

    result = EdfExporter._scale_one_channel(channel_samples, cfg)

    assert result.dtype == np.int16
    assert result[0] == -32768
    assert result[2] == 32767
    assert abs(int(result[1])) <= 1


def test_scale_one_channel_clips_out_of_range_values():
    cfg = EdfChannelConfig(
        label="Ch0",
        unit="uV",
        physical_min=-100.0,
        physical_max=100.0,
        digital_min=-32768,
        digital_max=32767,
    )
    channel_samples = np.array([-1000.0, 1000.0], dtype=np.float32)

    result = EdfExporter._scale_one_channel(channel_samples, cfg)

    assert result[0] == -32768
    assert result[1] == 32767


def test_scale_all_channels_to_int16_returns_expected_shape_and_dtype():
    session = _build_session(n_samples=4, n_channels=2)
    session.samples = np.array(
        [
            [-10.0, 10.0],
            [0.0, 0.0],
            [10.0, -10.0],
            [5.0, -5.0],
        ],
        dtype=np.float32,
    )

    result = EdfExporter._scale_all_channels_to_int16(session.samples, session.channels)

    assert result.shape == session.samples.shape
    assert result.dtype == np.int16


def test_export_creates_non_empty_file(tmp_path):
    session = _build_session(n_samples=500, n_channels=2, sampling_rate=250)
    session.samples = np.random.uniform(-50, 50, size=(500, 2)).astype(np.float32)

    output_path = tmp_path / "test.edf"

    EdfExporter.export(session, output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_export_writes_expected_file_size_for_simple_case(tmp_path):
    n_channels = 2
    sampling_rate = 250
    n_samples = 500

    session = _build_session(
        n_samples=n_samples,
        n_channels=n_channels,
        sampling_rate=sampling_rate,
    )
    output_path = tmp_path / "sized.edf"

    EdfExporter.export(session, output_path)

    header_size = 256 + n_channels * 256
    data_size = n_samples * n_channels * 2
    expected_size = header_size + data_size

    assert output_path.stat().st_size == expected_size
