import io
import os
import unittest

from duckyconvert import Converter


CONVERT_DATA_DIR = os.path.join(os.path.dirname(__file__), 'convert_to_file/')


class ConvertToFileTest(unittest.TestCase):
    def test_convert_to_file(self):
        duck = Converter()
        for root, _, files in os.walk(CONVERT_DATA_DIR):
            for fname in files:
                if not fname.endswith('.txt'):
                    continue

                fname = os.path.join(root, fname)
                fname_result = fname[:-4] + '.ino'

                with open(fname, 'r') as file, open(fname_result, 'r') as file_res:
                    out_stream = io.StringIO()
                    duck.convert_to_file(file, out_stream)
                    out_stream.seek(0)

                    self.assertEqual(out_stream.read(), file_res.read())
