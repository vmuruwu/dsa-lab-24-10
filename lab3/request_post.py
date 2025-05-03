import requests

url = "http://127.0.0.1:5000/number/"
data = {"jsonParam": 7}  # Задаём число

response = requests.post(url, json=data)
print(response.json())