class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements!r})"

class LetStatement(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"LetStatement({self.name!r}, {self.value!r})"

class MoveStatement(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return f"MoveStatement({self.name!r}, {self.value!r})"

class ReignStatement(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return (
            f"ReignStatement("
            f"{self.condition!r}, "
            f"{self.body!r})"
        )

class RepeatStatement(ASTNode):
    def __init__(self, count, body):
        self.count = count
        self.body = body

    def __repr__(self):
        return (
            f"RepeatStatement("
            f"{self.count!r},"
            f"{self.body!r}"
        )

class WhereStatement(ASTNode):
    def __init__(self, condition, then_branch, otherwise_branches=None, else_branch=None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
        self.otherwise_branches = otherwise_branches or []

    def __repr__(self):
        return (
            f"WhereStatement("
            f"{self.condition!r}"
            f"{self.then_branch!r}"
            f"{self.otherwise_branches!r}"
            f"{self.else_branch!r})"
        )

class OrdainStatement(ASTNode):
    def __init__(self, name, parameters, body):
        self.name = name
        self.parameters = parameters
        self.body = body

    def __repr__(self):
        return (
            f"OrdainStatement("
            f"{self.name!r},"
            f"{self.parameters!r},"
            f"{self.body!r})"
        )

class DepartStatement(ASTNode):
    def __repr__(self):
        return "DepartStatement()"

class ProceedStatement(ASTNode):
    def __repr__(self):
        return "ProceedStatement()"

class YieldStatement(ASTNode):
    def __init__(self, expression=None):
        self.expression = expression

    def __repr__(self):
        return f"YieldStatement({self.expression!r})"

class Literal(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Literal({self.value!r})"

class ListLiteral(ASTNode):
    def __init__(self, elements):
        self.elements = elements

    def __repr__(self):
        return f"ListLiteral({self.elements!r})"

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name!r})"

class BinaryExpression(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return (
            f"BinaryExpression("
            f"{self.left!r}, "
            f"{self.operator!r}, "
            f"{self.right!r}) "
        )

class ExpressionStatement(ASTNode):
    def __init__(self, expression):
        self.expression = expression

    def __repr__(self):
        return f"ExpressionStatement({self.expression!r})"

class CallExpression(ASTNode):
    def __init__(self, callee, arguments):
        self.callee = callee
        self.arguments = arguments

    def __repr__(self):
        return (
            f"CallExpression("
            f"{self.callee!r}"
            f"{self.arguments!r})"
        )

class IndexExpression(ASTNode):
    def __init__(self, object_, index):
        self.object = object_
        self.index = index

    def __repr__(self):
        return (
            f"IndexExpression("
            f"{self.object!r},"
            f"{self.index!r})"
        )
    
class SliceExpression(ASTNode):
    def __init__(self, object_, start, end):
        self.object = object_
        self.start = start
        self.end = end

    def __repr__(self):
        return (
            f"SliceExpression("
            f"{self.object!r},"
            f"{self.start!r},"
            f"{self.end!r})"
        )

class UnaryExpression(ASTNode):
    def __init__(self, operator, expression):
        self.operator = operator
        self.expression = expression

    def __repr__(self):
        return (
            f"UnaryExpression("
            f"{self.operator!r},"
            f"{self.expression!r}"
        )

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def parse(self):
        statements = []

        while not self.check("EOF"):
            statements.append(self.statement())

        return Program(statements)

    def statement(self):
        if self.match("LET"):
            return self.let_statement()

        if self.match("MOVE"):
            return self.move_statement()

        if self.match("ORDAIN"):
            return self.ordain_statement()

        if self.match("YIELD"):
            return self.yield_statement()
        
        if self.match("REIGN"):
            return self.reign_statement()
        
        if self.match("WHERE"):
            return self.where_statement()
        
        if self.match("REPEAT"):
            return self.repeat_statement()
        
        if self.match("DEPART"):
            return DepartStatement()
        
        if self.match("PROCEED"):
            return ProceedStatement()

        return ExpressionStatement(self.expression())

    def block(self):
        self.consume("COLON", "Expected  ':' after statement.")

        self.consume("INDENT", "Expected indented block.")

        statements = []

        while not self.check("DEDENT", "EOF"):
            statements.append(self.statement())

        self.consume("DEDENT", "Expected end of block.")

        return statements

    def let_statement(self):
        name = self.consume(
            "IDENTIFIER",
            "Expected variable name after 'let'."
        )

        self.consume(
            "LEFT_ARROW",
            "Expected '<-' after variable name."
        )

        value = self.expression()

        return LetStatement(
            name.value,
            value
        )

    def move_statement(self):
        name = self.consume(
            "IDENTIFIER",
            "Expected variable name after 'move'."
        )

        self.consume(
            "RIGHT_ARROW",
            "Expected '->' after variable name."
        )

        value = self.expression()
        return MoveStatement(name.value, value)

    def reign_statement(self):
        condition = self.expression()
        body = self.block()

        return ReignStatement(condition, body)

    def yield_statement(self):
        if self.check("DEDENT", "EOF"):
            return YieldStatement()
        
        expression = self.expression()
        return YieldStatement(expression)

    def where_statement(self):
        condition = self.expression()
        then_branch = self.block()

        otherwise_branches = []
        else_branch = None

        while self.match("OTHERWISE"):
            if self.match("WHERE"):
                otherwise_condition = self.expression()
                otherwise_body = self.block()
                otherwise_branches.append((otherwise_condition, otherwise_body))
            else:
                else_branch = self.block()
                break

        return WhereStatement(condition, then_branch, otherwise_branches, else_branch)

    def repeat_statement(self):
        self.consume(
            "LEFT_PAREN",
            "Expected '(' after repeat."
        )

        count = self.expression()

        self.consume(
            "RIGHT_PAREN",
            "Expected ')' after repeat count."
        )

        body = self.block()

        return RepeatStatement(count, body)

    def ordain_statement(self):
        name = self.consume(
            "IDENTIFIER",
            "Expected function name after 'ordain'."
        )

        self.consume(
            "LEFT_PAREN",
            "Expected '(' after function name."
        )

        parameters = []

        if not self.check("RIGHT_PAREN"):
            parameters.append(
                self.consume(
                    "IDENTIFIER",
                    "Expected parameter name"
                ).value
            )

            while self.match("COMMA"):
                parameters.append(
                    self.consume(
                        "IDENTIFIER",
                        "Expected parameter name after ','."
                    ).value
                )

        self.consume(
            "RIGHT_PAREN",
            "Expected ')' after parameters"
        )

        body = self.block()

        return OrdainStatement(name.value, parameters, body)

    def expression(self):
        return self.either()

    def either(self):
        expression = self.both()

        while self.match("EITHER"):
            right = self.both()
            expression = BinaryExpression(expression, "EITHER", right)

        return expression

    def both(self):
        expression = self.negation()

        while self.match("BOTH"):
            right = self.negation()
            expression = BinaryExpression(expression, "BOTH", right)

        return expression

    def negation(self):
        if self.match("NE"):
            expression = self.negation()
            return UnaryExpression("NE", expression)

        return self.comparison()

    def comparison(self):
        expression = self.term()

        while self.check(
            "BE",
            "NOT_EQUAL",
            "LESS",
            "LESS_EQUAL",
            "GREATER",
            "GREATER_EQUAL",
        ):

            operator = self.advance()
            right = self.term()

            expression = BinaryExpression(expression, operator.type, right)

        return expression

    def term(self):
        expression = self.factor()

        while self.check("PLUS", "MINUS"):
            operator = self.advance()
            right = self.factor()

            expression = BinaryExpression(expression, operator.type, right)

        return expression

    def factor(self):
        expression = self.primary()

        while self.check("STAR", "SLASH"):
            operator = self.advance()
            right = self.primary()

            expression = BinaryExpression(expression, operator.type, right)

        return expression

    def primary(self):
        if self.match("NUMBER"):
            return Literal(self.previous().value)

        if self.match("STRING"):
            return Literal(self.previous().value)

        if self.match("TRUTH"):
            return Literal(True)

        if self.match("NAY"):
            return Literal(False)

        if self.match("NAUGHT"):
            return Literal(None)

        if self.match("LEFT_BRACKET"):
            elements = []

            if not self.check("RIGHT_BRACKET"):
                elements.append(self.expression())

                while self.match("COMMA"):
                    elements.append(self.expression())

            self.consume(
                "RIGHT_BRACKET",
                "Expected ']' after list."
            )

            expression = ListLiteral(elements)

        elif self.match("IDENTIFIER"):
            expression = Identifier(self.previous().value)

        elif self.match("LEFT_PAREN"):
            expression = self.expression()

            self.consume(
                "RIGHT_PAREN",
                "Expected ')' after expression."
            )

        else:
            raise SyntaxError(
                f"Expected expression, got"
                f"{self.current().type} "
                f"at line {self.current().line}"
            )

        while True:
            if self.match("LEFT_PAREN"):
                arguments = []

                if not self.check("RIGHT_PAREN"):
                    arguments.append(self.expression())

                    while self.match("COMMA"):
                        arguments.append(self.expression())

                self.consume(
                    "RIGHT_PAREN",
                    "Expected ')' after arguments."
                )

                expression = CallExpression(expression, arguments)

            elif self.match("LEFT_BRACKET"):
                start = None
                end = None

                if not self.check("COLON", "RIGHT_BRACKET"):
                    start = self.expression()

                if self.match("COLON"):
                    if not self.check("RIGHT_BRACKET"):
                        end = self.expression()

                    expression = SliceExpression(expression, start, end)

                else:
                    expression = IndexExpression(expression, start)

                self.consume(
                    "RIGHT_BRACKET",
                    "Expected ']' after index or slice."
                )

            else:
                break

        return expression

    def match(self, *types):
        if self.check(*types):
            self.advance()
            return True

        return False

    def check(self, *types):
        return self.current().type in types

    def advance(self):
        if not self.check("EOF"):
            self.position += 1
        return self.previous()

    def consume(self, token_type, message):
        if self.check(token_type):
            return self.advance()

        raise SyntaxError(
            f"{message} "
            f"Got {self.current().type} "
            f"at line {self.current().line}"
        )

    def current(self):
        return self.tokens[self.position]

    def previous(self):
        return self.tokens[self.position - 1]