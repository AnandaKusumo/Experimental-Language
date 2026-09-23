from parser import (Program, LetStatement, MoveStatement,ReignStatement,IfStatement, DepartStatement, UtterStatement, Literal, Identifier, BinaryExpression, CallExpression)

class BreakSignal(Exception):
    pass

class Interpreter:
    def __init__(self):
        self.environment = {}

    def run(self, program):
        for statement in program.statements:
            self.execute(statement)

    def execute_block(self, statements):
        for statement in statements:
            self.execute(statement)

    def execute(self, statement):
        if isinstance(statement, LetStatement):
            value = self.evaluate(statement.value)
            self.environment[statement.name] = value
            return
        
        if isinstance(statement, MoveStatement):
            if statement.name not in self.environment:
                raise RuntimeError(f"Undefined variable: {statement.name}")
            
            value = self.evaluate(statement.value)
            self.environment[statement.name] = value
            return

        if isinstance(statement, UtterStatement):
            value = self.evaluate(statement.expression)
            print(value)
            return
        
        if isinstance(statement, ReignStatement):
            while self.evaluate(statement.condition):
                try:
                    self.execute_block(statement.body)

                except BreakSignal:
                    break
            return

        if isinstance(statement, DepartStatement):
            raise BreakSignal()

        if isinstance(statement, IfStatement):
            condition = self.evaluate(statement.condition)

            if condition:
                self.execute_block(statement.then_branch)
                return

            for condition, body in statement.elif_branches:
                if self.evaluate(condition):
                    self.execute_block(body)
                    return

            if statement.else_branch is not None:
                self.execute_block(statement.else_branch)

            return

        raise RuntimeError(f"Unknown statement {type(statement).__name__}")

    def evaluate(self, node):
        if isinstance(node, Literal):
            return node.value

        if isinstance(node, Identifier):
            if node.name not in self.environment:
                raise RuntimeError(f"Undefined variable:{node.name}")
            return self.environment[node.name]

        if isinstance(node, BinaryExpression):
            return self.evaluate_binary(node)
        
        if isinstance(node, CallExpression):
            return self.evaluate_call(node)

        raise RuntimeError(f"Unknown expression: {type(node).__name__}")

    def evaluate_binary(self, node):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        if node.operator == "PLUS":
            return left + right

        if node.operator == "MINUS":
            return left - right

        if node.operator == "STAR":
            return left * right

        if node.operator == "SLASH":
            return left / right

        if node.operator == "EQUAL_EQUAL":
            return left == right

        if node.operator == "NOT_EQUAL":
            return left != right

        if node.operator == "LESS":
            return left < right

        if node.operator == "LESS_EQUAL":
            return left <= right

        if node.operator == "GREATER":
            return left > right

        if node.operator == "GREATER_EQUAL":
            return left >= right

        raise RuntimeError(f"Unknown operator: {node.operator}")

    def evaluate_call(self, node):
        if not isinstance(node.callee, Identifier):
            raise RuntimeError("Can only call functions by name.")

        function_name = node.callee.name

        arguments = [self.evaluate(argument) for argument in node.arguments]

        if function_name == "inquire":
            if len(arguments) > 1:
                raise RuntimeError("inquire() takes at most one argument")

            prompt = arguments[0] if arguments else ""

            return input(prompt)

        raise RuntimeError("Undefined function: {function_name}")