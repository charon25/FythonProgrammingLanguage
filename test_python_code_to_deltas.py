import re
import unittest

from interpreter import Interpreter, PythonCodeError

class TestPythonCodeToDeltas(unittest.TestCase):

    def test_indentation_length(self):
        interpreter = Interpreter()

        line1 = "a = 1"
        line2 = "    a = 1"
        line3 = "     a = 1"

        self.assertTupleEqual(interpreter._get_line_indentation_depth(line1, last_length=0, current_depth=0), (0, 0))
        self.assertTupleEqual(interpreter._get_line_indentation_depth(line2, last_length=0, current_depth=0), (4, 1))
        self.assertTupleEqual(interpreter._get_line_indentation_depth(line2, last_length=4, current_depth=1), (4, 1))
        self.assertTupleEqual(interpreter._get_line_indentation_depth(line3, last_length=0, current_depth=0), (5, 1))
        self.assertTupleEqual(interpreter._get_line_indentation_depth(line3, last_length=4, current_depth=1), (5, 2))

    def test_get_all_matches(self):
        interpreter = Interpreter()

        self.assertListEqual(list(interpreter._get_all_matches_regex(re.compile(r'\d+'), '11 aa 11 1 aa 1111')), [(0, 2), (6, 8), (9, 10), (14, 18)])

    def test_whitespace_count(self):
        interpreter = Interpreter()

        line1 = "a = 1"
        line2 = "    a = 1"
        line3 = "     a = 1 # a b c"
        line4 = "    a = 'a# ' * 2"
        line5 = "    a = 'a# ' * 2 # a b c d e"
        line6 = '    a = "a# " * 2'
        line7 = '    a = "a# " * 2 # a b c d e'

        self.assertEqual(interpreter._get_line_whitespace_count(line1), 2)
        self.assertEqual(interpreter._get_line_whitespace_count(line2), 2)
        self.assertEqual(interpreter._get_line_whitespace_count(line3), 2)
        self.assertEqual(interpreter._get_line_whitespace_count(line4), 5)
        self.assertEqual(interpreter._get_line_whitespace_count(line5), 5)
        self.assertEqual(interpreter._get_line_whitespace_count(line6), 5)
        self.assertEqual(interpreter._get_line_whitespace_count(line7), 5)
        

    def test_syntax_error(self):
        interpreter = Interpreter()

        code1 = 'a ='
        code2 = '\n'.join(['if True:', 'a = 1'])
        code3 = '\n'.join(['if True:', '  a = 1', '       b = 1'])
        code4 = 'if = 1'

        with self.assertRaises(PythonCodeError):
            interpreter._python_code_to_deltas(code1)
        with self.assertRaises(PythonCodeError):
            interpreter._python_code_to_deltas(code2)
        with self.assertRaises(PythonCodeError):
            interpreter._python_code_to_deltas(code3)
        with self.assertRaises(PythonCodeError):
            interpreter._python_code_to_deltas(code4)

    def test_small_code(self):
        interpreter = Interpreter()

        code = '\n'.join(['a= 2', 'if a:', '    a = 3', '    b = "This is a very long" * a', '    print(b, sep=" ", end="")', 'a = len(b) * 2'])

        deltas = interpreter._python_code_to_deltas(code)

        self.assertListEqual(deltas, [(0, 0), (1, 1), (0, 6), (0, -5), (-1, 1)])


if __name__ == '__main__':
    unittest.main()
