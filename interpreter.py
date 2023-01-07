# The keys are the op code (Delta_I, Delta_w)
# The values are tuples containing:
#   - str: the opcode name
#   - bool: whether or not the opcode needs a number afterwards
#   - int: the default value if the number is not provided
OPCODES: dict[tuple[int, int], tuple[str, bool, int]] = {
    (-1, 1): ('print', True, 1),
    (-1, -1): ('read', True, 1),
    (-1, 2): ('copy', True, 1),
  # (-1, -2): # Unused for now
    (-1, 3): ('jmpz', True, 1),
    (-1,- 3): ('jmpnz', True, 1),

    (1, 1): ('push', True, 0),
    (1, -1): ('pop', False, None),
    (1, 2): ('add', False, None),
    (1, -2): ('sub', False, None),
    (1, 3): ('mul', False, None),
    (1, -3): ('div', False, None),
    (1, 4): ('mod', False, None),
    (1, -4): ('pow', False, None),
}


class Interpreter:
    def __init__(self) -> None:
        # TODO ajouter des fichiers
        self.stack: list[int] = []
        self.zero_flag: bool = True

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



    def execute(self, lines: list[str]) -> None:
        pass
