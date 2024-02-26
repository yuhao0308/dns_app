from flask import Flask, request, jsonify, abort
import socket
import json
import requests

app = Flask(__name__)


def dns_query(as_ip, as_port, hostname):
    """
    Perform a DNS query to the Authoritative Server to resolve the hostname to an IP address.
    """
    try:
        # Set up the socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            server_address = (as_ip, int(as_port))
            message = json.dumps({"Name": hostname, "Type": "A"}).encode()

            # Send the DNS query
            sock.sendto(message, server_address)

            # Wait for the response
            data, _ = sock.recvfrom(4096)
            response = json.loads(data.decode())

            return response.get('Address')
    except Exception as e:
        print(f"DNS Query Error: {e}")
        return None


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

    # Perform DNS query to resolve the hostname to an IP address
    fs_ip = dns_query(as_ip, as_port, hostname)
    if fs_ip is None:
        abort(500, 'Failed to resolve the hostname through the DNS query.')

    # Perform a GET request to the Fibonacci Service
    try:
        fs_url = f"http://{fs_ip}:{fs_port}/fibonacci?number={number}"
        response = requests.get(fs_url)
        if response.status_code == 200:
            return jsonify({"fibonacci_sequence": response.json()}), 200
        else:
            return "Failed to retrieve the Fibonacci sequence from FS.", response.status_code
    except Exception as e:
        print(f"GET Request to FS Error: {e}")
        abort(500, 'Failed to make a GET request to the Fibonacci Service.')


@app.route('/test')
def test():
    return "Test endpoint response", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
