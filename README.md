# SmartGrow Firmware

ESP32-based sensor node firmware for the **SmartGrow Lab** greenhouse monitoring project at HFU.

## Overview

Distributed sensor network for precision agriculture in controlled environments.
Each node collects environmental data and transmits it via MQTT to a central broker every 30 seconds.

**Sensors per node:**

| Sensor         | Model    | Measures                        | Interface |
|----------------|----------|---------------------------------|-----------|
| Temp/Humidity  | DHT22    | °C, % rH                        | GPIO 4    |
| CO₂            | MH-Z19B  | ppm                             | UART1     |
| Light          | BH1750   | lux                             | I²C       |
| Soil Moisture  | Capacitive | % volumetric water content    | ADC 34    |

## Hardware

- **MCU:** ESP32 DevKit v4 (240 MHz dual-core, 520 KB SRAM)
- **Power:** 5V USB or solar panel via TP4056 LiPo charger
- **Enclosure:** IP54 outdoor box, 3D-printed bracket for sensor mounting

## Repository Structure

```
smartgrow-firmware/
├── firmware/
│   ├── sensor_node.py       ← Main firmware (MicroPython)
│   ├── mqtt_client.py       ← Lightweight MQTT wrapper
│   ├── sensors.py           ← Sensor driver abstractions
│   └── config.json.example  ← Configuration template
├── model/
│   └── greenhouse_v2.tflite ← TFLite anomaly detection model
├── tools/
│   ├── flash.sh             ← Flash firmware to device
│   └── monitor.py           ← Serial monitor + log parser
├── tests/
│   ├── test_sensors.py      ← Unit tests for sensor drivers
│   └── test_anomaly.py      ← Tests for anomaly detection logic
├── docs/
│   ├── wiring_diagram.md    ← Pin mapping and wiring guide
│   └── calibration.md       ← Sensor calibration procedure
└── .github/
    └── workflows/
        └── ci.yml           ← Lint + test on push
```

## Quick Start

### Prerequisites

- Python 3.11+
- [esptool](https://github.com/espressif/esptool) for flashing
- [mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html) for file transfer

### Flash MicroPython

```bash
# Erase flash
esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash

# Flash MicroPython 1.22
esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 micropython-1.22-esp32.bin
```

### Deploy Firmware

```bash
# Copy config
cp firmware/config.json.example firmware/config.json
# Edit config.json with your WiFi credentials and MQTT broker

# Upload all firmware files
bash tools/flash.sh /dev/ttyUSB0
```

### Configuration

```json
{
  "wifi_ssid": "YOUR_SSID",
  "wifi_password": "YOUR_PASSWORD",
  "mqtt_broker": "mqtt.smartgrow-lab.hfu.local",
  "node_id": "node-01"
}
```

> ⚠️ Never commit `config.json` – it is listed in `.gitignore`.

## Architecture

```
[ESP32 Node]  →  MQTT  →  [Broker]  →  [InfluxDB]  →  [Grafana]
                                    ↘  [Alert Service]  →  Email/SMS
```

The anomaly detection runs in two layers:
1. **Rule-based** threshold checks (fast, always-on)
2. **TFLite model** for predictive anomaly scoring (loaded on boot)

## Related

- Project website: [smartgrow-lab.hfu.local](http://smartgrow-lab.hfu.local)
- Deployment: Kubernetes @ HFU (kubeconfig in shared NextCloud folder)
- Dashboard: Grafana (internal HFU network)

## Contributing

PRs welcome. Please run `pytest tests/` before submitting.

## License

MIT © cactusjack82
