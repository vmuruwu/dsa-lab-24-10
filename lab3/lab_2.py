import requests
import random

# === 1. GET /number/ ===
param_get = random.randint(1, 10)
get_response = requests.get('http://127.0.0.1:5000/number/', params={'param': param_get})

if get_response.status_code == 200:
    get_data = get_response.json()
    if 'result' in get_data and 'operation' in get_data:
        get_result = get_data['result']
        get_operation = get_data['operation']  # Запоминаем операцию
        print(f"[GET] param: {param_get}, result: {get_result}, operation: {get_operation}")
    else:
        print("Ошибка: отсутствуют ключи 'result' или 'operation' в ответе GET запроса.")
else:
    print(f"Ошибка GET запроса: {get_response.status_code}")

# === 2. POST /number/ ===
param_post = random.randint(1, 10)
headers = {'Content-Type': 'application/json'}
post_response = requests.post(
    'http://127.0.0.1:5000/number/',
    json={'jsonParam': param_post},
    headers=headers
)

if post_response.status_code == 200:
    post_data = post_response.json()
    if 'random_number' in post_data and 'operation' in post_data and 'result' in post_data:
        post_number = post_data['random_number']
        post_operation = post_data['operation']
        post_result = post_data['result']
        print(f"[POST] jsonParam: {param_post}, random: {post_number}, operation: {post_operation}, result: {post_result}")
    else:
        print("Ошибка: отсутствуют ключи 'random_number', 'operation' или 'result' в ответе POST запроса.")
else:
    print(f"Ошибка POST запроса: {post_response.status_code}")

# === 3. DELETE /number/ ===
delete_response = requests.delete('http://127.0.0.1:5000/number/')
if delete_response.status_code == 200:
    delete_data = delete_response.json()
    if 'random_number' in delete_data and 'operation' in delete_data:
        delete_number = delete_data['random_number']
        delete_operation = delete_data['operation']
        print(f"[DELETE] random: {delete_number}, operation: {delete_operation}")
    else:
        print("Ошибка: отсутствуют ключи 'random_number' или 'operation' в ответе DELETE запроса.")
else:
    print(f"Ошибка DELETE запроса: {delete_response.status_code}")

# === 4. Собираем выражение и считаем ===

    # Этап 1: GET результат <POST operation> POST результат
if post_operation == '+':
    intermediate = get_result + post_result
elif post_operation == '-':
    intermediate = get_result - post_result
elif post_operation == '*':
    intermediate = get_result * post_result
elif post_operation == '/':
    intermediate = get_result / post_result if post_result != 0 else float('inf')

# Этап 2: Результат выше <DELETE operation> DELETE число
if delete_operation == '+':
    final = intermediate + delete_number
elif delete_operation == '-':
    final = intermediate - delete_number
elif delete_operation == '*':
    final = intermediate * delete_number
elif delete_operation == '/':
    final = intermediate / delete_number if delete_number != 0 else float('inf')

print(f"\nИтоговое выражение: ({get_result} {post_operation} {post_result}) {delete_operation} {delete_number}")
print(f"Результат (int): {int(final)}")
