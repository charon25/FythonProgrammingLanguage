import argparse
import re
import sys
from typing import IO

from interpreter import FythonAssemblyError, FythonDivisionByZero, Interpreter, PythonCodeError
from interpreter_manager import InterpreterManager, InterpreterManagerError



def read_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interpreter of the Fython language.")

    parser.add_argument('input_path', help="Path to the interpreter input.")
    parser.add_argument('output_path', nargs='?', help="Path to the interpreter output if it was not executed. The file won't be used if it is.")

    parser.add_argument('--input-type', '-i', choices=['p', 'd', 'a'], default='p', help="Input type. 'p' for Fython code, 'd' for deltas list, 'a' for Fython assembly. Default 'p'.")
    parser.add_argument('--output-type', '-o', choices=['d', 'a', 'e'], default='e', help="Input type. 'd' for deltas list, 'a' for Fython assembly, 'e' for code execution. Default 'e'.")

    parser.add_argument('--program-output', '-O', help="File to write the program output if it was executed. If not provided, will output to stdout.")
    parser.add_argument('--program-input', '-I', help="File to read the program input from if it was executed. If not provided, will use stdin.")

    parser.add_argument('--output-format', '-f', choices=['char', 'number'], default='char', help="The format of the output if the program was executed. 'char' to write chars with corresponding Unicode code, 'number' to write the digits directly. Default 'char'.")

    return parser.parse_args()



def get_program_input(program_input: str) -> IO:
    try:
        if program_input is None:
            return sys.stdin
        return open(program_input, 'r')
    except IOError:
        print(f"main.py: error: could not read program input : '{program_input}'.")
        exit()

def get_program_output(program_output: str) -> IO:
    try:
        if program_output is None:
            return sys.stdout
        return open(program_output, 'w')
    except IOError:
        print(f"main.py: error: could not read program output : '{program_output}'.")
        exit()



if __name__ == '__main__':
    arguments = read_arguments()

    reader = get_program_input(arguments.program_input)
    writer = get_program_output(arguments.program_output)

    interpreter = Interpreter(file_out=writer, file_in=reader, output_format=arguments.output_format)
    manager = InterpreterManager(interpreter, arguments.input_type, arguments.output_type)

    try:
        manager.execute(arguments.input_path, arguments.output_path)
    except (InterpreterManagerError, PythonCodeError, FythonAssemblyError, FythonDivisionByZero) as e:
        print(f"main.py: error: {e}")
    # Catch everything so we can close the file at the end
    except Exception as e:     
        print(f"main.py: unknown error: {e}")
    except KeyboardInterrupt:
        pass

    if reader is not sys.stdin:
        reader.close()
    if writer is not sys.stdout:
        writer.close()
