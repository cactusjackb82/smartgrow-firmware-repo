"""
Tests for sensor driver abstractions.
Run with: pytest tests/test_sensors.py -v

Note: These tests use mocked hardware interfaces (no real ESP32 needed).
"""

import pytest
from unittest.mock import MagicMock, patch


# ── SoilMoisture ──────────────────────────────────────────────────────────────

class TestSoilMoisture:
    """
    SoilMoisture can be tested without hardware since read_percent()
    only depends on ADC values and calibration constants.
    """

    def _make_sensor(self, raw_value: int):
        """Helper: create a SoilMoisture instance with a mocked ADC."""
        with patch("machine.ADC"), patch("machine.Pin"):
            from firmware.sensors import SoilMoisture
            sensor = SoilMoisture.__new__(SoilMoisture)
            sensor._adc = MagicMock()
            sensor._adc.read = MagicMock(return_value=raw_value)
            return sensor

    def test_dry_soil_returns_zero(self):
        from firmware.sensors import SoilMoisture
        sensor = self._make_sensor(SoilMoisture.DRY_VALUE)
        assert sensor.read_percent() == 0.0

    def test_wet_soil_returns_hundred(self):
        from firmware.sensors import SoilMoisture
        sensor = self._make_sensor(SoilMoisture.WET_VALUE)
        assert sensor.read_percent() == 100.0

    def test_midpoint(self):
        from firmware.sensors import SoilMoisture
        mid = (SoilMoisture.DRY_VALUE + SoilMoisture.WET_VALUE) // 2
        sensor = self._make_sensor(mid)
        pct = sensor.read_percent()
        assert 45.0 <= pct <= 55.0

    def test_clamps_above_100(self):
        """ADC value below WET_VALUE (overwatered) should clamp to 100%."""
        from firmware.sensors import SoilMoisture
        sensor = self._make_sensor(SoilMoisture.WET_VALUE - 200)
        assert sensor.read_percent() == 100.0

    def test_clamps_below_zero(self):
        """ADC value above DRY_VALUE (bone dry) should clamp to 0%."""
        from firmware.sensors import SoilMoisture
        sensor = self._make_sensor(SoilMoisture.DRY_VALUE + 200)
        assert sensor.read_percent() == 0.0


# ── MH_Z19 (CO₂) ─────────────────────────────────────────────────────────────

class TestMHZ19:

    def test_parse_valid_response(self):
        """Test CO₂ parsing from a known good UART response."""
        # CO₂ = (0x06 << 8) | 0xA4 = 1700 ppm
        mock_response = bytes([0xff, 0x86, 0x06, 0xA4, 0x00, 0x00, 0x00, 0x00, 0x00])

        with patch("machine.UART"), patch("machine.Pin"):
            from firmware.sensors import MH_Z19
            sensor = MH_Z19.__new__(MH_Z19)
            sensor._uart = MagicMock()
            sensor._uart.any    = MagicMock(return_value=9)
            sensor._uart.read   = MagicMock(return_value=mock_response)

            assert sensor.read_co2() == 1700

    def test_returns_minus_one_on_short_response(self):
        with patch("machine.UART"), patch("machine.Pin"):
            from firmware.sensors import MH_Z19
            sensor = MH_Z19.__new__(MH_Z19)
            sensor._uart = MagicMock()
            sensor._uart.any = MagicMock(return_value=3)   # too short

            assert sensor.read_co2() == -1
