from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)


# Подключение к БД
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="tg_bot_vt",
        user="postgres",
        password="postgres",
        port=5432
    )
    return conn


@app.route('/load', methods=['POST'])
def load_currency():
    data = request.get_json()
    currency_name = data.get('currency_name')
    rate = data.get('rate')

    if not currency_name or not rate:
        return jsonify({'error': 'Отсутствует название валюты или курс'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Проверка существования валюты
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (currency_name,))
        if cur.fetchone():
            return jsonify({'error': 'Валюта уже существует'}), 400

        # Добавление новой валюты
        cur.execute(
            "INSERT INTO currencies (currency_name, rate) VALUES (%s, %s)",
            (currency_name, rate)
        )
        conn.commit()
        return jsonify({'message': f'Валюта {currency_name} успешно добавлена'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/update_currency', methods=['POST'])
def update_currency():
    data = request.get_json()
    currency_name = data.get('currency_name')
    new_rate = data.get('rate')

    if not currency_name or not new_rate:
        return jsonify({'error': 'Отсутствует название валюты или курс'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Проверка существования валюты
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (currency_name,))
        if not cur.fetchone():
            return jsonify({'error': 'Валюта не найдена'}), 404

        # Обновление курса
        cur.execute(
            "UPDATE currencies SET rate = %s WHERE currency_name = %s",
            (new_rate, currency_name)
        )
        conn.commit()
        return jsonify({'message': f'Курс валюты {currency_name} успешно обновлен'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/delete', methods=['POST'])
def delete_currency():
    data = request.get_json()
    currency_name = data.get('currency_name')

    if not currency_name:
        return jsonify({'error': 'Отсутствует название валюты'}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        # Проверка существования валюты
        cur.execute("SELECT 1 FROM currencies WHERE currency_name = %s", (currency_name,))
        if not cur.fetchone():
            return jsonify({'error': 'Валюта не найдена'}), 404

        # Удаление валюты
        cur.execute("DELETE FROM currencies WHERE currency_name = %s", (currency_name,))
        conn.commit()
        return jsonify({'message': f'Валюта {currency_name} успешно удалена'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


if __name__ == '__main__':
    app.run(port=5001, debug=True)