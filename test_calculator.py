"""Parser regression tests. Run with: python -m unittest -v"""

import unittest

from calculator import CalculationError, calculate


class CalculatorTests(unittest.TestCase):
    def test_arithmetic_precedence(self):
        self.assertEqual(calculate("1+2*3"), 7)
        self.assertEqual(calculate("(1+2)*3"), 9)
        self.assertEqual(calculate("3*-2"), -6)

    def test_decimals_and_unary_signs(self):
        self.assertEqual(calculate("0.1+0.2"), 0.3)
        self.assertEqual(calculate("--5"), 5)
        self.assertEqual(calculate("+3.5"), 3.5)

    def test_display_operators_and_whitespace(self):
        self.assertEqual(calculate(" 1 × 2\n+\t3 ÷ 3 "), 3)

    def test_invalid_input(self):
        for expression in (
            "",
            "1+",
            "*2",
            "/2",
            "1.2.3",
            "abc",
            "(1+2",
            "()",
            None,
            12,
        ):
            with self.subTest(expression=expression):
                with self.assertRaises(CalculationError):
                    calculate(expression)

    def test_division_by_zero_and_non_finite_result(self):
        with self.assertRaisesRegex(CalculationError, "Division by zero"):
            calculate("5/0")
        with self.assertRaises(CalculationError):
            calculate("1e3")

    def test_scientific_operators(self):
        self.assertEqual(calculate("√9"), 3)
        self.assertEqual(calculate("√(16)"), 4)
        self.assertEqual(calculate("5²"), 25)
        self.assertEqual(calculate("-3²"), -9)
        self.assertEqual(calculate("2^10"), 1024)
        self.assertEqual(calculate("2^3^2"), 512)
        self.assertEqual(calculate("50%"), 0.5)
        self.assertEqual(calculate("5²%"), 0.25)
        with self.assertRaisesRegex(CalculationError, "square root of a negative"):
            calculate("√-9")
        with self.assertRaisesRegex(CalculationError, "Invalid power operation"):
            calculate("(-2)^0.5")


if __name__ == "__main__":
    unittest.main()
