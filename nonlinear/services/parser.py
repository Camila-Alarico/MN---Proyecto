"""Restricted AST -> SymPy. Never pass untrusted strings to sympify/parse_expr/eval."""
import ast
import math
import sympy as sp

X = sp.Symbol('x', real=True)
FUNCTIONS = {'sin': sp.sin, 'cos': sp.cos, 'tan': sp.tan, 'exp': sp.exp,
             'log': sp.log, 'sqrt': sp.sqrt, 'abs': sp.Abs}


class MathInputError(ValueError):
    """An input/domain error safe to present to a student."""


def finite(value, label='valor'):
    if isinstance(value, bool):
        raise MathInputError(f'{label}: ingresa un número real finito.')
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError):
        raise MathInputError(f'{label}: ingresa un número real finito.') from None
    if not math.isfinite(number) or abs(number) > 1e12:
        raise MathInputError(f'{label}: valor no finito o fuera del límite ±10¹².')
    return number


class ParsedFunction:
    def __init__(self, expression):
        self.expression = expression

    def __call__(self, x):
        try:
            self._guard(self.expression, finite(x))
            result = float(self.expression.subs(X, finite(x)).doit().evalf())
            if not math.isfinite(result) or abs(result) > 1e100:
                raise ValueError()
            return result
        except (ValueError, TypeError, OverflowError, ZeroDivisionError):
            raise MathInputError('La función no produce un valor real finito en este punto. Revisa su dominio.') from None

    @staticmethod
    def _guard(node, x):
        """Bound intermediate values before SymPy evaluation, including nested exp."""
        if node == X:
            return x
        if node.is_Number:
            value = float(node)
        else:
            args = [ParsedFunction._guard(arg, x) for arg in node.args]
            functions = {sp.sin: math.sin, sp.cos: math.cos, sp.tan: math.tan,
                         sp.exp: math.exp, sp.log: math.log, sp.Abs: abs,
                         sp.sign: lambda n: 0 if n == 0 else math.copysign(1, n)}
            if node.func == sp.Add:
                value = sum(args)
            elif node.func == sp.Mul:
                value = math.prod(args)
            elif node.func == sp.Pow:
                value = math.pow(*args)
            elif node.func in functions:
                value = functions[node.func](*args)
            else:
                raise MathInputError('Expresión o derivada fuera del dominio permitido.')
        if not math.isfinite(value) or abs(value) > 1e100:
            raise MathInputError('Un valor intermedio desborda el límite numérico.')
        return value

    def derivative(self, order=1):
        expr = sp.diff(self.expression, X, order)
        if expr.has(sp.Derivative, sp.DiracDelta):
            raise MathInputError('La derivada no es regular. Evita abs en métodos que requieren derivadas.')
        return ParsedFunction(expr)

    @property
    def latex(self):
        return sp.latex(self.expression)


def parse_function(expression):
    if not isinstance(expression, str) or not expression.strip() or len(expression) > 200:
        raise MathInputError('Escribe una función de entre 1 y 200 caracteres.')
    try:
        tree = ast.parse(expression.strip().replace('^', '**'), mode='eval')
    except (SyntaxError, RecursionError):
        raise MathInputError('Expresión inválida. Usa x, operadores y funciones como sin(x).') from None
    if len(list(ast.walk(tree))) > 80:
        raise MathInputError('La expresión es demasiado compleja (máximo 80 nodos).')

    def build(node, depth=0):
        if depth > 12:
            raise MathInputError('Demasiados niveles de paréntesis o funciones.')
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            number = finite(node.value, 'Constante')
            return sp.Float(number) if isinstance(node.value, float) else sp.Integer(node.value)
        if isinstance(node, ast.Name) and node.id == 'x':
            return X
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = build(node.operand, depth + 1)
            return value if isinstance(node.op, ast.UAdd) else sp.Mul(-1, value, evaluate=False)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FUNCTIONS and len(node.args) == 1 and not node.keywords:
            return FUNCTIONS[node.func.id](build(node.args[0], depth + 1), evaluate=False)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
            left = build(node.left, depth + 1)
            right = build(node.right, depth + 1)
            if isinstance(node.op, ast.Pow):
                # Literal exponents only: prevents explosive nested powers and symbolic costs.
                literal = node.right.operand if isinstance(node.right, ast.UnaryOp) else node.right
                if not isinstance(literal, ast.Constant) or type(literal.value) not in (int, float) or abs(literal.value) > 20:
                    raise MathInputError('Usa exponentes numéricos constantes entre -20 y 20; para eˣ usa exp(x).')
                if left.has(sp.Pow):
                    raise MathInputError('No se permiten potencias anidadas; simplifica la expresión.')
                return sp.Pow(left, right, evaluate=False)
            if isinstance(node.op, ast.Add):
                return sp.Add(left, right, evaluate=False)
            if isinstance(node.op, ast.Sub):
                return sp.Add(left, sp.Mul(-1, right, evaluate=False), evaluate=False)
            if isinstance(node.op, ast.Mult):
                return sp.Mul(left, right, evaluate=False)
            return sp.Mul(left, sp.Pow(right, -1, evaluate=False), evaluate=False)
        raise MathInputError('Símbolo no permitido. Usa solo x, + - * / ^ y sin, cos, tan, exp, log, sqrt, abs.')

    return ParsedFunction(build(tree.body))
