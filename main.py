import argparse
import re
import sys
from typing import IO

from interpreter import Interpreter
from interpreter_manager import InterpreterManager


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

### === READING INPUT === ###

def read_file(input_path: str) -> str:
    try:
        with open(input_path, 'r', encoding='utf-8') as fi:
            return fi.read()
    except IOError:
        print(f"main.py: error: argument input_path: can't open '{input_path}'.")
        exit()

def read_python(input_path: str) -> str:
    return read_file(input_path)

def read_deltas(input_path: str) -> list[tuple[int, int]]:
    lines = read_file(input_path).splitlines()

    deltas: list[tuple[int, int]] = list()
    try:
        for line in lines:
            # This regex finds two numbers, possibly negative, seperated by anything other that a dash
            if (delta := re.findall(r'(-?[0-9])+[^0-9-]+(-?[0-9])+', line)):
                di, dw = map(int, delta[0])
                deltas.append((di, dw))
    except (ValueError, IndexError):
        print(f"main.py: error: could not read deltas file '{input_path}'.")
        exit()

    return deltas

def read_assembly(input_path: str) -> list[str]:
    return read_file(input_path).splitlines()

#############################

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

#############################

if __name__ == '__main__':
    arguments = read_arguments()
    print(arguments)

    reader = get_program_input(arguments.program_input)
    writer = get_program_output(arguments.program_output)

    interpreter = Interpreter(file_out=writer, file_in=reader, output_format=arguments.output_format)
    manager = InterpreterManager(interpreter, arguments.input_type, arguments.output_type)

    if reader is not sys.stdin:
        reader.close()
    if writer is not sys.stdout:
        writer.close()
