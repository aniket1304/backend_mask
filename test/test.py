import requests
import json

import base64

with open('test1.jpg', "rb") as img_file:
    im_b64 = base64.b64encode(img_file.read())
payload = {'coin': 'fivepeso', 'image': im_b64}
#print(type(payload['image']))

url = 'http://127.0.0.1:5000/mask_size'

#print(payload)
r = requests.post(url, payload)

print(r.json())

# convert server response into JSON format.
#print(r.json())