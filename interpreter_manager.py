from enum import Enum
import re

from interpreter import Interpreter


class InputType(Enum):
    PYTHON = 'p'
    DELTAS = 'd'
    ASSEMBLY = 'a'

class OutputType(Enum):
    DELTAS = 'd'
    ASSEMBLY = 'a'
    EXECUTE = 'e'


class InterpreterManagerError(Exception):
    pass


class InterpreterManager():
    def __init__(self, interpreter: Interpreter, input_type: str, output_type: str) -> None:
        self.interpreter = interpreter
        self.input_type = InputType(input_type)
        self.output_type = OutputType(output_type)

    ### INPUT READING
    def read_file(self, input_path: str) -> str:
        try:
            with open(input_path, 'r', encoding='utf-8') as fi:
                return fi.read()
        except IOError:
            raise InterpreterManagerError(f"main.py: error: can't open '{input_path}'.")

    def read_python(self, input_path: str) -> str:
        return self.read_file(input_path)

    def read_deltas(self, input_path: str) -> list[tuple[int, int]]:
        lines = self.read_file(input_path).splitlines()

        deltas: list[tuple[int, int]] = list()
        try:
            for line in lines:
                # This regex finds two numbers, possibly negative, separated by anything other that a dash
                if (delta := re.findall(r'(-?[0-9])+[^0-9-]+(-?[0-9])+', line)):
                    di, dw = map(int, delta[0])
                    deltas.append((di, dw))
        except (ValueError, IndexError):
            raise InterpreterManagerError(f"main.py: error: could not read deltas file '{input_path}'.")

        return deltas

    def read_assembly(self, input_path: str) -> list[str]:
        return self.read_file(input_path).splitlines()


    ### EXECUTION

    def _python_to_deltas(self, input_path: str, output_path: str) -> None:
        pass

    def _python_to_assembly(self, input_path: str, output_path: str) -> None:
        pass

    def _python_to_execute(self, input_path: str) -> None:
        pass

    def _deltas_to_deltas(self, input_path: str, output_path: str) -> None:
        pass

    def _deltas_to_assembly(self, input_path: str, output_path: str) -> None:
        pass

    def _deltas_to_execute(self, input_path: str) -> None:
        pass

    def _assembly_to_deltas(self, input_path: str, output_path: str) -> None:
        pass

    def _assembly_to_assembly(self, input_path: str, output_path: str) -> None:
        pass

    def _assembly_to_execute(self, input_path: str) -> None:
        pass


    def execute(self, input_path: str, output_path: str = None):
        if output_path is None and self.output_type != OutputType.EXECUTE:
            raise InterpreterManagerError(f"main.py: error: no output file provided")

        FUNCTIONS_DICT: dict[callable] = {
            (InputType.PYTHON, OutputType.DELTAS): self._python_to_deltas,
            (InputType.PYTHON, OutputType.ASSEMBLY): self._python_to_assembly,
            (InputType.PYTHON, OutputType.EXECUTE): self._python_to_execute,
            (InputType.DELTAS, OutputType.DELTAS): self._deltas_to_deltas,
            (InputType.DELTAS, OutputType.ASSEMBLY): self._deltas_to_assembly,
            (InputType.DELTAS, OutputType.EXECUTE): self._deltas_to_execute,
            (InputType.ASSEMBLY, OutputType.DELTAS): self._assembly_to_deltas,
            (InputType.ASSEMBLY, OutputType.ASSEMBLY): self._assembly_to_assembly,
            (InputType.ASSEMBLY, OutputType.EXECUTE): self._assembly_to_execute,
        }

        function = FUNCTIONS_DICT[(self.input_type, self.output_type)]

        if self.output_type == OutputType.EXECUTE:
            function(input_path)
        else:
            function(input_path, output_path)
