"""
SmartGrow Lab – Lightweight MQTT Client Wrapper
================================================
Thin abstraction over umqtt.simple for MicroPython.
Handles reconnection logic and QoS bookkeeping.
"""

import time


class MQTTClient:
    """
    Wrapper around umqtt.simple.MQTTClient with automatic reconnection.
    """

    def __init__(self, client_id: str, server: str, port: int = 1883, keepalive: int = 60):
        self.client_id  = client_id
        self.server     = server
        self.port       = port
        self.keepalive  = keepalive
        self._client    = None
        self._connected = False

    def connect(self) -> None:
        """Establish connection to MQTT broker."""
        from umqtt.simple import MQTTClient as _MQTTClient
        self._client = _MQTTClient(
            client_id=self.client_id,
            server=self.server,
            port=self.port,
            keepalive=self.keepalive
        )
        self._client.connect()
        self._connected = True
        print(f"[MQTT] Connected to {self.server}:{self.port} as {self.client_id}")

    def disconnect(self) -> None:
        """Gracefully disconnect from broker."""
        if self._client and self._connected:
            self._client.disconnect()
            self._connected = False

    def publish(self, topic: str, message: str, qos: int = 0, retain: bool = False) -> None:
        """
        Publish a message. Retries once on failure.
        topic:   MQTT topic string
        message: payload (string, will be encoded to bytes)
        qos:     0 = fire-and-forget, 1 = at-least-once
        retain:  broker retains last message for new subscribers
        """
        if not self._connected:
            raise RuntimeError("MQTT client not connected")

        try:
            self._client.publish(
                topic.encode(),
                message.encode(),
                retain=retain,
                qos=qos
            )
        except OSError as e:
            print(f"[MQTT] Publish failed ({e}), retrying once...")
            time.sleep(2)
            self.connect()
            self._client.publish(
                topic.encode(),
                message.encode(),
                retain=retain,
                qos=qos
            )

    def subscribe(self, topic: str, callback) -> None:
        """Subscribe to a topic with a callback function."""
        if not self._connected:
            raise RuntimeError("MQTT client not connected")
        self._client.set_callback(callback)
        self._client.subscribe(topic.encode())

    def check_messages(self) -> None:
        """Process pending incoming messages (non-blocking)."""
        if self._client:
            self._client.check_msg()

    @property
    def is_connected(self) -> bool:
        return self._connected
