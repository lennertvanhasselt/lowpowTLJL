# kNN Source used: https://machinelearningmastery.com/tutorial-to-implement-k-nearest-neighbors-in-python-from-scratch/

import math
import operator
import json
import paho.mqtt.client as mqtt

k = 2

matrix = [0, 0, 0, 0]
previoustime = 0.0
reset = False


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("/localisation/#")


def on_message(client, userdata, msg):
    global previoustime, matrix, reset, trainPs, k
    # print(msg.topic+" "+str(msg.payload))
    data = json.loads(str(msg.payload))
    if data['node'] == '43373134003e0041':
        entry = (data['gateway'], data['link_budget'], data['timestamp'])
        actualtime=float(data['timestamp'][-8:])
        if previoustime > 8 and actualtime < 2 or previoustime < actualtime-1:
            reset = True
            previoustime = actualtime

        if reset:
            for idx, element in enumerate(matrix):
                if element == 0:
                    matrix[idx] = 99
            neighbors = getNeighbors(trainPs, matrix, k)
            location = calculateLocation(neighbors)
            print location
            print matrix
            print 'Distance: ' + repr(neighbors)

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
        # print entry

        # print float(data['timestamp'][-8:])
        # print(entry)
        # matrix.append(entry)
        # sizeMatrix = len(matrix)


def loadDataset(filename):
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


def loadLocations(filename):
    f = open(filename, 'r')
    locations = []
    for line in f:
        location = [int(x) for x in line.rstrip('\n').split(',')]
        locations.append(location)
    f.close()
    return locations


def euclideanDistance(instance1, instance2, length):
    distance = 0
    for x in range(length):                     # x+1 because first element is location
        distance += pow((instance1[x] - instance2[x+1]), 2)  # check all distances
    return math.sqrt(distance)


def getNeighbors(trainingSet, testInstance, k):
    distances = []
    length=len(testInstance)-1  # amount of values in Instance
    for x in range(len(trainingSet)):  # test for every trainingspoint
        dist = euclideanDistance(testInstance, trainingSet[x], length)
        distances.append((trainingSet[x], dist))  # put every distance in matrix
    distances.sort(key=operator.itemgetter(1))  # Sort for distances[x][1]
    usedlocations = []
    todelete = []
    for x in range(len(distances)):  #Only use locations once (the closest value)
        if distances[x][0][0] in usedlocations:
            todelete.append(x)
        else:
            usedlocations.append(distances[x][0][0])
    for x in range(len(todelete)-1, -1, -1): #delete used locations top to bottom (-1 steps)
        del distances[todelete[x]]
    neighbors = []
    for x in range(k):
        neighbors.append(distances[x][0])  # put the first k distances in neighbors
    return neighbors


def calculateLocation(neighbors):
    global locations
    neighLocs = []
    for neighbor in neighbors:
        for location in locations:
            if neighbors[neighbor][0] == locations[location]:
                neighLocs.append(locations[location])
    sumx = 0
    sumy = 0
    for neighLoc in neighLocs:
        sumx += neighLocs[neighLoc][1]
        sumy += neighLocs[neighLoc][2]
    meanX = sumx/len(neighLocs)
    meanY = sumy/len(neighLocs)
    location = (meanX, meanY)
    return location


trainPs = loadDataset('database-test.txt')
locations = loadLocations('locations.txt')

client = mqtt.Client(protocol=mqtt.MQTTv31)
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("student", "cv1Dq6GXL9cqsStSHKp5")
client.connect("backend.idlab.uantwerpen.be", 1883, 60)


client.loop_forever()
