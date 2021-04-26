import requests
import os
import webbrowser
import time
import yaml
from pathlib import Path



oauth_host = os.getenv('OAUTH2_HOST', 'weaveworks.id')
oauth_port = os.getenv('OAUTH2_PORT', '443')

base_url = 'https://'+oauth_host+':'+oauth_port
dcr_url = '/register'
device_url = '/device'
token_url = '/token'

print ("========phase 1==================")
print("calling DCR for CID/CS")
r = requests.post(base_url+dcr_url, data = {'client_name':"wego-cli"})
dcr_resp = r.json();
client_id = dcr_resp['client_id'];
client_secret = dcr_resp['client_secret'];
print("received client ID", client_id)
print()
#  call the device code api
print ("========phase 2==================")
print("calling device api")
r = requests.post(base_url+device_url, data = {'client_id':client_id}, auth=(client_id, client_secret))
resp = r.json()
print ("device code", resp['device_code']);

print ()
print ("========phase 3==================")

# Open the returned URL
print ("opening url", resp['verification_uri_complete'])
time.sleep(5);
webbrowser.open_new(resp['verification_uri_complete']);

access_token = ""
refresh_token = ""

finished = False

reqdata = {
    'grant_type': "urn:ietf:params:oauth:grant-type:device_code",
    'device_code': resp['device_code'],
    'client_id': client_id
}

print ()
print ("========phase 4==================")

print ("polling for tokens while user does browser flow")
# Poll for the tokens
while not finished:
    r = requests.post(base_url+token_url, data = reqdata, auth=(client_id, client_secret))
    print("recieved status code", r.status_code)
    if (r.status_code==200):
        tokendata = r.json()
        access_token = tokendata['access_token']
        refresh_token = tokendata['refresh_token']
        finished = True
        break
    print('.', end='')
    time.sleep(resp['interval'])

config = {
    'client_id': client_id,
    'client_secret': client_secret,
    'access_token': access_token,
    'refresh_token': refresh_token
}

print ()
print ("========phase 5==================")

print ("saving to ~/.config/wego/secrets")
print (yaml.dump(config))
# save the tokens to the home directory

home = str(Path.home())

Path(home + "/.config/wego").mkdir(parents=True, exist_ok=True)
with open(home + '/.config/wego/secrets', 'w') as file:
    documents = yaml.dump(config, file)





