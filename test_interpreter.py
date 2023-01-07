import unittest

from interpreter import Interpreter

class TestPhi(unittest.TestCase):

    def test_construct_number_positive(self):
        interpreter = Interpreter()

        n1 = interpreter._construct_number([(0, 1)])
        n1230 = interpreter._construct_number([(0, 1), (0, 2), (0, 3), (0, 0)])
        n9876_pos = interpreter._construct_number([(0, 9), (0, 8), (0, 7), (0, 6)])
        n9876_neg = interpreter._construct_number([(0, -1), (0, -2), (0, -3), (0, -4)])

        self.assertEqual(n1, 1)
        self.assertEqual(n1230, 1230)
        self.assertEqual(n9876_pos, 9876)
        self.assertEqual(n9876_neg, 9876)

    def test_construct_number_negative(self):
        interpreter = Interpreter()

        nm1 = interpreter._construct_number([(0, 0), (0, 1)])
        nm1230 = interpreter._construct_number([(0, 0), (0, 1), (0, 2), (0, 3), (0, 0)])
        nm9876_pos = interpreter._construct_number([(0, 0), (0, 9), (0, 8), (0, 7), (0, 6)])
        nm9876_neg = interpreter._construct_number([(0, 0), (0, -1), (0, -2), (0, -3), (0, -4)])

        self.assertEqual(nm1, -1)
        self.assertEqual(nm1230, -1230)
        self.assertEqual(nm9876_pos, -9876)
        self.assertEqual(nm9876_neg, -9876)

    def test_construct_zero(self):
        interpreter = Interpreter()

        zero = interpreter._construct_number([(0, 0)])

        self.assertEqual(zero, 0)

    def test_construct_no_number(self):
        interpreter = Interpreter()

        zero = interpreter._construct_number([(1, 0)])

        self.assertEqual(zero, None)

    def test_construct_number_more_deltas(self):
        interpreter = Interpreter()

        zero = interpreter._construct_number([(0, 0), (1, 0)])
        ten = interpreter._construct_number([(0, 1), (0, 0), (-1, 10)])
        minus_one = interpreter._construct_number([(0, 0), (0, 1), (1, 1), (-1, 0)])

        self.assertEqual(zero, 0)
        self.assertEqual(ten, 10)
        self.assertEqual(minus_one, -1)

    def test_construct_number_more_deltas(self):
        interpreter = Interpreter()

        zero = interpreter._construct_number([(0, 0), (0, 0), (1, 0)])
        minus_one = interpreter._construct_number([(0, 0), (0, 0), (0, 1), (1, 1), (-1, 0)])

        self.assertEqual(zero, 0)
        self.assertEqual(minus_one, -1)


if __name__ == '__main__':
    unittest.main()
