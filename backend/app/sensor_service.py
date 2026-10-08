from __future__ import annotations

import re
import threading
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import median

try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False


@dataclass
class VitalsSnapshot:
    state: str = "disconnected"
    message: str = "ESP32 is not connected to COM3. Connect the ESP32 and start its sensor stream."
    heart_rate: float | None = None
    average_heart_rate: int | None = None
    active_port: str = "COM3"
    available_ports: list[str] = None
    updated_at: str | None = None


class Esp32VitalsService:
    """Reads MAX30102 / ESP32 serial output directly from serial hardware port without fake fallbacks."""

    # Connect the ESP32/MAX30102 board to this port.  The web UI intentionally
    # does not allow users to change it.
    ESP32_PORT = "COM3"

    def __init__(self, baudrate: int = 115200) -> None:
        self.port = self.ESP32_PORT
        self.baudrate = baudrate
        self._snapshot = VitalsSnapshot(
            active_port=self.port,
            available_ports=self.list_available_ports(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._samples: deque[float] = deque(maxlen=5)

    @staticmethod
    def list_available_ports() -> list[str]:
        if not SERIAL_AVAILABLE:
            return []
        try:
            return [p.device for p in serial.tools.list_ports.comports()]
        except Exception:
            return []

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
            snap = VitalsSnapshot(**self._snapshot.__dict__)
            snap.available_ports = self.list_available_ports()
        # Timeout check: if no reading updated for 6 seconds, mark disconnected
        if snap.updated_at and time.time() - datetime.fromisoformat(snap.updated_at).timestamp() > 6:
            snap.state = "disconnected"
            snap.message = f"No sensor data is being received on {self.port}. Check that the ESP32 is connected and transmitting."
            snap.heart_rate = None
        return snap

    def _set(self, **values: object) -> None:
        values["updated_at"] = datetime.now(timezone.utc).isoformat()
        with self._lock:
            for key, value in values.items():
                setattr(self._snapshot, key, value)

    def _read_loop(self) -> None:
        while not self._stop.is_set():
            if not SERIAL_AVAILABLE:
                self._set(
                    state="disconnected",
                    message="pyserial not available.",
                    heart_rate=None,
                )
                self._stop.wait(3)
                continue

            try:
                with serial.Serial(self.port, self.baudrate, timeout=1) as device:
                    self._set(
                        state="waiting",
                        message=f"ESP32 port {self.port} opened. Waiting for MAX30102 pulse stream...",
                        heart_rate=None,
                    )
                    while not self._stop.is_set():
                        line = device.readline().decode("utf-8", errors="ignore").strip()
                        if line:
                            self._parse_line(line)
            except Exception:
                avail = ", ".join(self.list_available_ports()) or "None"
                self._set(
                    state="disconnected",
                    message=f"ESP32 is unavailable on {self.port}. Connect it and close Arduino Serial Monitor. (System ports: {avail})",
                    heart_rate=None,
                )
                self._stop.wait(2)

    def _parse_line(self, line: str) -> None:
        if "SENSOR_MISSING" in line or "not detected" in line.lower():
            self._samples.clear()
            self._set(state="sensor_missing", message="Please connect MAX30102 sensor for accurate heart rate.", heart_rate=None)
            return
        if "FINGER_MISSING" in line or "place finger" in line.lower():
            self._samples.clear()
            self._set(state="finger_missing", message="Place your finger steadily on MAX30102 sensor.", heart_rate=None)
            return
        if "SENSOR_READY" in line or "MAX30102 detected" in line:
            self._set(state="ready", message="Sensor ready. Place finger on sensor.", heart_rate=None)
            return

        match = re.search(r"BPM:\s*([0-9]+(?:\.[0-9]+)?)\s*\|\s*Average BPM:\s*([0-9]+)", line)
        if not match:
            match = re.search(r"VITAL,BPM,([0-9]+(?:\.[0-9]+)?),AVG,([0-9]+)", line)

        if match:
            self._accept_reading(float(match.group(1)), float(match.group(2)))

    def _accept_reading(self, bpm: float, reported_average: float) -> None:
        if not 45 <= bpm <= 180 or not 45 <= reported_average <= 180:
            self._samples.clear()
            self._set(
                state="signal_unstable",
                message="Signal unstable. Keep your finger still on the sensor.",
                heart_rate=None,
            )
            return

        self._samples.append(bpm)
        filtered_bpm = float(median(self._samples))
        filtered_average = round(sum(self._samples) / len(self._samples))
        self._set(
            state="measuring",
            message=f"Stable live hardware heart rate received on {self.port}.",
            heart_rate=filtered_bpm,
            average_heart_rate=filtered_average,
        )
