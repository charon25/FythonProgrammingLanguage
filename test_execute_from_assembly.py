import unittest

from interpreter import Interpreter

class TestPhi(unittest.TestCase):

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




if __name__ == '__main__':
    unittest.main()
