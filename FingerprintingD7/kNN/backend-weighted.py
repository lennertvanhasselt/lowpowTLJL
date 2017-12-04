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
import paho.mqtt.client as mqtt
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


class BackendExample:
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
        print("Connected to MQTT broker on {}".format(
          self.config.broker,
        ))

    def on_mqtt_connect(self, client, config, flags, rc):							# Connect to MQTT broker and subscribe 
        # self.mq.subscribe("/tb")													# to the localisation topic
	self.mq.subscribe("/localisation/#")
        self.connected_to_mqtt = True

    def on_mqtt_message(self, client, config, msg):									# If a message is received, get the
	global previoustime, matrix, reset, trainPs, k, location						# address of node and gateway,
	# print(msg.topic+" "+str(msg.payload))											# RSSI and timestamp.
	k=int(self.config.k)
	data = json.loads(str(msg.payload))
	if data['node'] == '43373134003e0041':											# When node sends a message:
        	entry = (data['gateway'], data['link_budget'], data['timestamp'])
        	actualtime=float(data['timestamp'][-8:])								# Wait for 4 messages of different 
        	if previoustime > 8 and actualtime < 2 or previoustime < actualtime-1:  # gateways within a time window
            		reset = True													# @TODO @Liam: Waarom 1/2/8 s?
            		previoustime = actualtime

        	if reset:
            		for idx, element in enumerate(matrix):
                		if element == 0:
                    			matrix[idx] = 99
            		neighbors = self.getNeighbors(trainPs, matrix, k)
            		location = self.calculateLocation(neighbors)
            		print(str(location))
            		print('Distance: ' + repr(neighbors))

            		reset = False
            		matrix = [0, 0, 0, 0]

        	gateway = data['gateway']
        	if gateway[0:5] == 'b6b48':
            		matrix[0] = data['link_budget']
        	elif gateway[0:5] == 'f1f7e':
            		matrix[1] = data['link_budget']
        	elif gateway[0:5] == 'c2c4e':
            		matrix[2] = data['link_budget']
        	elif gateway[0:5] == '43e01':
            		matrix[3] = data['link_budget']
        	else:
            		print ("gateway not found   " + gateway[0:5])         
        
	'''
 	global location
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
	  gateway = data['node']
	  node_id = gateway
          response = self.device_controller_api.get_tenant_device_using_get(device_name=str(node_id))
          device_id = response.id.id

          # next, get the access token of the device
          response = self.device_controller_api.get_device_credentials_by_device_id_using_get(device_id=device_id)
          device_access_token = response.credentials_id

          # finally, store the sensor attribute on the node in TB
          response = self.device_api_controller_api.post_telemetry_using_post(
            device_token=device_access_token,
            json={"X":location[0],"Y":location[1]}  # Send X and Y coordinates of the node via MQTT in JSON format
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
            signal.pause()
          except KeyboardInterrupt:
            print("received KeyboardInterrupt... stopping processing")
            keep_running = False

                # The callback for when the client receives a CONNACK response from the server.
    '''
    def on_connect(self, client, userdata, flags, rc):
        print("connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("/localisation/#")

    def on_message(self, client, userdata, msg):
        global previoustime, matrix, reset, trainPs, k, location
        # print(msg.topic+" "+str(msg.payload))
        data = json.loads(str(msg.payload))
        if data['node'] == '43373134003e0041':
            entry = (data['gateway'], data['link_budget'], data['timestamp'])
            actualtime = float(data['timestamp'][-8:])
            if previoustime > 8 and actualtime < 2 or previoustime < actualtime - 1:
                reset = True
                previoustime = actualtime

            if reset:
                for idx, element in enumerate(matrix):
                    if element == 0:
                        matrix[idx] = 0
                neighbors = getNeighbors(trainPs, matrix, k)
                location = calculateLocation(neighbors)
                print(location)
                print('Distance: ' + repr(neighbors))

                reset = False
                matrix = [0, 0, 0, 0]

            gateway = data['gateway']
            if gateway[0:5] == 'b6b48':
                matrix[0] = data['link_budget']
            elif gateway[0:5] == 'f1f7e':
                matrix[1] = data['link_budget']
            elif gateway[0:5] == 'c2c4e':
                matrix[2] = data['link_budget']
            elif gateway[0:5] == '43e01':
                matrix[3] = data['link_budget']
            else:
                print("gateway not found   " + gateway[0:5])
                # print entry

                # print float(data['timestamp'][-8:])
                # print(entry)
                # matrix.append(entry)
                # sizeMatrix = len(matrix)
    '''

    def loadDataset(self, filename):  											# Read database with training points  
        f = open(filename, 'r')													# and format the data to comma-separated values
        trainPs = []
        for line in f:  														# delete '(' and ')\n'. Split on ', '.
            # trainP = [int(x) for x in line.lstrip('(').rstrip(')\n').split(',')]
            trainP = [int(x) for x in line.rstrip('\n').split(',')]
            trainPs.append(trainP)
        # for x in range(len(trainPs)):
        #    print trainPs[x]
        f.close()
        return trainPs

    def loadLocations(self, filename):											# Read file with locations of the map (image).
        f = open(filename, 'r')													# Locations are represented using pixels as 
        locations = []															# coordinates.
        for line in f:
            location = [int(x) for x in line.rstrip('\n').split(',')]
            locations.append(location)
        f.close()
        return locations

    def euclideanDistance(self, instance1, instance2, length):					# Calculate the Euclidean distance between
        distance = 0															# a measurement and an entry in the database.
        for x in range(length):  # x+1 because first element is location
	    if instance1[x]!=0:
            	distance += pow((instance1[x] - instance2[x + 1]), 2)  # check all distances
        return math.sqrt(distance)

    def getNeighbors(self, trainingSet, testInstance, k):						# Pattern matching: Get the k nearest neighbors
        distances = []															# as output of the kNN algorithm
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

    def calculateLocation(self, neighbors):				# Calculate the location of the node using the 
        global locations								# k distances (via RSSI) to the k nearest 
        neighLocs = []									# Access Points.
	sumDist = 0											# Use a weighted function:
	percentage = []										# The higher the RSSI, the closer the node to
	for x in range(len(neighbors)):						# that AP, so the higher the weight (percentage)
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

location = [5,5]
matrix = [0, 0, 0, 0]
previoustime = 0.0
reset = False

trainPs = BackendExample().loadDataset('database.txt')
locations = BackendExample().loadLocations('locations.txt')

'''
# example
neigh = BackendExample().getNeighbors(trainPs, [45, 62, 70, 70], 2)
location = BackendExample().calculateLocation(neigh)
print(str(location))
'''


'''
client = mqtt.Client(protocol=mqtt.MQTTv31)
client.on_connect = BackendExample().on_connect
client.on_message = BackendExample().on_message

client.username_pw_set("student", "cv1Dq6GXL9cqsStSHKp5")
client.connect("backend.idlab.uantwerpen.be", 1883, 60)
client.loop_forever()
'''

if __name__ == "__main__":
    BackendExample().run()



