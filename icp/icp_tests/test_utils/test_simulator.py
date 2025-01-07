# Test for Simulator
import pytest
import threading
import time
import json
import struct
import logging

from icp.mqtt.client import MQTTClient
from icp.icp_tests.test_components.mpu9250_simulator import MPU9250Simulator
from icp.utils.constants import FORMATS, MPUMessageType

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# MQTT Client Fixture
@pytest.fixture(scope="module")
def mqtt_client():
    client = MQTTClient(MQTT_BROKER, MQTT_PORT)
    threading.Thread(target=client.loop_forever, daemon=True).start()
    time.sleep(1)  # Ensure MQTT connection is established
    return client

def test_simulator(mqtt_client):
    result = {
        "imu_status_seq": [],
        "measures": [],
    }

    # Define handlers for testing
    def on_imu_status(topic, payload):
        logger.debug(f"received imu status: {payload}")
        result["imu_status_seq"].append(payload)  # Decoded as string

    def on_measure(topic, payload):
        msg_type, = struct.unpack("I", payload[:4])
        measure = struct.unpack(FORMATS[MPUMessageType(msg_type)], payload)
        result["measures"].append(measure)

    # Add handlers for expected topics
    mqtt_client.add_handler(
        {"topic": "/imu/calibration/imu/status", "type": "string"},
        on_imu_status
    )
    mqtt_client.add_handler(
        {"topic": "/imu/calibration/imu/measures", "type": "binary"},
        on_measure
    )

    # Simulate ComponentRegistry response
    def handle_registration(topic, payload):
        registration_request = payload
        component_name = registration_request["name"]

        # Mock resolved topics for MPU9250Simulator
        resolved_topics = {
            "control_status_in": {
                "topic": "/imu/calibration/control/status",
                "type": "string"
            },
            "settings_in": {
                "topic": "/imu/calibration/control/imu/settings",
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

        # Respond to the registration request
        mqtt_client.publish({ "topic": f"/system/registry/{component_name}/response", "type": "json"},resolved_topics)

    mqtt_client.add_handler(
        {"topic": "/system/registry/register", "type": "json"},
        handle_registration
    )

    # Start the simulator
    simulator = MPU9250Simulator(mqtt_client)
    simulator.start()
    time.sleep(2)

    ####################################################
    #### Start test flow
    ####################################################
    # Send a control status
    mqtt_client.publish({"topic": "/imu/calibration/control/status", "type": "string"},payload="starting")
    # Wait for imu idle status
    for i in range(10):
        time.sleep(1)
        num_imu_status_curr = len(result["imu_status_seq"])
        if len(result["imu_status_seq"]) > 0 and result["imu_status_seq"][-1] == "idle":
            break
        # resend message .. 
        mqtt_client.publish({"topic": "/imu/calibration/control/status", "type": "string"},payload="starting")

    assert result["imu_status_seq"][-1] == "idle"

    # Start measurement
    num_imu_status_prev = len(result["imu_status_seq"])
    mqtt_client.publish(
        {"topic": "/imu/calibration/control/status", "type": "string"},
        payload="waiting_measurements"
    )
    # Wait for imu sending_measurements status
    for i in range(10):
        time.sleep(1)
        num_imu_status_curr = len(result["imu_status_seq"])
        if num_imu_status_curr > num_imu_status_prev and result["imu_status_seq"][-1] == "sending_measurements":
            break
        # resend message .. 
        mqtt_client.publish({"topic": "/imu/calibration/control/status", "type": "string"},payload="waiting_measurements")

    assert result["imu_status_seq"][-1] == "sending_measurements"

    # Wait for measurements
    for i in range(10):
        time.sleep(1)
        if len(result["measures"]) > 0:
            break

    assert len(result["measures"]) > 0

    # processing measurement simulation
    num_imu_status_prev = len(result["imu_status_seq"])
    mqtt_client.publish({"topic": "/imu/calibration/control/status", "type": "string"},payload="processing")
    # Wait for imu idle status
    for i in range(10):
        time.sleep(1)
        num_imu_status_curr = len(result["imu_status_seq"])
        if num_imu_status_curr > num_imu_status_prev and result["imu_status_seq"][-1] == "idle":
            break
        # resend message .. 
        mqtt_client.publish({"topic": "/imu/calibration/control/status", "type": "string"},payload="processing")

    assert result["imu_status_seq"][-1] == "idle"

    # Ensure no further measurements
    previous_count = len(result["measures"])
    time.sleep(2)
    assert len(result["measures"]) == previous_count

    num_imu_status_prev = len(result["imu_status_seq"])
    mqtt_client.publish({"topic": "/imu/calibration/control/status", "type": "string"},payload="shutting_down")
    # Wait for imu idle status
    for i in range(10):
        time.sleep(1)
        num_imu_status_curr = len(result["imu_status_seq"])
        if num_imu_status_curr > num_imu_status_prev and result["imu_status_seq"][-1] == "offline":
            break
        # resend message .. 
        mqtt_client.publish({"topic": "/imu/calibration/control/status", "type": "string"},payload="shutting_down")

    assert result["imu_status_seq"][-1] == "offline"


