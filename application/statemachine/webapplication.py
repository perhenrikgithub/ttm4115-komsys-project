import stmpy
import paho.mqtt.client as mqtt
import json
broker, port = "mqtt20.iik.ntnu.no", 1883

class Application:
    stm: stmpy.Machine 
    known_scooters = {}
    active_scooter_id = None
    received_report = False

    def test(self):
        return "hei"

    def __init__(self, username='test'):
        self.username = username

        self.client = mqtt.Client()
        self.client.connect(broker, port)

        self.client.subscribe('gr8/scooters/status')
        self.client.subscribe('gr8/scooters/response/#')
        self.client.subscribe('gr8/scooters/report/#')
        self.client.subscribe('gr8/server/scooter_list')
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.request_scooter_list_from_server()

    def on_connect(self, client, userdata, flags, rc):
        print(f"{self.username}'s application connected to server")

    def on_message(self, client, userdata, msg):
        # print(f"{self.username}'s application received message: {msg.payload}")
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            print(f"[ERROR {self.scooter_id}] on_message(): {err}")
            return
        

        # sort on topic
        if msg.topic == 'gr8/scooters/status': 
            self.known_scooters[payload.get('scooter_id')] = {
                'status': payload.get('status'),
                'location': payload.get('location'),
                'battery': payload.get('battery'),
            }

        elif msg.topic == 'gr8/scooters/response/' + self.active_scooter_id:
            response = payload.get('response')
            if response == 'unlock_ok':
                # print(f"{self.username}'s application unlocked scooter {self.active_scooter_id}")
                #tell sm unlock_ok
                pass
            elif response == 'lock_ok':
                # print(f"{self.username}'s application locked scooter {self.active_scooter_id}")
                #tell sm lock_ok
                self.active_scooter_id = None
                pass

        elif msg.topic == 'gr8/scooters/report/' + self.active_scooter_id:
            self.received_report = True
                

    def req_unlock(self):
        # print("request_unlock_scooter()")
        if self.active_scooter_id is None:
            print("No active scooter to unlock")
            return
        self.received_report = False
        # publish to mqtt
        self.client.publish('gr8/scooters/action/'+ self.active_scooter_id, json.dumps({'action':'unlock'}), qos=1)
        

    def req_lock(self):
        # print("request_lock_scooter()")
        if self.active_scooter_id is None:
            print("No active scooter to lock")
            return
        
        # publish to mqtt
        self.client.publish('gr8/scooters/action/'+ self.active_scooter_id, json.dumps({'action':'lock'}), qos=1)
        
    def req_reserve(self):
        # print("request_reserve_scooter()")
        if self.active_scooter_id is None:
            print("No active scooter to reserve")
            return
        # publish to mqtt
        self.client.publish('gr8/scooters/action/'+ self.active_scooter_id, json.dumps({'action':'reserve'}), qos=1)


    def request_scooter_list_from_server(self):
        self.client.publish('gr8/server/scooter_list', 'Go', qos=1)




application_states = [
    {
        'name': 'idle',
    },
    {
        'name': 'active',
    },
    {
        'name': 'reserved',
    },
    {
        'name': 'wait_reserve',
        'entry': 'start_timer("t", 5000)',
    },
    {
        'name': 'wait_unlock',
        'entry': 'start_timer("t", 5000)',
    },
    {
        'name': 'wait_lock',
        'entry': 'start_timer("t", 5000)',
    },
]

application_transitions = [
    {
        'source': 'initial',
        'target': 'idle'
    },
    {
        'source': 'idle',
        'target': 'wait_reserve',
        'trigger': 'req_reserve',
    },
    {
        'source': 'wait_reserve',
        'target': 'reserved',
        'trigger': 'reserve_ok',
    },
    {
        'source': 'wait_reserve',
        'target': 'idle',
        'trigger': 't',
    },
    {
        'source': 'reserved',
        'target': 'wait_unlock',
        'trigger': 'req_unlock',
    },
    {
        'source': 'idle',
        'target': 'wait_unlock',
        'trigger': 'req_unlock',
    },
    {
        'source': 'wait_unlock',
        'target': 'active',
        'trigger': 'unlock_ok',
    },
    {
        'source': 'wait_unlock',
        'target': 'idle',
        'trigger': 't',
    },
    {
        'source': 'active',
        'target': 'wait_lock',
        'trigger': 'req_lock',
    },
    {
        'source': 'wait_lock',
        'target': 'idle',
        'trigger': 'lock_ok',
    },
    {
        'source': 'wait_lock',
        'target': 'active',
        'trigger': 't',
    }
]

