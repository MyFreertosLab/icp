# Test for Simulator
import pytest
import threading
import time
import json
import paho.mqtt.client as mqtt
import numpy as np
import struct
from icp.icp_tests.test_components.mpu9250_simulator import MPU9250Simulator

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# MQTT Client Fixture
@pytest.fixture(scope="module")
def mqtt_client():
    client = mqtt.MQTTClient(MQTT_BROKER, MQTT_PORT)
    threading.Thread(target=client.loop_forever, daemon=True).start()
    time.sleep(1)  # Ensure MQTT connection is established
    return client


def test_simulator():
    simulator = MPU9250Simulator()
    assert simulator is not None

