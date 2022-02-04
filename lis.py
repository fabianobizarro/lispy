import math
from mimetypes import init
import operator as op
from typing import Dict, Union

# =============== Types ============

Symbol = str
List = list
Number = (int, float)
Exp = Union[Symbol, List]


def atom(token: str):
    "Numbers become numbers; every other token is a symbol"
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


class Procedure(object):
    "A user-defined Scheme procedure"

    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env

    def __call__(self, *args: any):
        return eval(self.body, Env(self.parms, args, self.env))


# ==================================

# ========= Environment ============
class Env(dict):

    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        "Find the inhermost Env where var appears"
        return self if(var in self) else self.outer.find(var)


class StandarEnv(Env):
    "Standard environment"

    def __init__(self, parms=(), args=(), outer=None):
        super().__init__(parms, args, outer)
        self.update(vars(math))
        self.update({
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


def _standard_env() -> Env:
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

# ====================================


# ================== Parser ======================

def tokenize(chars: str) -> list:
    "Convert a string of characters into a list of tokens"
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()


def parse(program: str):
    "Read a Scheme expression from a string"
    return read_from_tokens(tokenize(program))


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

# ==========================================


def eval(x: Exp, env: Env):
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


def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop"
    env = StandarEnv()
    while True:
        val = eval(parse(input(prompt)), env)
        if val is not None:
            print(schemestr(val))


def schemestr(exp):
    if isinstance(exp, List):
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    else:
        return str(exp)


if __name__ == '__main__':
    repl()
