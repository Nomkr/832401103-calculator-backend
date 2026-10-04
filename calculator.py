"""Expression calculator.

Evaluates arithmetic expressions (+, -, *, /, ^, parentheses, unary
signs, square root, square and percent) with a hand-written recursive
descent parser. Raises CalculationError with a user-friendly message for
invalid input or division by zero. eval/exec is intentionally not used.
"""

import math


class CalculationError(Exception):
    """Raised when an expression is invalid or cannot be computed."""


def tokenize(expression):
    """Split an expression string into numbers and one-character symbols.

    Returns a list of floats and strings such as "+", "(", "√", "^".
    """
    if not isinstance(expression, str):
        raise CalculationError("Expression must be a string")
    if not expression.strip():
        raise CalculationError("Expression cannot be empty")
    if len(expression) > 200:
        raise CalculationError("Expression is too long (max 200 characters)")

    tokens = []
    i = 0
    while i < len(expression):
        ch = expression[i]
        if ("0" <= ch <= "9") or ch == ".":
            num = ""
            while i < len(expression) and (("0" <= expression[i] <= "9") or expression[i] == "."):
                num += expression[i]
                i += 1
            try:
                value = float(num)
            except ValueError:
                raise CalculationError("Invalid number")
            if not math.isfinite(value):
                raise CalculationError("Number out of range")
            tokens.append(value)
        elif ch in "+-*/^%()√²×÷":
            # Accept both UI symbols (× ÷) and ASCII operators.
            tokens.append({"×": "*", "÷": "/"}.get(ch, ch))
            i += 1
        elif ch.isspace():
            i += 1
        else:
            raise CalculationError("Invalid character: " + ch)
    return tokens


class Parser:
    """Recursive descent parser over a token list.

    Grammar, highest precedence first:

        expression := term (("+" | "-") term)*
        term       := power (("*" | "/") power)*
        power      := factor ("^" power)?          # right-associative
        factor     := primary postfix*
        primary    := number | "(" expression ")" | ("-" | "+" | "√") factor
        postfix    := "²" | "%"
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        """Return the current token without consuming it, or None at the end."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def next(self):
        """Consume and return the current token."""
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def parse_factor(self):
        """Parse a factor: a primary followed by postfix operators."""
        if self.peek() == "(":
            self.next()
            value = self.parse_expression()
            if self.peek() != ")":
                raise CalculationError("Missing closing parenthesis")
            self.next()
        elif self.peek() == "-":
            self.next()
            value = -self.parse_factor()
        elif self.peek() == "+":
            self.next()
            value = self.parse_factor()
        elif self.peek() == "√":
            self.next()
            try:
                value = math.sqrt(self.parse_factor())
            except ValueError:
                raise CalculationError("Cannot take square root of a negative number")
        elif isinstance(self.peek(), (int, float)):
            value = self.next()
        else:
            raise CalculationError("Invalid expression")

        # Postfix operators: square (x²) and percent (x%).
        while self.peek() in ("²", "%"):
            op = self.next()
            if op == "²":
                value = value * value
            else:
                value = value / 100
        return value

    def parse_power(self):
        """Parse a power: factors joined by right-associative ^."""
        value = self.parse_factor()
        if self.peek() == "^":
            self.next()
            try:
                value = math.pow(value, self.parse_power())
            except ValueError:
                raise CalculationError("Invalid power operation")
        return value

    def parse_term(self):
        """Parse a term: powers joined by * and /."""
        value = self.parse_power()
        while self.peek() in ("*", "/"):
            op = self.next()
            right = self.parse_power()
            if op == "*":
                value = value * right
            else:
                # Division by zero is converted to CalculationError in calculate().
                value = value / right
        return value

    def parse_expression(self):
        """Parse an expression: terms joined by + and -."""
        value = self.parse_term()
        while self.peek() in ("+", "-"):
            op = self.next()
            right = self.parse_term()
            if op == "+":
                value = value + right
            else:
                value = value - right
        return value


def _format_result(value):
    """Round to 10 decimals and drop the .0 suffix for whole numbers."""
    value = round(value, 10)
    if value == int(value):
        return int(value)
    return value


def calculate(expression):
    """Evaluate an expression string and return the numeric result.

    Raises CalculationError with a user-friendly message when the
    expression is invalid or the computation fails.
    """
    try:
        tokens = tokenize(expression)
        parser = Parser(tokens)
        result = parser.parse_expression()
    except CalculationError:
        raise
    except ZeroDivisionError:
        raise CalculationError("Division by zero")
    except (IndexError, ValueError, TypeError):
        raise CalculationError("Invalid expression")

    if not math.isfinite(result):
        raise CalculationError("Result out of range")

    # Leftover tokens mean the expression has trailing garbage such as "1+2)".
    if parser.pos != len(tokens):
        raise CalculationError("Invalid expression")

    return _format_result(result)


if __name__ == "__main__":
    print(calculate("1+2*3"))       # 7
    print(calculate("(1+2)*3"))     # 9
    print(calculate("√9+2^3"))      # 11
    print(calculate("50%"))         # 0.5
    print(calculate("5²"))          # 25

    print("--- error handling ---")
    for bad in ["5/0", "1+", "abc", "1.2.3", "(1+2", "√-9"]:
        try:
            calculate(bad)
            print(bad, "-> no error (unexpected)")
        except CalculationError as e:
            print(bad, "-> error:", e)
