import threading
import time
import json
import paho.mqtt.client as mqtt
import struct

import threading
import json
import logging

# Mapping globale dei pin
MAPPINGS = [
    {
        "source": {"component": "imu", "pin": "status_out"},
        "target": {"component": "point_estimator", "pin": "imu_status_in"},
        "topic": {"name": "/imu/calibration/imu/status", "type": "string"}
    },
    {
        "source": {"component": "point_estimator", "pin": "status_out"},
        "target": {"component": "imu", "pin": "control_status_in"},
        "topic": {"name": "/imu/calibration/point_estimator/status", "type": "string"}
    },
    {
        "source": {"component": "imu", "pin": "measurements_out"},
        "target": {"component": "point_estimator", "pin": "measurements_in"},
        "topic": {"name": "/imu/calibration/imu/measures", "type": "binary"}
    },
    {
        "source": {"component": "point_estimator", "pin": "imu_configs_out"},
        "target": {"component": "imu", "pin": "configs_in"},
        "topic": {"name": "/imu/calibration/imu/configs", "type": "binary"}
    }
]

class ComponentRegistry(threading.Thread):
    def __init__(self, mqtt_client):
        super().__init__()
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        self.running = True
        self.mappings = MAPPINGS
        self.registry = {}
        self.mqtt_client = mqtt_client
        self.mqtt_client.add_handler(
            {"topic": "/system/registry/register", "type": "json"}, self.handle_registration
        )
        self.logger.debug("initialized component")

    def handle_registration(self, topic, payload):
        registration_request = payload  # Il payload è già decodificato come JSON
        component_name = registration_request["name"]
        pins = registration_request["pins"]
        self.logger.debug(f"received registration from component {component_name}")

        # Risolvi i topic per ogni pin
        resolved_topics = {}
        for pin_type in ["input", "output"]:
            for pin in pins.get(pin_type, []):
                pname = pin["name"]
                resolved = False
                for mapping in self.mappings:
                    if pin_type == "input" and mapping["target"]["component"] == component_name and mapping["target"]["pin"] == pname:
                        resolved_topics[pname] = {
                            "topic": mapping["topic"]["name"],
                            "type": mapping["topic"]["type"]
                        }
                        resolved = True
                    elif pin_type == "output" and mapping["source"]["component"] == component_name and mapping["source"]["pin"] == pname:
                        resolved_topics[pname] = {
                            "topic": mapping["topic"]["name"],
                            "type": mapping["topic"]["type"]
                        }
                        resolved = True
                if not resolved:
                    self.logger.warning(f"mapping {pin_type} not resolved for pin {pname} in component {component_name}")


        self.registry[component_name] = resolved_topics
        # Rispondi con i topic risolti
        self.mqtt_client.publish({"topic": f"/system/registry/{component_name}/response","type": "json"}, resolved_topics)

    def shutdown(self):
        self.running = False

    def run(self):
        while self.running:
            time.sleep(20)
