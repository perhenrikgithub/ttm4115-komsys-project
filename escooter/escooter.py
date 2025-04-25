import stmpy
import paho.mqtt.client as mqtt
import json
import math
import time
import random
import animation
from IMUhelper import normalize_angle, ROLL_THRESHOLD, PITCH_THRESHOLD
from chargeDetector import is_charging
broker, port = "mqtt20.iik.ntnu.no", 1883

import pygame
pygame.mixer.init()
sound = pygame.mixer.Sound("sound2.wav")

class EScooter:
    stm: stmpy.Machine
    is_reserved = False
    x_offset = 0
    impact_detected = False
    impact_detected_critical = False

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

        if action == 'unlock':
            self.stm.send('unlock')
        
        elif action == 'lock':
            # check if the scooter is parked correctly
            # parking_ok, pitch, roll = self.detect_parking_ok()
            parking_ok = self.detect_parking_ok()
            
            if parking_ok:
                self.stm.send('lock')
            else:
                response = {
                    'response': 'error', 
                    'error': f'scooter not parked correctly', # Pitch: {(pitch / PITCH_THRESHOLD) *100:.2f}%, Roll: {(roll / ROLL_THRESHOLD) *100:.2f}%',
                }

                self.client.publish('gr8/scooters/' + self.scooter_id, json.dumps(response), qos=2)
        
        elif action == 'reserve':
            self.stm.send('reserve')
        
        # elif action == 'unreserve':
        #     self.stm.send('unreserve')

        else:
            print(f"[ERROR {self.scooter_id}] on_message(): Unknown action: {action}")

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
            # 'impact_detected': self.impact_detected,
            # 'impact_detected_critical': self.impact_detected_critical,
        }
        
        # publish an ack to the server and application, if not recieved, the app should try again
        self.client.publish('gr8/scooters/response/' + self.scooter_id, json.dumps(response), qos=2)

        # publish the status of the scooter (available, location, battery) to all apps and server
        self.publish_status(is_available=True)

    def unlock(self):
        print("unlock()")
        # if the rasberry pi had a lock, it should be unlocked here

        # screen stuff
        if self.sense is not None:
            animation.set_unlock_display(sense=self.sense)

        
        # publish an ack to the server and application, if not recieved, the app should try again
        response = {'response': 'unlock_ok'}
        self.client.publish('gr8/scooters/' + self.scooter_id, json.dumps(response), qos=2)
        
        # publish the status of the scooter (available, location, battery) to all apps and server
        self.publish_status(is_available=False)

    def reserve(self):
        print("reserve")

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
            sound.play()
        # turns on enigne (screen stuff)
        animation.set_display(self.sense, self.x_offset)
        self.x_offset = (self.x_offset + 1) % 8

    def stop(self):
        # turns off enigne (screen stuff)
        self.x_offset = 0
        animation.set_display(self.sense, self.x_offset)

    def detect_impact(self, t0=2, t1=4):
        accel = self.sense.get_accelerometer_raw()
        magnitude = math.sqrt(accel['x']**2 + accel['y']**2)
        return magnitude > t0, magnitude > t1, magnitude
    
    def detect_parking_ok(self):
        if self.sense is None:
            return True

        o = self.sense.get_orientation()
        pitch = normalize_angle(o["pitch"])
        roll = normalize_angle(o["roll"])

        print(f"Pitch: {pitch * 100 / PITCH_THRESHOLD:.2f}%, Roll: {roll * 100 / ROLL_THRESHOLD:.2f}%")
        
        return pitch < PITCH_THRESHOLD and roll < ROLL_THRESHOLD #, pitch, roll


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
