
import threading
import time
import json
import struct
import logging
from icp.icp_tests.test_components.measure_generator import MeasureGenerator

class MPU9250Simulator(threading.Thread):
    def __init__(self, mqtt_client, frequency=500):
        super().__init__()
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.frequency = frequency
        self.mqtt_client = mqtt_client
        self.generator = MeasureGenerator()
        self.topics = None  # Sarà popolato con i topic assegnati dal registro
        self.control_status = "unknown"
        self.status = "unknown"
        self.register_with_registry()
        self.logger.debug("initialized component")

    ###########################################
    #### Handlers
    ###########################################
    def handle_registry_response(self, topic, payload):
        # Salva i topic assegnati dal registro
        self.topics = payload
        self.logger.debug(f"received register response:  {payload}")

        # Configura i topic di input
        if "control_status_in" in self.topics:
            self.mqtt_client.add_handler(
                self.topics["control_status_in"],
                self.handle_control_status
            )
        if "settings_in" in self.topics:
            self.mqtt_client.add_handler(
                self.topics["settings_in"],
                self.handle_settings
            )
        self.set_state_idle()

    def handle_settings(self, topic, payload):
        self.logger(f"received settings from topic {topic}", topic)

    def handle_control_status(self, topic, payload):
        self.logger.debug(f"received control status: {payload}")
        self.control_status = payload
        if self.control_status == "waiting_measurements" or self.control_status == "receiving_measurements":
            self.set_state_sending_measurements()
        elif self.control_status == "shutting_down":
            self.set_state_offline()
        else:
            self.set_state_idle()            

    ###########################################
    #### Registration
    ###########################################
    def register_with_registry(self):
        self.set_state_registering()
        registration_message = {
            "name": "imu",
            "pins": {
                "input": [
                    {"name": "control_status_in", "type": "string"},
                    {"name": "settings_in", "type": "binary"}
                ],
                "output": [
                    {"name": "status_out", "type": "string"},
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
        self.logger.debug(f"sent registration request:  {registration_message}")
        # Ascolta la risposta del registro
        response_topic = "/system/registry/imu/response"
        self.mqtt_client.add_handler(
            {"topic": response_topic, "type": "json"},
            self.handle_registry_response
        )

    ###########################################
    #### Functionalities
    ###########################################
    def send_measurements(self):
        if "measurements_out" in self.topics:
           for payload in self.generator.generate_measurements():
               self.mqtt_client.publish(self.topics["measurements_out"],payload)

    ###########################################
    #### States and Transtions
    ###########################################
    def set_state_offline(self):
        if not self.is_state_offline():
           self.status = "offline"
           self.mqtt_client.publish(self.topics["status_out"],self.status)

    def is_state_offline(self):
        return self.status == "offline"

    def set_state_sending_measurements(self):
        if not self.is_state_sending_measurements():
           self.status = "sending_measurements"
           self.mqtt_client.publish(self.topics["status_out"],self.status)

    def is_state_sending_measurements(self):
        return self.status == "sending_measurements"

    def set_state_idle(self):
        if not self.is_state_idle():
           self.status = "idle"
           self.mqtt_client.publish(self.topics["status_out"],self.status)

    def is_state_idle(self):
        return self.status == "idle"

    def set_state_registering(self):
        if not self.is_state_registering():
           self.status = "registering"

    def is_state_registering(self):
        return self.status == "registering"

    ###########################################
    #### Thread Loop
    ###########################################
    def run(self):
        while not self.is_state_offline():
            if self.is_state_sending_measurements():
                self.send_measurements()
            time.sleep(1 / self.frequency)
        self.logger.debug(f"bye bye ...")
