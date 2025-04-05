from flask import Flask, request, jsonify
import random
import json

app = Flask(__name__)


# 1) GET /number/
@app.route('/number/', methods=['GET'])
def get_number():
    param = request.args.get('param', default=1, type = float)
    # Генерируем случайное число от 0 до 10
    random_num = random.random() * 10
    result = random_num * param
    return jsonify({"result": result})


if __name__ == '__main__':
    app.run(debug=True)