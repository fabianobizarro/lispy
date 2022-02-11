import math
import operator as op
from .types import Symbol, Number

class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."

    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var):
        "Find the innermost Env where var appears."
        return self if (var in self) else self.outer.find(var)


class StandartEnv(Env):
    "An environment with some Scheme standard procedures."

    def __init__(self, parms=(), args=(), outer=None):
        super().__init__(parms, args, outer)
        self.update(vars(math))  # sin, cos, sqrt, pi, ...
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
