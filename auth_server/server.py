import socket
import json
import os

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('0.0.0.0', 53533)
sock.bind(server_address)

# DNS records storage file
dns_records_file = 'dns_records.json'
# dns_records_file = '/Users/wangyuhao/Desktop/NYU/Data Communications and Networks/lab3/auth_server/dns_records.json'

# Load existing DNS records if the file exists
if os.path.exists(dns_records_file):
    with open(dns_records_file, 'r') as file:
        dns_records = json.load(file)

else:
    dns_records = {}


def save_dns_records():
    with open(dns_records_file, 'w') as file:
        json.dump(dns_records, file)


while True:
    try:
        print("Waiting for a connection...")
        data, address = sock.recvfrom(4096)
        try:
            print(f"Received {len(data)} bytes from {address}")
            message_lines = data.decode().split('\n')
            message_data = {line.split('=')[0]: line.split(
                '=')[1] for line in message_lines if '=' in line}
            print(f"Message: {message_data}")
        except json.JSONDecodeError:
            # Handle the case where the JSON is not decodable
            response = json.dumps({"error": "Invalid JSON format"}).encode()
            sock.sendto(response, address)
            continue

        # Determine the type of message and act accordingly
        if 'VALUE' in message_data:  # Registration request
            dns_records[message_data['NAME']] = message_data['VALUE']
            save_dns_records()
            response = "DNS registration successful"

        else:  # DNS query
            hostname = message_data.get('NAME')
            ip_address = dns_records.get(hostname, "Not found")
            response = f"TYPE=A\nNAME={hostname}\nVALUE={ip_address}\nTTL=10"

        sock.sendto(response.encode(), address)

    except Exception as e:
        print(f"An error occurred: {e}")
