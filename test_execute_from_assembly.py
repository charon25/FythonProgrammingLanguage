import unittest

from interpreter import FauxPythonAssemblyError, FauxPythonDivisionByZero, Interpreter

class TestExecuteFromAssembly(unittest.TestCase):

    def test_parse_instructions(self):
        interpreter = Interpreter()

        lines = ['pop', 'add', 'sub', 'mul', 'div', 'mod', 'pow', 'abs', 'print 2', 'read 2', 'copy 2', 'jmpz 2', 'jmpnz 2', 'place 2', 'pick 2', 'push 2', 'push 1234', 'jmp -5']
        instructions = interpreter._parse_lines_to_instructions(lines)

        self.assertListEqual(instructions, [('pop', None), ('add', None), ('sub', None), ('mul', None), ('div', None), ('mod', None), ('pow', None), ('abs', None), ('print', 2), ('read', 2), ('copy', 2), ('jmpz', 2), ('jmpnz', 2), ('place', 2), ('pick', 2), ('push', 2), ('push', 1234), ('jmp', -5)])

    def test_parse_instructions_whitespaces(self):
        interpreter = Interpreter()

        lines = ['add           ', '', '', 'push        3   ', '    sub         ']
        instructions = interpreter._parse_lines_to_instructions(lines)

        self.assertListEqual(instructions, [('add', None), ('push', 3), ('sub', None)])

    def test_parse_instructions_comments(self):
        interpreter = Interpreter()

        lines = ['add ;comment style 1', 'add //comment style 2', 'add #comment style 3', 'add %comment style 4', 'add !comment style 5']
        instructions = interpreter._parse_lines_to_instructions(lines)

        self.assertListEqual(instructions, [('add', None), ('add', None), ('add', None), ('add', None), ('add', None)])


    def test_execute_simple(self):
        interpreter = Interpreter()

        lines = ['push 1', 'push 3', 'add']
        stack, _ = interpreter._execute_assembly(lines)

        self.assertListEqual(stack, [4])

    def test_execute_all_maths(self):
        interpreter = Interpreter()

        lines = ['push 1', 'push 2', 'push 3', 'push 4', 'push 5', 'push 6', 'push -7', 'abs', 'mul', 'add', 'sub', 'abs', 'push 10', 'mod', 'div', 'pow']
        stack, _ = interpreter._execute_assembly(lines)

        self.assertListEqual(stack, [1, 2])

    def test_execute_all_stack_operation_no_io_no_jumps(self):
        interpreter = Interpreter()

        lines = ['push 4', 'copy 2', 'push 5', 'copy 2', 'push 6', 'copy 3', 'place 3', 'place -1', 'pick 3', 'pick -2']
        stack, _ = interpreter._execute_assembly(lines)

        self.assertListEqual(stack, [6, 4, 6, 5, 6, 5, 4])

    def test_execute_jumps(self):
        interpreter = Interpreter()

        lines = ['push 5', 'jmpnz 2', 'push 1', 'push 0', 'jmpz 2', 'push 0', 'push 3']
        stack, _ = interpreter._execute_assembly(lines)

        self.assertListEqual(stack, [5, 0, 3])

    def test_execute_jumps_2(self):
        interpreter = Interpreter()

        lines = ['push 0', 'jmpnz 2', 'push 1', 'push 0', 'jmpz 2', 'push 0', 'push 3']
        stack, _ = interpreter._execute_assembly(lines)

        self.assertListEqual(stack, [0, 1, 0, 3])

    def test_execute_io_format_char(self):
        class Reader:
            def __init__(self) -> None:
                self.i = 0
            def read(self, _) -> int:
                self.i += 1
                return chr(self.i)
        class Writer:
            def __init__(self) -> None:
                self.values = []
            def write(self, value: str):
                self.values.append(value)

        writer = Writer()
        interpreter = Interpreter(writer, Reader(), output_format='char')

        lines = ['read 2', 'print 1', 'read 3', 'print 2', 'push 100', 'print 1']
        stack, _ = interpreter._execute_assembly(lines)

        self.assertListEqual(stack, [1, 3])
        self.assertListEqual(writer.values, ['\x02', '\x05', '\x04', 'd'])

    def test_execute_io_format_number(self):
        class Reader:
            def __init__(self) -> None:
                self.i = 0
            def read(self, _) -> int:
                self.i += 1
                return self.i
        class Writer:
            def __init__(self) -> None:
                self.values = []
            def write(self, value: int):
                self.values.append(int(value))

        writer = Writer()
        interpreter = Interpreter(writer, Reader(), output_format='number')

        lines = ['read 2', 'print 1', 'read 3', 'print 2', 'push 100', 'print 1']
        stack, _ = interpreter._execute_assembly(lines)

        self.assertListEqual(stack, [1, 3])
        self.assertListEqual(writer.values, [2, 5, 4, 100])

    def test_execute_not_enough_elements(self):
        def assertOK(interpreter: Interpreter, lines: list[str], final_stack: list[int], final_zero_flag: bool = None):
            stack, zero_flag = interpreter._execute_assembly(lines)
            self.assertListEqual(stack, final_stack)
            if not final_zero_flag is None:
                self.assertEqual(zero_flag, final_zero_flag)

        interpreter = Interpreter()

        assertOK(interpreter, ['copy 4'], [0, 0, 0, 0])
        assertOK(interpreter, ['place 2'], [0])
        assertOK(interpreter, ['pick 3'], [0])
        assertOK(interpreter, ['push 1', 'pop 2'], [], True)
        assertOK(interpreter, ['push 2', 'add'], [2])
        assertOK(interpreter, ['add'], [0])
        assertOK(interpreter, ['push 2', 'sub'], [-2])
        assertOK(interpreter, ['sub'], [0])
        assertOK(interpreter, ['push 2', 'mul'], [0])
        assertOK(interpreter, ['mul'], [0])
        assertOK(interpreter, ['push 2', 'div'], [0])
        assertOK(interpreter, ['div'], [0])
        assertOK(interpreter, ['push 2', 'mod'], [0])
        assertOK(interpreter, ['mod'], [0])
        assertOK(interpreter, ['push 2', 'pow'], [1])
        assertOK(interpreter, ['pow'], [1])
        assertOK(interpreter, ['abs'], [0])

    def test_division_by_zero(self):
        interpreter = Interpreter()

        lines1 = ['push 1', 'push 0', 'div']
        lines2 = ['push 1', 'push 0', 'mod']
        lines3 = ['push 0', 'push -1', 'pow']

        with self.assertRaises(FauxPythonDivisionByZero):
            interpreter._execute_assembly(lines1)
        with self.assertRaises(FauxPythonDivisionByZero):
            interpreter._execute_assembly(lines2)
        with self.assertRaises(FauxPythonDivisionByZero):
            interpreter._execute_assembly(lines3)

    def test_nonexistent_instruction(self):
        interpreter = Interpreter()

        assembly = ['lol 12']

        with self.assertRaises(FauxPythonAssemblyError):
            interpreter._execute_assembly(assembly)


    def test_execute_fibonacci(self):
        class Reader:
            def __init__(self) -> None:
                self.value = 0
            def set_value(self, value: int):
                self.value = value
            def read(self, _) -> int:
                return self.value
        class Writer:
            def __init__(self) -> None:
                self.values = []
            def reset(self):
                self.values = []
            def write(self, value: int):
                self.values.append(int(value))

        def fibonacci(n):
            a, b = 0, 1
            for _ in range(n):
                yield b
                a, b = b, a + b


        writer = Writer()
        reader = Reader()
        interpreter = Interpreter(file_out=writer, file_in=reader, output_format='number')

        lines = ['read 1', 'push 1', 'add', 'push 0', 'push 1', 'pick -1', 'push 1', 'sub', 'copy 3', 'abs', 'add', 'pop 1', 'jmpz 7', 'place -1', 'copy 3', 'print 1', 'pick -2', 'add', 'jmpnz -13']

        for n in (-10, 0, 10, 100):
            reader.set_value(n)
            interpreter._execute_assembly(lines)
            self.assertListEqual(writer.values, list(fibonacci(n)))
            writer.reset()


if __name__ == '__main__':
    unittest.main()
