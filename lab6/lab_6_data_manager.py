from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)


# Подключение к БД
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="currency_db",
        user="postgres",
        password="postgres",
        port=5432
    )
    return conn


@app.route('/convert', methods=['GET'])
def convert_currency():
    currency_name = request.args.get('currency')
    amount = request.args.get('amount')

    if not currency_name or not amount:
        return jsonify({'error': 'Отсутствует валюта или сумма'}), 400

    try:
        amount = float(amount)
    except ValueError:
        return jsonify({'error': 'Сумма должна быть числом'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Получение курса валюты
        cur.execute("SELECT rate FROM currencies WHERE currency_name = %s", (currency_name,))
        result = cur.fetchone()

        if not result:
            return jsonify({'error': 'Валюта не найдена'}), 404

        rate = result[0]
        converted_amount = amount * rate

        return jsonify({
            'original_amount': amount,
            'currency': currency_name,
            'rate': rate,
            'converted_amount': converted_amount
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/currencies', methods=['GET'])
def get_currencies():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT currency_name, rate FROM currencies ORDER BY currency_name")
        currencies = cur.fetchall()

        result = [{'currency': curr[0], 'rate': curr[1]} for curr in currencies]

        return jsonify({'currencies': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    app.run(port=5002, debug=True)