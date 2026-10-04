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
        with self.assertRaisesRegex(CalculationError, "不能除以 0"):
            calculate("5/0")
        with self.assertRaises(CalculationError):
            calculate("1e3")


if __name__ == "__main__":
    unittest.main()
