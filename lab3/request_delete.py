import requests

response = requests.delete("http://127.0.0.1:5000/number/")
print(response.json())