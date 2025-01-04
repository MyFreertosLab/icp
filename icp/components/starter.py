# Starter Component Implementation
class Starter:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.received_hello = False

    def start(self):
        self.mqtt_client.publish('/imu/calibration/st/hello', 'hello')
        # Wait for response, implement further logic here

