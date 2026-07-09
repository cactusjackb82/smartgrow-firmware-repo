# Wiring Diagram & Pin Mapping

## ESP32 DevKit v4 – Sensor Connections

```
                    ┌─────────────────────┐
                    │      ESP32          │
        DHT22 ──────┤ GPIO 4              │
                    │                     │
       MH-Z19B ─────┤ GPIO 16 (RX)        │
                    │ GPIO 17 (TX)        │
                    │                     │
       BH1750 ──────┤ GPIO 21 (SDA) I²C   │
                    │ GPIO 22 (SCL) I²C   │
                    │                     │
  Soil Moisture ────┤ GPIO 34 (ADC)       │
                    │                     │
          3.3V ─────┤ 3V3                 │
            GND ────┤ GND                 │
                    └─────────────────────┘
```

## Sensor Power Requirements

| Sensor     | Voltage | Current (typ) | Notes                        |
|------------|---------|---------------|------------------------------|
| DHT22      | 3.3V    | 1.5 mA        | 10kΩ pull-up on data line    |
| MH-Z19B    | 5V      | 150 mA peak   | Use level shifter for UART   |
| BH1750     | 3.3V    | 0.12 mA       | ADDR pin → GND (addr 0x23)   |
| Soil probe | 3.3V    | 5 mA          | Capacitive, no corrosion     |

> ⚠️ The MH-Z19B requires 5V supply but communicates at 3.3V TTL levels.
> Use a voltage divider or level shifter on the TX line from the sensor.

## I²C Addresses

| Device  | Address | Notes              |
|---------|---------|--------------------|
| BH1750  | 0x23    | ADDR pin tied low  |

## Notes

- Run I²C at 400 kHz (fast mode) for reliable BH1750 reads
- DHT22 minimum sampling interval: 2 seconds
- MH-Z19B warm-up time: ~3 minutes after cold boot
- Soil sensor ADC: use 11dB attenuation for full 0–3.3V range (GPIO 34 is input-only)
