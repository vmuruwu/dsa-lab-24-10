from flask import Flask, request, jsonify
import random

app = Flask(__name__)

@app.route('/number/', methods=['POST'])
def post_number():
    data = request.get_json()
    if not data or 'jsonParam' not in data:
        return jsonify({"error": "Invalid JSON or missing 'jsonParam'"}), 400

    json_param = data['jsonParam']
    random_num = random.random() * 10
    operation = random.choice(['+', '-', '*', '/'])

    if operation == '+':
        result = random_num + json_param
    elif operation == '-':
        result = random_num - json_param
    elif operation == '*':
        result = random_num * json_param
    elif operation == '/':
        result = random_num / json_param if json_param != 0 else "undefined (division by zero)"

    return jsonify({
        "random_number": random_num,
        "operation": operation,
        "result": result
    })

if __name__ == '__main__':
    app.run(debug=True)