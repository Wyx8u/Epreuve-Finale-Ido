import paho.mqtt.client as pmc

BROKER = "mqttbroker.lan"
PORT = 1883
TOPIC = "final/#"

def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("Connecté")
    else:
        print("Erreur code %d\n", code)

def reception_msg(cl,userdata,msg):
    if msg.topic.split("/")[2] == "T":
        print("Reçu:",msg.payload.decode(), "Host:", msg.topic.split("/")[1])

    elif msg.topic.split("/")[2] == "H":
        print("Reçu:",msg.payload.decode(), "Host:", msg.topic.split("/")[1])


client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.on_message = reception_msg

client.connect(BROKER,PORT)
client.subscribe(TOPIC)
client.loop_forever()