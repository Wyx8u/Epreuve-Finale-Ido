import paho.mqtt.client as pmc

BROKER = "mqttbroker.lan"
PORT = 1883
TOPIC = "test"

def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("Connecté")
    else:
        print("Erreur code %d\n", code)

client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion

client.connect(BROKER,PORT)
client.publish(TOPIC,"allo")
client.disconnect()