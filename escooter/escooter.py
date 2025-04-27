import stmpy
import paho.mqtt.client as mqtt
import json
import math
import time
import random
import escooter.animation as animation
from escooter.IMUhelper import normalize_angle, ROLL_THRESHOLD, PITCH_THRESHOLD
from escooter.chargeDetector import is_charging
broker, port = "mqtt20.iik.ntnu.no", 1883

import pygame
pygame.mixer.init()
sound = pygame.mixer.Sound("escooter/sound2.wav")

class EScooter:
    stm: stmpy.Machine
    is_reserved = False
    x_offset = 0
    # impact_detected = False
    # impact_detected_critical = False 

    pitch: float
    roll: float


    # variables that are used to determine what the user are going to pay
    reserve_start_time: time.time
    reserve_end_time: time.time
    cost_per_minute_reserved: float = 3.5 # kr/min
    cost_per_km: float = 15 # kr/km
    number_of_km: float = random.uniform(1, 4) # no way to measure this, therefore random number
    multiplier_parked_in_charging_station: float = 0.7
    # multiplier_impact_detected: float = 1.1
    # multiplier_impact_detected_critical: float = 1.3
    is_reported = False
    multiplier_is_reported_by_another_user: float = 1.6

    def __init__(self, scooter_id: str, sense=None):
        self.scooter_id = scooter_id
        self.gps = self.set_GPS()
        # print(f"[init] S{self.scooter_id}")
        
        self.sense = sense
        if self.sense is not None:
            animation.set_lock_display(sense=self.sense)
            self.sense.stick.direction_any = self.handle_event
    

        self.client = mqtt.Client()
        self.client.connect(broker, port)
        self.client.subscribe('gr8/scooters/action/' + self.scooter_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.loop_start()

        # publish the status of the scooter (available, location, battery) to all apps and server
        self.publish_status(is_available=True)
    
    def on_connect(self, client, userdata, flags, rc):
        # print(f"[MQTT - S{self.scooter_id}] Connected to broker")
        pass

    def on_message(self, client, userdata, msg):
        # handles the message from the server, which is a json object
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            print(f"[ERROR {self.scooter_id}] on_message(): {err}")
            return
        action = payload.get('action')

        print(f"Scooter {self.scooter_id} received action: {action}")

        if action == 'unlock':
            self.stm.send('unlock')
        
        elif action == 'lock':
            print("scooter recieved action lock!")
            # check if the scooter is parked correctly
            parking_ok = self.detect_parking_ok()

            if parking_ok:
                self.stm.send('lock')
            else:
                response = {
                        'response': 'error', 
                        'error_message': 'Scooter not parked correctly',
                    }

                # error blinking (if there is a sense hat) aswell as additional details for the user
                if self.sense is not None:
                    animation.error_blink(sense=self.sense, error_text="Parking bad!")
                    response['details'] = f"Pitch: {(self.pitch / PITCH_THRESHOLD) *100:.2f}%, Roll: {(self.roll / ROLL_THRESHOLD) *100:.2f}%"

                self.client.publish('gr8/scooters/' + self.scooter_id, json.dumps(response), qos=2)
        
        elif action == 'reserve':
            self.stm.send('reserve')
            self.reserve_start_time = time.time()
            self.is_reserved = True

        elif action == 'report':
            self.is_reported = True
            # self.client.publish('gr8/scooters/' + self.scooter_id, "Reported!!!!", qos=2) #!! Denne linjen krasjet ting??!

            print(f"reported === {self.is_reported}")

    def handle_event(self, event):
        if event.action == 'held':
            self.stm.send('gas')
        elif event.action == 'released':
            self.stm.send('release')

    def set_GPS(self, gps=None):
        if gps is not None:
            self.gps = gps
            return gps
        # returns a random GPS location in Trondheim (as the raspberry pi does not have GPS), if properly implemented, this would return the actual GPS location
        return f"{random.uniform(63.3800, 63.4600)}, {random.uniform(10.3300, 10.4900)}"

    def get_battery(self):
        # returns a set battery as the raspberry pi does not have a battery, if properly implemented, this would return the actual battery level
        return f"{random.randint(25, 98)}%"
        return '60%'
    
    def check_if_charging(self):
        # return True if the scooter is charging, False otherwise. Simulated by if a usb device is connected or not
        return is_charging()
    
    def publish_status(self, is_available):
        status = {
            'available': is_available,
            'scooter_id': self.scooter_id,
            'location': self.gps, 
            'battery': self.get_battery(),
            'is_currently_charging': self.check_if_charging()
        }
        self.client.publish('gr8/scooters/status', json.dumps(status), qos=1)

    def lock(self):
        # screen stuff
        if self.sense is not None:
            animation.set_lock_display(sense=self.sense)

        response = {
            'response': 'lock_ok', 
            'bill': self.calculate_bill(),
        }
        
        # publish an ack to the server and application, if not recieved, the app should try again
        self.client.publish('gr8/scooters/' + self.scooter_id, json.dumps(response), qos=2)

        # publish the status of the scooter (available, location, battery) to all apps and server
        self.publish_status(is_available=True)

    def unlock(self):
        # screen stuff
        if self.sense is not None:
            animation.set_unlock_display(sense=self.sense)

        
        # publish an ack to the server and application, if not recieved, the app should try again
        response = {'response': 'unlock_ok'}
        self.client.publish('gr8/scooters/' + self.scooter_id, json.dumps(response), qos=2)
        
        # publish the status of the scooter (available, location, battery) to all apps and server
        self.publish_status(is_available=False)

    def reserve(self):

        # screen stuff
        if self.sense is not None:
            animation.set_reserved_display(sense=self.sense)

        # ? is this necessary?
        # publish an ack to the server and application, if not recieved, the app should try again
        response = {'response': 'reserve_ok'}
        self.client.publish('gr8/scooters/' + self.scooter_id, json.dumps(response), qos=2)
        self.publish_status(is_available=False)

    # def unreserve(self):
    #     print("unreserve")

    #     # screen stuff
    #     if self.sense is not None:
    #         animation.set_unreserved_display(sense=self.sense)

    #     # ? is this necessary?
    #     # publish an ack to the server and application, if not recieved, the app should try again
    #     response = {'response': 'ok'}
    #     self.client.publish('gr8/scooters/' + self.scooter_id, json.dumps(response), qos=2)

    def move(self):
        if self.sense is not None:
            sound.stop()
            sound.play()
        # turns on enigne (screen stuff)
        animation.set_display(self.sense, self.x_offset)
        self.x_offset = (self.x_offset + 1) % 8

    def stop(self):
        # turns off enigne (screen stuff)
        if self.sense is not None:
            sound.stop()

        self.x_offset = 0
        animation.set_display(self.sense, self.x_offset)

    # def detect_impact(self, t0=2, t1=4):
    #     accel = self.sense.get_accelerometer_raw()
    #     magnitude = math.sqrt(accel['x']**2 + accel['y']**2)
    #     return magnitude > t0, magnitude > t1, magnitude
    
    def detect_parking_ok(self):
        if self.sense is None:
            return True

        o = self.sense.get_orientation()
        pitch = normalize_angle(o["pitch"])
        roll = normalize_angle(o["roll"])

        self.pitch = pitch
        self.roll = roll

        print(f"Pitch: {pitch * 100 / PITCH_THRESHOLD:.2f}%, Roll: {roll * 100 / ROLL_THRESHOLD:.2f}%")
        
        return pitch < PITCH_THRESHOLD and roll < ROLL_THRESHOLD #, pitch, roll
    
    def calculate_bill(self):
        bill = {
            'number_of_km': self.number_of_km,
            'cost_per_km': self.cost_per_km,
            'trip_cost': 0,
            'time_reserved': 0,
            'cost_per_minute_reserved': self.cost_per_minute_reserved,
            'reservation_cost': 0,
            'charging_discount': False, 
            # 'impact_multiplier': False,
            # 'critical_impact_multiplier': False,
            'reported_multiplier': False,
            'multipliers': {
                'charging_discount': self.multiplier_parked_in_charging_station,
                # 'impact_multiplier': self.multiplier_impact_detected,
                # 'critical_impact_multiplier': self.multiplier_impact_detected_critical,
                'reported_multiplier': self.multiplier_is_reported_by_another_user
            }
        }
        # cost of the trip (pr km)
        trip_cost = self.number_of_km * self.cost_per_km

        # if reserved, calculate the cost of the reservation
        if self.is_reserved:
            self.reserve_end_time = time.time()
            time_reserved = self.reserve_end_time - self.reserve_start_time
            bill['time_reserved'] = time_reserved
            bill['reservation_cost'] = (time_reserved / 60) * self.cost_per_minute_reserved

        # ======= multipliers =======
        # if the scooter is parked in a charging station, apply the multiplier (discount)
        if self.check_if_charging():
            bill['charging_discount'] = True
            trip_cost = trip_cost * self.multiplier_parked_in_charging_station

        # # if the scooter has been impacted, apply the multiplier (increase)
        # if self.impact_detected:
        #     bill['impact_multiplier'] = True
        #     bill['trip_cost'] *= self.multiplier_impact_detected

        # # if the scooter has been impacted critically, apply the multiplier (increase)
        # if self.impact_detected_critical:
        #     bill['critical_impact_multiplier'] = True
        #     bill['trip_cost'] *= self.multiplier_impact_detected_critical

        # if the scooter has been reported by another user, apply the multiplier (increase)
        if self.is_reported:
            bill['reported_multiplier'] = True
            trip_cost *= self.multiplier_is_reported_by_another_user


        bill['trip_cost'] = trip_cost

        return bill
        


escooter_states = [
        {
            'name': 'idle'
        },
        {
            'name': 'reserved',
            'entry': 'reserve',
        },
        {
            'name': 'unlocked'
        },
        {
            'name': 'driving'
        }
    ]

escooter_transition = [
        {
            'source': 'initial',
            'target': 'idle'
        },

        {
            'source': 'idle',
            'target': 'reserved',
            'trigger': 'reserve',
            'effect': 'reserve'
        },
        {
            'source': 'reserved',
            'target': 'unlocked',
            'trigger': 'unlock',
            'effect': 'unlock'

        },
        {
            'source': 'idle',
            'target': 'unlocked',
            'trigger': 'unlock',
            'effect': 'unlock'
        },
        {
            'source': 'unlocked',
            'target': 'idle',
            'trigger': 'lock',
            'effect': 'lock'
        },
        {
            'source': 'unlocked',
            'target': 'driving',
            'trigger': 'gas',
            'effect': 'move; start_timer("t", 100)'
        },
        {
            'source': 'driving',
            'target': 'unlocked',
            'trigger': 'release',
            'effect': 'stop_timer("t"); stop'
        },
        {
            'source': 'driving',
            'target': 'driving',
            'trigger': 't',
            'effect': 'move; start_timer("t", 100)'
        }

    ]
