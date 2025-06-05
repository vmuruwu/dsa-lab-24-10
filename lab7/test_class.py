# протестировать класс Triangle на корректность с помощью pytest.

import pytest
from triangle_class import Triangle, IncorrectTriangleSides

# Позитивные тесты
def test_equilateral_triangle():
    t = Triangle(3, 3, 3)
    assert t.triangle_type() == "equilateral"
    assert t.perimeter() == 10

def test_isosceles_triangle():
    t = Triangle(5, 5, 3)
    assert t.triangle_type() == "isosceles"
    assert t.perimeter() == 13

def test_nonequilateral_triangle():
    t = Triangle(4, 5, 6)
    assert t.triangle_type() == "nonequilateral"
    assert t.perimeter() == 15

# Негативные тесты
@pytest.mark.parametrize("a,b,c", [
    (0, 2, 2),
    (-1, 3, 3),
    (1, 2, 3),
    (10, 2, 2),
])
def test_invalid_triangles(a, b, c):
    with pytest.raises(IncorrectTriangleSides):
        Triangle(a, b, c)
