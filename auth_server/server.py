import socket
import json

# Create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('0.0.0.0', 53533)
sock.bind(server_address)

# DNS records storage
dns_records = {}

while True:
    try:
        print("Waiting for a connection...")
        data, address = sock.recvfrom(4096)
        try:
            print(f"Received {len(data)} bytes from {address}")
            message = json.loads(data.decode())
            print(f"Message: {message}")
        except json.JSONDecodeError:
            # Handle the case where the JSON is not decodable
            response = json.dumps({"error": "Invalid JSON format"}).encode()
            sock.sendto(response, address)
            continue

        # Determine the type of message and act accordingly
        if message.get('type') == 'register':
            # Store the hostname to IP mapping
            hostname = message.get('hostname')
            ip = message.get('ip')
            if hostname and ip:
                dns_records[hostname] = ip
                response = json.dumps(
                    {"status": "Registration successful"}).encode()
                sock.sendto(response, address)
            else:
                response = json.dumps(
                    {"error": "Hostname or IP missing"}).encode()
                sock.sendto(response, address)

        elif message.get('type') == 'query':
            # Respond with the IP address for the given hostname
            hostname = message.get('hostname')
            if hostname:
                ip_address = dns_records.get(hostname, "Not found")
                response = json.dumps({"ip": ip_address}).encode()
                sock.sendto(response, address)
            else:
                response = json.dumps(
                    {"error": "Hostname missing in query"}).encode()
                sock.sendto(response, address)
        else:
            # Handle unknown message type
            response = json.dumps({"error": "Unknown message type"}).encode()
            sock.sendto(response, address)
    except Exception as e:
        print(f"An error occurred: {e}")
