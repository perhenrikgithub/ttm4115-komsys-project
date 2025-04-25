from escooter.escooter import EScooter, escooter_states, escooter_transition
import stmpy
from sense_hat import SenseHat
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
broker, port = "mqtt20.iik.ntnu.no", 1883

# ========== Settings ==============

ADD_MORE_SCOOTERS = True
ADD_FIFTH_SCOOTER = False

# ======= Settings done ============

sense = SenseHat()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    # client.subscribe("gr8/scooters/action/1")

client = mqtt.Client()
client.connect(broker, port)
client.on_connect = on_connect
client.loop_start()

RaspberryPi = EScooter("RaspberryPi", sense)
Pi_machine = stmpy.Machine(name=f'escooter1', transitions=escooter_transition, obj=RaspberryPi, states=escooter_states)
RaspberryPi.stm = Pi_machine
RaspberryPi.set_GPS("63.419413, 10.401522") # near hovedbygget
RaspberryPi.publish_status(is_available=True)

driver = stmpy.Driver() 
driver.add_machine(Pi_machine)

if ADD_MORE_SCOOTERS: 
    escooter = EScooter("Scooter1")
    escooter_machine1 = stmpy.Machine(name=f'escooter1', transitions=escooter_transition, obj=escooter, states=escooter_states)
    escooter.stm = escooter_machine1

    escooter2 = EScooter("Scooter2")
    escooter_machine2 = stmpy.Machine(name=f'escooter2', transitions=escooter_transition, obj=escooter, states=escooter_states)
    escooter2.stm = escooter_machine2

    escooter3 = EScooter("Scooter3")
    escooter_machine3 = stmpy.Machine(name=f'escooter3', transitions=escooter_transition, obj=escooter, states=escooter_states)
    escooter3.stm = escooter_machine3

    driver.add_machine(escooter_machine1)
    driver.add_machine(escooter_machine2)
    driver.add_machine(escooter_machine3)

if ADD_FIFTH_SCOOTER:
    escooter4 = EScooter("Scooter 4 (added later)")
    escooter_machine4 = stmpy.Machine(name=f'new scooter', transitions=escooter_transition, obj=escooter, states=escooter_states)
    escooter4.stm = escooter_machine4
    driver.add_machine(escooter_machine4)

driver.start()