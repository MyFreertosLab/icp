# MQTT Client Implementation
import paho.mqtt.client as mqtt
import json
from icp.utils.constants import TOPICS

# MQTT Client Setup
class MQTTClient:
    def __init__(self, broker, port):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.handlers = {}
        self.client.connect(broker, port, 60)

    def handle_message(self, topic, payload):
        for key, info in TOPICS.items():
          if info["topic"] == topic:
            message_type = info["type"]
            if message_type == "json":
                payload = json.loads(payload.decode("utf-8"))
            elif message_type == "string":
                payload = payload.decode("utf-8")
            # Per "binary", il payload rimane invariato
            return key, payload
          
    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code ", rc)
        for topic in self.handlers:
            client.subscribe(topic)

    def on_message(self, client, userdata, msg):
        key, payload = self.handle_message(msg.topic, msg.payload)
        if msg.topic in self.handlers:
            handler = self.handlers[msg.topic]
            handler(msg.topic, payload)  # decoded payload

    def add_handler(self, topic_info, handler):
        topic = topic_info["topic"]
        self.handlers[topic] = handler
        self.client.subscribe(topic)

    def publish(self, topic_info, payload):
        topic = topic_info["topic"]
        message_type = topic_info["type"]

        if message_type == "json":
           payload = json.dumps(payload).encode("utf-8")
        elif message_type == "string":
           payload = payload.encode("utf-8")
        self.client.publish(topic, payload)

    def loop_forever(self):
        self.client.loop_forever()

