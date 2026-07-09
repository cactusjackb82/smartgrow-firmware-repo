"""
Tests for anomaly detection logic in sensor_node.py.
Run with: pytest tests/test_anomaly.py -v
"""

import pytest
import sys
import types

# ── Mock MicroPython-only modules before importing firmware ───────────────────
for mod in ["machine", "network", "dht", "umqtt", "umqtt.simple",
            "tflite_runtime", "tflite_runtime.interpreter"]:
    sys.modules[mod] = types.ModuleType(mod)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def nominal_reading():
    """A perfectly normal sensor reading – no alerts expected."""
    return {
        "node_id":       "node-03",
        "timestamp":     1697241600,
        "temperature":   22.5,
        "humidity":      65.0,
        "co2_ppm":       800,
        "light_lux":     4200,
        "soil_moisture": 55.0
    }


@pytest.fixture
def high_temp_reading(nominal_reading):
    return {**nominal_reading, "temperature": 76.0}


@pytest.fixture
def low_humidity_reading(nominal_reading):
    return {**nominal_reading, "humidity": 3.0}


@pytest.fixture
def multi_alert_reading(nominal_reading):
    return {**nominal_reading, "temperature": 76.0, "humidity": 3.0, "co2_ppm": 1800}


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestCheckAnomalies:

    def test_nominal_reading_produces_no_alerts(self, nominal_reading):
        from firmware.sensor_node import check_anomalies
        alerts = check_anomalies(nominal_reading)
        assert alerts == []

    def test_high_temperature_triggers_alert(self, high_temp_reading):
        from firmware.sensor_node import check_anomalies
        alerts = check_anomalies(high_temp_reading)
        assert any("TEMP_HIGH" in a for a in alerts)

    def test_low_humidity_triggers_alert(self, low_humidity_reading):
        from firmware.sensor_node import check_anomalies
        alerts = check_anomalies(low_humidity_reading)
        assert any("HUMIDITY_LOW" in a for a in alerts)

    def test_multiple_simultaneous_alerts(self, multi_alert_reading):
        from firmware.sensor_node import check_anomalies
        alerts = check_anomalies(multi_alert_reading)
        assert len(alerts) >= 2

    def test_alert_contains_measured_value(self, high_temp_reading):
        """Alert string should include the actual measured value."""
        from firmware.sensor_node import check_anomalies
        alerts = check_anomalies(high_temp_reading)
        temp_alerts = [a for a in alerts if "TEMP_HIGH" in a]
        assert len(temp_alerts) == 1
        # Value in alert should reflect post-calibration temperature
        assert "°C" in temp_alerts[0]


class TestMaintenanceWindow:

    def test_in_window_returns_true(self):
        from unittest.mock import patch
        import time as _time
        mock_tm = _time.struct_time((2023, 10, 14, 3, 17, 0, 5, 287, 0))
        with patch("time.localtime", return_value=mock_tm):
            from firmware.sensor_node import _in_maintenance_window
            assert _in_maintenance_window() is True

    def test_outside_window_returns_false(self):
        from unittest.mock import patch
        import time as _time
        mock_tm = _time.struct_time((2023, 10, 14, 14, 0, 0, 5, 287, 0))
        with patch("time.localtime", return_value=mock_tm):
            from firmware.sensor_node import _in_maintenance_window
            assert _in_maintenance_window() is False
