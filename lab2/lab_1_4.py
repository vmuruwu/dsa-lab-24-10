numbers = []
print("Введите последовательность целых чисел. Для завершения ввода введите 'q':")

while True:
    input_data = input("Введите число (или 'q' для завершения): ")


    if input_data.lower() == 'q':
        if not numbers:
            print("Ошибка: последовательность не должна быть пустой!")
            continue
        break

    if input_data == '':
        print('Ошибка: введите число!')
        continue

    try:
        number = int(input_data)
        numbers.append(number)
    except ValueError:
        print("Ошибка: введено не число!")


sum_numbers = 0
count_numbers = 0
i = 0

while i < len(numbers):
    sum_numbers += numbers[i]
    count_numbers += 1
    i += 1

print(f"Сумма всех чисел: {sum_numbers}")
print(f"Количество чисел: {count_numbers}")
