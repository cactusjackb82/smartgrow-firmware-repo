"""
SmartGrow Lab – Sensor Driver Abstractions
==========================================
Thin wrappers around raw sensor libraries.
Provides a consistent .read() interface for all sensor types.
"""

import time


class DHT22:
    """
    Temperature and humidity sensor driver.
    Datasheet: https://www.sparkfun.com/datasheets/Sensors/Temperature/DHT22.pdf
    Operating range: -40–80°C, 0–100% rH
    Accuracy: ±0.5°C, ±2–5% rH
    """

    def __init__(self, pin: int):
        import dht
        import machine
        self._sensor = dht.DHT22(machine.Pin(pin))

    def read(self) -> tuple[float, float]:
        """
        Returns (temperature_celsius, humidity_percent).
        Raises OSError on read failure.
        Note: sensor needs at least 2 seconds between reads.
        """
        self._sensor.measure()
        return self._sensor.temperature(), self._sensor.humidity()


class MH_Z19:
    """
    CO₂ sensor driver (UART-based).
    Measurement range: 0–5000 ppm
    Accuracy: ±(50 ppm + 5% of reading)
    Warm-up time: 3 minutes after power-on
    """

    _CMD_READ_CO2 = b'\xff\x01\x86\x00\x00\x00\x00\x00\x79'

    def __init__(self, uart_id: int, tx_pin: int, rx_pin: int):
        import machine
        self._uart = machine.UART(
            uart_id,
            baudrate=9600,
            tx=machine.Pin(tx_pin),
            rx=machine.Pin(rx_pin)
        )

    def read_co2(self) -> int:
        """Returns CO₂ concentration in ppm. Returns -1 on read failure."""
        self._uart.write(self._CMD_READ_CO2)
        time.sleep_ms(100)

        if self._uart.any() < 9:
            return -1

        response = self._uart.read(9)
        if response[0] != 0xff or response[1] != 0x86:
            return -1

        return (response[2] << 8) | response[3]

    def calibrate_zero(self) -> None:
        """
        Trigger zero-point calibration. Run only in fresh air (400 ppm baseline).
        WARNING: This permanently adjusts the sensor's internal reference.
        """
        cmd = b'\xff\x01\x87\x00\x00\x00\x00\x00\x78'
        self._uart.write(cmd)
        time.sleep(1)


class BH1750:
    """
    Ambient light sensor driver (I²C).
    Measurement range: 1–65535 lux
    Resolution: 1 lux (high-res mode)
    """

    _I2C_ADDR        = 0x23
    _CMD_CONT_H_RES  = 0x10   # continuous high-resolution mode

    def __init__(self, i2c_scl: int, i2c_sda: int):
        import machine
        self._i2c = machine.I2C(
            0,
            scl=machine.Pin(i2c_scl),
            sda=machine.Pin(i2c_sda),
            freq=400_000
        )
        self._i2c.writeto(self._I2C_ADDR, bytes([self._CMD_CONT_H_RES]))
        time.sleep_ms(180)   # measurement time in high-res mode

    def read_lux(self) -> float:
        """Returns ambient light in lux."""
        raw = self._i2c.readfrom(self._I2C_ADDR, 2)
        return ((raw[0] << 8) | raw[1]) / 1.2


class SoilMoisture:
    """
    Capacitive soil moisture sensor driver (ADC-based).
    Returns percentage: 0% = dry, 100% = saturated.

    Calibration values (adjust per sensor batch):
      DRY_VALUE: raw ADC reading in completely dry soil (~2800 for 3.3V ADC)
      WET_VALUE: raw ADC reading submerged in water   (~1200 for 3.3V ADC)
    """

    DRY_VALUE = 2800
    WET_VALUE = 1200

    def __init__(self, adc_pin: int):
        import machine
        self._adc = machine.ADC(machine.Pin(adc_pin))
        self._adc.atten(machine.ADC.ATTN_11DB)   # 0–3.3V range

    def read_raw(self) -> int:
        """Returns raw 12-bit ADC value (0–4095)."""
        # Average 5 readings to reduce noise
        readings = [self._adc.read() for _ in range(5)]
        return sum(readings) // len(readings)

    def read_percent(self) -> float:
        """Returns soil moisture as percentage (0–100%)."""
        raw = self.read_raw()
        pct = (self.DRY_VALUE - raw) / (self.DRY_VALUE - self.WET_VALUE) * 100
        return round(max(0.0, min(100.0, pct)), 1)
