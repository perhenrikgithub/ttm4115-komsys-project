import stmpy
import paho.mqtt.client as mqtt
import json
broker, port = "mqtt20.iik.ntnu.no", 1883

class Application:
    stm: stmpy.Machine 
    known_scooters = {}

    def __init__(self, username: str):
        self.username = username

        self.client = mqtt.Client()
        self.client.connect(broker, port)

        self.client.subscribe('gr8/scooters/status')
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"{self.username}'s application connected to server")

    def on_message(self, client, userdata, msg):
        # print(f"{self.username}'s application received message: {msg.payload}")
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            print(f"[ERROR {self.scooter_id}] on_message(): {err}")
            return
        
        #sort on topic
        if msg.topic == 'gr8/scooters/status':
            scooter_id = payload.get('scooter_id')
            status = payload.get('status')
            location = payload.get('location')
            battery = payload.get('battery')
            
            scooter = {
                'status': status,
                'location': location,
                'battery': battery
            }

            if scooter_id not in self.known_scooters and status == 'available' and battery > 20:
                self.known_scooters[scooter_id] = scooter
                # print(f"Scooter added: {scooter_id}")
            elif scooter_id in self.known_scooters and status != 'available':
                del self.known_scooters[scooter_id]
                # print(f"Scooter removed: {scooter_id}")
    

    def get_scooter_list(self):
        self.client.publish('gr8/server/scooter_list', 'Go', qos=1)

            


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

    def unlock(self):
        print("unlock_scooter()")
        # publish to mqtt
        pass

    def file_report(self):
        print("file_report()")
        #publish to mqtt
        pass

    def lock(self):
        print("lock_scooter()")
        # publish to mqtt
        pass

application_states = [
    {
        'name': 'idle',
        'entry': 'list_available_scooters'
    },
    {
        'name': 'active',
    },
]

application_transitions = [
    {
        'source': 'initial',
        'target': 'idle'
    },
    {
        'source': 'idle',
        'target': 'active',
        'trigger': 'unlock',
        'effect': 'unlock'
    },
    {
        'source': 'idle',
        'target': 'idle',
        'trigger': 'report',
        'effect': 'file_report'
    },
    {
        'source': 'idle',
        'target': 'idle',
        'trigger': 'reserve',
        'effect': 'file_report'
    },
    {
        'source': 'active',
        'target': 'idle',
        'trigger': 'lock',
        'effect': 'lock'
    },
]

application = Application()
application_machine = stmpy.Machine(name=f'application', transitions=application_transitions, obj=application, states=application_states)
application.stm = application_machine

driver = stmpy.Driver()
driver.add_machine(application_machine)
driver.start()