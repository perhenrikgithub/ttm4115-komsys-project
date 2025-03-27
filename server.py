import stmpy
import paho.mqtt.client as mqtt
import json
from shared import broker, port


class Server:
    
    users = []
    scooters = []


    def __init__(self):
        print("Server is initialized")

        # mqtt stuff
        self.client = mqtt.Client()
        self.client.connect(broker, port)
        self.client.subscribe('gr8/#') # TODO: add topic
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"Server connected to broker")

    def on_message(self, client, userdata, msg):
        print(f"Server received message: {msg.payload}")

        m = json.loads(msg.payload)
        print(f"[SERVER] {m}")

    def reserve_scooter(self):
        pass

    def unreserve_scooter(self):
        pass

    def unlock_scooter(self):
        self.client.publish('gr8/scooters/action/1', json.dumps({'action': 'unlock'}))

    def lock_scooter(self):
        self.client.publish('gr8/scooters/action/1', json.dumps({'action': 'lock'}))

