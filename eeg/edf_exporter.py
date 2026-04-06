from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np

from eeg.edf_utils import EegSessionData


class EdfExporter:
    """
    Convert EEG session data to EDF format.
    """

    @staticmethod
    def export(session: EegSessionData, output_path: str | Path) -> None:
        EdfExporter._validate_session(session)

        record_duration_sec = 1.0
        samples_per_record = EdfExporter._build_samples_per_record(session, record_duration_sec)
        n_records, trimmed_samples = EdfExporter._align_samples_to_full_records(
            session.samples, samples_per_record
        )

        main_header = EdfExporter._build_main_header(session, n_records, record_duration_sec)
        signal_headers = EdfExporter._build_signal_headers(session, samples_per_record)

        digital_samples = EdfExporter._scale_all_channels_to_int16(
            trimmed_samples, session.channels
        )

        with open(output_path, "wb") as f:
            EdfExporter._write_header(f, main_header, signal_headers)
            EdfExporter._write_data_records(f, digital_samples, samples_per_record, n_records)

    @staticmethod
    def _write_header(f, main_header: dict[str, str], signal_headers: list[dict[str, str]]) -> None:
        f.write(EdfExporter._ascii_field(main_header["version"], 8))
        f.write(EdfExporter._ascii_field(main_header["patient_id"], 80))
        f.write(EdfExporter._ascii_field(main_header["recording_id"], 80))
        f.write(EdfExporter._ascii_field(main_header["startdate"], 8))
        f.write(EdfExporter._ascii_field(main_header["starttime"], 8))
        f.write(EdfExporter._ascii_field(main_header["header_bytes"], 8))
        f.write(EdfExporter._ascii_field(main_header["reserved"], 44))
        f.write(EdfExporter._ascii_field(main_header["n_records"], 8))
        f.write(EdfExporter._ascii_field(main_header["record_duration"], 8))
        f.write(EdfExporter._ascii_field(main_header["ns"], 4))

        EdfExporter._write_signal_field_block(f, signal_headers, "label", 16)
        EdfExporter._write_signal_field_block(f, signal_headers, "transducer_type", 80)
        EdfExporter._write_signal_field_block(f, signal_headers, "physical_dimension", 8)
        EdfExporter._write_signal_field_block(f, signal_headers, "physical_min", 8)
        EdfExporter._write_signal_field_block(f, signal_headers, "physical_max", 8)
        EdfExporter._write_signal_field_block(f, signal_headers, "digital_min", 8)
        EdfExporter._write_signal_field_block(f, signal_headers, "digital_max", 8)
        EdfExporter._write_signal_field_block(f, signal_headers, "prefiltering", 80)
        EdfExporter._write_signal_field_block(f, signal_headers, "samples_per_record", 8)
        EdfExporter._write_signal_field_block(f, signal_headers, "reserved", 32)

    @staticmethod
    def _build_signal_headers(
        session: EegSessionData,
        samples_per_record: list[int],
    ) -> list[dict[str, str]]:
        headers: list[dict[str, str]] = []

        for i, ch in enumerate(session.channels):
            headers.append(
                {
                    "label": ch.label,
                    "transducer_type": ch.transducer_type,
                    "physical_dimension": ch.unit,
                    "physical_min": EdfExporter._format_number(ch.physical_min),
                    "physical_max": EdfExporter._format_number(ch.physical_max),
                    "digital_min": str(ch.digital_min),
                    "digital_max": str(ch.digital_max),
                    "prefiltering": ch.prefilter,
                    "samples_per_record": str(samples_per_record[i]),
                    "reserved": "",
                }
            )

        return headers

    @staticmethod
    def _build_main_header(
        session: EegSessionData,
        n_records: int,
        record_duration_sec: float,
    ) -> dict[str, str]:
        ns = len(session.channels)
        header_bytes = 256 + ns * 256

        start_dt = session.metadata.start_datetime or datetime.now()

        return {
            "version": "0",
            "patient_id": session.metadata.patient_id,
            "recording_id": session.metadata.recording_id,
            "startdate": EdfExporter._format_date_dd_mm_yy(start_dt),
            "starttime": EdfExporter._format_time_hh_mm_ss(start_dt),
            "header_bytes": str(header_bytes),
            "reserved": "",
            "n_records": str(n_records),
            "record_duration": EdfExporter._format_number(record_duration_sec),
            "ns": str(ns),
        }

    @staticmethod
    def _write_signal_field_block(
        f,
        signal_headers: list[dict[str, str]],
        key: str,
        width: int,
    ) -> None:
        for hdr in signal_headers:
            f.write(EdfExporter._ascii_field(hdr[key], width))

    @staticmethod
    def _validate_session(session: EegSessionData) -> None:
        if not isinstance(session.samples, np.ndarray):
            raise TypeError("samples must be a NumPy array")

        if session.samples.ndim != 2:
            raise ValueError("samples must have shape (n_samples, n_channels)")

        if session.samples.shape[0] == 0:
            raise ValueError("samples cannot be empty")

        if session.samples.shape[1] == 0:
            raise ValueError("samples must contain at least one channel")

        if session.sampling_rate <= 0:
            raise ValueError("sampling_rate must be positive")

        if len(session.channels) != session.samples.shape[1]:
            raise ValueError(
                f"Channel config count ({len(session.channels)}) does not match "
                f"samples channel count ({session.samples.shape[1]})"
            )

        for i, ch in enumerate(session.channels):
            if ch.digital_min >= ch.digital_max:
                raise ValueError(f"Invalid digital range for channel {i}: {ch.label}")

            if ch.physical_min >= ch.physical_max:
                raise ValueError(f"Invalid physical range for channel {i}: {ch.label}")

    @staticmethod
    def _align_samples_to_full_records(
        samples: np.ndarray,
        samples_per_record: list[int],
    ) -> tuple[int, np.ndarray]:
        samples_per_record_first_channel = samples_per_record[0]

        n_total_samples = samples.shape[0]
        n_records = n_total_samples // samples_per_record_first_channel
        n_used_samples = n_records * samples_per_record_first_channel

        if n_records == 0:
            raise ValueError("Not enough samples for even one EDF data record")

        trimmed_samples = samples[:n_used_samples, :]
        return n_records, trimmed_samples

    @staticmethod
    def _build_samples_per_record(
        session: EegSessionData,
        record_duration_sec: float,
    ) -> list[int]:
        samples_per_channel = int(session.sampling_rate * record_duration_sec)

        if samples_per_channel <= 0:
            raise ValueError("samples_per_channel must be positive")

        return [samples_per_channel for _ in session.channels]

    @staticmethod
    def _ascii_field(value: str, width: int) -> bytes:
        text = str(value)
        text = text[:width]
        text = text.ljust(width, " ")
        return text.encode("ascii")

    @staticmethod
    def _format_date_dd_mm_yy(dt: datetime) -> str:
        return dt.strftime("%d.%m.%y")

    @staticmethod
    def _format_time_hh_mm_ss(dt: datetime) -> str:
        return dt.strftime("%H.%M.%S")

    @staticmethod
    def _format_number(value: float) -> str:
        if isinstance(value, int) or float(value).is_integer():
            return str(int(value))
        return f"{value:.6f}".rstrip("0").rstrip(".")

    @staticmethod
    def _scale_all_channels_to_int16(
        samples: np.ndarray,
        channel_configs,
    ) -> np.ndarray:
        digital = np.empty_like(samples, dtype=np.int16)

        for ch_idx, cfg in enumerate(channel_configs):
            digital[:, ch_idx] = EdfExporter._scale_one_channel(samples[:, ch_idx], cfg)

        return digital

    @staticmethod
    def _scale_one_channel(channel_samples: np.ndarray, channel_config) -> np.ndarray:
        phys_min = channel_config.physical_min
        phys_max = channel_config.physical_max
        dig_min = channel_config.digital_min
        dig_max = channel_config.digital_max

        clipped = np.clip(channel_samples, phys_min, phys_max)
        scale = (dig_max - dig_min) / (phys_max - phys_min)
        digital = (clipped - phys_min) * scale + dig_min

        return np.rint(digital).astype(np.int16)

    @staticmethod
    def _write_data_records(
        f,
        digital_samples: np.ndarray,
        samples_per_record: list[int],
        n_records: int,
    ) -> None:
        n_channels = digital_samples.shape[1]
        samples_per_channel = samples_per_record[0]

        for rec_idx in range(n_records):
            start = rec_idx * samples_per_channel
            end = start + samples_per_channel

            for ch_idx in range(n_channels):
                record_chunk = digital_samples[start:end, ch_idx]
                f.write(record_chunk.astype("<i2").tobytes())
