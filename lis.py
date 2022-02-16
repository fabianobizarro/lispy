import sys
from src.file import run_file
from src.repl import repl


def main(args: list[str]) -> None:
    if len(args) == 1:
        repl()
    else:

        with open(args[1]) as file:
            try:
                run_file(file)
            except Exception as err:
                key = err.args[0]
                print(f'\t {key!r} was not defined')
                cmd = ' '.join(args)
                print('    You can define it as an option:')
                print(f'      $ {cmd} {key}=<value>')


if __name__ == '__main__':
    main(sys.argv)
