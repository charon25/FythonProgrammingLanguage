import ast
import re
from typing import IO



# The keys are the op code (Delta_I, Delta_w)
# The values are tuples containing:
#   - str: the opcode name
#   - bool: whether or not the opcode needs a number afterwards
#   - int: the default value if the number is not provided
OPCODES: dict[tuple[int, int], tuple[str, bool, int]] = {
    (-1, 1): ('print', True, 1),
    (-1, -1): ('read', True, 1),
    (-1, 2): ('copy', True, 2),
  # (-1, -2): # Unused for now
    (-1, 3): ('jmpz', True, 1),
    (-1, -3): ('jmpnz', True, 1),
    (-1, 4): ('place', True, 1),
    (-1, -4): ('pick', True, 1),

    (1, 1): ('push', True, 0),
    (1, -1): ('pop', True, 1),
    (1, 2): ('add', False, None),
    (1, -2): ('sub', False, None),
    (1, 3): ('mul', False, None),
    (1, -3): ('div', False, None),
    (1, 4): ('mod', False, None),
    (1, -4): ('pow', False, None),
    (1, 5): ('abs', False, None)
}

# Build the inverse dictionary : the string instruction is the key, the tuple opcode is the value
INVERSE_OPCODES: dict[str, tuple[int, int]] = {
    instruction: opcode for opcode, (instruction, _, _) in OPCODES.items()
}


REGEX_INSTRUCTION_NO_ARG = re.compile(r'^\s*([a-z]+)')
REGEX_INSTRUCTION_ARG = re.compile(r'^\s*([a-z]+)\s*(-?[0-9]+)')
REGEX_INDENTATION = re.compile(r'^(\s*)')
REGEX_LITERAL_STR_DOUBLE_QUOTES = re.compile(r'"(?:[^"\\\\]|\\\\[\\s\\S])*"')
REGEX_LITERAL_STR_SINGLE_QUOTES = re.compile(r"'(?:[^'\\\\]|\\\\[\\s\\S])*'")
REGEX_COMMENT = re.compile(r'#[\s\S]*$')


class PythonCodeError(Exception):
    pass

class FythonDivisionByZero(Exception):
    pass

class FythonAssemblyError(Exception):
    pass


class Interpreter:
    def __init__(self, file_out: IO = None, file_in: IO = None, **kwargs) -> None:
        self.file_out = file_out
        self.file_in = file_in

        self.output_format = kwargs.get('output_format', 'char')



    def _print(self, value: int) -> None:
        """Print the provided character to the file_out stream, formatted according to the 'output_format' parameter. If any error occurs during the writing, nothing will happen."""

        if self.file_out is None:
            return

        try:
            if self.output_format == 'char':
                # The value is inside the correct range of the chr function
                if 0 <= value < 0x110000:
                    self.file_out.write(chr(value))
                else:
                    self.file_out.write('�')

            elif self.output_format == 'number':
                self.file_out.write(str(value))
        except Exception:
            pass

    def _input(self) -> int:
        """Read one character from the file_in stream, formatted according to the 'output_format' parameter. If any error occurs, will return 0."""

        if self.file_in is None:
            return 0

        try:
            if self.output_format == 'char':
                return ord(self.file_in.read(1))
            elif self.output_format == 'number':
                return self.file_in.read(1)
        except Exception:
            return 0


    def _get_line_indentation_depth(self, line: str, last_length: int, current_depth: int, previous_lengths: list[int]) -> int:
        indentation: str = REGEX_INDENTATION.findall(line)[0]
        indentation_length = len(indentation.replace("\t", "    ")) # Replace every tab with 4 spaces so the len calculation is accurate

        if indentation_length > last_length:
            previous_lengths.append(indentation_length)
            return (indentation_length, current_depth + 1)
        elif indentation_length < last_length:
            for k, previous_length in enumerate(reversed(previous_lengths)):
                if indentation_length == previous_length:
                    previous_lengths = previous_lengths[:-k]
                    return (indentation_length, current_depth - k)

        return (indentation_length, current_depth)

    def _get_all_matches_regex(self, pattern: re.Pattern, string: str) -> tuple[int, int]:
        previous_end = 0
        while match := pattern.search(string):
            start, end = match.span()
            yield (previous_end + start, previous_end + end)
            string = string[end:]
            previous_end += end


    def _get_line_whitespace_count(self, line: str) -> int:
        line = line.strip()
        line_no_str_literal = line

        # This will replace every string literal by a sequence of period the same length
        # This allows to remove comments without affecting # symbols in strings
        for start, end in self._get_all_matches_regex(REGEX_LITERAL_STR_DOUBLE_QUOTES, line_no_str_literal):
            line_no_str_literal = f'{line_no_str_literal[:start]}{"." * (end - start)}{line_no_str_literal[end:]}'
        for start, end in self._get_all_matches_regex(REGEX_LITERAL_STR_SINGLE_QUOTES, line_no_str_literal):
            line_no_str_literal = f'{line_no_str_literal[:start]}{"." * (end - start)}{line_no_str_literal[end:]}'

        # Find if there is a comment and if yes remove it
        if match := REGEX_COMMENT.search(line_no_str_literal):
            comment_start, _ = match.span()
            line = line[:comment_start]
        
        line = line.strip()
        
        if line == '':
            return None
        
        return len(line.split()) - 1


    def python_code_to_deltas(self, code: str) -> list[tuple[int, int]]:
        try:
            ast.parse(code)
        except Exception:
            raise PythonCodeError("Invalid Python code")

        lines = code.splitlines()
        values: list[tuple[int, int]] = list()

        indentation_length = 0
        indentation_depth = 0
        previous_lengths: list[int] = [0]

        for line in lines:
            # Remove empty lines
            if line.strip() == '':
                continue

            indentation_length, indentation_depth = self._get_line_indentation_depth(line, indentation_length, indentation_depth, previous_lengths)
            whitespace_count = self._get_line_whitespace_count(line)
            # This means the line was only a comment, so remove it
            if whitespace_count is None:
                continue

            values.append((indentation_depth, whitespace_count))

        # This will take successive differences of each element in the tuples
        return [(next_indent - indent, next_whitespace - whitespace) for (indent, whitespace), (next_indent, next_whitespace) in zip(values, values[1:])]



    def _delta_w_modulo_10(self, dw: int) -> int:
        """Compute sign(dw) * (abs(dw) % 10). E.g. 5 => 5, 28 => 28, -3 => -3, -13 => -3, 0 => 0"""
        if dw < 0:
            return -((-dw) % 10)
        return dw % 10


    def deltas_to_assembly(self, deltas: list[tuple[int, int]]) -> list[str]:
        lines = []
        index = 0

        # If any error occurs while reading a tuple, just go to the next one
        while index < len(deltas):
            try:
                di, dw = deltas[index]
            except ValueError: # Not enough or too many elements to unpack
                continue
            try:
                opcode = (di, self._delta_w_modulo_10(dw))
            except TypeError: # dw is not an integer
                continue

            if opcode in OPCODES:
                name, need_number, default_number = OPCODES[opcode]

                if need_number:
                    number, offset = self._construct_number_from_deltas(deltas[index+1:], default_number)
                    lines.append(f'{name} {number}')
                    index += offset

                else:
                    lines.append(name)

            # Comments management
            elif di == 0:
                if dw > 0:
                    index += dw
                elif dw < 0:
                    offset = self._find_block_comment_end(deltas[index+1:])
                    index += offset

            index += 1

        return lines


    def _find_block_comment_end(self, deltas: list[tuple[int, int]]) -> int:
        """Return the offset to the end of the block comment (di == 0, dw < 0)."""

        for offset, (di, dw) in enumerate(deltas):
            if di == 0 and dw < 0:
                return offset + 1
        return len(deltas)

    def _construct_number_from_deltas(self, deltas: list[tuple[int, int]], default_number: int) -> tuple[int, int]:
        """Return the constructed number and how many lines it took."""

        digits = []
        # The variable needs to be declared before hand
        # as if deltas is empty, it will not be declared by the for loop
        offset = 0
        # Loop while the first element of the tuple is 0
        for offset, (di, dw) in enumerate(deltas):
            if di != 0:
                break
            digits.append(dw)
        # If deltas if empty after the loop (ie we did not break)
        # we need to add one to offset, as it could not go pass the last correct value
        else:
            offset += 1

        # There is no number, so return the default
        if len(digits) == 0:
            return (default_number, 0)

        # Special case for zero
        if digits == [0]:
            return (0, 1)

        sign = -1 if digits[0] == 0 else 1
        # Build a number from its digits, with digits < 0 being complemented to 10 (eg -1 => 9)
        value = int(''.join(map(lambda d:str(d) if d >= 0 else str(10 + d), digits)))
        return (sign * value, offset)



    def assembly_to_deltas(self, lines: list[str]) -> list[tuple[int, int]]:
        instructions = self._parse_lines_to_instructions(lines)
        deltas: list[tuple[int, int]] = list()

        for instruction, value in instructions:
            if instruction not in INVERSE_OPCODES:
                raise FythonAssemblyError(f"unknown instruction '{instruction}'.")

            deltas.append(INVERSE_OPCODES[instruction])
            if value is not None:
                deltas.extend(self._number_to_deltas(value))

        return deltas


    def _number_to_deltas(self, n: int) -> list[tuple[int, int]]:
        if n == 0:
            return [(0, 0)]
        
        prefix = [] if n > 0 else [(0, 0)]
        digits = [(0, int(digit)) for digit in str(abs(n))]
        return prefix + digits



    def _parse_lines_to_instructions(self, lines: list[str]) -> list[tuple[str, int]]:
        """Return a list of tuples of the form (instruction, argument) based on the lines specified."""

        instructions: list[tuple[str, int]] = []

        for line in lines:
            if match := REGEX_INSTRUCTION_ARG.findall(line.lower()):
                # match will be of the form [('push', 1)]
                instructions.append((match[0][0], int(match[0][1])))
            elif match := REGEX_INSTRUCTION_NO_ARG.findall(line.lower()):
                # match will be of the form [('add')]
                instructions.append((match[0], None))

        return instructions


    def execute_assembly(self, lines: list[str]) -> tuple[list[int], bool]:
        stack: list[int] = list()
        zero_flag: bool = True
        instruction_pointer = 0

        instructions = self._parse_lines_to_instructions(lines)

        # The incrementation of the instruction pointer is at the bottom of the loop
        while instruction_pointer < len(lines):
            instruction, argument = instructions[instruction_pointer]

            if instruction == 'print':
                for _ in range(argument):
                    if stack: # Check the stack is not empty
                        element = stack.pop()
                        self._print(element)
                        # Zero flag is assigned only if it printed something
                        zero_flag = (element == 0)

            elif instruction == 'read':
                for _ in range(argument):
                    stack.append(self._input())
                # Zero flag is assigned only if it read something
                if argument >= 1:
                    zero_flag = (stack[-1] == 0)

            elif instruction == 'copy':
                # If the stack is empty, copy 0
                if stack:
                    stack.extend([stack.pop()] * argument)
                else:
                    stack = [0] * argument
                # Zero flag is assigned only if it copied something
                if argument >= 1:
                    zero_flag = (stack[-1] == 0)

            elif instruction == 'jmpz':
                if zero_flag:
                    # jmpz 0 go to the next instruction to avoid infinite loop on itself
                    if argument == 0:
                        argument = 1
                    instruction_pointer += argument
                    continue # Continue here so the instruction pointer is not incremented

            elif instruction == 'jmpnz':
                if not zero_flag:
                    # jmpnz 0 go to the next instruction to avoid infinite loop on itself
                    if argument == 0:
                        argument = 1
                    instruction_pointer += argument
                    continue # Continue here so the instruction pointer is not incremented

            elif instruction == 'place':
                if stack:
                    element = stack.pop()
                    # Zero flag is assigned by the moved element
                    zero_flag = (element == 0)

                    # The indexing is reversed compared to Python (L is length of stack) :
                    # arg = 0 corresponds to top of stack (index L of insert) ; arg = 1 corresponds to below top element (index L - 1 of insert)
                    # so index = L - arg
                    # arg = -1 corresponds to bottom of stack (index 0 of insert) ; arg = -2 corresponds to second-to-last element (index 1 of insert)
                    # so index = - (arg + 1)
                    if argument >= 0:
                        index = len(stack) - argument
                    else:
                        index = - argument - 1

                    stack.insert(index, element)
                else: # If the stack is empty, push a 0
                    stack = [0]

            elif instruction == 'pick':
                if stack:
                    # The indexing is reversed compared to Python (L is length of stack) :
                    # arg = 0 corresponds to top of stack (index L - 1 of pop) ; arg = 1 corresponds to below top element (index L - 2 of pop)
                    # so index = L - (arg + 1)
                    # arg = -1 corresponds to bottom of stack (index 0 of pop) ; arg = -2 corresponds to second-to-last element (index 1 of pop)
                    # so index = - (arg + 1)
                    if argument >= 0:
                        index = len(stack) - argument - 1
                    else:
                        index = - argument - 1

                    stack.append(stack.pop(index))
                    # Zero flag is assigned by the moved element
                    zero_flag = (stack[-1] == 0)
                else: # If the stack is empty, push a 0
                    stack = [0]

            elif instruction == 'push':
                stack.append(argument)
                # Zero flag is assigned by the pushed element
                zero_flag = (stack[-1] == 0)

            elif instruction == 'pop':
                # l = l[:-n] removes the last n element from l if n > 0
                if argument > 0:
                    # If the stack have less or as much elements than should be popped, remove them all and raise the zero flag
                    if len(stack) <= argument:
                        stack = []
                        zero_flag = True
                    else:
                        # Zero flag is assigned according to the last poped element, which is at index -arg
                        zero_flag = (stack[-argument] == 0)
                        stack = stack[:-argument]

            elif instruction == 'add':
                # Default values are 0, 0 (picked in this order is the stack does not have enough elements)
                if len(stack) == 0:
                    top, below = 0, 0
                elif len(stack) == 1:
                    top, below = stack.pop(), 0
                else:
                    top, below = stack.pop(), stack.pop()
                stack.append(below + top)
                # For maths operation, zero flag is assigned according to the result
                zero_flag = (stack[-1] == 0)

            elif instruction == 'sub':
                # Default values are 0, 0 (picked in this order is the stack does not have enough elements)
                if len(stack) == 0:
                    top, below = 0, 0
                elif len(stack) == 1:
                    top, below = stack.pop(), 0
                else:
                    top, below = stack.pop(), stack.pop()
                stack.append(below - top)
                # For maths operation, zero flag is assigned according to the result
                zero_flag = (stack[-1] == 0)

            elif instruction == 'mul':
                # Default values are 0, 0 (picked in this order is the stack does not have enough elements)
                if len(stack) == 0:
                    top, below = 0, 0
                elif len(stack) == 1:
                    top, below = stack.pop(), 0
                else:
                    top, below = stack.pop(), stack.pop()
                stack.append(below * top)
                # For maths operation, zero flag is assigned according to the result
                zero_flag = (stack[-1] == 0)

            elif instruction == 'div':
                # Default values are 1, 0 (picked in this order is the stack does not have enough elements)
                if len(stack) == 0:
                    top, below = 1, 0
                elif len(stack) == 1:
                    top, below = stack.pop(), 0
                else:
                    top, below = stack.pop(), stack.pop()
                if top == 0:
                    raise FythonDivisionByZero("division by zero during execution.")
                stack.append(below // top)
                # For maths operation, zero flag is assigned according to the result
                zero_flag = (stack[-1] == 0)

            elif instruction == 'mod':
                # Default values are 1, 0 (picked in this order is the stack does not have enough elements)
                if len(stack) == 0:
                    top, below = 1, 0
                elif len(stack) == 1:
                    top, below = stack.pop(), 0
                else:
                    top, below = stack.pop(), stack.pop()
                if top == 0:
                    raise FythonDivisionByZero("modulo by zero during execution")
                stack.append(below % top)
                # For maths operation, zero flag is assigned according to the result
                zero_flag = (stack[-1] == 0)

            elif instruction == 'pow':
                # Default values are 1, 1 (picked in this order is the stack does not have enough elements)
                if len(stack) == 0:
                    top, below = 1, 1
                elif len(stack) == 1:
                    top, below = stack.pop(), 1
                else:
                    top, below = stack.pop(), stack.pop()
                if top >= 0:
                    stack.append(below ** top)
                else:
                    if below > 1:
                        stack.append(0)
                    elif below == 1:
                        stack.append(1)
                    elif below == 0:
                        raise FythonDivisionByZero("zero to a negative power during execution.")
                    else: # below < 0:
                        stack.append(-1)
                # For maths operation, zero flag is assigned according to the result
                zero_flag = (stack[-1] == 0)

            elif instruction == 'abs':
                if stack:
                    stack.append(abs(stack.pop()))
                else: # If the stack is empty, act as if it had a 0
                    stack = [0]
                # For maths operation, zero flag is assigned according to the result
                zero_flag = (stack[-1] == 0)

            else:
                raise FythonAssemblyError(f"unknown instruction '{instruction}'.")

            instruction_pointer += 1

        return (stack, zero_flag)
