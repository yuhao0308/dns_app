from flask import Flask, request, jsonify

app = Flask(__name__)

# Assuming you will store the registered hostnames and their details in a dictionary:
registered_hosts = {}


@app.route('/register', methods=['PUT'])
def register():
    data = request.get_json()
    # Store the hostname and its details
    hostname = data.get('hostname')
    fs_ip = data.get('ip')
    as_ip = data.get('as_ip')
    as_port = data.get('as_port')
    if hostname and fs_ip and as_ip and as_port:
        registered_hosts[hostname] = {
            'fs_ip': fs_ip,
            'as_ip': as_ip,
            'as_port': as_port
        }
        return jsonify({'message': 'Registration successful'}), 200
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
