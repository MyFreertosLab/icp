# Initializer Component Implementation
class Initializer:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def initialize(self):
        self.mqtt_client.publish('/imu/calibration/init/calreq', b'calibration_data')
        # Wait for acknowledgment

