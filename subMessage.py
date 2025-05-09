import paho.mqtt.client as pmc
import pigpio

pi = pigpio.pi()        
R = 21
B = 20
W = 19

BROKER = "mqttbroker.lan"
PORT = 1883
TOPIC = "final/#"

donneesRecuesT = {}
donneesRecuesH = {}

def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("Connecté")
    else:
        print("Erreur code %d\n", code)

#Marc-Antoine
def reception_msg(cl,userdata,msg):

    # Gestion du topic H ou T
    if msg.topic.split("/")[2] == "T":
        # print("Reçu:",msg.payload.decode(), "Host:", msg.topic.split("/")[1])

        try:
            cle = msg.topic.split("/")[1]
            donneesRecuesT[cle] = (msg.payload.decode())
            print(donneesRecuesT)
        except IndexError: # Cas si un topic ne contient pas de "/"
            print(">>> ERREUR:",msg.topic,msg.payload.decode())
        except ValueError: # Cas si le message MQTT n'est pas un nombre
            print(">>> ERREUR:",msg.topic,msg.payload.decode())

        if(max(donneesRecuesT, key=donneesRecuesT.get)) == "marc":
            pi.write(B, 0)
            pi.write(W, 0)
            pi.write(R, 1)

    elif msg.topic.split("/")[2] == "H":
        # print("Reçu:",msg.payload.decode(), "Host:", msg.topic.split("/")[1])

        try:
            cle = msg.topic.split("/")[1]
            donneesRecuesH[cle] = (msg.payload.decode())
            print(donneesRecuesH)
        except IndexError: # Cas si un topic ne contient pas de "/"
            print(">>> ERREUR:",msg.topic,msg.payload.decode())
        except ValueError: # Cas si le message MQTT n'est pas un nombre
            print(">>> ERREUR:",msg.topic,msg.payload.decode())

        if(max(donneesRecuesH, key=donneesRecuesH.get)) == "marc":
            pi.write(B, 1)
            pi.write(W, 0)
            pi.write(R, 0)

client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.on_message = reception_msg

client.connect(BROKER,PORT)
client.subscribe(TOPIC)
client.loop_forever()