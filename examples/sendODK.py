import urequests
import binascii
import network
import os
import uos


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

    if response.status_code in (200, 201):
        print('Submission successful')
        log_submission(file_path, success=True, response_text=response.text)
    else:
        print('Submission failed with status code:', response.status_code)
        print('Response:', response.text)
        log_submission(file_path, success=False, response_text=response.text)


def log_submission(file_path, success, response_text):
    with open('log.txt', 'a') as log_file:
        status = 'Success' if success else 'Failure'
        log_entry = f"File: {file_path}, Status: {status}, Response: {response_text}\n"
        log_file.write(log_entry)


def walk(directory):
    file_paths = []
    for entry in uos.listdir(directory):
        entry_path = directory + '/' + entry
        if uos.stat(entry_path)[0] & 0x4000:
            file_paths.extend(walk(entry_path))
        else:
            file_paths.append(entry_path)
    return file_paths


def load_submitted_files():
    submitted_files = set()
    if 'log.txt' in uos.listdir():
        print("Log file exists")
        with open('log.txt', 'r') as log_file:
            for line in log_file:
                file_path, status, _ = line.strip().split(', ')
                if status == 'Status: Success':  # Correct the status check
                    # Extract the filename from the full file path
                    filename = file_path.split('/')[-1]
                    print("Adding filename to submitted files:", filename)
                    submitted_files.add(filename)
                else:
                    print("Skipping file:", file_path, "with status:", status)
    else:
        print("Log file does not exist")
    print("Submitted files:", submitted_files)
    return submitted_files


def submit_xml_files_in_folder(folder_path, url, username, password):
    # Load the set of submitted files from the log
    submitted_files = load_submitted_files()

    file_paths = walk(folder_path)
    for file_path in file_paths:
        if file_path.endswith('.xml'):
            # Extract the filename from the full file path
            filename = file_path.split('/')[-1]
            if filename not in submitted_files:
                print('Submitting file:', file_path)
                submit_submission(file_path, url, username, password)
                print('---')

                # Update the log only after a successful submission
                if filename not in submitted_files:
                    log_submission(file_path, success=True, response_text='')

                submitted_files.add(filename)  # Update the set with the filename

    print("Submitted files:", submitted_files)

print("Connecting to Wi-Fi...")
connect_to_wifi('YOURNETWORKSSID', 'YOURNETWORKPASSWORD")

folder_path = 'instances'  # Update with the actual folder path
url = 'https://YOURCENTRALURL/v1/projects/YOURPROJECTID/forms/YOURFORMNAME/submissions'
username = 'YOURCENTRALUSERNAME"
password = 'YOURCENTRALPASSWORD'

submit_xml_files_in_folder(folder_path, url, username, password)
