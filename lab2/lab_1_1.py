##Считать с клавиатуры три произвольных числа, найти минимальное среди них и вывести на экран.


number_1 = float(input("Введите первое число: "))
number_2 = float(input("Введите второе число: "))
number_3 = float(input("Введите третье число: "))

min_number = number_1

if number_2 < min_number:
    min_number = number_2
if number_3 < min_number:
    min_number = number_3

print("Минимальное число:", min_number)



