# Test for Simulator
import pytest
import threading
import time
import json
import struct
from icp.mqtt.client import MQTTClient
from icp.icp_tests.test_components.mpu9250_simulator import MPU9250Simulator
from icp.utils.constants import FORMATS, MPUMessageType

MQTT_BROKER = "localhost"
MQTT_PORT = 1883

# MQTT Client Fixture
@pytest.fixture(scope="module")
def mqtt_client():
    client = MQTTClient(MQTT_BROKER, MQTT_PORT)
    threading.Thread(target=client.loop_forever, daemon=True).start()
    time.sleep(1)  # Ensure MQTT connection is established
    return client

def test_simulator(mqtt_client):
    result = {
        "hellos": [],
        "measures": [],
    }

    # Define handlers for testing
    def on_hello(topic, payload):
        result["hellos"].append(payload)  # Decoded as string

    def on_measure(topic, payload):
        msg_type, = struct.unpack("I", payload[:4])
        measure = struct.unpack(FORMATS[MPUMessageType(msg_type)], payload)
        result["measures"].append(measure)

    # Add handlers for expected topics
    mqtt_client.add_handler(
        {"topic": "/imu/calibration/mpu/hello", "type": "string"},
        on_hello
    )
    mqtt_client.add_handler(
        {"topic": "/imu/calibration/mpu/measures", "type": "binary"},
        on_measure
    )

    # Simulate ComponentRegistry response
    def handle_registration(topic, payload):
        registration_request = payload
        component_name = registration_request["name"]

        # Mock resolved topics for MPU9250Simulator
        resolved_topics = {
            "hello_in": {
                "topic": "/imu/calibration/st/hello",
                "type": "string"
            },
            "commands_in": {
                "topic": "/imu/calibration/mpu/command",
                "type": "string"
            },
            "hello_out": {
                "topic": "/imu/calibration/mpu/hello",
                "type": "string"
            },
            "measurements_out": {
                "topic": "/imu/calibration/mpu/measures",
                "type": "binary"
            }
        }

        # Respond to the registration request
        mqtt_client.publish({ "topic": f"/system/registry/{component_name}/response", "type": "json"},resolved_topics)

    mqtt_client.add_handler(
        {"topic": "/system/registry/register", "type": "json"},
        handle_registration
    )

    # Start the simulator
    simulator = MPU9250Simulator(mqtt_client)
    simulator.start()

    ####################################################
    #### Start test flow
    ####################################################
    # Send hello
    mqtt_client.publish({"topic": "/imu/calibration/st/hello", "type": "string"},payload="hello")
    # Wait for hello response
    for i in range(10):
        time.sleep(1)
        if len(result["hellos"]) > 0:
            break
        # resend message .. 
        mqtt_client.publish({"topic": "/imu/calibration/st/hello", "type": "string"},payload="hello")

    assert len(result["hellos"]) > 0

    # Start measurement
    mqtt_client.publish(
        {"topic": "/imu/calibration/mpu/command", "type": "string"},
        payload="start"
    )

    # Wait for measurements
    for i in range(10):
        time.sleep(1)
        if len(result["measures"]) > 0:
            break

    assert len(result["measures"]) > 0

    # Stop measurement
    mqtt_client.publish(
        {"topic": "/imu/calibration/mpu/command", "type": "string"},
        payload="stop"
    )
    time.sleep(2)

    # Ensure no further measurements
    previous_count = len(result["measures"])
    time.sleep(2)
    assert len(result["measures"]) == previous_count

    simulator.shutdown()
    simulator.join()


