# Test for MQTT Client
import pytest
from icp.mqtt.client import MQTTClient

def test_mqtt_client():
    client = MQTTClient('localhost', 1883)
    assert client is not None

