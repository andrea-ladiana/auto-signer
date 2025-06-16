import unittest
from pdf_signer import _parse_pages_basic

class TestParsePagesBasic(unittest.TestCase):
    def test_single_numbers(self):
        self.assertEqual(_parse_pages_basic('1', 10), [0])
        self.assertEqual(_parse_pages_basic('3', 10), [2])

    def test_range(self):
        self.assertEqual(_parse_pages_basic('1-3', 10), [0, 1, 2])
        self.assertEqual(_parse_pages_basic('8-15', 10), [7, 8, 9])

    def test_mix_and_duplicates(self):
        self.assertEqual(_parse_pages_basic('1,1,2-3,2', 10), [0, 1, 2])
        self.assertEqual(_parse_pages_basic('3-5,2,4', 10), [1, 2, 3, 4])

    def test_first_last(self):
        self.assertEqual(_parse_pages_basic('first', 10), [0])
        self.assertEqual(_parse_pages_basic('last', 10), [9])

if __name__ == '__main__':
    unittest.main()
