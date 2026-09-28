import sys

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser

VERSION = "0.1.0"

def run_source(source, interpreter):
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    program = parser.parse()

    interpreter.run(program)

def run_file(filename):
    try:
        with open(filename, "r", encoding="utf-8") as file:
            source = file.read()

        interpreter = Interpreter()
        run_source(source, interpreter)

    except FileNotFoundError:
        print(f"Venturis: file not found: {filename}")

    except Exception as error:
        print(f"Venturis error: {error}")

def repl():
    print(f"Venturis version: {VERSION}")
    print("Interactive mode.")
    print("Type 'exit' or press Ctrl+C to leave.")
    print()

    interpreter = Interpreter()

    while True:
        try:
            source = input(">>> ")

            if source.strip() == "exit":
                break

            if not source.strip():
                continue

            run_source(source, interpreter)

        except KeyboardInterrupt:
            print()
            break

        except EOFError:
            print()
            break

        except Exception as error:
            print(f"Venturis error: {error}")

def main():
    if len(sys.argv) == 1:
        repl()
        return

    if len(sys.argv) == 2:
        argument = sys.argv[1]

        if argument in ("--version", "-v"):
            print(f"Venturis {VERSION}")
            return

        if argument in ("--help", "-h"):
            print("Usage:")
            print(" venturis                Start interactive mode")
            print(" venturis <file.vent>    Run a Venturis source file")
            print(" venturis --version      Show version")
            print(" venturis --help         Show this help")
            return

        run_file(argument)
        return

    print("Venturis: too many arguments.")
    print("Use 'venturis --help' for usage.")

if __name__ == "__main__":
    main()