import paho.mqtt.client as pmc
import pigpio
import time

pi = pigpio.pi()        
R = 20
B = 19

BROKER = "10.10.1.151"
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
            print("Topic Temp", donneesRecuesT)
        except IndexError: # Cas si un topic ne contient pas de "/"
            print(">>> ERREUR:",msg.topic,msg.payload.decode())
        except ValueError: # Cas si le message MQTT n'est pas un nombre
            print(">>> ERREUR:",msg.topic,msg.payload.decode())

    elif msg.topic.split("/")[2] == "H":
        # print("Reçu:",msg.payload.decode(), "Host:", msg.topic.split("/")[1])
        try:
            cle = msg.topic.split("/")[1]
            donneesRecuesH[cle] = (msg.payload.decode())
            print("Topic Humidity", donneesRecuesH)
        except IndexError: # Cas si un topic ne contient pas de "/"
            print(">>> ERREUR:",msg.topic,msg.payload.decode())
        except ValueError: # Cas si le message MQTT n'est pas un nombre
            print(">>> ERREUR:",msg.topic,msg.payload.decode())

    if(max(donneesRecuesT.values(), default=0 ,key=donneesRecuesT.get)) == "marc":
        pi.write(R, 1)
    else:
        pi.write(R, 0)

    if(max(donneesRecuesH.values(), default=0 , key=donneesRecuesH.get)) == "marc":
        pi.write(B, 1)
    else:
        pi.write(B, 0)

    print(max(donneesRecuesT.values(), default=0))
    print(max(donneesRecuesH.values(), default=0))

client = pmc.Client(pmc.CallbackAPIVersion.VERSION2)
client.on_connect = connexion
client.on_message = reception_msg

client.connect(BROKER,PORT)
client.subscribe(TOPIC)
client.loop_forever()