
import threading
import time
import json
import struct
from icp.icp_tests.test_components.measure_generator import MeasureGenerator

class MPU9250Simulator(threading.Thread):
    def __init__(self, mqtt_client, frequency=500):
        super().__init__()
        self.frequency = frequency
        self.mqtt_client = mqtt_client
        self.generator = MeasureGenerator()
        self.running_measurements = False
        self.running = True
        self.topics = None  # Sarà popolato con i topic assegnati dal registro
        self.register_with_registry()

    def register_with_registry(self):
        # Messaggio di registrazione con i pin definiti
        registration_message = {
            "name": "MPU9250Simulator",
            "pins": {
                "input": [
                    {"name": "hello_in", "type": "string"},
                    {"name": "commands_in", "type": "string"}
                ],
                "output": [
                    {"name": "hello_out", "type": "string"},
                    {"name": "measurements_out", "type": "binary"}
                ]
            }
        }
        # Invia la registrazione al registro
        self.mqtt_client.publish({
            "topic": "/system/registry/register",
            "type": "json"},
            registration_message
        )

        # Ascolta la risposta del registro
        response_topic = "/system/registry/MPU9250Simulator/response"
        self.mqtt_client.add_handler(
            {"topic": response_topic, "type": "json"},
            self.handle_registry_response
        )

    def handle_registry_response(self, topic, payload):
        # Salva i topic assegnati dal registro
        self.topics = payload
        print(f"Received topics from registry: {self.topics}")

        # Configura i topic di input
        if "hello_in" in self.topics:
            self.mqtt_client.add_handler(
                self.topics["hello_in"],
                self.handle_hello
            )
        if "commands_in" in self.topics:
            self.mqtt_client.add_handler(
                self.topics["commands_in"],
                self.handle_command
            )

    def handle_command(self, topic, payload):
        command = payload  # Decodificato automaticamente
        if command == "start":
            self.generator.running = True
            self.running_measurements = True
        elif command == "stop":
            self.running_measurements = False
            self.generator.running = False

    def handle_hello(self, topic, payload):
        if payload == "hello":
            if "hello_out" in self.topics:
                self.mqtt_client.publish(self.topics["hello_out"],"hello")

    def start_sending_measurements(self):
        for payload in self.generator.generate_measurements():
            if not self.running_measurements:
                break
            if "measurements_out" in self.topics:
                self.mqtt_client.publish(self.topics["measurements_out"],payload)

    def shutdown(self):
        self.running = False

    def run(self):
        while self.running:
            if self.running_measurements:
                self.start_sending_measurements()
            time.sleep(1 / self.frequency)
