import os
import requests
import urllib3
import json
from requests_toolbelt import MultipartEncoder
from urllib3.exceptions import InsecureRequestWarning
urllib3.disable_warnings(InsecureRequestWarning)

try:
    roomId = os.environ['WEBEX_ROOM_ID']
    access_token = os.environ['WEBEX_ACCESS_TOKEN']
except Exception, e:
    print(e)

def send_message(msg):
    post_data = {
        'roomId': roomId,
        'text': msg
    }

    response = requests.post(
        url='https://api.ciscospark.com/v1/messages',
        auth=None,
        headers={'Authorization': 'Bearer ' + access_token, 'Content-Type': 'application/json'},
        data=json.dumps(post_data),
        verify=False,
        timeout=15
    )

    if response.status_code != 200:
        raise Exception('{} status code: {}'.format(response.text, response.status_code))

def upload_file(msg, path):
    post_data = {
        'files': ('attendance.csv', open(path, 'rb'), 'file/csv'),
        'roomId': roomId,
        'text': msg
    }

    m = MultipartEncoder(fields=post_data)

    response = requests.post(
        url='https://api.ciscospark.com/v1/messages',
        auth=None,
        headers={'Authorization': 'Bearer ' + access_token, 'Content-Type': m.content_type},
        data=m,
        verify=False,
        timeout=15
    )

    if response.status_code != 200:
        raise Exception('{} status code: {}'.format(response.text, response.status_code))
