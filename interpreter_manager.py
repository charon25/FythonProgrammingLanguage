from enum import Enum
import re
import sys

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
            raise InterpreterManagerError(f"can't open '{input_path}'.")

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
            raise InterpreterManagerError(f"can't read deltas file '{input_path}'.")

        return deltas

    def read_assembly(self, input_path: str) -> list[str]:
        return self.read_file(input_path).splitlines()

    ### OUTPUT WRITNG
    def write_deltas(self, deltas: list[tuple[int, int]], output_path: str) -> None:
        try:
            with open(output_path, 'w') as fo:
                fo.write("di\tdw\n")
                fo.write("\n".join(f'{di}\t{dw}' for di, dw in deltas))
        except IOError:
            raise InterpreterManagerError(f"can't open output file '{output_path}'.")

    def write_assembly(self, assembly: list[str], output_path: str) -> None:
        try:
            with open(output_path, 'w') as fo:
                fo.write("\n".join(assembly))
        except IOError:
            raise InterpreterManagerError(f"can't open output file '{output_path}'.")


    ### EXECUTION
    def _python_to_deltas(self, input_path: str, output_path: str) -> None:
        python_code = self.read_python(input_path)
        deltas = self.interpreter.python_code_to_deltas(python_code)
        self.write_deltas(deltas, output_path)

    def _python_to_assembly(self, input_path: str, output_path: str) -> None:
        python_code = self.read_python(input_path)
        deltas = self.interpreter.python_code_to_deltas(python_code)
        assembly = self.interpreter.deltas_to_assembly(deltas)
        self.write_assembly(assembly, output_path)

    def _python_to_execute(self, input_path: str) -> None:
        python_code = self.read_python(input_path)
        deltas = self.interpreter.python_code_to_deltas(python_code)
        assembly = self.interpreter.deltas_to_assembly(deltas)
        self.interpreter.execute_assembly(assembly)

    def _deltas_to_deltas(self, input_path: str, output_path: str) -> None:
        deltas = self.read_deltas(input_path)
        self.write_deltas(deltas, output_path)

    def _deltas_to_assembly(self, input_path: str, output_path: str) -> None:
        deltas = self.read_deltas(input_path)
        assembly = self.interpreter.deltas_to_assembly(deltas)
        self.write_assembly(assembly, output_path)

    def _deltas_to_execute(self, input_path: str) -> None:
        deltas = self.read_deltas(input_path)
        assembly = self.interpreter.deltas_to_assembly(deltas)
        self.interpreter.execute_assembly(assembly)

    def _assembly_to_deltas(self, input_path: str, output_path: str) -> None:
        assembly = self.read_assembly(input_path)
        deltas = self.interpreter.assembly_to_deltas(assembly)
        self.write_deltas(deltas, output_path)

    def _assembly_to_assembly(self, input_path: str, output_path: str) -> None:
        assembly = self.read_assembly(input_path)
        self.write_assembly(assembly, output_path)

    def _assembly_to_execute(self, input_path: str) -> None:
        assembly = self.read_assembly(input_path)
        self.interpreter.execute_assembly(assembly)


    def execute(self, input_path: str, output_path: str = None):
        if output_path is None and self.output_type != OutputType.EXECUTE:
            raise InterpreterManagerError(f"no output file provided.")
        if output_path is not None and self.output_type == OutputType.EXECUTE:
            print("main.py: warning: the provided output file is not used.")

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
            if self.interpreter.file_out is sys.stdout:
                print("Program execution:\n==========")
            function(input_path)
            print("\n==========\nExecution complete!")
        else:
            function(input_path, output_path)
            print(f"Conversion from {self.input_type.name} to {self.output_type.name} successful!")
