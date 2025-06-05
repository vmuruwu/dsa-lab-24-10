
#здесь функция get_triangle_type, которую нужно протестировать

class IncorrectTriangleSides(Exception):
#Исключение для некорректных сторон треугольника.
    pass

def get_triangle_type(a, b, c):
    # Проверка, что стороны положительные
    if a <= 0 or b <= 0 or c <= 0:
        raise IncorrectTriangleSides("Стороны должны быть положительными числами.")

    # Проверка неравенства треугольника
    if a + b <= c or a + c <= b or b + c <= a:
        raise IncorrectTriangleSides("Сумма любых двух сторон должна быть больше третьей.")

    if a == b == c:
        return "equilateral"
    elif a == b or b == c or a == c:
        return "isosceles"
    else:
        return "nonequilateral"
