import json
import paho.mqtt.client as mqtt


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

    global previous_time, reset, rssis, gateways
    actual_time = float(data['timestamp'][-8:])
    if previous_time > 8 and actual_time < 2 or previous_time < actual_time - 1:    # kNN: node stuurt bericht --> reset bij ...
        reset = True                                                                # database creatie: wacht op bericht van GW die nog niet heeft geantwoord
        previous_time = actual_time

    if reset:
        del gateways[:]

    elif data['node'] == '43373134003e0041':                          # Check node ID
        if data['gateway'] not in gateways:
            if data['gateway'][0:5] == 'b6b48':
                gateways.append(data['gateway'])
                rssis[0] = data['link_budget']
            elif data['gateway'][0:5] == 'f1f7e':
                gateways.append(data['gateway'])
                rssis[1] = data['link_budget']
            elif data['gateway'][0:5] == 'c2c4e':
                gateways.append(data['gateway'])
                rssis[2] = data['link_budget']
            elif data['gateway'][0:5] == '43e01':
                gateways.append(data['gateway'])
                rssis[3] = data['link_budget']
            else:
                print('GW not found!')

    if len(gateways) == 4:                                          # wait for 4 messages of different gateways,
        client.disconnect()                                         # disconnect,
        write_database(rssis)                                       # and write data to database


# Write entry to datasbase in the format (nr,RSSI1,RSSI2,RSSI3,RSSI4)
def write_database(rssis):
    database = open('testdatabase.txt', 'a')                        # Open database
    training_point_number = 1                                       # @ TODO change training point number!!!
    database.write(str(training_point_number) + rssis[0] + ',' + rssis[1] + ',' + rssis[2] + ',' + rssis[3] + '\n')
    database.close()                                                # Close database

################################################################

gateways = []
rssis = [0, 0, 0, 0]
previous_time = 0.0
reset = False


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


