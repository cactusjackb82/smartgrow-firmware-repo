#!/usr/bin/env python3
"""
SmartGrow Lab – Serial Monitor & Log Parser
============================================
Connects to a sensor node via serial and pretty-prints log output.
Optionally writes parsed readings to a local CSV for debugging.

Usage:
    python3 tools/monitor.py --port /dev/ttyUSB0
    python3 tools/monitor.py --port /dev/ttyUSB0 --csv logs/node03.csv
"""

import argparse
import csv
import json
import re
import sys
from datetime import datetime

try:
    import serial
except ImportError:
    print("[ERROR] pyserial not installed. Run: pip install pyserial")
    sys.exit(1)


BAUD_RATE   = 115200
PAYLOAD_RE  = re.compile(r'\[DEBUG\] Payload: (\{.+\})')
ALERT_RE    = re.compile(r'\[ALERT\] (\[.+\])')


def parse_line(line: str) -> dict | None:
    """Extract structured data from a DEBUG log line."""
    m = PAYLOAD_RE.search(line)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            return None
    return None


def colorize(line: str) -> str:
    """Add terminal colors based on log level."""
    if "[CRITICAL]" in line: return f"\033[1;31m{line}\033[0m"
    if "[ERROR]"    in line: return f"\033[31m{line}\033[0m"
    if "[ALERT]"    in line: return f"\033[33m{line}\033[0m"
    if "[WARN]"     in line: return f"\033[33m{line}\033[0m"
    if "[INFO]"     in line: return f"\033[32m{line}\033[0m"
    if "[DEBUG]"    in line: return f"\033[90m{line}\033[0m"
    if "[BOOT]"     in line: return f"\033[1;36m{line}\033[0m"
    return line


def main():
    parser = argparse.ArgumentParser(description="SmartGrow serial monitor")
    parser.add_argument("--port",  default="/dev/ttyUSB0", help="Serial port")
    parser.add_argument("--baud",  default=BAUD_RATE, type=int)
    parser.add_argument("--csv",   default=None, help="Optional CSV output path")
    args = parser.parse_args()

    csv_file   = None
    csv_writer = None

    if args.csv:
        csv_file   = open(args.csv, "a", newline="")
        csv_writer = csv.DictWriter(csv_file, fieldnames=[
            "timestamp", "node_id", "temperature", "humidity",
            "co2_ppm", "light_lux", "soil_moisture"
        ])
        if csv_file.tell() == 0:
            csv_writer.writeheader()
        print(f"[monitor] Logging to {args.csv}")

    print(f"[monitor] Connecting to {args.port} @ {args.baud} baud... (Ctrl+C to exit)\n")

    try:
        with serial.Serial(args.port, args.baud, timeout=1) as ser:
            while True:
                raw = ser.readline()
                if not raw:
                    continue

                line = raw.decode("utf-8", errors="replace").strip()
                ts   = datetime.now().strftime("%H:%M:%S")

                print(f"{ts}  {colorize(line)}")

                if csv_writer:
                    data = parse_line(line)
                    if data:
                        data["timestamp"] = datetime.utcnow().isoformat()
                        csv_writer.writerow(data)
                        csv_file.flush()

    except KeyboardInterrupt:
        print("\n[monitor] Stopped.")
    except serial.SerialException as e:
        print(f"[ERROR] Could not open {args.port}: {e}")
    finally:
        if csv_file:
            csv_file.close()


if __name__ == "__main__":
    main()
