"""
generate_token.py

Execute this script to generate a new token if the previous one is expired.
Copy the token!
"""

import requests
import json
import jsonpickle

url = "http://thingsboard.idlab.uantwerpen.be:8080/api/auth/login"
data = '{"username":"your_user_name", "password":"your_password"}'
headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
r = requests.post(url, data=data, headers=headers)
jwt_token = r.json()['token']
print("Bearer " + jwt_token)
