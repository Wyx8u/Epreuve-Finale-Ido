import paho.mqtt.client as pmc
import time
import board
import adafruit_dht
import socket

hostname =socket.gethostname()

BROKER = "mqttbroker.lan"
PORT = 1883
TOPIC_HUMIDITY = f"final/{hostname}/H"
TOPIC_TEMPERATURE = f"final/{hostname}/T"

sensor = adafruit_dht.DHT11(board.D4)

def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("Connecté")
    else:
        print("Erreur code %d\n", code)
        
# Complete Project Details: https://RandomNerdTutorials.com/raspberry-pi-dht11-dht22-python/
# Based on Adafruit_CircuitPython_DHT Library Example
# Marc-Antoine
while True:
    try:
        # Print the values to the serial port
        temperature_c = sensor.temperature
        humidity = sensor.humidity

        p_humidity = "Temp:{0:0.1f}ºC".format(temperature_c)
        p_temperature = "Humidity:{0:0.1f}%".format(humidity)

        client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
        client.on_connect = connexion
        client.connect(BROKER,PORT)

        client.publish(TOPIC_HUMIDITY, p_humidity)
        client.publish(TOPIC_TEMPERATURE, p_temperature)

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        sensor.exit()
        raise error

    time.sleep(3)