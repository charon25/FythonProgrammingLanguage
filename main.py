import argparse
import sys


def read_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interpreter of the Fython language.")

    parser.add_argument('input_path', help="Path to the interpreter input.", type=argparse.FileType('r', encoding='utf-8'))
    parser.add_argument('output_path', nargs='?', help="Path to the interpreter output if it was not executed. The file won't be used if it is.", type=argparse.FileType('w', encoding='utf-8'))

    parser.add_argument('--input-type', '-i', choices=['p', 'd', 'a'], default='p', help="Input type. 'p' for Fython code, 'd' for deltas list, 'a' for Fython assembly. Default 'p'.")
    parser.add_argument('--output-type', '-o', choices=['d', 'a', 'e'], default='e', help="Input type. 'd' for deltas list, 'a' for Fython assembly, 'e' for code execution. Default 'e'.")

    parser.add_argument('--program-output', '-O', type=argparse.FileType('r', encoding='utf-8'), default=sys.stdout, help="File to write the program output if it was executed. If not provided, will output to stdout.")
    parser.add_argument('--program-input', '-I', type=argparse.FileType('w', encoding='utf-8'), default=sys.stdin, help="File to read the program input from if it was executed. If not provided, will use stdin.")

    parser.add_argument('--output-format', '-f', choices=['char', 'number'], default='char', help="The format of the output if the program was executed. 'char' to write chars with corresponding Unicode code, 'number' to write the digits directly. Default 'char'.")

    return parser.parse_args()



if __name__ == '__main__':
    print(read_arguments())
