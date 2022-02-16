

from typing import Any, Protocol
from .environment import Env, StandartEnv
from .parser import tokenize, read_from_tokens
from .evaluator import evaluate


class TextReader(Protocol):
    def read(self) -> str:
        ...


def run_file(source_file: TextReader, env: Env | None = None) -> Any:
    source = source_file.read()
    return run(source)


def run_lines(source: str, env: Env):
    standart_env = StandartEnv()
    if env is not None:
        standart_env.update(env)
    tokens = tokenize(source)
    while tokens:
        exp = read_from_tokens(tokens)
        yield evaluate(exp, standart_env)


def run(source: str, env: Env | None = None):
    for result in run_lines(source, env):
        pass
    return result
