#Считать с клавиатуры три произвольных числа, вывести в консоль те числа, которые попадают в интервал [1, 50].

num1 = int(input('Введите число 1: '))
num2  = int(input('Введите число 2: '))
num3 = int(input('Введите число 3: '))

numbers = [num1, num2, num3]
in_interval = [num for num in numbers if 1<= num <=50]

if in_interval:
    print("Числа, входящие в интервал:", ", ".join(map(str, in_interval)))
else:
    print("Нет чисел, входящих в интервал.")