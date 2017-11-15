
import json
import paho.mqtt.client as mqtt
# from scipy.spatial import distance
# a = (1,2,3)
# b = (4,5,6)
# dst = distance.euclidean(a,b)
matrix = []


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/localisation/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    data = json.loads(str(msg.payload))
    if data['node'] == '43373134003e0041':
        entry = (data['gateway'], data['link_budget'], data['timestamp'])
        print(entry)
        matrix.append(entry)
        sizeMatrix = len(matrix)

        database = open('database.txt', 'a')
        database.write('Location 5:' + str(entry) + '\n')
        database.close()

        if sizeMatrix > 40:
            client.disconnect()

def process_data():
    database = open('database_without_timestamp.txt','r')
    database.read()

client = mqtt.Client(protocol=mqtt.MQTTv31)
client.on_connect = on_connect
client.on_message = on_message

client.connect("backend.idlab.uantwerpen.be", 1883, 60)



# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()


