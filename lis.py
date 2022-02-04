import math
import operator as op
import re
import sys
from typing import Dict, Union

Symbol = str
List = list
Number = (int, float)
Exp = Union[Symbol, List]


class Env(dict):

    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        "Find the inhermost Env where var appears"
        return self if(var in self) else self.outer.find(var)


class Procedure(object):
    "A user-defined Scheme procedure"

    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env

    def __call__(self, *args: any):
        return eval(self.body, Env(self.parms, args, self.env))


class Symbol(str):
    pass


def Sym(s, symbol_table={}):
    "Find or create unique Symbol entry for str s in symbol table"
    if s not in symbol_table:
        symbol_table[s] = Symbol(s)
    return symbol_table[s]


_quote, _if, _set, _define, _lambda, _begin, _definemacro, = map(Sym,
                                                                 "quote   if   set!  define   lambda   begin   define-macro".split())

_quasiquote, _unquote, _unquotesplicing = map(Sym,
                                              "quasiquote   unquote   unquote-splicing".split())
eof_object = Symbol('#<eof-object>')  # Note: uninterned; can't be read

quotes = {"'": _quote, "`": _quasiquote, ",": _unquote, ",@": _unquotesplicing}


class InPort(object):
    "An input port. Retains a line of chars."
    tokenizer = r'''\s*(,@|[('`,)]|"(?:[\\].|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)'''

    def __init__(self, file):
        self.file = file
        self.line = ''

    def next_token(self):
        "Return the next token, reading new text into line buffer if needed."
        while True:
            if self.line == '':
                self.line = self.file.readline()
            if self.line == '':
                return eof_object
            token, self.line = re.match(InPort.tokenizer, self.line).groups()
            if token != '' and not token.startswith(';'):
                return token


def readchar(inport):
    "Read the next character from an input port."
    if inport.line != '':
        ch, inport.line = inport.line[0], inport.line[1:]
        return ch
    else:
        return inport.file.read(1) or eof_object


def read(inport):
    "Read a Scheme expression from an input port."
    def read_ahead(token):
        if '(' == token:
            L = []
            while True:
                token = inport.next_token()
                if token == ')':
                    return L
                else:
                    L.append(read_ahead(token))
        elif ')' == token:
            raise SyntaxError('unexpected )')
        elif token in quotes:
            return [quotes[token], read(inport)]
        elif token is eof_object:
            raise SyntaxError('unexpected EOF in list')
        else:
            return atom(token)
    # body of read:
    token1 = inport.next_token()
    return eof_object if token1 is eof_object else read_ahead(token1)


def standard_env() -> Env:
    "And environment with some Scheme standard procedures"
    env = Env()
    env.update(vars(math))
    env.update({
        '+': op.add,
        '-': op.sub,
        '*': op.mul,
        '/': op.truediv,
        '>': op.gt,
        '<': op.lt,
        '>=': op.ge,
        '<=': op.le,
        '=': op.eq,
        'abs': abs,
        'append':  op.add,
        'apply': lambda proc, args: proc(*args),
        'begin': lambda *x: x[-1],
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x, y: [x] + y,
        'eq?': op.is_,
        'expt': pow,
        'equal?': op.eq,
        'length': len,
        'list': lambda *x: List(x),
        'list?': lambda x: isinstance(x, List),
        'map': map,
        'max': max,
        'min': min,
        'not': op.not_,
        'null?': lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'print': print,
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })

    return env


global_env = standard_env()


def tokenize(chars: str) -> list:
    "Convert a string of characters into a list of tokens"

    print(chars)
    print(hasattr(chars, 'replace'))
    print(type(chars))

    return []

    return chars.replace('(', ' ( ').replace(')', ' ) ').split()


# def parse(program: str):
#     "Read a Scheme expression from a string"
#     return read_from_tokens(read(program))
def parse(inport):
    "Parse a program: read and expand/error-check it."
    # Backwards compatibility: given a str, convert it to an InPort
    if isinstance(inport, str):
        inport = InPort(StringIO.StringIO(inport))
    return read_from_tokens(read(inport))


def read_from_tokens(tokens: list):
    "Read an expressino from a sequence of tokens"
    if len(tokens) == 0:
        raise SyntaxError('Unexpected EOF')

    token = tokens.pop(0)
    if token == '(':
        l = []
        while tokens[0] != ')':
            l.append(read_from_tokens(tokens))
        tokens.pop(0)  # closing ')'
        return l
    elif token == ')':
        raise SyntaxError('Unexpected )')
    else:
        return atom(token)


def atom(token):
    'Numbers become numbers; #t and #f are booleans; "..." string; otherwise Symbol.'
    if token == '#t':
        return True
    elif token == '#f':
        return False
    elif token[0] == '"':
        return token[1:-1].decode('string_escape')
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            try:
                return complex(token.replace('i', 'j', 1))
            except ValueError:
                return Sym(token)


def to_string(x):
    "Convert a Python object back into a Lisp-readable string."
    if x is True:
        return "#t"
    elif x is False:
        return "#f"
    elif op.is_(x, Symbol):
        return x
    elif op.is_(x, str):
        return '"%s"' % x.encode('string_escape').replace('"', r'\"')
    elif op.is_(x, list):
        return '('+' '.join(map(to_string, x))+')'
    elif op.is_(x, complex):
        return str(x).replace('j', 'i')
    else:
        return str(x)


def eval(x: Exp, env: Env = global_env):
    "Evaluates an expression in an environment"
    if isinstance(x, Symbol):  # variable
        return env.find(x)[x]
    elif not isinstance(x, List):  # constant
        return x

    op, *args = x
    if op == 'quote':
        return args[0]
    elif x[0] == 'if':
        (test, conseq, alt) = args
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)
    elif op == 'define':
        (symbol, exp) = args
        env[symbol] = eval(exp, env)
    elif op == 'set!':
        (symbol, exp) = args
        env.find(symbol)[symbol] = eval(exp, env)
    elif op == 'lambda':
        (parms, body) = args
        return Procedure(parms, body, env)
    else:
        proc = eval(op, env)
        vals = [eval(arg, env) for arg in args]
        return proc(*vals)


def load(filename):
    "Eval every expression from a file."
    repl(None, InPort(open(filename)), None)


def repl(prompt='lispy> ', inport: InPort = InPort(sys.stdin), out=sys.stdout):
    "A prompt-read-eval-print loop."
    sys.stderr.write("Lispy version 2.0\n")
    while True:
        try:
            if prompt:
                sys.stderr.write(prompt)
            x = parse(inport)
            if x is eof_object:
                return
            val = eval(x)
            if val is not None and out:
                print(to_string(val))
        except Exception as e:
            print('%s: %s' % (type(e).__name__, e))


def schemestr(exp):
    if isinstance(exp, List):
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    else:
        return str(exp)


if __name__ == '__main__':
    repl()
