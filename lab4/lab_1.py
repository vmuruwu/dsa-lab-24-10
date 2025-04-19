import os

# Безопасный способ (возвращает None, если переменной нет)
api_token = os.getenv('API_TOKEN')
print(f"API Token (getenv): {api_token}")

# Альтернативный способ (вызывает исключение, если переменной нет)
try:
    api_token_alt = os.environ['API_TOKEN']
    print(f"API Token (environ): {api_token_alt}")
except KeyError:
    print("Переменная API_TOKEN не найдена в окружении")

# Проверка перед использованием
if api_token:
    print("Токен доступен, можно делать API-запросы")
else:
    print("Ошибка: API_TOKEN не установлен")