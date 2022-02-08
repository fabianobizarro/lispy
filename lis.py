from __future__ import division
from doctest import UnexpectedException
from email.quoprimime import quote
import math
import operator as op
import sys
from typing import Callable, NoReturn
from xmlrpc.client import Boolean
import lis
# from exceptions import UndefinedSymbol, UnexpectedCloseParen, EvaluatorException

# Types

Symbol = str          # A Lisp Symbol is implemented as a Python str
List = list         # A Lisp List is implemented as a Python list
Number = (int, float)  # A Lisp Number is implemented as a Python int or float

# Parsing: parse, tokenize, and read_from_tokens


def parse(program):
    "Read a Scheme expression from a string."
    return read_from_tokens(tokenize(program))


def tokenize(s):
    "Convert a string into a list of tokens."
    return s.replace('(', ' ( ').replace(')', ' ) ').split()


def read_from_tokens(tokens):
    "Read an expression from a sequence of tokens."
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF while reading')
    token = tokens.pop(0)
    if '(' == token:
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)  # pop off ')'
        return L
    elif ')' == token:
        raise SyntaxError('unexpected )')
    else:
        return atom(token)


def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)

# Environments


def standard_env():
    "An environment with some Scheme standard procedures."
    env = Env()
    env.update(vars(math))  # sin, cos, sqrt, pi, ...
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
        'abs':     abs,
        'append':  op.add,
        'apply': lambda proc, args: proc(*args),
        'begin': lambda *x: x[-1],
        'car': lambda x: x[0],
        'cdr': lambda x: x[1:],
        'cons': lambda x, y: [x] + y,
        'eq?':     op.is_,
        'equal?':  op.eq,
        'length':  len,
        'list': lambda *x: list(x),
        'list?': lambda x: isinstance(x, list),
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?': lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env


class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."

    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)


global_env = standard_env()

# Interaction: A REPL

ELLIPSIS = '\N{HORIZONTAL ELLIPSIS}'


def repl(prompt='lis.py> '):
    "A prompt-read-eval-print loop."
    while True:
        val = evaluate(parse(input(prompt)))
        if val is not None:
            print(lispstr(val))


def lispstr(exp):
    "Convert a Python object back into a Lisp-readable string."
    if isinstance(exp, List):
        return '(' + ' '.join(map(lispstr, exp)) + ')'
    else:
        return str(exp)


class EvaluatorException(Exception):
    pass


class UnexpectedCloseParen(Exception):
    pass


QUIT_COMMAND = '.q'
InputFn = Callable[[str], str]


class QuitRequest(Exception):
    """Signal to quit multi-line input."""


def multiline_input(prompt1: str,
                    prompt2: str,
                    *,
                    quit_cmd: str = QUIT_COMMAND,
                    input_fn: InputFn = input) -> str:

    paren_cnt = 0
    lines = []
    prompt = prompt1
    while True:
        line = input_fn(prompt).rstrip()
        if line == quit_cmd:
            raise QuitRequest()
        for char in line:
            if char == '(':
                paren_cnt += 1
            elif char == ')':
                paren_cnt -= 1
            if paren_cnt < 0:
                raise_unexpected_paren(line)
        lines.append(line)
        prompt = prompt2
        if paren_cnt == 0:
            break

    return '\n'.join(lines)


def raise_unexpected_paren(line: str) -> NoReturn:
    max_msg_len = 16
    if len(line) < max_msg_len:
        msg = line
    else:
        msg = ELLIPSIS + line[-(max_msg_len-1):]
    raise UnexpectedCloseParen(msg)


def multiline_repl(prompt1: str = '> ',
                   prompt2: str = '... ',
                   error_mark: str = '***',
                   *,
                   quit_cmd: str = QUIT_COMMAND,
                   input_fn: InputFn = input) -> None:
    "Read-Eval-Print-Loop"

    print(f'To Exit type {QUIT_COMMAND}', file=sys.stderr)

    while True:
        # ___________________________________________ Read
        try:
            source = multiline_input(prompt1, prompt2,
                                     quit_cmd=quit_cmd,
                                     input_fn=input_fn)
        except (EOFError, QuitRequest):
            break
        except UnexpectedCloseParen as exc:
            print(error_mark, exc)
            continue
        if not source:
            continue

        # ___________________________________________ Eval
        current_exp = lis.parse(source)
        try:
            result = lis.evaluate(current_exp, global_env)
        except EvaluatorException as exc:
            print(error_mark, exc)
            continue

        # ___________________________________________ Print
        if result is not None:
            print(s_expr(result))


def s_expr(obj: object) -> str:
    "Convert Python object into Lisp s-expression."
    if obj == True:
        return '#t'
    elif obj == False:
        return '#f'
    elif isinstance(obj, list):
        items = ' '.join(s_expr(x) for x in obj)
        return f'({items})'
    elif isinstance(obj, Symbol):
        return obj
    else:
        return repr(obj)
    # match obj:
    #     case True:
    #         return '#t'
    #     case False:
    #         return '#f'
    #     case list(obj):
    #         items = ' '.join(s_expr(x) for x in obj)
    #         return f'({items})'
    #     case lis.Symbol(x):
    #         return x
    #     case _:
    #         return repr(obj)


# Procedures

# def s_expr(obj: object) -> str:
#     "Convert Python object into Lisp s-expression."
#     match obj:
#         case True:
#             return '#t'
#         case False:
#             return '#f'
#         case list(obj):
#             items = ' '.join(s_expr(x) for x in obj)
#             return f'({items})'
#         case lis.Symbol(x):
#             return x
#         case _:
#             return repr(obj)


class Procedure(object):
    "A user-defined Scheme procedure."

    def __init__(self, parms, body, env):
        self.parms, self.body, self.env = parms, body, env

    def __call__(self, *args):
        return evaluate(self.body, Env(self.parms, args, self.env))

# eval


def evaluate(x, env=global_env):
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol):      # variable reference
        return env.find(x)[x]
    elif not isinstance(x, List):  # constant literal
        return x
    elif x[0] == 'quote':          # (quote exp)
        (_, exp) = x
        return exp
    elif x[0] == 'if':             # (if test conseq alt)
        (_, test, conseq, alt) = x
        exp = (conseq if evaluate(test, env) else alt)
        return evaluate(exp, env)
    elif x[0] == 'define':         # (define var exp)
        (_, var, exp) = x
        env[var] = evaluate(exp, env)
    elif x[0] == 'set!':           # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = evaluate(exp, env)
    elif x[0] == 'lambda':         # (lambda (var...) body)
        (_, parms, body) = x
        return Procedure(parms, body, env)
    else:                          # (proc arg...)
        proc = evaluate(x[0], env)
        args = [evaluate(exp, env) for exp in x[1:]]
        return proc(*args)


PROMPT1 = '\N{WHITE RIGHT-POINTING TRIANGLE}  '
PROMPT2 = '\N{MIDLINE HORIZONTAL ELLIPSIS}    '
ERROR_MARK = '\N{POLICE CARS REVOLVING LIGHT} '


if __name__ == '__main__':
    # repl()
    multiline_repl(PROMPT1, PROMPT2, ERROR_MARK)
