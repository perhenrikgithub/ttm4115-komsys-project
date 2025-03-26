import stmpy
import paho.mqtt.client as mqtt
import json
from shared import broker, port

class Application:
    stm: stmpy.Machine 

    def __init__(self, username: str):
        self.username = username
        self.client = mqtt.Client()
        self.client.connect(broker, port)
        self.client.subscribe('gr8/scooters')

    def on_connect(self, client, userdata, flags, rc):
        print(f"{self.username}'s application connected to server")

    def on_message(self, client, userdata, msg):
        print(f"{self.username}'s application received message: {msg.payload}")

    # def reserve_scooter(self, scooter_id):
    #     print("reserve_scooter()")
    #     # publish to mqtt
    #     pass

    # def unreserve_scooter(self, scooter_id):
    #     print("unreserve_scooter()")
    #     # publish to mqtt
    #     pass

    def list_available_scooters(self):
        print("list_available_scooters()")
        # publish to mqtt
        pass

    def unlock_scooter(self, scooter_id):
        print("unlock_scooter()")
        # publish to mqtt
        pass

    def park_scooter(self, scooter_id):
        print("park_scooter()")
        # publish to mqtt
        pass

    def calculate_bill(self, scooter_id):
        print("calculate_bill()")
        # publish to mqtt
        pass

    def complete_transaction(self, scooter_id):
        print("complete_transaction()")
        # publish to mqtt
        pass

    def file_report(self, scooter_id, contents):
        print("file_report()")
        
        pass

application_states = [
    {
        'name': 'reserved',
        'entry': 'reserve_scooter'
    },
    {
        'name': 'driving',
        'entry': 'unlock_scooter'
    },
    {
        'name': 'park_scooter',
        'entry': 'park_scooter'
    },
    {
        'name': 'calculate_bill_and_pay',
        'entry': 'calculate_bill',
        'exit': 'complete_transaction'
    },
    {
        'name': 'idle',
    }
]

application_transitions = [
    {
        'source': 'initial',
        'target': 'idle'
    },
    {
        'source': 'idle',
        'target': 'reserved',
        'trigger': 'reserve'
    },
    {
        'source': 'reserved',
        'target': 'driving',
        'trigger': 'unlock'
    },
    {
        'source': 'idle',
        'target': 'driving',
        'trigger': 'unlock'
    },
    {
        'source': 'driving',
        'target': 'park_scooter',
        'trigger': 'park'
    },
    {
        'source': 'park_scooter',
        'target': 'calculate_bill_and_pay',
        'trigger': 'recive'
    },
    {
        'source': 'calculate_bill_and_pay',
        'target': 'idle',
        'trigger': 'pay'
    },
    {
        'source': 'idle',
        'target': 'idle',
        'trigger': 'report',
        'action': 'file_report'
    },
    {
        'source': 'reserved',
        'target': 'reserved',
        'trigger': 'report',
        'action': 'file_report'
    },
]

application = Application()
application_machine = stmpy.Machine(name=f'application', transitions=application_transitions, obj=application, states=application_states)
application.stm = application_machine

driver = stmpy.Driver()
driver.add_machine(application_machine)
driver.start()