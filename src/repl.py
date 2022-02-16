from distutils.log import error
import traceback
import sys
from typing import Callable, NoReturn
from .exceptions import EvaluatorException, QuitRequestException, UnexpectedCloseParen
from .environment import StandartEnv
from .evaluator import evaluate, s_expr
from .parser import parse

InputFn = Callable[[str], str]

DEBUG_COMMAND = '.d'
QUIT_COMMAND = '.q'
ELLIPSIS = '\N{HORIZONTAL ELLIPSIS}'

PROMPT1 = '\N{WHITE RIGHT-POINTING TRIANGLE}  '
PROMPT2 = '\N{MIDLINE HORIZONTAL ELLIPSIS}    '
ERROR_MARK = '\N{POLICE CARS REVOLVING LIGHT} '

#    multiline_repl(PROMPT1, PROMPT2, ERROR_MARK)


def repl(prompt1: str = PROMPT1,
         prompt2: str = PROMPT2,
         error_mark: str = ERROR_MARK,
         *,
         quit_cmd: str = QUIT_COMMAND,
         input_fn: InputFn = input) -> None:
    "Read-Eval-Print-Loop"

    global_env = StandartEnv()
    debug = True

    print(f'To Exit type {QUIT_COMMAND}', file=sys.stderr)
    print(
        f'To enable/disable debug informations type {DEBUG_COMMAND}', file=sys.stderr)

    while True:
        # ___________________________________________ Read
        try:
            source = multiline_input(prompt1, prompt2,
                                     quit_cmd=quit_cmd,
                                     input_fn=input_fn)
            if source == DEBUG_COMMAND:
                debug = not debug
                print(
                    f'Debug {"enabled" if debug else "disabled"}')
                continue
        except (EOFError, QuitRequestException, KeyboardInterrupt):
            break
        except UnexpectedCloseParen as exc:
            print(error_mark, exc)
            continue
        if not source:
            continue

        # ___________________________________________ Eval
        current_exp = parse(source)

        if debug:
            print('Tokens', current_exp)

        try:
            result = evaluate(current_exp, global_env)
        except EvaluatorException as exc:
            print(error_mark, exc)
            # traceback.print_exc()
            continue
        except LookupError as l:
            print(error_mark, f' \'{l}\' not defined')
            continue
        except Exception as ex:
            # todo: validate this guy
            if (debug):
                traceback.print_exc()

            print(error_mark, ex)
            continue

        # ___________________________________________ Print
        if result is not None:
            print(s_expr(result))


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
            raise QuitRequestException()
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
