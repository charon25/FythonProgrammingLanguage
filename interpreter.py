import re
import sys
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


REGEX_INSTRUCTION_NO_ARG = re.compile(r'^\s*([a-z]+)')
REGEX_INSTRUCTION_ARG = re.compile(r'^\s*([a-z]+)\s*(-?[0-9]+)')


class Interpreter:
    def __init__(self, file_out: IO = None, file_in: IO = None, **kwargs) -> None:
        self.stack: list[int] = []
        self.zero_flag: bool = True

        self.file_out = file_out
        if self.file_out is None:
            self.file_out = sys.stdout

        self.file_in = file_in
        if self.file_in is None:
            self.file_in = sys.stdin



    def _print(self, char: int) -> None:
        """Print the provided character to the file_out stream, formatted according to the interpreter parameters."""
        # TODO : mettre à jour
        self.file_out.write(str(char))

    def _input(self) -> int:
        """Read one character from the file_in stream, formatted according to the interpreter parameters."""

        # TODO : mettre à jour
        return self.file_in.read(1)


    def _delta_w_modulo_10(self, dw: int) -> int:
        """Compute sign(dw) * (abs(dw) % 10). E.g. 5 => 5, 28 => 28, -3 => -3, -13 => -3, 0 => 0"""
        if dw < 0:
            return -((-dw) % 10)
        return dw % 10


    def _deltas_to_assembly(self, deltas: list[tuple[int, int]]) -> list[str]:
        lines = []
        # TODO : gestion erreur si deltas pas liste de tuples
        index = 0
        while index < len(deltas):
            di, dw = deltas[index]
            opcode = (di, self._delta_w_modulo_10(dw))

            if opcode in OPCODES:
                name, need_number, default_number = OPCODES[opcode]

                if need_number:
                    number, offset = self._construct_number(deltas[index+1:], default_number)
                    lines.append(f'{name} {number}')
                    index += offset

                else:
                    lines.append(name)
            index += 1

        return lines


    def _construct_number(self, deltas: list[tuple[int, int]], default_number: int) -> tuple[int, int]:
        digits = []
        # The variable needs to be declared before hand
        # as if deltas is empty, it will not be declared by the for loop
        offset = 0
        # Loop while the first element of the tuple is 0
        for offset, (di, dn) in enumerate(deltas):
            if di != 0:
                break
            digits.append(dn)
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


    def _execute(self, lines: list[str]) -> None:
        self.stack: list[int] = list()
        self.zero_flag: bool = True
        instruction_pointer = 0

        instructions = self._parse_lines_to_instructions(lines)

        # The incrementation of the instruction pointer is at the bottom of the loop
        while instruction_pointer < len(lines):
            instruction, argument = instructions[instruction_pointer]

            if instruction == 'print':
                for _ in range(argument):
                    if self.stack: # Check the stack is not empty
                        element = self.stack.pop()
                        self._print(element)
                        # Zero flag is assigned only if it printed something
                        self.zero_flag = (element == 0)

            elif instruction == 'read':
                for _ in range(argument):
                    self.stack.append(self._input())
                # Zero flag is assigned only if it read something
                if argument >= 1:
                    self.zero_flag = (self.stack[-1] == 0)

            elif instruction == 'copy':
                # If the stack is empty, copy 0
                if self.stack:
                    self.stack.extend([self.stack.pop()] * argument)
                else:
                    self.stack = [0] * argument
                # Zero flag is assigned only if it copied something
                if argument >= 1:
                    self.zero_flag = (self.stack[-1] == 0)

            elif instruction == 'jmpz':
                if self.zero_flag:
                    # jmpz 0 go to the next instruction to avoid infinite loop on itself
                    if argument == 0:
                        argument = 1
                    instruction_pointer += argument
                    continue # Continue here so the instruction pointer is not incremented

            elif instruction == 'jmpnz':
                if not self.zero_flag:
                    # jmpnz 0 go to the next instruction to avoid infinite loop on itself
                    if argument == 0:
                        argument = 1
                    instruction_pointer += argument
                    continue # Continue here so the instruction pointer is not incremented

            elif instruction == 'place':
                if self.stack:
                    element = self.stack.pop()
                    # Zero flag is assigned by the moved element
                    self.zero_flag = (element == 0)

                    # The indexing is reversed compared to Python (L is length of stack) :
                    # arg = 0 corresponds to top of stack (index L of insert) ; arg = 1 corresponds to below top element (index L - 1 of insert)
                    # so index = L - arg
                    # arg = -1 corresponds to bottom of stack (index 0 of insert) ; arg = -2 corresponds to second-to-last element (index 1 of insert)
                    # so index = - (arg + 1)
                    if argument >= 0:
                        index = len(self.stack) - argument
                    else:
                        index = - argument - 1

                    self.stack.insert(index, element)
                else: # If the stack is empty, push a 0
                    self.stack = [0]

            elif instruction == 'pick':
                if self.stack:
                    # The indexing is reversed compared to Python (L is length of stack) :
                    # arg = 0 corresponds to top of stack (index L - 1 of pop) ; arg = 1 corresponds to below top element (index L - 2 of pop)
                    # so index = L - (arg + 1)
                    # arg = -1 corresponds to bottom of stack (index 0 of pop) ; arg = -2 corresponds to second-to-last element (index 1 of pop)
                    # so index = - (arg + 1)
                    if argument >= 0:
                        index = len(self.stack) - argument - 1
                    else:
                        index = - argument - 1

                    self.stack.append(self.stack.pop(index))
                    # Zero flag is assigned by the moved element
                    self.zero_flag = (self.stack[-1] == 0)
                else: # If the stack is empty, push a 0
                    self.stack = [0]

            elif instruction == 'push':
                self.stack.append(argument)
                # Zero flag is assigned by the pushed element
                self.zero_flag = (self.stack[-1] == 0)

            elif instruction == 'pop':
                # l = l[:-n] removes the last n element from l if n > 0
                if argument > 0:
                    # If the stack have less or as much elements than should be popped, remove them all and raise the zero flag
                    if len(self.stack) <= argument:
                        self.stack = []
                        self.zero_flag = True
                    else:
                        # Zero flag is assigned according to the last poped element, which is at index -arg
                        self.zero_flag = (self.stack[-argument] == 0)
                        self.stack = self.stack[:-argument]

            elif instruction == 'add':
                # Default values are 0, 0 (picked in this order is the stack does not have enough elements)
                if len(self.stack) == 0:
                    top, below = 0, 0
                elif len(self.stack) == 1:
                    top, below = self.stack.pop(), 0
                else:
                    top, below = self.stack.pop(), self.stack.pop()
                self.stack.append(below + top)
                # For maths operation, zero flag is assigned according to the result
                self.zero_flag = (self.stack[-1] == 0)

            elif instruction == 'sub':
                # Default values are 0, 0 (picked in this order is the stack does not have enough elements)
                if len(self.stack) == 0:
                    top, below = 0, 0
                elif len(self.stack) == 1:
                    top, below = self.stack.pop(), 0
                else:
                    top, below = self.stack.pop(), self.stack.pop()
                self.stack.append(below - top)
                # For maths operation, zero flag is assigned according to the result
                self.zero_flag = (self.stack[-1] == 0)

            elif instruction == 'mul':
                # Default values are 0, 0 (picked in this order is the stack does not have enough elements)
                if len(self.stack) == 0:
                    top, below = 0, 0
                elif len(self.stack) == 1:
                    top, below = self.stack.pop(), 0
                else:
                    top, below = self.stack.pop(), self.stack.pop()
                self.stack.append(below * top)
                # For maths operation, zero flag is assigned according to the result
                self.zero_flag = (self.stack[-1] == 0)

            elif instruction == 'div':
                # Default values are 1, 0 (picked in this order is the stack does not have enough elements)
                if len(self.stack) == 0:
                    top, below = 1, 0
                elif len(self.stack) == 1:
                    top, below = self.stack.pop(), 0
                else:
                    top, below = self.stack.pop(), self.stack.pop()
                if top == 0:
                    pass # TODO division par 0
                self.stack.append(below // top)
                # For maths operation, zero flag is assigned according to the result
                self.zero_flag = (self.stack[-1] == 0)

            elif instruction == 'mod':
                # Default values are 1, 0 (picked in this order is the stack does not have enough elements)
                if len(self.stack) == 0:
                    top, below = 1, 0
                elif len(self.stack) == 1:
                    top, below = self.stack.pop(), 0
                else:
                    top, below = self.stack.pop(), self.stack.pop()
                if top == 0:
                    pass # TODO division par 0
                self.stack.append(below % top)
                # For maths operation, zero flag is assigned according to the result
                self.zero_flag = (self.stack[-1] == 0)

            elif instruction == 'pow':
                # Default values are 1, 1 (picked in this order is the stack does not have enough elements)
                if len(self.stack) == 0:
                    top, below = 1, 1
                elif len(self.stack) == 1:
                    top, below = self.stack.pop(), 1
                else:
                    top, below = self.stack.pop(), self.stack.pop()
                if top >= 0:
                    self.stack.append(below ** top)
                else:
                    if below > 1:
                        self.stack.append(0)
                    elif below == 1:
                        self.stack.append(1)
                    elif below == 0:
                        pass # TODO division par 0
                    else: # below < 0:
                        self.stack.append(-1)
                # For maths operation, zero flag is assigned according to the result
                self.zero_flag = (self.stack[-1] == 0)

            elif instruction == 'abs':
                if self.stack:
                    self.stack.append(abs(self.stack.pop()))
                else: # If the stack is empty, act as if it had a 0
                    self.stack = [0]
                # For maths operation, zero flag is assigned according to the result
                self.zero_flag = (self.stack[-1] == 0)

            else:
                pass #TODO gestion erreur

            instruction_pointer += 1

