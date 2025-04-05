numbers = []
print("Введите последовательность целых чисел. Для завершения ввода введите 'q':")

while True:
    input_data = input("Введите число (или 'q' для завершения): ").strip()


    if input_data.lower() == 'q':
        if not numbers:
            print("Ошибка: последовательность не должна быть пустой!")
            continue
        break

    if not input_data:
        print('Ошибка: введите число!')
        continue

    try:
        number = int(input_data)
        numbers.append(number)
    except ValueError:
        print("Ошибка: введено не число!")

# Вычисление суммы и количества
sum_numbers = sum(numbers)
count_numbers = len(numbers)

# Вывод результатов
print(f"Сумма всех чисел: {sum_numbers}")
print(f"Количество чисел: {count_numbers}")