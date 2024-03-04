from flask import Flask, request, jsonify
import socket
import json

app = Flask(__name__)

# Assuming you will store the registered hostnames and their details in a dictionary:
registered_hosts = {}


@app.route('/register', methods=['PUT'])
def register():
    data = request.get_json()
    hostname = data.get('hostname')
    fs_ip = data.get('ip')
    as_ip = data.get('as_ip')
    as_port = int(data.get('as_port'))

    if hostname and fs_ip and as_ip and as_port:
        dns_message = f'TYPE=A\nNAME={hostname}\nVALUE={fs_ip}\nTTL=10\n'

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(dns_message.encode(), (as_ip, as_port))

            try:
                sock.settimeout(20)  # Set timeout for waiting for a response
                data, _ = sock.recvfrom(1024)
                response = data.decode()

                if "successful" in response.lower():
                    return jsonify({"status": "Registration successful"}), 201
                else:
                    return jsonify({"status": "Registration failed", "message": response}), 500
            except socket.timeout:
                return jsonify({"error": "No response from Authoritative Server"}), 408
    else:
        return jsonify({'error': 'Missing parameters'}), 400


def fibonacci(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


@app.route('/fibonacci')
def get_fibonacci():
    # Extract the 'number' parameter from the request
    number = request.args.get('number', type=int)
    if number is None:
        return jsonify({'error': 'No number provided'}), 400
    # Calculate the Fibonacci number
    try:
        fib_number = fibonacci(number)
        return jsonify({'fibonacci': fib_number}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=9090)
