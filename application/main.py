from frontend.app import create_app
from statemachine.webapplication import Application, application_states, application_transitions
#from escooter.escooter import EScooter, escooter_states, escooter_transition

import stmpy
import paho.mqtt.client as mqtt
import json
#Tankern her er å starte opp state machine og server samtidig
broker, port = "mqtt20.iik.ntnu.no", 1883

application = Application("emrik")
application_machine = stmpy.Machine(name=f'application', transitions=application_transitions, obj=application, states=application_states)
application.stm = application_machine

#escooter1 = EScooter("1")
#escooter1_stm = stmpy.Machine(name="es1", transitions=escooter_transition, obj=escooter1, states=escooter_states)
#escooter1.stm = escooter1_stm

driver = stmpy.Driver()
driver.add_machine(application_machine)
#driver.add_machine(escooter1_stm)
driver.start()

app = create_app(application)

if __name__ == "__main__":
    app.run(debug=True, port=5003)




