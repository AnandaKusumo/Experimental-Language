from parser import (Program, LetStatement, MoveStatement,ReignStatement, WhereStatement, RepeatStatement, DepartStatement, ProceedStatement, UtterStatement, OrdainStatement, YieldStatement, Literal, ListLiteral, Identifier, BinaryExpression, IndexExpression, SliceExpression, CallExpression, ExpressionStatement, UnaryExpression)

class BreakSignal(Exception):
    pass

class ContinueSignal(Exception):
    pass

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class Environment:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def define(self, name, value):
        self.values[name]= value

    def get(self, name):
        if name in self.values:
            return self.values[name]

        if self.parent is not None:
            return self.parent.get(name)

        raise RuntimeError(f"Undefined Variable: {name}")

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
            return

        if self.parent is not None:
            self.parent.assign(name, value)
            return

        raise RuntimeError(f"Undefined variable: {name}")

class VenturisFunction:
    def __init__(self, name, parameters, body, interpreter):
        self.name = name
        self.parameters = parameters
        self.body = body
        self.interpreter = interpreter

    def call(self, arguments):
        if len(arguments) != len(self.parameters):
            raise RuntimeError(
                f"{self.name}() expects "
                f"{len(self.parameters)} argument(s), "
                f"got {len(arguments)}."
            )

        previous_environment = self.interpreter.environment

        local_environment = Environment(parent=previous_environment)

        for parameter, argument in zip(self.parameters, arguments):
            local_environment.define(parameter, argument)

        self.interpreter.environment = local_environment

        try:
            self.interpreter.execute_block(self.body)

        except ReturnSignal as signal:
            return signal.value
        
        finally:
            self.interpreter.environment = previous_environment

        return None

class Interpreter:
    def __init__(self):
        self.environment = Environment()

    def run(self, program):
        for statement in program.statements:
            self.execute(statement)

    def execute_block(self, statements):
        for statement in statements:
            self.execute(statement)

    def execute(self, statement):
        if isinstance(statement, LetStatement):
            value = self.evaluate(statement.value)
            self.environment.define(statement.name, value)
            return
        
        if isinstance(statement, MoveStatement):
            value = self.evaluate(statement.value)
            self.environment.assign(statement.name, value)
            return

        if isinstance(statement, OrdainStatement):
            function = VenturisFunction(
                statement.name,
                statement.parameters,
                statement.body,
                self
            )

            self.environment.define(statement.name, function)
            return

        if isinstance(statement, YieldStatement):
            if statement.expression is None:
                raise ReturnSignal(None)

            value = self.evaluate(statement.expression)
            raise ReturnSignal(value)

        if isinstance(statement, UtterStatement):
            value = self.evaluate(statement.expression)
            print(value)
            return
        
        if isinstance(statement, ReignStatement):
            while self.evaluate(statement.condition):
                try:
                    self.execute_block(statement.body)

                except ContinueSignal:
                    continue

                except BreakSignal:
                    break
            return

        if isinstance(statement, RepeatStatement):
            count = self.evaluate(statement.count)

            if not isinstance(count, int):
                raise RuntimeError("repeat() expects an integer.")

            if count < 0:
                raise RuntimeError("repeat() expects a non-negative integer.")

            for _ in range(count):
                try:
                    self.execute_block(statement.body)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break

            return

        if isinstance(statement, DepartStatement):
            raise BreakSignal()
        
        if isinstance(statement, ProceedStatement):
            raise ContinueSignal()

        if isinstance(statement, WhereStatement):
            if self.evaluate(statement.condition):
                self.execute_block(statement.then_branch)
                return

            for condition, body in statement.otherwise_branches:
                if self.evaluate(condition):
                    self.execute_block(body)
                    return

            if statement.else_branch is not None:
                self.execute_block(statement.else_branch)

            return

        if isinstance(statement, ExpressionStatement):
            self.evaluate(statement.expression)
            return

        raise RuntimeError(f"Unknown statement {type(statement).__name__}")

    def evaluate(self, node):
        if isinstance(node, Literal):
            return node.value

        if isinstance(node, Identifier):
            return self.environment.get(node.name)

        if isinstance(node, ListLiteral):
            return [self.evaluate(element) for element in node.elements]

        if isinstance(node, BinaryExpression):
            return self.evaluate_binary(node)

        if isinstance(node, IndexExpression):
            object_ = self.evaluate(node.object)
            index = self.evaluate(node.index)

            return object_[index]

        if isinstance(node, SliceExpression):
            object_ = self.evaluate(node.object)

            start = (self.evaluate(node.start) if node.start is not None else None)

            end = (self.evaluate(node.end) if node.end is not None else None)

            return object_[start:end]
        
        if isinstance(node, CallExpression):
            return self.evaluate_call(node)

        if isinstance(node, UnaryExpression):
            value = self.evaluate(node.expression)

            if node.operator == "NE":
                return not value

            raise RuntimeError(f"Unknown unary operator: {node.operator}")

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

        if node.operator == "BE":
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

        if node.operator == "BOTH":
            return left and right

        if node.operator == "EITHER":
            return left or right

        raise RuntimeError(f"Unknown operator: {node.operator}")

    def evaluate_call(self, node):
        if not isinstance(node.callee, Identifier):
            raise TypeError("Can only call functions by name.")

        function_name = node.callee.name

        arguments = [self.evaluate(argument) for argument in node.arguments]

        if function_name == "inquire":
            if len(arguments) > 1:
                raise RuntimeError("inquire() takes at most one argument")

            prompt = arguments[0] if arguments else ""

            return input(prompt)
        
        if function_name == "whole":
            if len(arguments) != 1:
                raise RuntimeError("whole() expects exactly one argument")

            return int(arguments[0])

        try:
            function = self.environment.get(function_name)
        except RuntimeError:
            raise RuntimeError(f"Undefined function: {function_name}")

        if not isinstance(function, VenturisFunction):
            raise TypeError(f"{function_name} is not a function")

        return function.call(arguments)