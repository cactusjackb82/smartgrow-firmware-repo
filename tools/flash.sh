#!/bin/bash
# =============================================================================
# SmartGrow Lab – Flash & Deploy Script
# Usage: bash tools/flash.sh [PORT] [NODE_ID]
# Example: bash tools/flash.sh /dev/ttyUSB0 node-03
# =============================================================================

set -e

PORT="${1:-/dev/ttyUSB0}"
NODE_ID="${2:-node-01}"
FIRMWARE_DIR="firmware"

echo "╔══════════════════════════════════════╗"
echo "║  SmartGrow Firmware Deployer v2.3    ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "  Port:    $PORT"
echo "  Node ID: $NODE_ID"
echo ""

# Check dependencies
command -v mpremote >/dev/null 2>&1 || { echo "[ERROR] mpremote not found. Install: pip install mpremote"; exit 1; }

# Check config exists
if [ ! -f "$FIRMWARE_DIR/config.json" ]; then
    echo "[ERROR] config.json not found."
    echo "        Copy firmware/config.json.example → firmware/config.json and fill in credentials."
    exit 1
fi

# Patch node_id into config
python3 -c "
import json
with open('$FIRMWARE_DIR/config.json', 'r') as f:
    cfg = json.load(f)
cfg['node_id'] = '$NODE_ID'
with open('$FIRMWARE_DIR/config.json', 'w') as f:
    json.dump(cfg, f, indent=2)
print(f'  Node ID set to: $NODE_ID')
"

echo "[1/4] Uploading sensor drivers..."
mpremote connect "$PORT" cp "$FIRMWARE_DIR/sensors.py"     :sensors.py

echo "[2/4] Uploading MQTT client..."
mpremote connect "$PORT" cp "$FIRMWARE_DIR/mqtt_client.py" :mqtt_client.py

echo "[3/4] Uploading config..."
mpremote connect "$PORT" cp "$FIRMWARE_DIR/config.json"    :config.json

echo "[4/4] Uploading main firmware..."
mpremote connect "$PORT" cp "$FIRMWARE_DIR/sensor_node.py" :main.py

echo ""
echo "✓ Deploy complete. Resetting device..."
mpremote connect "$PORT" reset

echo "✓ Node $NODE_ID is live on $PORT"
