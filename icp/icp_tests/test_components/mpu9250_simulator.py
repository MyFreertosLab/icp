
import threading
import time
import json
import paho.mqtt.client as mqtt
import struct
from icp.utils.constants import TOPICS
from icp.icp_tests.test_components.measure_generator import MeasureGenerator

class MPU9250Simulator(threading.Thread):
    def __init__(self, mqtt_client, frequency=500):
        super().__init__()
        self.frequency = frequency
        self.mqtt_client = mqtt_client
        self.generator = MeasureGenerator()
        self.running_measurements = False
        self.running = True
        mqtt_client.add_handler(TOPICS["mpu_command"], self.handle_command)
        mqtt_client.add_handler(TOPICS["starter_hello"], self.handle_hello)

    def handle_command(self, topic, payload):
        command = payload
        if command == "start":
            self.generator.running = True
            self.running_measurements = True
        elif command == "stop":
            self.running_measurements = False
            self.generator.running = False

    def handle_hello(self, topic, payload):
        if payload == "hello":
           self.mqtt_client.publish(TOPICS["mpu_hello"], "hello")

    def start_sending_measurements(self):
        for topic_key, payload in self.generator.generate_measurements():
          if not self.running_measurements:
            break
          self.mqtt_client.publish(topic_key, payload)
    def shutdown(self):
        self.running = False

    def run(self):
        while self.running:
            if self.running_measurements:
                self.start_sending_measurements()
            time.sleep(1/self.frequency)
