from __future__ import annotations

import os
import re
import threading
import time
from collections import deque
from statistics import median
from dataclasses import dataclass
from datetime import datetime, timezone

import serial
from serial import SerialException


@dataclass
class VitalsSnapshot:
    state: str = "disconnected"
    message: str = "ESP32 is unavailable on COM13. Connect it, then close Arduino Serial Monitor or any other serial app."
    heart_rate: float | None = None
    average_heart_rate: int | None = None
    updated_at: str | None = None


class Esp32VitalsService:
    """Reads the MAX30102 sketch's serial output without exposing COM access to the browser."""

    def __init__(self, port: str | None = None, baudrate: int = 115200) -> None:
        self.port = port or os.getenv("ESP32_PORT", "COM13")
        self.baudrate = baudrate
        self._snapshot = VitalsSnapshot()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._samples: deque[float] = deque(maxlen=5)

    def start(self) -> None:
        if self._thread is None:
            self._thread = threading.Thread(target=self._read_loop, daemon=True, name="esp32-vitals")
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def snapshot(self) -> VitalsSnapshot:
        with self._lock:
            snapshot = VitalsSnapshot(**self._snapshot.__dict__)
        if snapshot.updated_at and time.time() - datetime.fromisoformat(snapshot.updated_at).timestamp() > 8:
            snapshot.state = "disconnected"
            snapshot.message = "ESP32 is unavailable on COM13. Connect it, then close Arduino Serial Monitor or any other serial app."
            snapshot.heart_rate = None
        return snapshot

    def _set(self, **values: object) -> None:
        values["updated_at"] = datetime.now(timezone.utc).isoformat()
        with self._lock:
            for key, value in values.items():
                setattr(self._snapshot, key, value)

    def _read_loop(self) -> None:
        while not self._stop.is_set():
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1) as device:
                    self._set(state="waiting", message="ESP32 connected. Waiting for the MAX30102 sensor.", heart_rate=None)
                    while not self._stop.is_set():
                        line = device.readline().decode("utf-8", errors="ignore").strip()
                        if line:
                            self._parse_line(line)
            except (SerialException, OSError):
                self._set(
                    state="disconnected",
                    message="ESP32 is unavailable on COM13. Connect it, then close Arduino Serial Monitor or any other serial app.",
                    heart_rate=None,
                )
                self._stop.wait(2)

    def _parse_line(self, line: str) -> None:
        if "SENSOR_MISSING" in line or "not detected" in line.lower():
            self._samples.clear()
            self._set(state="sensor_missing", message="Please connect the sensor for accurate prediction.", heart_rate=None)
            return
        if "FINGER_MISSING" in line or "place finger" in line.lower():
            self._samples.clear()
            self._set(state="finger_missing", message="Place your finger steadily on the sensor.", heart_rate=None)
            return
        if "SENSOR_READY" in line or "MAX30102 detected" in line:
            self._set(state="ready", message="Sensor connected. Place your finger on the sensor.")
            return

        match = re.search(r"BPM:\s*([0-9]+(?:\.[0-9]+)?)\s*\|\s*Average BPM:\s*([0-9]+)", line)
        if not match:
            match = re.search(r"VITAL,BPM,([0-9]+(?:\.[0-9]+)?),AVG,([0-9]+)", line)
        if match:
            self._accept_reading(float(match.group(1)), float(match.group(2)))

    def _accept_reading(self, bpm: float, reported_average: float) -> None:
        # MAX30102 optical readings can briefly spike when the finger moves.
        # Never forward physiologically implausible values; smooth valid values
        # with a short rolling median before exposing them to the UI/model.
        if not 45 <= bpm <= 180 or not 45 <= reported_average <= 180:
            self._samples.clear()
            self._set(
                state="signal_unstable",
                message="Signal unstable. Keep your finger still on the sensor and wait for a stable reading.",
                heart_rate=None,
                average_heart_rate=None,
            )
            return

        self._samples.append(bpm)
        filtered_bpm = float(median(self._samples))
        filtered_average = round(sum(self._samples) / len(self._samples))
        self._set(
            state="measuring",
            message="Stable live heart rate received from the MAX30102.",
            heart_rate=filtered_bpm,
            average_heart_rate=filtered_average,
        )
