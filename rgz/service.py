from flask import Flask, request, jsonify

app = Flask(__name__)

STATIC_RATES = {
    "USD": 100.01,
    "EUR": 110.55
}

@app.route("/rate", methods=["GET"])
def get_rate():
    try:
        currency = request.args.get("currency")
        if not currency or currency.upper() not in STATIC_RATES:
            return jsonify({"message": "UNKNOWN CURRENCY"}), 400
        rate = STATIC_RATES[currency.upper()]
        return jsonify({"rate": rate}), 200
    except Exception:
        return jsonify({"message": "UNEXPECTED ERROR"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
