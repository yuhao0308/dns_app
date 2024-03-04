import logging
from flask import Flask, request, jsonify, abort
import socket
import json
import requests


app = Flask(__name__)
app.debug = True

# Configure logging
logging.basicConfig(filename='debug.log', level=logging.DEBUG)


# Function to perform a DNS query
def dns_query(as_ip, as_port, hostname):
    # DNS query message
    dns_query_message = f'TYPE=A\nNAME={hostname}\n'

    # Send the DNS query message to AS via UDP
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(dns_query_message.encode(), (as_ip, as_port))
        # Wait for the response from AS
        data, _ = sock.recvfrom(1024)
        response_data = data.decode().split('\n')
        response = {line.split('=')[0]: line.split('=')[1]
                    for line in response_data if '=' in line}

        if 'VALUE' in response:
            return response['VALUE']
        else:
            raise Exception('Failed to resolve hostname')


# Route to handle fibonacci requests
@app.route('/fibonacci')
def fibonacci():
    # Extract parameters from the request
    hostname = request.args.get('hostname')
    fs_port = request.args.get('fs_port')
    number = request.args.get('number')
    as_ip = request.args.get('as_ip')
    as_port = request.args.get('as_port')

    # Validate parameters
    if not all([hostname, fs_port, number, as_ip, as_port]):
        abort(400, 'Bad request. Please make sure all parameters are provided.')

    # Perform DNS query to get the IP address of FS
    fs_ip = dns_query(as_ip, int(as_port), hostname)
    if not fs_ip:
        abort(500, 'DNS query failed.')

    # Make an HTTP GET request to the FS using the IP address retrieved from the DNS query
    fs_url = f'http://{fs_ip}:{fs_port}/fibonacci?number={number}'
    response = requests.get(fs_url)

    if response.status_code == 200:
        return jsonify(response.json()), 200
    else:
        abort(response.status_code, response.text)


@app.route('/test')
def test():
    return "Test endpoint response", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
