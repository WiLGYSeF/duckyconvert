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
    'STRING this is a "test"': r'Keyboard.print("this is a \"test\"");',
    'MENU': 'typekey(KEY_MENU);',
    'PAGE_UP': 'typekey(KEY_PAGE_UP);',
    'RETURN': 'typekey(KEY_ENTER);',
    'CTRL b': "keycombo('B', 1, KEY_LEFT_CTRL);",
    'CTRL-ALT-SHIFT c': "keycombo('C', 3, KEY_LEFT_CTRL, KEY_LEFT_ALT, KEY_LEFT_SHIFT);",
    'CTRL-INVALID b': Exception(),
}

TRANSLATE_LINE_DIGISPARK = {
    'DELAY 100': 'DigiKeyboard.delay(100);',
    'STRING this is a "test"': r'DigiKeyboard.print("this is a \"test\"");',
}

TYPE_STRING = [
    {
        STRING: 'f',
        MODIFIERS: [],
        RESULT: "typekey('F');"
    },
    {
        STRING: 'F',
        MODIFIERS: [],
        RESULT: "typekey('F');"
    },
    {
        STRING: 'abcdef',
        MODIFIERS: [],
        RESULT: 'Keyboard.print("abcdef");'
    },
    {
        STRING: 'abcd"ef"',
        MODIFIERS: [],
        RESULT: r'Keyboard.print("abcd\"ef\"");'
    },
    {
        STRING: 'b',
        MODIFIERS: ['CTRL', 'SHIFT'],
        RESULT: "keycombo('B', 2, KEY_LEFT_CTRL, KEY_LEFT_SHIFT);"
    },
    {
        STRING: 'abcdef',
        MODIFIERS: ['CTRL', 'SHIFT'],
        RESULT: """\
keycombo(0, 2, KEY_LEFT_CTRL, KEY_LEFT_SHIFT);
Keyboard.print("abcdef");
keycombo(0, 0);"""
    },
    {
        STRING: 'F6',
        MODIFIERS: [],
        RESULT: 'typekey(KEY_F6);'
    }
]

TYPE_STRING_DIGISPARK = [
    {
        STRING: 'yeet',
        MODIFIERS: ['ALT'],
        RESULT: """\
keycombo(0, 1, MOD_ALT_LEFT);
DigiKeyboard.print("yeet");
keycombo(0, 0);"""
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

    def test_translate_line_digispark(self):
        for key, val in TRANSLATE_LINE_DIGISPARK.items():
            duck = Converter()
            duck.convert_type = duckyconvert.TYPE_DIGISPARK
            if isinstance(val, Exception):
                self.assertRaises(Exception, duck.translate_line, key)
            else:
                self.assertEqual(duck.translate_line(key), val)

        duck.translate_line('STRING abcdef')
        duck.translate_line('DEFAULT_DELAY 125')
        self.assertEqual(duck.translate_line('REPEAT 2'), '''
for (int _repeat = 0; _repeat < 2; _repeat++)
{
    DigiKeyboard.print("abcdef");
    DigiKeyboard.delay(125);
}
''')

    def test_translate_line_default_delay(self):
        duck = Converter()
        duck.translate_line('DEFAULT_DELAY 125')
        self.assertEqual(duck.global_delay, 125)

    def test_translate_line_flash_macro(self):
        duck = Converter()
        duck.flash_macro = True
        self.assertEqual(duck.translate_line('STRING abcdef'), 'Keyboard.print(F("abcdef"));')

    def test_translate_line_repeat(self):
        duck = Converter()
        self.assertRaises(ValueError, duck.translate_line, 'REPEAT 2')

        duck.translate_line('STRING abcdef')

        self.assertRaises(ValueError, duck.translate_line, 'REPEAT a')
        self.assertRaises(ValueError, duck.translate_line, 'REPEAT -2')

        self.assertEqual(duck.translate_line('REPEAT 2'), '''
for (int _repeat = 0; _repeat < 2; _repeat++)
{
    Keyboard.print("abcdef");
}
''')
        self.assertEqual(duck.translate_line('REPEAT'), 'Keyboard.print("abcdef");')

        duck.translate_line('DEFAULT_DELAY 125')
        self.assertEqual(duck.translate_line('REPEAT 2'), '''
for (int _repeat = 0; _repeat < 2; _repeat++)
{
    Keyboard.print("abcdef");
    delay(125);
}
''')

    def test_type_string(self):
        duck = Converter()
        for entry in TYPE_STRING:
            self.assertEqual(duck.type_string(entry[STRING], entry[MODIFIERS]), entry[RESULT])

    def test_type_string_digispark(self):
        duck = Converter()
        duck.convert_type  = duckyconvert.TYPE_DIGISPARK
        for entry in TYPE_STRING_DIGISPARK:
            self.assertEqual(duck.type_string(entry[STRING], entry[MODIFIERS]), entry[RESULT])

    def test_get_key_from_str(self):
        duck = Converter()
        for key, val in GET_KEY_FROM_STR.items():
            self.assertEqual(duck.get_key_from_str(key), val)

    def test_get_key_from_str_teensy(self):
        duck = Converter()
        duck.convert_type = duckyconvert.TYPE_TEENSY
        for key, val in GET_KEY_FROM_STR_TEENSY.items():
            self.assertEqual(duck.get_key_from_str(key), val)
