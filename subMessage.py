import paho.mqtt.client as pmc
import pigpio
import socket

# GPIO setup
pi = pigpio.pi()
RED_LED = 20   
BLUE_LED = 19  

# MQTT broker configuration
BROKER = "10.10.1.151"
PORT = 1883
TOPIC = "final/#" 

# Dictionaries to store the latest values per host
receivedTemps = {}
receivedHums = {}

# Hostnames with the highest values
max_temp_host = ''
max_hum_host = ''

# Called when the MQTT client connects to the broker
def on_connect(client, userdata, flags, code, properties):
   if code == 0:
       print("Connected to MQTT broker")
   else:
       print(f"Connection failed, code {code}")

# Called whenever a message is received on a subscribed topic
def on_message(client, userdata, msg):
   global max_temp_host, max_hum_host, receivedTemps, receivedHums
   try:
       parts = msg.topic.split("/")
       host = parts[1]
       sensor_type = parts[2]
       value = int(msg.payload.decode())
   except (IndexError, ValueError):
       print(">>> ERROR processing message:", msg.topic, msg.payload.decode())
       return
   
   # Handle temperature data
   if sensor_type == "T":
       receivedTemps[host] = value
       print("Received Temperature Data:", receivedTemps)
       # Find the host with the highest temperature
       max_temp_host = max(receivedTemps, key=receivedTemps.get)
       print("Current Max Temp Host:", max_temp_host)
       # Turn on red LED only if this device has the max temperature
       pi.write(RED_LED, 1 if max_temp_host == socket.gethostname() else 0)

   # Handle humidity data
   elif sensor_type == "H":
       receivedHums[host] = value
       print("Received Humidity Data:", receivedHums)
       # Find the host with the highest humidity
       max_hum_host = max(receivedHums, key=receivedHums.get)
       print("Current Max Humidity Host:", max_hum_host)
       # Turn on blue LED only if this device has the max humidity
       pi.write(BLUE_LED, 1 if max_hum_host == socket.gethostname() else 0)

# MQTT client setup
client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

# Connect and subscribe to the broker
client.connect(BROKER, PORT)
client.subscribe(TOPIC)

# Start the MQTT loop
client.loop_forever()