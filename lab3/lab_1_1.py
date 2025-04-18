from flask import Flask, request, jsonify
import random
import json

app = Flask(__name__)

# СЕРВЕРНАЯ ЧАСТЬ
# 1) GET /number/
@app.route('/number/', methods=['GET'])
def get_number():
    param = request.args.get('param', default=1, type=float)
    # Генерируем случайное число от 1 до 10
    random_num = random.randint(1, 10)
    result = random_num * param
    operation = '*'  # Здесь операция умножения
    return jsonify({"result": result, "operation": operation})



@app.route('/number/', methods=['POST'])
def post_number():
    data = request.get_json()
    if not data or 'jsonParam' not in data:
        return jsonify({"error": "Invalid JSON or missing 'jsonParam'"}), 400

    json_param = data['jsonParam']
    random_num = random.randint(1, 10)
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


# 3) DELETE /number/
@app.route('/number/', methods=['DELETE'])
def delete_number():
    random_num = random.randint(1, 10)
    operation = random.choice(['+', '-', '*', '/'])

    return jsonify({
        "random_number": random_num,
        "operation": operation
    })


if __name__ == '__main__':
    app.run(debug=True)

