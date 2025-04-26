from flask import Flask, render_template, redirect, flash, request, url_for
from statemachine.webapplication import Application, application_states, application_transitions
import time
import stmpy
import paho.mqtt.client as mqtt
import json
        
#sett opp aplication instanas
application = Application(username="Emrik")
application_machine = stmpy.Machine(name=f'application', transitions=application_transitions, obj=application, states=application_states)
application.stm = application_machine
driver = stmpy.Driver()
driver.add_machine(application_machine)
driver.start()

app = Flask(__name__)
app.secret_key ="fuck_omega"


@app.route("/")
def home():
    application.request_scooter_list_from_server() #To get updated list
    scooters = application.getList()
    return render_template('index.html', scooters = scooters)


@app.route('/active', methods=['POST']) #bør kalle state machine , sjekker om den kan leie
def active():
    scooter_name = request.form.get('scooter_name')
    application.setActiveScooterID(scooter_name)
    application.req_unlock()

    # Wait for unlock_ok confirmation
    timeout = 5 
    poll_interval = 0.3 
    while timeout > 0:
        if getattr(application, "unlock_done", False):
            application.unlock_done = False  # reset the flag
            return render_template('active.html') # TODO check if this redirect is correct
        
        if application.error_message:
            application.error_message = None
            flash(application.error_message)

        time.sleep(poll_interval)
        timeout -= poll_interval  # Decrease timeout by poll_interval

    flash('Could not unlock the escooter (timeout)')
    return redirect(url_for('index')) # TODO check if this redirect is correct
    
    
@app.route('/lock', methods=['POST'])
def stop():
    application.req_lock()
    return redirect('/')
   

@app.route('/reserve', methods=['POST'])
def reserve():
    scooter_name = request.form.get('scooter_name')
    application.setActiveScooterID(scooter_name)

    if application.req_reserve():
        return render_template('reserve.html')
    else: 
        flash("Could not reserve this scooter")        

  
if __name__ == "__main__":
    app.run(debug=True, port=5014)

