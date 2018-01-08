""" BACKEND.py
 This script is the main script being executed on the backend, an Ubuntu server.
 The backend controls when GPS and compass need to be enabled or disabled.
 It serves as an interface for DASH7 and LoRaWAN. 
 
 DASH7 communication: 
	- Receive RSSI from 4 different gateways via MQTT
	- (A fingerprinting database is constructed using 30 training points)
	- Calculate position of node using kNN
	- Send position (X,Y) to ThingsBoard (TB)
	- Check if GPS needs to be enabled
	
LoRaWAN communication:
	- Receive GPS coordinates
	- Send location (lat,long) to Thingsboard
	- Check if DASH7 needs to be enabled
"""

# !/usr/bin/env python

from __future__ import print_function
import argparse
import socket
import subprocess
from datetime import datetime
import jsonpickle
import serial
import time
import paho.mqtt.client as mqtt
import signal
import struct
import math
import operator
import json
from d7a.alp.command import Command
from d7a.alp.operations.responses import ReturnFileData
from d7a.system_files.system_file_ids import SystemFileIds
from d7a.system_files.system_files import SystemFiles
from modem.modem import Modem
import time
from pprint import pprint
from tb_api_client import swagger_client
from tb_api_client.swagger_client import ApiClient, Configuration
from tb_api_client.swagger_client.rest import ApiException


class Backend:
    def __init__(self):
        argparser = argparse.ArgumentParser()
        argparser.add_argument("-v", "--verbose", help="verbose", default=False, action="store_true")
        argparser.add_argument("-b", "--broker", help="mqtt broker hostname", default="localhost")
        argparser.add_argument("-u", "--url", help="URL of the thingsboard server", default="http://localhost:8080")
        argparser.add_argument("-t", "--token", help="token to access the thingsboard API", required=True)
        argparser.add_argument("-us", "--username", help="Username to access broker", default="none")
        argparser.add_argument("-pw", "--password", help="Password to access broker", default="none")
        argparser.add_argument("-k", "--k", help="Amount of neighbours", default=2)
        self.mq = None
        self.connected_to_mqtt = False

        self.config = argparser.parse_args()
        self.connect_to_mqtt()

        api_client_config = Configuration()
        api_client_config.host = self.config.url
        api_client_config.api_key['X-Authorization'] = self.config.token
        api_client_config.api_key_prefix['X-Authorization'] = 'Bearer'
        api_client = ApiClient(api_client_config)

        self.device_controller_api = swagger_client.DeviceControllerApi(api_client=api_client)
        self.device_api_controller_api =swagger_client.DeviceApiControllerApi(api_client=api_client)

    def connect_to_mqtt(self):
        self.connected_to_mqtt = False

        self.mq = mqtt.Client("", True, None, mqtt.MQTTv31)
        self.mq.on_connect = self.on_mqtt_connect
        self.mq.on_message = self.on_mqtt_message
        if self.config.username!="none":
            self.mq.username_pw_set(self.config.username, self.config.password)
        self.mq.connect(self.config.broker, 1883, 60)
        # self.mq.loop_forever()
        self.mq.loop_start()
        while not self.connected_to_mqtt: pass  # busy wait until connected
        print("Connected to MQTT broker on {}".format(self.config.broker))

    def on_mqtt_connect(self, client, config, flags, rc):
        self.mq.subscribe("/tb")
        # self.mq.subscribe("/loriot/#")

        self.connected_to_mqtt = True

    def on_mqtt_message(self, client, config, msg):
        global previoustime, matrix, reset, trainPs, k, location, alarmcounter
        # print(msg.topic+" "+str(msg.payload))
        k=int(self.config.k)
        data = json.loads(str(msg.payload))
        if data['alp']['interface_status']['operation']['operand']['interface_status']['addressee']['id'] == '4771339728167632949':
        # if data['node'] == '43373134003e0041':
            # entry = (data['gateway'], data['link_budget'], data['timestamp']) # TODO timestamp???
            actualtime=time.time()
            entry = (data['deviceId'], data['alp']['interface_status']['operation']['operand']['interface_status']['link_budget'], actualtime)
            # actualtime=float(data['timestamp'][-8:])
            if previoustime > 8 and actualtime < 2 or previoustime < actualtime-1:
                reset = True
                previoustime = actualtime
            if reset:
                counter = 0
                for idx, element in enumerate(matrix):
                    if element == 0:
                        matrix[idx] = 0
                        counter += 1
                if counter < 2:
                    neighbors = self.getNeighbors(trainPs, matrix, k)
                    location = self.calculateLocation(neighbors)
                alarm = False
                if location[0] > 1017:
                    alarmcounter += 1
                    if alarmcounter > 1:
                        alarm = True
                else:
                    alarmcounter = 0
                print("\r\n alarm is "+alarm)
                print(str(location))
                #  print('Distance: ' + repr(neighbors))

                reset = False
                matrix = [0, 0, 0, 0]

            gateway = entry[0]
            if gateway[0:5] == 'b6b48':
                matrix[0] = entry[1]
            elif gateway[0:5] == 'f1f7e':
                matrix[1] = entry[1]
            elif gateway[0:5] == 'c2c4e':
                matrix[2] = entry[1]
            elif gateway[0:5] == '43e01':
                matrix[3] = entry[1]
            else:
                print ("gateway not found   " + gateway[0:5])
        '''
            # global location
            # msg contains already parsed command in ALP in JSON
            print("ALP Command received from TB: {}".format(msg.payload))
            try:
                obj = jsonpickle.json.loads(msg.payload)
            except:
                print("Payload not valid JSON, skipping") # TODO issue with TB rule filter, to be fixed
                return
    
            gateway = obj["deviceId"]
            cmd = jsonpickle.decode(jsonpickle.json.dumps(obj["alp"]))
            node_id = gateway  # overwritten below with remote node ID when received over D7 interface
            # get remote node id (when this is received over D7 interface)
            if cmd.interface_status != None and cmd.interface_status.operand.interface_id == 0xd7:
                node_id = '{:x}'.format(cmd.interface_status.operand.interface_status.addressee.id)
    
            # look for returned file data which we can parse, in this example file 64
            my_sensor_value = 0
            for action in cmd.actions:
                if type(action.operation) is ReturnFileData and action.operand.offset.id == 64:
                    my_sensor_value = struct.unpack("L", bytearray(action.operand.data))[0] # parse binary payload (adapt to your needs)
                    print("node {} sensor value {}".format(node_id, my_sensor_value))
        '''
        # save the parsed sensor data as an attribute to the device, using the TB API
        try:
            # first get the deviceId mapped to the device name
            gateway = data['deviceId']
            node_id = gateway
            response = self.device_controller_api.get_tenant_device_using_get(device_name=str(node_id))
            device_id = response.id.id

            # next, get the access token of the device
            response = self.device_controller_api.get_device_credentials_by_device_id_using_get(device_id=device_id)
            device_access_token = response.credentials_id

            # finally, store the sensor attribute on the node in TB
            response = self.device_api_controller_api.post_telemetry_using_post(
            device_token=device_access_token,
            json={"X":location[0], "Y":location[1], "latitude":latitude, "longitude":longitude, "direction":data['alp']['actions']['operation']['operand']['data'][0]}
            )
            # print(str(location[0])+"   "+str(location[1]))
            print("Updated my_sensor attribute for node {}".format(node_id))

        except ApiException as e:
            print("Exception when calling API: %s\n" % e)

    def __del__(self):
        try:
          self.mq.loop_stop()
          self.mq.disconnect()
        except:
          pass

    def run(self):
        print("Started")
        keep_running = True
        while keep_running:
            try:
                pass
                # signal.pause() # @TODO signal.pause() werkt niet in Pycharm!!!
            except KeyboardInterrupt:
                print("received KeyboardInterrupt... stopping processing")
                keep_running = False

                # The callback for when the client receives a CONNACK response from the server.

    def loadDataset(self, filename):
        f = open(filename, 'r')
        trainPs = []
        for line in f:  # delete '(' and ')\n'. Split on ', '.
            # trainP = [int(x) for x in line.lstrip('(').rstrip(')\n').split(',')]
            trainP = [int(x) for x in line.rstrip('\n').split(',')]
            trainPs.append(trainP)
        # for x in range(len(trainPs)):
        #    print trainPs[x]
        f.close()
        return trainPs

    def loadLocations(self, filename):
        f = open(filename, 'r')
        locations = []
        for line in f:
            location = [int(x) for x in line.rstrip('\n').split(',')]
            locations.append(location)
        f.close()
        return locations

    def euclideanDistance(self, instance1, instance2, length):
        distance = 0
        for x in range(length):  # x+1 because first element is location
            if instance1[x]!=0:
                distance += pow((instance1[x] - instance2[x + 1]), 2)  # check all distances
        return math.sqrt(distance)

    def getNeighbors(self, trainingSet, testInstance, k):
        distances = []
        length = len(testInstance) - 1  # amount of values in Instance
        for x in range(len(trainingSet)):  # test for every trainingspoint
            dist = self.euclideanDistance(testInstance, trainingSet[x], length)
            distances.append((trainingSet[x], dist))  # put every distance in matrix
        distances.sort(key=operator.itemgetter(1))  # Sort for distances[x][1]
        usedlocations = []
        todelete = []
        for x in range(len(distances)):  # Only use locations once (the closest value)
            if distances[x][0][0] in usedlocations:
                todelete.append(x)
            else:
                usedlocations.append(distances[x][0][0])
        for x in range(len(todelete) - 1, -1, -1):  # delete used locations top to bottom (-1 steps)
            del distances[todelete[x]]
        neighbors = []
        for x in range(k):
            temp = [distances[x][0][0], distances[x][0][1], distances[x][0][2], distances[x][0][3], distances[x][0][4], distances[x][1]]
            print(temp)
            neighbors.append(temp)  # put the first k distances in neighbors
        return neighbors

    def calculateLocation(self, neighbors):
        global locations
        neighLocs = []
        sumDist = 0
        percentage = []
        for x in range(len(neighbors)):
            sumDist += neighbors[x][5]
            percentage.append(neighbors[x][5])
        percentage = [(1-x/sumDist) for x in percentage]
        sumDist = sum(percentage)
        percentage = [x/sumDist for x in percentage]
        for x in range(len(neighbors)):
            for location in locations:
                if neighbors[x][0] == location[0]:
                    neighLocs.append(location)
        sumx = 0
        sumy = 0
        for x in range(len(neighLocs)):
            sumx += neighLocs[x][1]*percentage[x]
            sumy += neighLocs[x][2]*percentage[x]
        location = (sumx, sumy)
        return location

 # kNN Source used: https://machinelearningmastery.com/tutorial-to-implement-k-nearest-neighbors-in-python-from-scratch/

k = 2
alarmcounter = 0

location = [5,5]
matrix = [0, 0, 0, 0]
previoustime = 0.0
reset = False

trainPs = Backend().loadDataset('database.txt')
locations = Backend().loadLocations('locations.txt')

'''
# example
neigh = Backend().getNeighbors(trainPs, [45, 62, 70, 70], 2)
location = Backend().calculateLocation(neigh)
print(str(location))
'''


'''
client = mqtt.Client(protocol=mqtt.MQTTv31)
client.on_connect = Backend().on_connect
client.on_message = Backend().on_message

client.username_pw_set("student", "cv1Dq6GXL9cqsStSHKp5")
client.connect("backend.idlab.uantwerpen.be", 1883, 60)
client.loop_forever()
'''


class Read_GPS_coordinates:
    def __init__(self):                         # Init coordinates with unrealistic values
        global data, latitude, longitude, ns, we, hdop
        latitude = 91.0
        ns = 'N'
        longitude = 181.0
        we = 'E'
        hdop = 0
        data = [latitude, ns, longitude, we, hdop]

    def reset_coordinate(self):
        global data, latitude, longitude, ns, we, hdop
        latitude = 91.0
        ns = 'N'
        longitude = 181.0
        we = 'E'
        hdop = 0
        data = [latitude, ns, longitude, we, hdop]

    def read_coordinate(self, s):               # Read HEX string sent over LoRa and convert coordinate data
        global data, latitude, longitude, ns, we, hdop
        [latitude, ns, longitude, we, hdop] = s.decode('hex').split(',')
        latitude = float(latitude)
        longitude = float(longitude)
        hdop = float(hdop)

        deg = math.floor(latitude/100)          # Convert latitude and longitude to correct format
        min = latitude - (deg*100)              # 51.1234567 04.1234567
        latitude = deg + (min/60)
        print(latitude)
        deg = math.floor(longitude / 100)
        min = longitude - (deg * 100)
        longitude = deg + (min / 60)
        print(longitude)

        if ns == 'S':
            latitude *= -1
        if we == 'W':
            longitude *= -1

    def print_coordinate(self):
        print('Coordinate: {}{} {}{} (HDOP = {})'.format(ns, latitude, we, longitude, hdop))






global data, latitude, ns, longitude, we, hdop
GPSread = Read_GPS_coordinates()
#while True:
s = "353131302e363538302c4e2c30303432342e3934312c452c312e31"
GPSread.reset_coordinate()
GPSread.read_coordinate(s)
GPSread.print_coordinate()

if __name__ == "__main__":
    Backend().run()




