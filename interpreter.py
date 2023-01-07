
IO_CMD = -1
NUMBER_CMD = 0
OP_CMD = 1

PRINT = 1
READ = -1


class Interpreter:
    def __init__(self) -> None:
        self.stack = []


    def _deltas_to_assembly(self, deltas: list[tuple[int, int]]) -> list[str]:
        self.stack = []
        adding_number = False

        # TODO : gestion erreur si deltas pas liste de tuples
        index = 0
        while index < len(deltas):
            di, dn = deltas[index]
            if di == IO_CMD:
                index_increase = self._execute_io_cmd(deltas[index:])
                index += index_increase
            elif di == OP_CMD:
                adding_number = self._execute_op_cmd(dn)
                index += 1
                if adding_number:
                    number = self._construct_number(deltas[index:])


    def _execute_io_cmd(self, deltas: list[tuple[int, int]]) -> None:
        # The first element is the type of I/O
        dn = deltas[0][1]
        number = self._construct_number(deltas[1:])

        if dn == PRINT:
            #TODO : changer la façon dont on print
            # lst[-1:-number-1:-1] returns the last 'number' elements for the lst, backwards
            print(''.join(chr(value) for value in self.stack[-1:-number-1:-1]), end='')
        elif dn == READ:
            # pad the string with the NUL character if there are not enough chars in the input
            str_input = input(f'Input {number} characters : ').ljust(number, '\x00')
            self.stack.extend(ord(c) for c in str_input)


    def _execute_op_cmd(self, dn: int) -> bool:
        pass


    def _construct_number(self, deltas: list[tuple[int, int]]) -> int:
        digits = []
        # Loop while the first element of the tuple is 0
        for di, dn in deltas:
            if di != 0:
                break
            digits.append(dn)
        
        if len(digits) == 0:
            return None

        if digits == [0]:
            return 0

        sign = -1 if digits[0] == 0 else 1
        # Build a number from its digits, with digits < 0 being complemented to 10 (ie -1 => 9)
        value = int(''.join(map(lambda d:str(d) if d >= 0 else str(10 + d), digits)))
        return sign * value



    def execute(self, lines: list[str]) -> None:
        pass
