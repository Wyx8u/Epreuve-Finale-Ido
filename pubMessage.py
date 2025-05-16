import paho.mqtt.client as pmc
import time
import board
import adafruit_dht
import socket
import pigpio

pi = pigpio.pi()        
BTN = 16
W = 21

sendingData = False
press_duration = 0
pi.write(W, 0)

hostname =socket.gethostname()

BROKER = "10.10.1.151"
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
        temperature_c = sensor.temperature
        humidity = sensor.humidity
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(2.0)
        continue
    except Exception as error:
        sensor.exit()
        raise error
    except KeyboardInterrupt:
        exit

    client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
    client.on_connect = connexion
    client.connect(BROKER,PORT)

    p_temperature = int("{0:0.0f}".format(temperature_c))
    p_humidity = int("{0:0.0f}".format(humidity))

    if pi.read(BTN) == 0:
        start_time = time.time()
        while pi.read(BTN) == 0:
            time.sleep(0.1)
            press_duration = time.time() - start_time
            print(press_duration)

    if press_duration > 1:
        if sendingData == False:
            sendingData = True
        else:
            sendingData = False

    if press_duration < 2:
        client.publish(TOPIC_HUMIDITY, p_humidity)
        client.publish(TOPIC_TEMPERATURE, p_temperature)

    while sendingData:
        pi.write(W, 1)
        client.publish(TOPIC_HUMIDITY, p_humidity)
        client.publish(TOPIC_TEMPERATURE, p_temperature)
        time.sleep(10) # METTRE A 30