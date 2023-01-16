from enum import Enum
from interpreter import Interpreter


class InputType(Enum):
    PYTHON = 'p'
    DELTAS = 'd'
    ASSEMBLY = 'a'

class OutputType(Enum):
    DELTAS = 'd'
    ASSEMBLY = 'a'
    EXECUTE = 'e'


class InterpreterManager():
    def __init__(self, interpreter: Interpreter, input_type: str, output_type: str) -> None:
        self.interpreter = interpreter
        self.input_type = InputType(input_type)
        self.output_type = OutputType(output_type)


    def execute(self):
        pass
