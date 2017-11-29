#!/usr/bin/env python

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
