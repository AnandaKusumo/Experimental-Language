KEYWORDS = {
    # Variable & value
    "let": "LET",  # declare a variable
    "move": "MOVE",  # change the value of a variable

    # Output & program control
    "away": "AWAY",  # exit the program
    "clean": "CLEAN",  # clear the terminal

    # Operations
    "split": "SPLIT",  # split a value into parts
    "conn": "CONN",  # establish a connection

    # Conditional statements
    "where": "WHERE",  # begin a conditional statement
    "otherwise": "OTHERWISE", # alternative branch of a condition

    # Loops
    "reign": "REIGN",  # begin a conditional loop
    "depart": "DEPART",  # break out of a loop
    "proceed": "PROCEED",  # continue to the next iteration
    "wherein": "WHEREIN",  # membership or containment
    "repeat": "REPEAT",  # to begin a loop for as many counts

    # Functions
    "ordain": "ORDAIN",  # define a function
    "yield": "YIELD",  # return a value from a function
    "abide": "ABIDE",  # do nothing and continue
    "lambda": "LAMBDA",  # define an anonymous function

    # Exception handling
    "assay": "ASSAY",  # begin an exception-handling block
    "proclaim": "PROCLAIM",  # raise an exception
    "atlast": "ATLAST",  # execute after an exception-handling block

    # Context & assertions
    "amid": "AMID",  # execute within a managed context
    "affirm": "AFFIRM",  # assert that a condition is true

    # Logical & comparison operators
    "naught": "NAUGHT",  # None
    "ne": "NE",  # logical NOT
    "both": "BOTH",  # logical AND
    "either": "EITHER",  # logical OR
    "be": "BE",  # identity comparison

    # Variables & scope
    "revoke": "REVOKE",  # delete a variable or object reference
    "global": "GLOBAL",  # refer to a global variable
    "nonlocal": "NONLOCAL",  # refer to a variable in an enclosing scope

    # Pattern matching
    "accord": "ACCORD",  # begin pattern matching
    "case": "CASE",  # define a matching case

    # Asynchronous programming
    "unbound": "UNBOUND",  # define an asynchronous function
    "await": "AWAIT",  # wait for an asynchronous operation

    # Source & destination
    "whence": "WHENCE",  # specify a source or origin
    "whither": "WHITHER",  # specify a destination

    # Aliases & miscellaneous
    "as": "AS",  # assign an alternative name

    # Boolean expression
    "truth": "TRUTH", # True
    "nay": "NAY", # False
}

class Token:
    def __init__(self, type_, value, line):
        self.type = type_
        self.value  = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line})"

class Lexer:
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.line = 1
        self.tokens = []

        self.indent_stack = [0]
        self.at_line_start = True

    def tokenize(self):
        while self.position < len(self.source):
            if self.at_line_start:
                self.handle_indentation()

                if self.position >= len(self.source):
                    break

            char = self.source[self.position]

            if char in " \t\r":
                self.position += 1
                continue

            if char == "\n":
                self.line += 1
                self.position += 1
                self.at_line_start = True
                continue

            if char == "#":
                self.skip_comment()
                continue

            if char == '"':
                self.read_string()
                continue

            if char.isdigit():
                self.read_number()
                continue

            if char.isalpha() or char == "_":
                self.read_identifier()
                continue

            if self.position + 1 < len(self.source):
                two_chars = self.source[self.position:self.position + 2]

                if two_chars == "!=":
                    self.tokens.append(Token("NOT_EQUAL", "!=", self.line))
                    self.position += 2
                    continue

                if two_chars == "<=":
                    self.tokens.append(Token("LESS_EQUAL", "<=", self.line))
                    self.position += 2
                    continue

                if two_chars == ">=":
                    self.tokens.append(Token("GREATER_EQUAL", ">=", self.line))
                    self.position += 2
                    continue

                if two_chars == "<-":
                    self.tokens.append(Token("LEFT_ARROW", "<-", self.line))
                    self.position += 2
                    continue

                if two_chars == "->":
                    self.tokens.append(Token("RIGHT_ARROW", "->", self.line))
                    self.position += 2
                    continue

            operators = {
                "=": "EQUAL",
                "+": "PLUS",
                "-": "MINUS",
                "*": "STAR",
                "/": "SLASH",
                "<": "LESS",
                ">": "GREATER",
            }

            if char in operators:
                self.tokens.append(Token(operators[char], char, self.line))
                self.position += 1
                continue

            symbols = {
                "(": "LEFT_PAREN",
                ")": "RIGHT_PAREN",
                "{": "LEFT_BRACE",
                "}": "RIGHT_BRACE",
                "[": "LEFT_BRACKET",
                "]": "RIGHT_BRACKET",
                ",": "COMMA",
                ".": "DOT",
                ":": "COLON"
            }

            if char in symbols:
                self.tokens.append(Token(symbols[char], char, self.line))
                self.position += 1
                continue

            raise SyntaxError(f"Unknown character {char!r} at line {self.line}")

        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(
                Token("DEDENT", None, self.line)
            )

        self.tokens.append(Token("EOF", None, self.line))
        return self.tokens

    def read_string(self):
        self.position += 1

        start = self.position
        value = ""

        while self.position < len(self.source):
            char = self.source[self.position]

            if char == '"':
                self.tokens.append(Token("STRING", value, self.line))
                self.position += 1
                return

            if char == "\\":
                self.position += 1

                if self.position >= len(self.source):
                    break

                escaped = self.source[self.position]

                escapes = {
                    "n": "\n",
                    "t": "\t",
                    '"': '"',
                    "\\": "\\",
                }

                value += escapes.get(escaped, escaped)
                self.position += 1
                continue

            if char == "\n":
                self.line += 1

            value += char
            self.position += 1

        raise SyntaxError(f"Unterminated string at line {self.line}")

    def read_number(self):
        start = self.position

        while (
            self.position < len(self.source)
            and self.source[self.position].isdigit()
        ):
            self.position += 1

        if (
            self.position < len(self.source)
            and self.source[self.position] == "."
            and self.position + 1 < len(self.source)
            and self.source[self.position + 1].isdigit()
        ):
            self.position += 1

            while (
                self.position < len(self.source)
                and self.source[self.position].isdigit()
            ):
                self.position += 1

            value = self.source[start:self.position]
            self.tokens.append(Token("NUMBER", float(value), self.line))

        else:
            value = self.source[start:self.position]
            self.tokens.append(Token("NUMBER", int(value), self.line))

    def read_identifier(self):
        start = self.position

        while self.position < len(self.source):
            char = self.source[self.position]

            if char.isalnum() or char == "_":
                self.position += 1
            else:
                break

        value = self.source[start:self.position]

        token_type = KEYWORDS.get(value, "IDENTIFIER")

        self.tokens.append(Token(token_type, value, self.line))

    def skip_comment(self):
        while (
            self.position < len(self.source) and self.source[self.position] != "\n"
        ):
            self.position += 1

    def handle_indentation(self):
        start = self.position
        spaces = 0

        while self.position < len(self.source):
            char = self.source[self.position]

            if char == " ":
                spaces += 1
                self.position +=1

            elif char == "\t":
                spaces += 4
                self.position += 1

            else:
                break

        if self.position >= len(self.source):
            return

        if self.source[self.position] == "#":
            self.at_line_start = False
            return

        current_indent = self.indent_stack[-1]

        if spaces > current_indent:
            self.indent_stack.append(spaces)
            self.tokens.append(Token("INDENT", spaces, self.line))

        elif spaces < current_indent:
            while (
                len(self.indent_stack) > 1
                and spaces < self.indent_stack[-1]
            ):
                self.indent_stack.pop()
                self.tokens.append(Token("DEDENT", None, self.line))

            if spaces != self.indent_stack[-1]:
                raise IndentationError(f"Unmatched indentation at line {self.line}")

        self.at_line_start = False