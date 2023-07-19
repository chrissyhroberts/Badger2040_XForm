import urequests
import binascii
import badger2040
import network
import os

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        print('Already connected to Wi-Fi')
        return
    
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        pass
    
    print('Connected to Wi-Fi')
    print('Network config:', wlan.ifconfig())
    
def base64_encode(string):
    # Encoding the string to bytes
    encoded_bytes = string.encode('utf-8')
    
    # Encoding bytes to base64
    encoded_base64_bytes = binascii.b2a_base64(encoded_bytes)
    
    # Decoding base64 bytes to string
    encoded_base64_string = encoded_base64_bytes.decode('utf-8').strip()
    
    return encoded_base64_string

def submit_submission(file_path, url, username, password):
    with open(file_path, 'r') as file:
        xml_data = file.read()

    encoded_credentials = base64_encode(username + ':' + password)
    
    headers = {
        'Content-Type': 'application/xml',
        'Authorization': 'Basic ' + encoded_credentials
    }

    response = urequests.post(url, headers=headers, data=xml_data)

    if response.status_code == 201:
        print('Submission successful')
    else:
        print('Submission failed with status code:', response.status_code)
        print('Response:', response.text)

def submit_xml_files_in_folder(folder_path, url, username, password):
    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith('.xml'):
                file_path = os.path.join(root, file_name)
                print('Submitting file:', file_path)
                submit_submission(file_path, url, username, password)
                print('---')

print("Connecting to Wi-Fi...")
connect_to_wifi('SSID', 'password')

folder_path = 'instances'  # Update with the actual folder path
url = 'https://YOURSERVERURL/v1/projects/YOURPID/forms/YOURFORMID/submissions'
username = 'YOURUSERNAME'
password = 'YOURPASSWORD'

submit_xml_files_in_folder(folder_path, url, username, password)
