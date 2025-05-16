from flask import Flask, jsonify, request
import threading
import time
import paho.mqtt.client as mqtt
import board
import adafruit_dht
import pigpio
import socket
 
app = Flask(__name__)
 
# MQTT + GPIO setup
pi = pigpio.pi()
BTN = 16
R = 21
B = 20
W = 19
pi.set_mode(BTN, pigpio.INPUT)
pi.set_mode(R, pigpio.OUTPUT)
pi.set_mode(B, pigpio.OUTPUT)
pi.set_mode(W, pigpio.OUTPUT)
 
hostname = socket.gethostname()
BROKER = "10.10.1.151"
PORT = 1883
TOPIC_HUMIDITY = f"final/{hostname}/H"
TOPIC_TEMPERATURE = f"final/{hostname}/T"
 
sensor = adafruit_dht.DHT11(board.D4)
 
# Global variables
send_data = True
last_temperature = None
last_humidity = None
 
# MQTT client setup
client = mqtt.Client()
 
def mqtt_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker")
    else:
        print(f"Failed to connect, return code {rc}")
 
client.on_connect = mqtt_connect
client.connect(BROKER, PORT)
 
# Read/publish sensor data
def read_and_publish():
    global last_temperature, last_humidity, send_data
    while True:
        if send_data:
            try:
                temperature = sensor.temperature
                humidity = sensor.humidity
                last_temperature = temperature
                last_humidity = humidity
 
                client.publish(TOPIC_TEMPERATURE, temperature)
                client.publish(TOPIC_HUMIDITY, humidity)
                print(f"Published: Temp={temperature}C, Humidity={humidity}%")
            except RuntimeError as e:
                print(f"Sensor error: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")
        time.sleep(30)
 
# Toggle data sending
def button_handler():
    global send_data
    while True:
        if pi.read(BTN) == 1:
            start_time = time.time()
            while pi.read(BTN) == 1:
                time.sleep(0.1)
            press_duration = time.time() - start_time
 
            if press_duration > 2:
                send_data = not send_data
                pi.write(W, 1 if send_data else 0)
                print(f"Data sending {'enabled' if send_data else 'disabled'}")
            else:
                if last_temperature is not None and last_humidity is not None:
                    client.publish(TOPIC_TEMPERATURE, last_temperature)
                    client.publish(TOPIC_HUMIDITY, last_humidity)
                    print("Published data on button press")
        time.sleep(0.1)
 
# API endpoints
@app.route('/etat', methods=['POST'])
def set_state():
    global send_data
    data = request.json
    if 'etat' in data:
        send_data = bool(data['etat'])
        pi.write(W, 1 if send_data else 0)
        return jsonify({"message": "State updated", "etat": send_data}), 200
    return jsonify({"error": "Invalid request"}), 400
 
@app.route('/donnees', methods=['GET'])
def get_data():
    if last_temperature is not None and last_humidity is not None:
        return jsonify({"T": last_temperature, "H": last_humidity}), 200
    return jsonify({"error": "No data available"}), 400
 
def run_flask():
    app.run(host='0.0.0.0', port=3000, use_reloader=False)
 
def start_mqtt():
    client.loop_start()
 
if __name__ == '__main__':
    threading.Thread(target=start_mqtt, daemon=True).start()
    threading.Thread(target=button_handler, daemon=True).start()
    run_flask()
 