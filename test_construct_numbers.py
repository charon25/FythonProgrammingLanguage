import unittest

from interpreter import Interpreter

class TestPhi(unittest.TestCase):

    def test_positive_numbers(self):
        interpreter = Interpreter()

        n1 = interpreter._construct_number([(0, 1)], None)
        n1230 = interpreter._construct_number([(0, 1), (0, 2), (0, 3), (0, 0)], None)
        n9876_pos = interpreter._construct_number([(0, 9), (0, 8), (0, 7), (0, 6)], None)
        n9876_neg = interpreter._construct_number([(0, -1), (0, -2), (0, -3), (0, -4)], None)

        self.assertEqual(n1, (1, 1))
        self.assertEqual(n1230, (1230, 4))
        self.assertEqual(n9876_pos, (9876, 4))
        self.assertEqual(n9876_neg, (9876, 4))

    def test_negative_numbers(self):
        interpreter = Interpreter()

        nm1 = interpreter._construct_number([(0, 0), (0, 1)], None)
        nm1230 = interpreter._construct_number([(0, 0), (0, 1), (0, 2), (0, 3), (0, 0)], None)
        nm9876_pos = interpreter._construct_number([(0, 0), (0, 9), (0, 8), (0, 7), (0, 6)], None)
        nm9876_neg = interpreter._construct_number([(0, 0), (0, -1), (0, -2), (0, -3), (0, -4)], None)

        self.assertEqual(nm1, (-1, 2))
        self.assertEqual(nm1230, (-1230, 5))
        self.assertEqual(nm9876_pos, (-9876, 5))
        self.assertEqual(nm9876_neg, (-9876, 5))

    def test_zero(self):
        interpreter = Interpreter()

        zero = interpreter._construct_number([(0, 0)], None)

        self.assertEqual(zero, (0, 1))

    def test_no_number(self):
        interpreter = Interpreter()

        default = interpreter._construct_number([(1, 0)], 666)

        self.assertEqual(default, (666, 0))

    def test_more_deltas_after(self):
        interpreter = Interpreter()

        zero = interpreter._construct_number([(0, 0), (1, 0)], None)
        ten = interpreter._construct_number([(0, 1), (0, 0), (-1, 10)], None)
        minus_one = interpreter._construct_number([(0, 0), (0, 1), (1, 1), (-1, 0)], None)

        self.assertEqual(zero, (0, 1))
        self.assertEqual(ten, (10, 2))
        self.assertEqual(minus_one, ((-1, 2)))

    def test_multiple_zeros(self):
        interpreter = Interpreter()

        zero = interpreter._construct_number([(0, 0), (0, 0), (0, 0), (1, 0)], None)
        minus_one = interpreter._construct_number([(0, 0), (0, 0), (0, 1), (1, 1), (-1, 0)], None)

        self.assertEqual(zero, (0, 3))
        self.assertEqual(minus_one, (-1, 3))


if __name__ == '__main__':
    unittest.main()
