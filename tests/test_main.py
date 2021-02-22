import unittest

import duckyconvert


class MainTest(unittest.TestCase):
    def test_main(self):
        duckyconvert.main(['-l', 'LED_BUILTIN', 'tests/convert_to_file/linux_test/linux_test.txt', '-'])
