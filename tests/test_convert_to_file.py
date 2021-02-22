import glob
import io
import os
import unittest

from duckyconvert import Converter


CONVERT_TO_FILE_DIR = os.path.join(os.path.dirname(__file__), 'convert_to_file/')


class ConvertToFileTest(unittest.TestCase):
    def test_convert_to_file(self):
        duck = Converter()
        for fname in glob.glob(os.path.join(CONVERT_TO_FILE_DIR, '*.txt')):
            fname_result = fname[:-4] + '.ino'
            with open(fname, 'r') as file, open(fname_result, 'r') as file_res:
                out_stream = io.StringIO()
                duck.convert_to_file(file, out_stream)
                out_stream.seek(0)

                self.assertEqual(out_stream.read(), file_res.read())
