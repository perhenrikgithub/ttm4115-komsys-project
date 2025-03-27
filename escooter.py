import stmpy
import paho.mqtt.client as mqtt
import json
import random
from shared import broker, port
import animation
import time

class EScooter:
    stm: stmpy.Machine
    is_reserved = False
    x_offset = 0 # is used to handle animation
    reserve_start_time: time
    reserve_finish_time: time
    ride_start_time: time
    ride_finish_time: time

    def __init__(self, scooter_id: str):
        self.scooter_id = scooter_id
        print(f"[init] S{self.scooter_id}")
        
        self.client = mqtt.Client()
        self.client.connect(broker, port)
        self.client.subscribe('gr8/scooters/action/' + self.scooter_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT - S{self.scooter_id}] Connected to broker")

    def on_message(self, client, userdata, msg):
        print(f"[MQTT - S{self.scooter_id}] Message recieved: {msg.payload}")

        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            print(f"[ERROR {self.scooter_id}] on_message(): {err}")
            return
        action = payload.get('action')

        if action == 'unlock':
            self.stm.send('unlock')
        
        elif action == 'lock':
            self.stm.send('lock')
        
        elif action == 'reserve':
            self.stm.send('reserve')
        
        elif action == 'unreserve':
            self.stm.send('unreserve')

        # elif action == 'status':
        #     pass

    def get_GPS(self):
        # returns a random GPS location in Trondheim (as the raspberry pi does not have GPS), if properly implemented, this would return the actual GPS location
        return f"{random.uniform(63.3800, 63.4600)}, {random.uniform(10.3300, 10.4900)}"

    def get_battery(self):
        # returns a set battery as the raspberry pi does not have a battery, if properly implemented, this would return the actual battery level
        return '60%'
    
    def is_available(self):
        return self.stm.state == 'idle'
    
    def publish_status(self):
        status = {
            'available': self.is_available(),
            'scooter_id': self.scooter_id,
            'location': self.get_GPS(), 
            'battery': self.get_battery(),
        }
        self.client.publish('gr8/scooters/status', json.dumps(status))

    def lock(self):
        print("lock()")
        # if the rasberry pi has a lock, it should be locked here

        # ? is this necessary?
        # publish an ack to the server and application, if not recieved, the app should try again
        response = {'status': 'ok'}
        self.client.publish('gr8/scooters/' + self.scooter_id, json.dumps(response))

        # publish the status of the scooter (available, location, battery) to all apps and server
        self.publish_status()

    def unlock(self):
        print("unlock()")
        # if the rasberry pi has a lock, it should be unlocked here

        # ? is this necessary?
        # publish an ack to the server and application, if not recieved, the app should try again
        response = {'status': 'ok'}
        self.client.publish('gr8/scooters/' + self.scooter_id, json.dumps(response))
        
        # publish the status of the scooter (available, location, battery) to all apps and server
        self.publish_status()

    def reserve(self):
        print("reserve")

    def unreserve(self):
        print("unreserve")

    def move(self):
        # turns on engine (screen stuff)
        animation.set_display(self.x_offset)
        self.x_offset = (self.x_offset + 1) % 8

    def stop(self):
        # turns off enigne (screen stuff)
        animation.set_display(0) 



escooter_states = [
        {
            'name': 'idle'
        },
        {
            'name': 'reserved',
            'entry': 'reserve',
            'exit': 'unreserve'
        },
        {
            'name': 'unlocked'
        },
        {
            'name': 'driving',
            'entry': 'move; start_timer("t", 300)',

        }
    ]

escooter_transition = [
        {
            'source': 'initial',
            'target': 'idle'
        },
        {
            'source': 'idle',
            'target': 'reserved',
            'trigger': 'reserve',
            'effect': 'reserve'
        },
        {
            'source': 'reserved',
            'target': 'idle',
            'trigger': 'unreserve',
            'effect': 'unreserve'
        },
        {
            'source': 'reserved',
            'target': 'unlocked',
            'trigger': 'unlock',
            'effect': 'unlock; unreseve'

        },
        {
            'source': 'idle',
            'target': 'unlocked',
            'trigger': 'unlock',
            'effect': 'unlock'
        },
        {
            'source': 'unlocked',
            'target': 'idle',
            'trigger': 'lock',
            'effect': 'lock'
        },
        {
            'source': 'unlocked',
            'target': 'driving',
            'trigger': 'gas',
        },
        {
            'source': 'driving',
            'target': 'unlocked',
            'trigger': 'release',
            'effect': 'stop'
        },
        {
            'source': 'driving',
            'target': 'driving',
            'trigger': 't',
        }

    ]

# from server import Server
# server = Server()

driver = stmpy.Driver()

escooter = EScooter("1")
escooter_machine = stmpy.Machine(name=f'escooter1', transitions=escooter_transition, obj=escooter, states=escooter_states)
escooter.stm = escooter_machine

driver.add_machine(escooter_machine)
driver.start()

# with open("graph.gv", "w") as file:
#     print(stmpy.get_graphviz_dot(escooter_machine), file=file)
# dot -Tsvg graph.gv -o graph.svg

