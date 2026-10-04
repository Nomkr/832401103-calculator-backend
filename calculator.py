"""
calculator.py —— 计算器的"核心工程师"。

这个文件负责后端最重要的一件事：把一段文字表达式（字符串）变成数字结果。
它不碰网络、不碰数据库，所以可以单独运行、单独测试。

支持：加减乘除、优先级、括号、负数、正号、小数。
会拒绝：非法表达式、除零，并通过 CalculationError 报告原因。

例子：
    "1+2*3"    -> 7
    "(1+2)*3"  -> 9
    "-5+8"     -> 3
    "3.14*2"   -> 6.28
"""

import math


class CalculationError(Exception):
    """计算错误：表达式非法、除零等。str(e) 就是对用户友好的原因。"""
    pass


def tokenize(expression):
    """
    分词：把文字表达式拆成一个个"零件"(token) 的列表。

    例子：
        "1+2*3"  -> [1.0, "+", 2.0, "*", 3.0]
    """
    if not isinstance(expression, str):
        raise CalculationError("表达式必须是字符串")
    if not expression.strip():
        raise CalculationError("表达式不能为空")
    if len(expression) > 200:
        raise CalculationError("表达式过长（最多 200 个字符）")

    tokens = []                # 装零件的小车（列表）
    i = 0                      # "手指"，指向当前正在看第几个字符
    while i < len(expression):
        ch = expression[i]
        if ch.isdigit() or ch == ".":   # 数字或小数点
            num = ""            # 把连续的数字和小数点拼成一个完整的数
            while i < len(expression) and (expression[i].isdigit() or expression[i] == "."):
                num = num + expression[i]
                i = i + 1
            try:
                value = float(num)
            except ValueError:
                raise CalculationError("非法数字")
            if not math.isfinite(value):
                raise CalculationError("数字超出范围")
            tokens.append(value)
        elif ch in "+-*/()×÷":    # 运算符或括号
            # API 同时接受用户界面的乘除符号，内部统一使用 ASCII 运算符。
            tokens.append({"×": "*", "÷": "/"}.get(ch, ch))
            i = i + 1
        elif ch.isspace():      # 空白字符：跳过（允许换行或制表符）
            i = i + 1
        else:                   # 其它字符（字母等）：非法，直接抛错
            raise CalculationError("非法字符: " + ch)
    return tokens


class Parser:
    """解析器：从零件列表里，按"优先级"算出结果。"""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        """看一眼手指位置的零件，但手指不往前挪。"""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def next(self):
        """取出手指位置的零件，并把手指往前挪一格。"""
        token = self.tokens[self.pos]
        self.pos = self.pos + 1
        return token

    def parse_factor(self):
        """最底层：一个数、一对括号，或带正负号的数（如 -5、3*-2）。"""
        if self.peek() == "(":
            self.next()                     # 跳过左括号 (
            value = self.parse_expression() # 括号里重新算一整个表达式（递归）
            if self.peek() != ")":
                raise CalculationError("缺少右括号")
            self.next()                     # 跳过右括号 )
            return value
        elif self.peek() == "-":            # 负号（负数）
            self.next()
            return -self.parse_factor()     # 对后面的数取相反数（递归）
        elif self.peek() == "+":            # 正号（+5 就是 5）
            self.next()
            return self.parse_factor()
        elif isinstance(self.peek(), (int, float)):
            return self.next()              # 普通数字
        else:
            # 不能把运算符或表达式结尾当成数字，否则输入如 "*2"
            # 会一路传到 math.isfinite，变成服务端 500 错误。
            raise CalculationError("非法表达式")

    def parse_term(self):
        """中间层：负责乘除（优先级高，先算）。"""
        value = self.parse_factor()
        while self.peek() in ("*", "/"):
            op = self.next()
            right = self.parse_factor()
            if op == "*":
                value = value * right
            else:                           # op == "/"
                value = value / right       # 除零时这里会抛 ZeroDivisionError
        return value

    def parse_expression(self):
        """最外层：负责加减（优先级低，最后算）。"""
        value = self.parse_term()
        while self.peek() in ("+", "-"):
            op = self.next()
            right = self.parse_term()
            if op == "+":
                value = value + right
            else:                           # op == "-"
                value = value - right
        return value


def _format_result(value):
    """整理结果：消除浮点误差，整数显示成整数（7.0 -> 7）。"""
    value = round(value, 10)        # 四舍五入到 10 位小数，消除 0.1+0.2 的误差
    if value == int(value):         # 如果是整数（如 7.0）
        return int(value)           # 显示成 7
    return value


def calculate(expression):
    """
    计算一个表达式，返回结果。
    如果表达式非法或除零，抛出 CalculationError。
    """
    try:
        tokens = tokenize(expression)          # 可能抛 CalculationError / ValueError
        parser = Parser(tokens)
        result = parser.parse_expression()     # 可能抛 IndexError / ZeroDivisionError
    except CalculationError:
        raise                                   # 我们自己抛的，原样往上抛
    except ZeroDivisionError:
        raise CalculationError("不能除以 0")
    except (IndexError, ValueError, TypeError):
        raise CalculationError("非法表达式")

    if not math.isfinite(result):
        raise CalculationError("结果超出范围")

    # 算完后，如果还有没被用掉的零件，说明结构不对（如 "1+2)"）
    if parser.pos != len(tokens):
        raise CalculationError("非法表达式")

    return _format_result(result)


# 直接运行本文件时，执行下面的测试
if __name__ == "__main__":
    # 正常计算
    print(calculate("1+2*3"))      # 7
    print(calculate("(1+2)*3"))    # 9
    print(calculate("-5+8"))       # 3
    print(calculate("3.14*2"))     # 6.28

    # 错误处理测试：每个非法输入都应该抛错并给出原因
    print("--- 错误处理 ---")
    for bad in ["5/0", "1+", "abc", "1.2.3", "(1+2"]:
        try:
            calculate(bad)
            print(bad, "-> 没报错（不该发生）")
        except CalculationError as e:
            print(bad, "-> 错误：", e)
