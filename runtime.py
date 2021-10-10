import rich
from lexer import Op, StringLiteral, IntLiteral, FloatLiteral, Ident

class Expression:
    def __init__(self, tokens):
        self.tokens = tokens
    def __repr__(self):
        return f'Expr{repr(self.tokens)}'
    def add(self, item):
        self.tokens.append(item)
    def exec(self, ctx):
        function = ctx.functions[self.tokens[0].value]
        args = [Value.get(token) for token in self.tokens[1:]]
        return function(ctx, *args)

class Block:
    def __init__(self, expressions):
        self.expressions = expressions
    def __repr__(self):
        return f'Block{repr(self.expressions)}'
    def add(self, item):
        self.expressions.append(item)
    def exec(self, ctx):
        for expr in self.expressions:
            expr.exec(ctx)

def generate_tree(tokens, result_type=Expression):
    if tokens[0].value == '[':
        result = Block([])
        working = []
        level = 0
        for token in tokens[1:-1]:
            if token.value in ['(', '[']:
                level += 1
                working.append(token)
            elif token.value in [')', ']']:
                level -= 1
                working.append(token)
            elif token.value is None:
                if level == 0:
                    result.add(generate_tree(working))
                    working = []
                else:
                    working.append(token)
            else:
                working.append(token)
        return result

    elif tokens[0].value == '(':
        return generate_tree(tokens[1:-1])

    else:
        result = result_type([])
        working = []
        worksig = Block
        level = 0
        for token in tokens:
            if token.value in ['(', '[']:
                level += 1
                if level > 1:
                    working.append(token)
                else:
                    if token.value == '(':
                        worksig = Expression
                    else:
                        worksig = Block
            elif token.value in [')', ']']:
                level -= 1
                if level >= 1:
                    working.append(token)
                elif level == 0:
                    if worksig == Expression:
                        result.add(generate_tree(working, worksig))
                    else:
                        result.add(generate_tree([Op('[')]+working+[Op(']')], worksig))
                    working = []
            else:
                if level == 0:
                    result.add(token)
                else:
                    working.append(token)
        return result


class Value:
    def __init__(self, data):
        self.data = data
    def get(token):
        conversion_map = {
            StringLiteral: String,
            IntLiteral: Integer,
            FloatLiteral: Float,
            Ident: Variable,
        }
        if token.__class__ in conversion_map:
            return conversion_map[token.__class__](token.value)
        else:
            return token

class Integer(Value):
    into=int
    def exec(self, ctx):
        return self.data
class Float(Value):
    into=float
    def exec(self, ctx):
        return self.data
class String(Value):
    into=str
    def exec(self, ctx):
        return self.data
class Boolean(Value):
    into=bool
    def exec(self, ctx):
        return self.data
class Variable(Value):
    def exec(self, ctx):
        return ctx.variables[self.data]

class Context:
    def __init__(self, variables, functions, types):
        self.variables = variables
        self.functions = functions
        self.types = types
    def default():
        return Context(
            {
                'version': '0.0.1',
                'true': Boolean(True),
                'false': Boolean(False)
            },
            {funcname[1:-1]: getattr(STD, funcname) for funcname in dir(STD)},
            {cls.__name__: cls for cls in [
                Integer,
                Float,
                String,
                Boolean,
                Variable
            ]}
        )

class STD:
    def _println_(ctx, *args):
        print(*[arg.exec(ctx) for arg in args])
    def _print_(ctx, text):
        print(text.exec(ctx), end="")
    def _input_(ctx):
        return input()
    def _set_(ctx, name, value):
        ctx.variables[name.exec(ctx)] = value.exec(ctx)
    def _get_(ctx, name):
        return ctx.variables[name.exec(ctx)]
    def _cast_(ctx, target, value):
        casting_func = ctx.types[target.exec(ctx)].into
        return casting_func(value.exec(ctx))

    def _equal_(ctx, a, b):
        return a.exec(ctx) == b.exec(ctx)
    def _notequal_(ctx, a, b):
        return a.exec(ctx) != b.exec(ctx)

    def _add_(ctx, a, b):
        return a.exec(ctx)+b.exec(ctx)
    def _subtract_(ctx, a, b):
        return a.exec(ctx)-b.exec(ctx)
    def _times_(ctx, a, b):
        return a.exec(ctx)*b.exec(ctx)
    def _divide_(ctx, a, b):
        return a.exec(ctx)/b.exec(ctx)

    def _if_(ctx, condition, actions, else_block=Block([])):
        if condition.exec(ctx):
            actions.exec(ctx)
        else:
            else_block.exec(ctx)
    def _while_(ctx, condition, actions):
        while condition.exec(ctx):
            actions.exec(ctx)


def run(tokens):

    tree = generate_tree(tokens)
    ctx = Context.default()
    tree.exec(ctx)
