import paho.mqtt.client as pmc
import time
import board
import adafruit_dht
import socket
import pigpio
import threading

# Setup for GPIO and MQTT
pi = pigpio.pi()
BTN = 16  
W = 21    
pi.write(W, 0)  
hostname = socket.gethostname()

# MQTT broker configuration
BROKER = "10.10.1.151"
PORT = 1883

# MQTT topics for humidity and temperature
TOPIC_HUMIDITY = f"final/{hostname}/H"
TOPIC_TEMPERATURE = f"final/{hostname}/T"

# DHT11 sensor setup on GPIO4
sensor = adafruit_dht.DHT11(board.D4)

# Global variables
sendingData = False
press_duration = 0

# Called when the client connects to the MQTT broker
def on_connect(client, userdata, flags, code, properties):
   if code == 0:
       print("Connected")
   else:
       print(f"Connection error, code {code}")
client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.connect(BROKER, PORT)

# Reads temperature and humidity from the sensor
def read_data():
   try:
       temperature = sensor.temperature
       humidity = sensor.humidity
       return int(round(temperature)), int(round(humidity))
   except RuntimeError as error:
       print("Sensor error:", error.args[0])
   except Exception as error:
       sensor.exit()
       raise error
   return None, None

# Automatically sends data if sendingData is True
def auto_send():
   global sendingData
   while True:
       if sendingData:
           pi.write(W, 1)
           temp, hum = read_data()
           if temp is not None and hum is not None:
               client.publish(TOPIC_TEMPERATURE, temp)
               client.publish(TOPIC_HUMIDITY, hum)
           time.sleep(30)  # Wait 30 seconds between readings
       else:
           pi.write(W, 0)
           time.sleep(1)

# Handles button press logic to toggle auto send or send once
def button_handler():
   global sendingData, press_duration
   while True:
       if pi.read(BTN) == 0:  # Button pressed
           start = time.time()
           while pi.read(BTN) == 0:
               time.sleep(0.1)
           press_duration = time.time() - start
           if press_duration > 1.5:
               # Long press: toggle automatic mode
               pi.write(W, 0)
               sendingData = not sendingData
               print("Auto mode:", sendingData)
           else:
               # Short press: send data once
               temp, hum = read_data()
               if temp is not None and hum is not None:
                   client.publish(TOPIC_TEMPERATURE, temp)
                   client.publish(TOPIC_HUMIDITY, hum)
                   print("Data sent manually")

# Main loop starts threads for auto send and button logic
if __name__ == "__main__":
   threading.Thread(target=auto_send, daemon=True).start()
   threading.Thread(target=button_handler, daemon=True).start()
   try:
       while True:
           time.sleep(1)
   except KeyboardInterrupt:
       print("Shutting down")
       sensor.exit()
       pi.write(W, 0)
       pi.stop()