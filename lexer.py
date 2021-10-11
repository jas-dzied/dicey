import rich
import sys

CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
DIGITS = '0123456789.-'

BINARY_OPS = '+-*/:'
OTHER_OPS = '()[]{}'

class Token:
    def __init__(self, value=None):
        self.value = value
    def __repr__(self):
        return f'({self.__class__.__name__}:{repr(self.value)})'
    def exec(self, ctx):
        return self
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.value == other.value

class IntLiteral(Token):
    pass
class FloatLiteral(Token):
    pass
class StringLiteral(Token):
    pass
class Op(Token):
    pass
class Break(Token):
    pass
class Ident(Token):
    pass

class Lexer:
    def __init__(self, text):
        self.text = text+'\n'
        self.i = -1
        self.row = 0
        self.column = 0
        self.advance()
    def advance(self):
        self.i += 1
        self.char = self.text[self.i]
        self.column += 1
        if self.char == '\n':
            self.row += 1
            self.column = 0
    def reverse(self):
        self.i -= 1
        self.char = self.text[self.i]
    def next(self):
        return self.text[self.i+1]

    def make_number(self):
        result = ''
        while self.char in DIGITS:
            result += self.char
            self.advance()
        if '.' in result:
            self.tokens.append(FloatLiteral(float(result)))
        else:
            self.tokens.append(IntLiteral(int(result)))
        self.reverse()

    def make_ident(self):
        result = ''
        while self.char in CHARS:
            result += self.char
            self.advance()
        self.tokens.append(Ident(result))
        self.reverse()

    def make_string(self):
        result = ''
        self.advance()
        while self.char != '"':
            result += self.char
            self.advance()
        self.tokens.append(StringLiteral(result))

    def lex(self):
        self.tokens = []

        while True:

            if self.char in DIGITS:
                self.make_number()

            elif self.char in CHARS:
                self.make_ident()

            elif self.char == '"':
                self.make_string()

            elif self.char == ';':
                self.tokens.append(Break())

            elif self.char in ' \n':
                pass

            else:
                self.tokens.append(Token(self.char))
                #rich.print(f"[bold red]ERROR[/] on [red](line {self.row}, character {self.column}):")
                #rich.print(f"   Invalid character: {self.char}")
                #error_line = self.text.split('\n')[self.row]
                #rich.print(f"      [white on #4a4a4a]{error_line}[/]")
                #rich.print("    "+" "*self.column+"[red]^[/]")
                #sys.exit(1)

            if self.i+1 >= len(self.text):
                break
            else:
                self.advance()

        return self.tokens

if __name__ == '__main__':
    import rich
    with open('./test.dice', 'r') as file:
        tokens = Lexer(file.read()).lex()
    rich.print(tokens)
