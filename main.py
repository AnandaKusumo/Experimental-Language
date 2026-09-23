import sys

from interpreter import Interpreter
from lexer import Lexer
from parser import Parser


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <source.vent>")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, "r", encoding="utf-8") as file:
            source = file.read()

    except FileNotFoundError:
        print(f"File not found: {filename}")
        sys.exit(1)


    #source code tokens
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    #tokens
    parser = Parser(tokens)
    tree = parser.parse()

    #AST
    interpreter = Interpreter()
    interpreter.run(tree)

if __name__ == "__main__":
    main()