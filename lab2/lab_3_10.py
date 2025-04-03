import sys
# 1. Считать параметры с командной строки
if len(sys.argv) < 2:
    print("Ошибка: необходимо передать хотя бы один элемент.")
    sys.exit()

try:
    numbers = [int(arg) for arg in sys.argv[1:]]  # Преобразуем все параметры в целые числа
except ValueError:
    print("Ошибка: все параметры должны быть целыми числами.")
    sys.exit()

# 2. Вывод повторяющихся элементов
duplicates = set(x for x in numbers if numbers.count(x) > 1)
if duplicates:
    print("Повторяющиеся элементы:", *duplicates)
else:
    print("Повторяющихся элементов нет.")

# 3. Преобразование массива
transformed_arr = []
for num in numbers:
    if num <= 10:
        transformed_arr.append(0)
    elif num >= 20:
        transformed_arr.append(1)

# 4. Вывод первоначального и преобразованного массива
print("Исходный массив:", *numbers)
print("Преобразованный массив:", *transformed_arr)
