# Test for Simulator
import pytest
import threading
import time
import json
import paho.mqtt.client as mqtt
import numpy as np
import struct
from icp.mqtt.client import MQTTClient
from icp.icp_tests.test_components.mpu9250_simulator import MPU9250Simulator
from icp.utils.constants import TOPICS, FORMATS, MPUMessageType

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
    hello_received = False
    measure_received = False

    simulator = MPU9250Simulator(mqtt_client)
    result = {
        "hellos": [],
        "measures": [],
    }

    def on_hello(topic, payload):
        hello = payload
        result["hellos"].append(hello)
        
    def on_measure(topic, payload):
        msg_type, = struct.unpack("I", payload[:4])
        measure = struct.unpack(FORMATS[MPUMessageType(msg_type)], payload)
        result["measures"].append(measure)

    mqtt_client.add_handler(TOPICS["mpu_hello"], on_hello)
    mqtt_client.add_handler(TOPICS["mpu_measures"], on_measure)
 
    simulator.start()

    ####################################################
    #### Start test flow
    ####################################################
    # send hello
    mqtt_client.publish(TOPICS["starter_hello"], "hello")
    # Risposta hello ricevuta
    for i in range(10):
        time.sleep(1)
        measure_received = (len(result["measures"]) > 0)
        hello_received = (len(result["hellos"]) > 0)
        if hello_received:
            break

    assert hello_received
    measure_received = (len(result["measures"]) > 0)
    assert not measure_received

    # Ciclo di misurazione
    for j in range(10):
      # Start misurazione
      mqtt_client.publish(TOPICS["mpu_command"], "start")
      # Misure ricevute
      for i in range(10):
        time.sleep(1)
        measure_received = (len(result["measures"]) > 0)
        if measure_received:
            break
        
      assert measure_received
      # Stop misurazione
      mqtt_client.publish(TOPICS["mpu_command"], "stop")
      time.sleep(2)
      measure_received = False
      # Misure non più ricevute
      time.sleep(2)
      assert not measure_received
   
    time.sleep(2)  # Allow time for execution
    simulator.shutdown()
    simulator.join()


