from flask import Flask, render_template, redirect


app = Flask(__name__)

@app.route("/") #kanskje vise aktuelle sykler, om mulig
def home():
    scooters = [
            {"name": "Scooter 1"},
            {"name": "Scooter 2"}
    ]
    return render_template('index.html', scooters = scooters)

test = True
test2 = True
test3 = True

@app.route('/start', methods=['POST']) #bør kalle state machine , sjekker om den kan leie
def start():
    if test:
        return render_template('renting.html')
    
@app.route('/stop', methods=['POST'])
def stop():
    if test2:
        return redirect('/')
    
@app.route('/reserve', methods=['POST'])
def reserve():
    if test3:
        return render_template('reserve.html')