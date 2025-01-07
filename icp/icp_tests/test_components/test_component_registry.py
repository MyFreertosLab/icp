# Test for ComponentRegistry
import pytest
import threading
import time
import json
from icp.mqtt.client import MQTTClient
from icp.components.component_registry import ComponentRegistry

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# MQTT Client Fixture
@pytest.fixture(scope="module")
def mqtt_client():
    client = MQTTClient(MQTT_BROKER, MQTT_PORT)
    threading.Thread(target=client.loop_forever, daemon=True).start()
    time.sleep(1)  # Ensure MQTT connection is established
    return client

# ComponentRegistry Fixture
@pytest.fixture(scope="module")
def component_registry(mqtt_client):
    registry = ComponentRegistry(mqtt_client)
    registry_thread = threading.Thread(target=registry.run, daemon=True)
    registry_thread.start()
    time.sleep(3)
    return registry

def test_component_registry_registration(mqtt_client, component_registry):
    result = {"response": None}
    # Define a handler to capture the registry's response
    def on_response(topic, payload):
        result["response"] = payload

    # Add handler for the response topic
    mqtt_client.add_handler(
        {"topic": "/system/registry/imu/response", "type": "json"},
        on_response
    )

    # Send a registration request
    registration_message = {
        "name": "imu",
        "pins": {
            "input": [
                {"name": "control_status_in", "type": "string"},
                {"name": "configs_in", "type": "binary"}
            ],
            "output": [
                {"name": "status_out", "type": "string"},
                {"name": "measurements_out", "type": "binary"}
            ]
        }
    }

    time.sleep(1)
    mqtt_client.publish({"topic": "/system/registry/register","type": "json"}, registration_message)
    time.sleep(1)

    # Wait for the response
    for _ in range(10):
        if result["response"] is not None:
            break
        mqtt_client.publish({"topic": "/system/registry/register","type": "json"}, registration_message)
        time.sleep(1)

    assert result["response"] is not None

    # Verify the resolved topics
    expected_response = {
            "control_status_in": {
                "topic": "/imu/calibration/point_estimator/status",
                "type": "string"
            },
            "configs_in": {
                "topic": "/imu/calibration/imu/configs",
                "type": "binary"
            },
            "status_out": {
                "topic": "/imu/calibration/imu/status",
                "type": "string"
            },
            "measurements_out": {
                "topic": "/imu/calibration/imu/measures",
                "type": "binary"
            }
        }

    assert result["response"] == expected_response

    component_registry.shutdown()
 