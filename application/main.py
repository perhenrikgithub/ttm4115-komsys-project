from frontend.app import app
from statemachine.application import Application

import stmpy
import paho.mqtt.client as mqtt
import json
#Tankern her er å starte opp state machine og server samtidig
broker, port = "mqtt20.iik.ntnu.no", 1883

application = Application()
application_machine = stmpy.Machine(name=f'application', transitions=application_transitions, obj=application, states=application_states)
application.stm = application_machine

driver = stmpy.Driver()
driver.add_machine(application_machine)
driver.start()

if __name__ == "__main__":
    app.run(debug=True)



