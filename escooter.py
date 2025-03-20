import stmpy
import paho.mqtt.client as mqtt
import json
import random
from shared import broker, port

class EScooter:
    stm: stmpy.Machine

    def __init__(self, scooter_id: str):
        self.scooter_id = scooter_id
        
        self.client = mqtt.Client()
        self.client.connect(broker, port)
        # self.client.subscribe('gr8/scooters')
        self.client.subscribe('gr8/scooters/' + self.scooter_id)
        print(f"Scooter is initilizes with id: {self.scooter_id}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_start()
    
    def on_connect(self, client, userdata, flags, rc):
        print(f"Scooter {self.scooter_id} connected to server")

    def get_state(self):
        return self.stm.state

    def on_message(self, client, userdata, msg):
        print(f"Scooter {self.scooter_id} received message: {msg.payload}")
        if msg.payload == 'unlock':
            self.stm.send('unlock')
        elif msg.payload == 'lock':
            self.stm.send('lock')

    def get_GPS(self):
        return f"{random.uniform(63.3800, 63.4600)}, {random.uniform(10.3300, 10.4900)}"

    def lock_scooter(self):
        print("lock_scooter()")
        response = {
            'scooter_id': self.scooter_id, 
            'GPS': self.get_GPS(), 
            'available': True
        }
        self.client.publish('gr8/scooters/' + self.scooter_id, json.dumps(response))

    def unlock_scooter(self):
        print("unlock_scooter()")
        response = {
            'scooter_id': self.scooter_id, 
            'GPS': self.get_GPS(), 
            'available': False
        }
        self.client.publish('gr8/scooters/' + self.scooter_id, json.dumps(response))

    def move_forward(self):
        print("move_forward()")
        # turns off enigne (screen stuff)
        pass

    def stop_moving(self):
        print("stop_moving()")
        # turns off enigne (screen stuff)
        pass



escooter_states = [
        {
            'name': 'locked', 
            'entry': 'lock_scooter',
            'exit': 'unlock_scooter'
        },
        {
            'name': 'off'
        },
        {
            'name': 'on',
            'entry': 'move_forward',
            'exit': 'stop_moving'
        }
    ]

escooter_transition = [
        {
            'source': 'initial',
            'target': 'locked'
        },

        {
            'source': 'locked',
            'target': 'off',
            'trigger': 'unlock'
        },
        {
            'source': 'off',
            'target': 'on',
            'trigger': 'gas'
        },
        {
            'source': 'on',
            'target': 'off',
            'trigger': 'release'
        },
        {
            'source': 'off',
            'target': 'locked',
            'trigger': 'lock'
        }
    ]

escooter = EScooter("1")
escooter_machine = stmpy.Machine(name=f'escooter1', transitions=escooter_transition, obj=escooter, states=escooter_states)
escooter.stm = escooter_machine
print(escooter.get_GPS())

driver = stmpy.Driver()
driver.add_machine(escooter_machine)
driver.start()