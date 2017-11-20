import json
import paho.mqtt.client as mqtt
# from scipy.spatial import distance
# a = (1,2,3)
# b = (4,5,6)
# dst = distance.euclidean(a,b)


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

    if data['node'] == '43373134003e0041':                          # Check node ID
        entry = (data['gateway'], data['link_budget'])              # , data['timestamp']
        print(entry)

        if data['gateway'] not in gateways:
            gateways.append(data['gateway'])
            matrix.append(entry)
            write_database(matrix)                                  # write data to database

    if len(matrix) > 4:                                             # wait for 4 messages of different gateways
                client.disconnect()                                 # and disconnect


# Write 4 entries to datasbase (1 per GW)
def write_database(matrix):
    database = open('testdatabase.txt', 'a')                        # Open database
    training_point_number = 1                                       # @ TODO change training point number!!!
    rssis = str(matrix[0][2]) + ',' + str(matrix[1][2]) + ',' + str(matrix[2][2]) + ',' + str(matrix[3][2])
    database.write(str(training_point_number) + rssis + '\n')       # Write line: (nr, RSSI1,RSSI2,RSSI3,RSSI4)
    database.close()                                                # Close database

################################################################

matrix = []
gateways = []

client = mqtt.Client(protocol=mqtt.MQTTv31)
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("student", "cv1Dq6GXL9cqsStSHKp5")
client.connect("backend.idlab.uantwerpen.be", 1883, 60)


# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()


