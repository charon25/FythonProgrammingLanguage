import unittest

from interpreter import FythonAssemblyError, Interpreter

class TestAssemblyToDeltas(unittest.TestCase):

    def test_number_to_deltas_positive(self):
        interpreter = Interpreter()

        self.assertListEqual(interpreter._number_to_deltas(1234), [(0, 1), (0, 2), (0, 3), (0, 4)])
        self.assertListEqual(interpreter._number_to_deltas(9), [(0, 9)])

    def test_number_to_deltas_negative(self):
        interpreter = Interpreter()

        self.assertListEqual(interpreter._number_to_deltas(-1234), [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)])
        self.assertListEqual(interpreter._number_to_deltas(-9), [(0, 0), (0, 9)])

    def test_number_to_deltas_zero(self):
        interpreter = Interpreter()

        self.assertListEqual(interpreter._number_to_deltas(0), [(0, 0)])
        

    def test_instructions_with_arguments(self):
        interpreter = Interpreter()

        assembly = ['print 2', 'read 2', 'copy 2', 'jmpz 2', 'jmpnz 2', 'place 2', 'pick 2', 'push 2', 'pop 2']
        expected_deltas = [(-1, 1), (0, 2), (-1, -1), (0, 2), (-1, 2), (0, 2), (-1, 3), (0, 2), (-1, -3), (0, 2), (-1, 4), (0, 2), (-1, -4), (0, 2), (1, 1), (0, 2), (1, -1), (0, 2)]

        self.assertListEqual(interpreter.assembly_to_deltas(assembly), expected_deltas)

    def test_instructions_no_arguments(self):
        interpreter = Interpreter()

        assembly = ['add', 'sub', 'mul', 'div', 'mod', 'pow', 'abs']
        expected_deltas = [(1, 2), (1, -2), (1, 3), (1, -3), (1, 4), (1, -4), (1, 5)]

        self.assertListEqual(interpreter.assembly_to_deltas(assembly), expected_deltas)

    def test_reciprocity(self):
        interpreter = Interpreter()

        assembly = ['read 1', 'push 1', 'add', 'push 0', 'push 1', 'pick -1', 'push 1', 'sub', 'copy 3', 'abs', 'add', 'pop 1', 'jmpz 7', 'place -1', 'copy 3', 'print 1', 'pick -2', 'add', 'jmpnz -13']

        self.assertListEqual(interpreter.deltas_to_assembly(interpreter.assembly_to_deltas(assembly)), assembly)


    def test_nonexistant_instruction(self):
        interpreter = Interpreter()

        assembly = ['lol 12']

        with self.assertRaises(FythonAssemblyError):
            interpreter.assembly_to_deltas(assembly)

if __name__ == '__main__':
    unittest.main()
