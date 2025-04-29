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
    if application.active_scooter_id == "null":
        scooter_name = request.form.get('scooter_name')
        application.setActiveScooterID(scooter_name)
    application.req_unlock()
    application.received_report = False

    timeout = 5 
    poll_interval = 0.5 
    while timeout > 0:
        print(f"Poll returned: {application.unlock_successful}")
        time.sleep(poll_interval)

        if application.unlock_successful:
            application.unlock_successful = False  # reset the flag
            return render_template('active.html') 
        
        if application.error_message:
            flash(application.error_message)
            application.error_message = None

        timeout -= poll_interval  # Decrease timeout by poll_interval

    flash('Scooter timed out, or scooter is already in use')
    return redirect('/') 
    
    
@app.route('/lock', methods=['POST'])
def stop():
    application.req_lock() #! change here

    timeout = 5 
    poll_interval = 0.5 
    while timeout > 0:
        print(f"Poll returned: {application.lock_successful}") #! change here
        time.sleep(poll_interval)

        if application.lock_successful: #! change here
            application.lock_successful = False  # reset the flag #! change here
            flash(application.bill, "bill")
            application.bill = None # reset the bill

            return redirect("/") #home() #! change here
        
        if application.error_message:
            print(f"error message: {application.error_message}")
            flash(application.error_message)
            application.error_message = None
            return redirect('/active') #! change here

        timeout -= poll_interval  # Decrease timeout by poll_interval

    flash('Could not lock scooter (connection timeout)') #! change here
    return redirect('/active') 
   

@app.route('/reserve', methods=['POST'])
def reserve():
    scooter_name = request.form.get('scooter_name')
    application.setActiveScooterID(scooter_name)

    application.req_reserve() #! change here

    # Wait for key confirmation e.g. 'unlock_ok'
    timeout = 5 
    poll_interval = 0.5 
    while timeout > 0:
        print(f"Poll returned: {application.reserve_successful}") #! change here
        time.sleep(poll_interval)

        if application.reserve_successful: #! change here
            application.reserve_successful = False  # reset the flag #! change here
            return render_template('reserve.html') #! change here
        
        if application.error_message:
            print(f"error message: {application.error_message}")
            flash(application.error_message)
            application.error_message = None

        timeout -= poll_interval  # Decrease timeout by poll_interval

    flash('Could not reserve scooter (connection timeout)') #! change here
    return redirect('/')

@app.route('/report', methods=['POST'])
def report():
    scooter_name = request.json.get('scooter_name')  # Get the scooter name from the request
    # if not scooter_name:
    #     flash("Scooter name is required to report an issue.", "error")
    #     return redirect('/')

    # Publish a report message to the MQTT broker
    topic = f'gr8/scooters/action/{scooter_name}'
    payload = json.dumps({'action': 'report'})
    application.client.publish(topic, payload, qos=1)

    flash(f"Report for scooter '{scooter_name}' has been submitted.", "success")
    return redirect('/')

  
if __name__ == "__main__":
    app.run(debug=True, port=5015)

