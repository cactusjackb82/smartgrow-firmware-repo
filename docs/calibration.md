# Sensor Calibration Procedure

## DHT22 – Temperature & Humidity

The DHT22 is factory-calibrated and generally does not require field calibration.
If readings drift significantly (>2°C or >5% rH vs. reference instrument):

1. Compare against a calibrated reference sensor for 30 minutes
2. Calculate mean offset
3. Update `_SENSOR_OFFSET` in `sensor_node.py` accordingly

**Known issue – node-03 (AU field deployment):**
Batch #7 DHT22 sensors showed systematic offsets in high-temperature, low-humidity
environments. Calibration offsets documented in:
`/SmartGrow_Deployment/calibration/node03_offset_report_AU.pdf`

---

## MH-Z19B – CO₂

Zero-point calibration should be performed after:
- First installation
- Any firmware update that resets sensor state
- Readings drift > 100 ppm vs. reference (400 ppm fresh outdoor air)

```python
# Trigger via firmware (connect serial monitor first):
from sensors import MH_Z19
sensor = MH_Z19(uart_id=1, tx_pin=17, rx_pin=16)
sensor.calibrate_zero()   # Run outdoors in fresh air only!
```

> ⚠️ Never run zero calibration indoors – 400 ppm is the atmospheric baseline.
> Running indoors (800–1200 ppm) will permanently offset the sensor low.

---

## Soil Moisture – Capacitive Sensor

Capacitive soil sensors vary significantly between batches.
Recalibrate when replacing sensors or after long-term deployment.

**Procedure:**
1. Measure `read_raw()` with sensor in completely dry soil → `DRY_VALUE`
2. Measure `read_raw()` with sensor submerged in water → `WET_VALUE`
3. Update constants in `sensors.py`:

```python
class SoilMoisture:
    DRY_VALUE = 2800   # ← replace with your measured value
    WET_VALUE = 1200   # ← replace with your measured value
```

**Reference values (HFU lab, 3.3V supply):**

| Batch | DRY_VALUE | WET_VALUE |
|-------|-----------|-----------|
| #1    | 2810      | 1190      |
| #2    | 2750      | 1210      |
| #3    | 2830      | 1175      |
