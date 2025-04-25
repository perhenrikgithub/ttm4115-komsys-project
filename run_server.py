from server.server import Server
import stmpy
import paho.mqtt.client as mqtt

server = Server()

driver = stmpy.Driver()
driver.start()

broker, port = "mqtt20.iik.ntnu.no", 1883
client = mqtt.Client()
client.connect(broker, port)
client.loop_start()

