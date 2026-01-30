import unittest
from stringutils import to_upper, reverse_string

class TestStringUtils(unittest.TestCase):
    def test_upper(self):
        self.assertEqual(to_upper("hello"), "HELLO")

    def test_reverse(self):
        self.assertEqual(reverse_string("abc"), "cba")

if __name__ == '__main__':
    unittest.main()
