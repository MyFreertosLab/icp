# MQTT Client Implementation
import paho.mqtt.client as mqtt

class MQTTClient:
    def __init__(self, broker, port):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.handlers = {}
        self.client.connect(broker, port, 60)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code" , rc)
        for topic in self.handlers:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        if msg.topic in self.handlers:
            self.handlers[msg.topic](msg.topic, msg.payload)

    def add_handler(self, topic, handler):
        self.handlers[topic] = handler
        self.client.subscribe(topic)

    def publish(self, topic, payload):
        self.client.publish(topic, payload)

    def loop_forever(self):
        self.client.loop_forever()

