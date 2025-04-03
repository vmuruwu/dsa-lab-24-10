#Считать с клавиатуры три произвольных числа, вывести в консоль те числа, которые попадают в интервал [1, 50].

number_1 = float(input('Введите 1 число: '))
number_2 = float(input('Введите 2 число: '))
number_3 = float(input('Введите 3 число: '))

num_list = []

if 1 <= number_1 <= 50:
    num_list.append(number_1)
if 1 <= number_2 <= 50:
    num_list.append(number_2)
if 1 <= number_3 <= 50:
    num_list.append(number_3)

if num_list:
    print('Числа в интервале [1, 50]:', *num_list)
else:
    print('Нет чисел, входящих в интервал [1, 50].')