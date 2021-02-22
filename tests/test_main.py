import io
import os
import sys
import unittest

import duckyconvert


CONVERT_DATA_DIR = os.path.join(os.path.dirname(__file__), 'convert_data/')


class MainTest(unittest.TestCase):
    def test_linux_test_led(self):
        self.check_main('linux_test_led', ['-l', 'LED_BUILTIN'])

    def test_linux_test_digispark(self):
        self.check_main('linux_test_digispark', ['--digispark'])

    def test_linux_test_led_teensy(self):
        self.check_main('linux_test_led_teensy', ['--teensy', '-l', 'LED_BUILTIN'])

    def test_linux_test_led_delay(self):
        self.check_main('linux_test_led_delay', ['-l', 'LED_BUILTIN', '-p', '100'])

    def check_main(self, name, args):
        old_stdout = sys.stdout
        stream = io.StringIO()
        sys.stdout = stream

        fname = os.path.join(CONVERT_DATA_DIR, '%s/%s.txt' % (name, name))
        fname_result = fname[:-4] + '.ino'

        args.append(fname)
        args.append('-')
        duckyconvert.main(args)

        sys.stdout = old_stdout

        stream.seek(0)
        print(stream.read())
        stream.seek(0)

        with open(fname_result, 'r') as file:
            self.assertEqual(stream.read(), file.read())
