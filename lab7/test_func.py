# тестируем функцию get_triangle_type с помощью стандартной библиотеки unittest

import unittest
from triangle_func import get_triangle_type, IncorrectTriangleSides

class TestGetTriangleType(unittest.TestCase):
    def test_equilateral(self):
        self.assertEqual(get_triangle_type(3, 3, 3), "equilateral")

    def test_isosceles(self):
        self.assertEqual(get_triangle_type(4, 4, 5), "isosceles")
        self.assertEqual(get_triangle_type(5, 4, 5), "isosceles")

    def test_nonequilateral(self):
        self.assertEqual(get_triangle_type(3, 4, 5), "nonequilateral")

    def test_incorrect_sides_zero(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(0, 3, 3)

    def test_incorrect_sides_negative(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(-1, 3, 3)

    def test_triangle_inequality_violation(self):
        with self.assertRaises(IncorrectTriangleSides):
            get_triangle_type(1, 2, 3)

if __name__ == '__main__':
    unittest.main()
