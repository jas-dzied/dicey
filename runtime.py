import rich
import sys
from lexer import Op, Token, StringLiteral, IntLiteral, FloatLiteral, Ident
import random

randgen = random.SystemRandom()

class Expression:
    def __init__(self, tokens):
        self.tokens = tokens
    def __repr__(self):
        return f'Expr{repr(self.tokens)}'
    def add(self, item):
        self.tokens.append(item)
    def exec(self, ctx):
        if self.tokens[0].value in ctx.functions:
            function = ctx.functions[self.tokens[0].value]
        elif Value.get(self.tokens[0]).value(ctx) in ctx.functions:
            function = ctx.functions[Value.get(self.tokens[0]).value(ctx)]
        else:
            rich.print(f"[bold red]ERROR[/]")
            rich.print(f"   Undefined function: {self.tokens[0].value}")
            sys.exit(1)
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
class List(Value):
    into=list
    def exec(self, ctx):
        return self.data

class Context:
    def __init__(self, variables, functions, types, dice_rolls, dice_count, python_runtime):
        self.variables = variables
        self.functions = functions
        self.types = types
        self.dice_rolls = dice_rolls
        self.dice_count = dice_count
        self.python_runtime = python_runtime
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
                Variable,
                List
            ]},
            [],
            1,
            {}
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

    def _neg_(ctx, a):
        return -1*a.exec(ctx)

    def _if_(ctx, condition, actions, else_block=Block([])):
        if condition.exec(ctx):
            actions.exec(ctx)
        else:
            else_block.exec(ctx)
    def _while_(ctx, condition, actions):
        while condition.exec(ctx):
            actions.exec(ctx)

    def _dice_(ctx, amount, sides):
        ctx.dice_rolls.append(sides.exec(ctx))
        ctx.dice_count *= amount.exec(ctx)
    def _roll_(ctx):
        global randgen
        results = []
        for _ in range(ctx.dice_count):
            results.append([randgen.randint(1, sides) for sides in ctx.dice_rolls])
        return results

    def _list_(ctx, *items):
        return [item.exec(ctx) for item in items]
    def _push_(ctx, lst, item, at=None):
        if at is None:
            lst.exec(ctx).append(item.exec(ctx))
        else:
            lst.exec(ctx).insert(at.exec(ctx), item.exec(ctx))
    def _pop_(ctx, lst, at=None):
        if at is None:
            return lst.exec(ctx).pop()
        else:
            return lst.exec(ctx).pop(at.exec(ctx))
    def _index_(ctx, lst, at):
        return lst.exec(ctx)[at.exec(ctx)]
    def _range_(ctx, lst, op1=None, op2=None, op3=None):
        if op1 == Token(':'):
            return lst.exec(ctx)[:op2.exec(ctx)]
        elif op2 == Token(':') and op3 is not None:
            return lst.exec(ctx)[op1.exec(ctx):op3.exec(ctx)]
        elif op2 == Token(':'):
            return lst.exec(ctx)[op1.exec(ctx):]
    def _eval_py_(ctx, code):
        return eval(code.exec(ctx), ctx.python_runtime)
    def _exec_py_(ctx, code):
        return exec(code.exec(ctx), ctx.python_runtime)

def run(tokens):

    tree = generate_tree(tokens)
    ctx = Context.default()
    tree.exec(ctx)
