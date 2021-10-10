from lexer import BINARY_OPS

def generate_token_tree(tokens):
    result = []
    top = 0
    middle = []
    for token in tokens:
        if token.val == '(':
            top += 1
            if top > 1:
                middle.append(token)
        elif token.val == ')':
            top -= 1
            if top == 0:
                result.append(generate_token_tree(middle))
                middle = []
            else:
                middle.append(token)
        elif top == 0:
            result.append(token)
        else:
            middle.append(token)
    return result

def set_rt(rt, name, val):
    rt[name] = val
    print(rt)

class Runtime:
    def __init__(self):
        self.variables = {'true': True, 'false': False}
        self.builtins = {
            'print': self._print,
            'set': self._set,
            'if': self._if
        }
    def _print(self, *args):
        print(*args)
    def _set(self, name, value):
        self.variables[name] = value
        return value
    def get(self, name):
        return self.variables[name]
    def _if(self, condition, expression):
        print(condition, expression)
        if condition:
            return expression

def evaluate_expression(expression, runtime):

    global builtins


    if isinstance(expression, list):
        op = expression[0].val

        if op in BINARY_OPS:

            value1 = evaluate_expression(expression[1], runtime)
            value2 = evaluate_expression(expression[2], runtime)

            if op == '+':
                return value1 + value2
            elif op == '-':
                return value1 - value2
            elif op == '*':
                return value1 * value2
            elif op == '/':
                return value1 / value2

        elif op in runtime.builtins:

            args = [evaluate_expression(expr, runtime) for expr in expression[1:]]
            return runtime.builtins[op](*args)


    else:
        if expression.tt == "ident":
            return runtime.get(expression.val)
        elif expression.tt in ["string", "int", "float"]:
            return expression.val

def run(tokens):
    runtime = Runtime()
    statements = []
    working = []
    for token in tokens:
        if token.tt == 'break':
            statements.append(working)
            working = []
        else:
            working.append(token)
    for statement in statements:
        token_tree = generate_token_tree(statement)
        print(token_tree)
        evaluate_expression(token_tree, runtime)
