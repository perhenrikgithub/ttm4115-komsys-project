from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
import paho.mqtt.client as mqtt
import json
import sys

class StateMachineGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.mqtt_client = mqtt.Client()

        #setup main layout
        self.setWindowTitle("Application")
        self.layout = QVBoxLayout()

        #add reserve button to layout
        self.reserve_button = QPushButton("Reserve")
        self.reserve_button.clicked.connect(self.reserve)
        self.layout.addWidget(self.reserve_button)

        #add unlock button to layout
        self.unlock_button = QPushButton("Unlock")
        self.unlock_button.clicked.connect(self.unlock)
        self.layout.addWidget(self.unlock_button)

        #add report button to layout
        self.report_button = QPushButton("Report")
        self.report_button.clicked.connect(self.report)
        self.layout.addWidget(self.report_button)

        #add park button to layout
        self.park_button = QPushButton("Park")
        self.park_button.clicked.connect(self.park)
        self.layout.addWidget(self.park_button)
        self.park_button.setEnabled(False) # Initially hidden

