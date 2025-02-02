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


class MPU9250SimulatorTest:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.simulator = None
        self.result = {"imu_status_seq": [], "measures": []}
        self.setup_handlers()

    def setup_handlers(self):
        """Configura i gestori MQTT per raccogliere dati dai topic."""
        self.mqtt_client.add_handler(
            {"topic": "/imu/calibration/imu/status", "type": "string"},
            self.on_imu_status
        )
        self.mqtt_client.add_handler(
            {"topic": "/imu/calibration/imu/measures", "type": "binary"},
            self.on_measure
        )

        # Mock del Component Registry
        self.mqtt_client.add_handler(
            {"topic": "/system/registry/register", "type": "json"},
            self.handle_registration
        )

    def on_imu_status(self, topic, payload):
        """Gestore per lo stato IMU."""
        logger.debug(f"received imu status: {payload}")
        self.result["imu_status_seq"].append(payload)

    def on_measure(self, topic, payload):
        """Gestore per le misurazioni."""
        msg_type, = struct.unpack("I", payload[:4])
        measure = struct.unpack(FORMATS[MPUMessageType(msg_type)], payload)
        self.result["measures"].append(measure)

    def handle_registration(self, topic, payload):
        """Risponde al messaggio di registrazione del simulatore."""
        registration_request = payload
        component_name = registration_request["name"]

        resolved_topics = {
            "control_status_in": {"topic": "/imu/calibration/control/status", "type": "string"},
            "settings_in": {"topic": "/imu/calibration/control/imu/settings", "type": "binary"},
            "status_out": {"topic": "/imu/calibration/imu/status", "type": "string"},
            "measurements_out": {"topic": "/imu/calibration/imu/measures", "type": "binary"}
        }

        self.mqtt_client.publish(
            {"topic": f"/system/registry/{component_name}/response", "type": "json"},
            resolved_topics
        )

    def wait_for_condition(self, condition, retries=10, delay=1, status_topic=None, status_payload=None):
      """
      Attende che una condizione sia vera, ripubblicando lo stato corrente se fornito.
    
      Args:
        condition (callable): Funzione booleana che rappresenta la condizione.
        retries (int): Numero massimo di tentativi.
        delay (float): Intervallo di attesa tra i tentativi (in secondi).
        status_topic (dict): Il topic MQTT per ripubblicare lo stato, se necessario.
        status_payload (str): Lo stato da ripubblicare sul topic.
    
      Returns:
        bool: True se la condizione è soddisfatta, False altrimenti.
      """
      for _ in range(retries):
        if condition():
            return True
        if status_topic and status_payload:
            self.mqtt_client.publish(status_topic, payload=status_payload)
            logger.debug(f"Re-published status: {status_payload} to topic: {status_topic}")
        time.sleep(delay)
      return False

    def run_test(self):
        """Esegue il flusso completo di test."""
        # Avvia il simulatore
        self.simulator = MPU9250Simulator(self.mqtt_client)
        self.simulator.start()
        time.sleep(2)

        # Fase 1: Stato Idle
        logger.info("Testing IMU idle state when starting ...")
        self.mqtt_client.publish(
            {"topic": "/imu/calibration/control/status", "type": "string"},
            payload="starting"
        )
        assert self.wait_for_condition(
            lambda: len(self.result["imu_status_seq"]) > 0 and self.result["imu_status_seq"][-1] == "idle",
            retries=10,
            delay=1,
            status_topic={"topic": "/imu/calibration/control/status", "type": "string"},
            status_payload="starting"
        )

        # Fase 2: Misurazioni in corso
        logger.info("Testing IMU sending measurements state when waiting_measurements...")
        self.mqtt_client.publish(
            {"topic": "/imu/calibration/control/status", "type": "string"},
            payload="waiting_measurements"
        )
        assert self.wait_for_condition(
            lambda: len(self.result["imu_status_seq"]) > 0 and self.result["imu_status_seq"][-1] == "sending_measurements",
            retries=10,
            delay=1,
            status_topic={"topic": "/imu/calibration/control/status", "type": "string"},
            status_payload="waiting_measurements"
        )
        assert self.wait_for_condition(lambda: len(self.result["measures"]) > 0)

        # Fase 3: Stato di elaborazione
        logger.info("Testing IMU idle state when processing...")
        self.mqtt_client.publish(
            {"topic": "/imu/calibration/control/status", "type": "string"},
            payload="processing"
        )
        assert self.wait_for_condition(
            lambda: len(self.result["imu_status_seq"]) > 0 and self.result["imu_status_seq"][-1] == "idle",
            retries=10,
            delay=1,
            status_topic={"topic": "/imu/calibration/control/status", "type": "string"},
            status_payload="processing"
        )

        # Fase 4: Spegnimento
        logger.info("Testing IMU offline state when shutting_down...")
        assert self.wait_for_condition(
            lambda: len(self.result["imu_status_seq"]) > 0 and self.result["imu_status_seq"][-1] == "offline",
            retries=10,
            delay=1,
            status_topic={"topic": "/imu/calibration/control/status", "type": "string"},
            status_payload="shutting_down"
        )
        logger.info("IMU simulator reached offline state successfully.")

        self.simulator.join()


@pytest.fixture(scope="module")
def mqtt_client():
    client = MQTTClient(MQTT_BROKER, MQTT_PORT)
    threading.Thread(target=client.loop_forever, daemon=True).start()
    time.sleep(1)  # Assicurati che la connessione MQTT sia stabilita
    return client


def test_simulator(mqtt_client):
    test = MPU9250SimulatorTest(mqtt_client)
    test.run_test()

