from flask import Flask, render_template, redirect, flash
from statemachine.webapplication import Application, application_states, application_transitions

import stmpy
import paho.mqtt.client as mqtt
import json


broker, port = "mqtt20.iik.ntnu.no", 1883 #sett opp aplication instanas
application = Application("emrik")
application_machine = stmpy.Machine(name=f'application', transitions=application_transitions, obj=application, states=application_states)
application.stm = application_machine
driver = stmpy.Driver()
driver.add_machine(application_machine)
driver.start()

app = Flask(__name__)
app.secret_key ="fuck_omega"


@app.route("/") #kanskje vise aktuelle sykler, om mulig
def home():
    application.request_scooter_list_from_server() #To get updated list
    scooters = application.getList()
    return render_template('index.html', scooters = scooters)


@app.route('/start', methods=['POST']) #bør kalle state machine , sjekker om den kan leie
def start():
    if application.req_unlock():
        return render_template('renting.html')
    else:
        flash("You cant rent this scooter") #flash is used to sendfeedback to users
    
@app.route('/stop', methods=['POST'])
def stop():
    if application.req_lock():
        return redirect('/')
    else:
        flash("You can not park here")
    
@app.route('/reserve', methods=['POST'])
def reserve():
    if application.req_reserve():
        return render_template('reserve.html')
    else: 
        flash("Could not reserve this scooter")        

  
if __name__ == "__main__":
    app.run(debug=True, port=5004)

