
import threading
import time
import json
import paho.mqtt.client as mqtt
import struct
from icp.utils.constants import TOPICS
from icp.icp_tests.test_components.measure_generator import MeasureGenerator

class MPU9250Simulator(threading.Thread):
    def __init__(self, mqtt_client):
        super().__init__()
        self.mqtt_client = mqtt_client
        self.generator = MeasureGenerator()
        self.running = False
        mqtt_client.add_handler(TOPICS["mpu_command"], self.handle_command)
        mqtt_client.add_handler(TOPICS["starter_hello"], self.handle_hello)

    def handle_command(self, topic, payload):
        command = payload.decode()
        if command == "start":
            self.running = True
            self.generator.running = True
            self.start_sending_measurements()
        elif command == "stop":
            self.running = False
            self.generator.running = False

    def handle_hello(self, topic, payload):
        if payload.decode() == "hello":
            self.mqtt_client.publish(TOPICS["mpu_hello"], "hello")

    def start_sending_measurements(self):
        for topic, payload in self.generator.generate_measurements():
            if not self.running:
                break
            self.mqtt_client.publish(topic, payload)

    def run(self):
        while True:
            time.sleep(0.1)

