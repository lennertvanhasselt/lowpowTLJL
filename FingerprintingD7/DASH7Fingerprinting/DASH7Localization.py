import json
import paho.mqtt.client as mqtt
import winsound

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/localisation/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    # print(msg.topic+" "+str(msg.payload))
    data = json.loads(str(msg.payload))

    global previous_time, rssis, gateways, counter
    actual_time = float(data['timestamp'][-8:])
    if previous_time > 8 and actual_time < 2 or previous_time < actual_time - 1:  # database creatie: wacht op bericht van GW die nog niet heeft geantwoord
        previous_time = actual_time

    if len(gateways) == 4:
        del gateways[:]
        counter += 1

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

    if len(gateways) == 4:                                          # wait for 4 messages of 4 different gateways,
        write_database(rssis)                                       # and write data to database
        if counter == 5:
            client.disconnect()                                     # disconnect MQTT broker
            winsound.Beep(840, 250)



# Write entry to datasbase in the format (nr,RSSI1,RSSI2,RSSI3,RSSI4)
def write_database(rssis):
    database = open('database.txt', 'a')                            # Open database
    global training_point_number
    database.write(str(training_point_number) + ',' + str(rssis[0]) + ',' + str(rssis[1]) + ',' + str(rssis[2]) + ',' + str(rssis[3]) + '\n')
    database.close()                                                # Close database

################################################################

gateways = []
rssis = [0, 0, 0, 0]
previous_time = 0.0
counter = 0
training_point_number = input('Give trainingspoint location')

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


