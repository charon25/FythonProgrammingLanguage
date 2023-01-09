import unittest

from interpreter import Interpreter

class TestDeltasToAssembly(unittest.TestCase):

    def test_delta_w_modulo(self):
        interpreter = Interpreter()

        delta_w = list(range(-20, 21))
        expected = [0, -9, -8, -7, -6, -5, -4, -3, -2, -1] * 2 + [0] + [1, 2, 3, 4, 5, 6, 7, 8, 9, 0] * 2

        self.assertListEqual(list(interpreter._delta_w_modulo_10(dw) for dw in delta_w), expected)

    def test_opcodes_no_arguments(self):
        interpreter = Interpreter()

        deltas = [(1, 2), (1, -2), (1, 3), (1, -3), (1, 4), (1, -4), (1, 5)]
        expected = ['add', 'sub', 'mul', 'div', 'mod', 'pow', 'abs']

        self.assertListEqual(interpreter._deltas_to_assembly(deltas), expected)

    def test_opcodes_arguments_always_2(self):
        interpreter = Interpreter()

        deltas = [(-1, 1), (0, 2), (-1, -1), (0, 2), (-1, 2), (0, 2), (-1, 3), (0, 2), (-1, -3), (0, 2), (-1, 4), (0, 2), (-1, -4), (0, 2), (1, 1), (0, 2), (1, -1), (0, 2)]
        expected = ['print 2', 'read 2', 'copy 2', 'jmpz 2', 'jmpnz 2', 'place 2', 'pick 2', 'push 2', 'pop 2']

        self.assertListEqual(interpreter._deltas_to_assembly(deltas), expected)

    def test_with_bigger_number(self):
        interpreter = Interpreter()

        deltas = [(1, 1), (0, 1), (0, 2), (0, 3), (0, 4), (1, 1), (0, 0), (0, -9), (0, -8), (0, -7), (0, -6), (1, 2)]
        expected = ['push 1234', 'push -1234', 'add']

        self.assertListEqual(interpreter._deltas_to_assembly(deltas), expected)

    def test_opcodes_modulo_w(self):
        interpreter = Interpreter()

        deltas = [(1, -11), (1, 52), (1, -32), (1, 773), (1, -23), (1, 44), (1, -33334)]
        expected = ['pop 1', 'add', 'sub', 'mul', 'div', 'mod', 'pow']

        self.assertListEqual(interpreter._deltas_to_assembly(deltas), expected)

    def test_opcodes_nop(self):
        interpreter = Interpreter()

        deltas = [(-3, 4), (-2, -2), (-1, 0), (0, 0), (0, 5), (1, 0)]
        expected = []

        self.assertListEqual(interpreter._deltas_to_assembly(deltas), expected)

    def test_opcodes_default_values(self):
        interpreter = Interpreter()

        deltas = [(-1, 1), (-1, -1), (-1, 2), (-1, 3), (-1, -3), (-1, 4), (-1, -4), (1, 1), (1, -1)]
        expected = ['print 1', 'read 1', 'copy 2', 'jmpz 1', 'jmpnz 1', 'place 1', 'pick 1', 'push 0', 'pop 1']

        self.assertListEqual(interpreter._deltas_to_assembly(deltas), expected)


if __name__ == '__main__':
    unittest.main()
