

# Types

Symbol = str          # A Lisp Symbol is implemented as a Python str
List = list         # A Lisp List is implemented as a Python list
Number = (int, float)  # A Lisp Number is implemented as a Python int or float

# Exp = Union[Symbol, Exp]


def atom(token):
    "Numbers become numbers; every other token is a symbol."
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)
