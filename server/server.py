import paho.mqtt.client as mqtt
import json
broker, port = "mqtt20.iik.ntnu.no", 1883

class Server:    
    known_scooters = {}

    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(broker, port)
        self.client.subscribe('gr8/server/#')
        self.client.subscribe('gr8/scooters/status')
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Server connected to broker")

    def on_message(self, client, userdata, msg):
        if msg.topic == "gr8/server/scooter_list":
            self.publish_scooter_list()

        elif msg.topic == "gr8/scooters/status":
            try:
                payload = json.loads(msg.payload.decode("utf-8"))
            except Exception as err:
                print(f"[ERROR {self.scooter_id}] on_message(): {err}")
                return
            
            print(f"Received scooter status: {payload}")

            self.known_scooters[payload.get('scooter_id')] = {
                'available': payload.get('available'),
                'location': payload.get('location'),
                'battery': payload.get('battery')    ,
                'is_currently_charging': payload.get('is_currently_charging')
            }
    
    def publish_scooter_list(self):
        self.client.publish("gr8/scooters/scooter_list", json.dumps(self.known_scooters))

