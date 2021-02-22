import unittest

import duckyconvert
from duckyconvert import Converter


STRING = 'string'
MODIFIERS = 'modifiers'
RESULT = 'result'

TRANSLATE_LINE = {
    'INVALID': Exception(),
    'REM': '//',
    'REM abc': '// abc',
    'DELAY': Exception(),
    'DELAY abc': Exception(),
    'DELAY 50': 'delay(50);',
    'STRING this is a "test"': r'kbd_print("this is a \"test\"");',
    'MENU': 'kbd_type(KEY_MENU);',
    'PAGE_UP': 'kbd_type(KEY_PAGE_UP);',
    'RETURN': 'kbd_type(KEY_ENTER);',
    'CTRL b': "kbd_type('B', 1, KEY_LEFT_CTRL);",
    'CTRL-ALT-SHIFT c': "kbd_type('C', 3, KEY_LEFT_CTRL, KEY_LEFT_ALT, KEY_LEFT_SHIFT);",
    'CTRL-ALT SHIFT c': "kbd_type('C', 3, KEY_LEFT_CTRL, KEY_LEFT_ALT, KEY_LEFT_SHIFT);",
    'CTRL-ALT-SHIFT': "kbd_type(0, 3, KEY_LEFT_CTRL, KEY_LEFT_ALT, KEY_LEFT_SHIFT);",
    'CTRL-INVALID b': Exception(),
}

TYPE_STRING = [
    {
        STRING: 'f',
        MODIFIERS: [],
        RESULT: "kbd_type('F');"
    },
    {
        STRING: 'F',
        MODIFIERS: [],
        RESULT: "kbd_type('F');"
    },
    {
        STRING: 'abcdef',
        MODIFIERS: [],
        RESULT: 'kbd_print("abcdef");'
    },
    {
        STRING: 'abcd"ef"',
        MODIFIERS: [],
        RESULT: r'kbd_print("abcd\"ef\"");'
    },
    {
        STRING: 'b',
        MODIFIERS: ['CTRL', 'SHIFT'],
        RESULT: "kbd_type('B', 2, KEY_LEFT_CTRL, KEY_LEFT_SHIFT);"
    },
    {
        STRING: 'abcdef',
        MODIFIERS: ['CTRL', 'SHIFT'],
        RESULT: 'kbd_print("abcdef");'
    },
    {
        STRING: 'F6',
        MODIFIERS: [],
        RESULT: 'kbd_type(KEY_F6);'
    }
]

GET_KEY_FROM_STR = {
    'F12': 'KEY_F12',
    'F25': None,
    'Fa': None,
    '=': "'='",
    'g': "'G'",
    'ENTER': 'KEY_ENTER',
    'ESCAPE': 'KEY_ESC',
    'yeet': None
}

GET_KEY_FROM_STR_TEENSY = {
    '=': 'KEY_EQUAL'
}


class DuckyconvertTest(unittest.TestCase):
    def test_translate_line(self):
        for key, val in TRANSLATE_LINE.items():
            duck = Converter()
            if isinstance(val, Exception):
                self.assertRaises(Exception, duck.translate_line, key)
            else:
                self.assertEqual(duck.translate_line(key), val)

    def test_translate_line_default_delay(self):
        duck = Converter()
        duck.translate_line('DEFAULT_DELAY 125')
        self.assertEqual(duck.global_delay, 125)

    def test_translate_line_flash_macro(self):
        duck = Converter(flash_macro=True)
        self.assertEqual(duck.translate_line('STRING abcdef'), 'kbd_print(F("abcdef"));')

    def test_translate_line_repeat(self):
        duck = Converter()
        self.assertRaises(ValueError, duck.translate_line, 'REPEAT 2')

        duck.translate_line('STRING abcdef')

        self.assertRaises(ValueError, duck.translate_line, 'REPEAT a')
        self.assertRaises(ValueError, duck.translate_line, 'REPEAT -2')

        self.assertEqual(duck.translate_line('REPEAT 2'), '''
for (int _repeat = 0; _repeat < 2; _repeat++)
{
    kbd_print("abcdef");
}'''
        )
        self.assertEqual(duck.translate_line('REPEAT'), 'kbd_print("abcdef");')

        duck.translate_line('DEFAULT_DELAY 125')
        self.assertEqual(duck.translate_line('REPEAT 2'), '''
for (int _repeat = 0; _repeat < 2; _repeat++)
{
    kbd_print("abcdef");
    delay(125);
}'''
        )

    def test_type_string(self):
        duck = Converter()
        for entry in TYPE_STRING:
            self.assertEqual(duck.type_string(entry[STRING], entry[MODIFIERS]), entry[RESULT])

    def test_get_key_from_str(self):
        duck = Converter()
        for key, val in GET_KEY_FROM_STR.items():
            self.assertEqual(duck.get_key_from_str(key), val)

    def test_get_key_from_str_teensy(self):
        duck = Converter(convert_type=duckyconvert.TYPE_TEENSY)
        for key, val in GET_KEY_FROM_STR_TEENSY.items():
            self.assertEqual(duck.get_key_from_str(key), val)
