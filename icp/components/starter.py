import threading
import time
import json
import paho.mqtt.client as mqtt
import struct
from icp.utils.constants import TOPICS

# Starter Microservice
class Starter(threading.Thread):
    def __init__(self, mqtt_client):
        super().__init__()
        self.mqtt_client = mqtt_client
        self.received_hello = False
        mqtt_client.add_handler(TOPICS["mpu_hello"], self.handle_hello_response)

    def handle_hello_response(self, topic, payload):
        if payload.decode() == "hello":
            self.received_hello = True

    def run(self):
        self.mqtt_client.publish(TOPICS["starter_hello"], "hello")
        while not self.received_hello:
            time.sleep(10)
        self.mqtt_client.publish(TOPICS["starter_events"], json.dumps({"event": "started"}))
        print("Starter: Device handshake completed.")
