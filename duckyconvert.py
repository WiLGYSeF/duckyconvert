import argparse
import re
import sys

import file_template


TYPE_ARDUINO = 'arduino'
TYPE_DIGISPARK = 'digispark'
TYPE_TEENSY = 'teensy'

KEYS_UNPRINTABLE = [
    'ENTER', 'ESC', 'BACKSPACE', 'TAB', 'SPACE', 'CAPS_LOCK', 'PRINTSCREEN', 'SCROLL_LOCK',
    'PAUSE', 'INSERT', 'HOME', 'PAGE_UP', 'DELETE', 'END', 'PAGE_DOWN', 'RIGHT',
    'LEFT', 'DOWN', 'UP', 'NUM_LOCK',

    'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
    'F13', 'F14', 'F15', 'F16', 'F17', 'F18', 'F19', 'F20', 'F21', 'F22', 'F23', 'F24'
]

KEYS_UNPRINTABLE_REPLACE = {
    'RETURN': 'ENTER',
    'ESCAPE': 'ESC',
    'CAPSLOCK': 'CAPS_LOCK',
    'PRINTSCR': 'PRINTSCREEN',
    'PRTSC': 'PRINTSCREEN',
    'SCROLLLOCK': 'SCROLL_LOCK',
    'BREAK': 'PAUSE',
    'PAGEUP': 'PAGE_UP',
    'PAGEDOWN': 'PAGE_DOWN',
    'RIGHTARROW': 'RIGHT',
    'LEFTARROW': 'LEFT',
    'DOWNARROW': 'DOWN',
    'UPARROW': 'UP',
    'NUMLOCK': 'NUM_LOCK'
}

MODIFIER_KEYMAPS = {
    TYPE_ARDUINO: {
        'CONTROL': 'KEY_LEFT_CTRL',
        'CTRL': 'KEY_LEFT_CTRL',
        'SHIFT': 'KEY_LEFT_SHIFT',
        'ALT': 'KEY_LEFT_ALT',
        'GUI': 'KEY_LEFT_GUI',
        'SUPER': 'KEY_LEFT_GUI',
        'WINDOWS': 'KEY_LEFT_GUI'
    },
    TYPE_TEENSY: {
        'CONTROL': 'MODIFIERKEY_CTRL',
        'CTRL': 'MODIFIERKEY_CTRL',
        'SHIFT': 'MODIFIERKEY_SHIFT',
        'ALT': 'MODIFIERKEY_ALT',
        'GUI': 'MODIFIERKEY_GUI',
        'SUPER': 'MODIFIERKEY_GUI',
        'WINDOWS': 'MODIFIERKEY_GUI'
    },
    TYPE_DIGISPARK: {
        'CONTROL': 'MOD_CONTROL_LEFT',
        'CTRL': 'MOD_CONTROL_LEFT',
        'SHIFT': 'MOD_SHIFT_LEFT',
        'ALT': 'MOD_ALT_LEFT',
        'GUI': 'MOD_GUI_LEFT',
        'SUPER': 'MOD_GUI_LEFT',
        'WINDOWS': 'MOD_GUI_LEFT'
    }
}

CMD_SPECIAL = ['REM', 'DEFAULT_DELAY', 'DEFAULTDELAY', 'REPEAT']


class Converter:
    def __init__(self, **kwargs):
        self.convert_type = kwargs.get('convert_type', TYPE_ARDUINO)
        self.flash_macro = kwargs.get('flash_macro', False)
        self.led_pin = kwargs.get('led_pin', None)
        self.keyboard_init_wait = kwargs.get('keyboard_init_wait', 2000)
        self.press_delay = kwargs.get('press_delay', 0)

        self.global_delay = 0
        self.last_cmd = None

    def translate_line(self, line):
        cmd = line
        val = None

        idx = line.find(' ')
        if idx != -1:
            cmd = line[0:idx]
            val = line[idx + 1:]

        result = self.translate_cmd(cmd, val)
        if cmd not in CMD_SPECIAL:
            self.last_cmd = [cmd, val]
        return result

    def translate_cmd(self, cmd, val):
        def check_for_val():
            if val is None:
                raise ValueError('expecting value for %s' % cmd)

        if cmd == 'REM':
            return '//' if val is None else '// ' + val
        if cmd in ('DEFAULT_DELAY', 'DEFAULTDELAY'):
            check_for_val()
            self.global_delay = int(val.strip())
            return None
        if cmd == 'DELAY':
            check_for_val()
            return 'delay(%d);' % int(val.strip())
        if cmd == 'STRING':
            check_for_val()
            return self.type_string(val)

        modifiers = [
            'CONTROL',
            'CTRL',
            'SHIFT',
            'ALT',
            'GUI',
            'SUPER',
            'WINDOWS'
        ]

        for mod in modifiers:
            if not cmd.startswith(mod):
                continue

            modifiers = cmd.split('-')
            if val is not None and ' ' in val:
                valspl = val.split(' ')
                modifiers.extend(valspl[:-1])
                val = valspl[-1]

            return self.type_string(val, modifiers)

        if cmd in ('APP', 'MENU'):
            return 'kbd_type(KEY_MENU);'
        if cmd == 'REPEAT':
            if self.last_cmd is None:
                raise ValueError('no command to repeat')

            rcount = 1
            if val is not None:
                try:
                    rcount = int(val.strip())
                    if rcount <= 0:
                        raise ValueError
                except ValueError as verr:
                    raise ValueError("invalid repeat count: %s" % val) from verr

            if rcount == 1:
                return self.translate_cmd(self.last_cmd[0], self.last_cmd[1])

            string = '''
for (int _repeat = 0; _repeat < %s; _repeat++)
{
''' % (rcount)

            result = self.translate_cmd(self.last_cmd[0], self.last_cmd[1])
            if result is not None:
                string += self.indent_block(result, 1)
                if self.global_delay > 0:
                    string += self.indent_block('delay(%d);' % self.global_delay, 1)

            return string + '}\n'
        if cmd in KEYS_UNPRINTABLE_REPLACE or cmd in KEYS_UNPRINTABLE:
            return 'kbd_type(KEY_%s);' % KEYS_UNPRINTABLE_REPLACE.get(cmd, cmd)

        raise ValueError('unknown command: %s' % cmd)

    def type_string(self, string, modifiers=None):
        if modifiers is None:
            modifiers = []

        modifiers = list(map(
            lambda x: MODIFIER_KEYMAPS[self.convert_type][x],
            modifiers
        ))

        if string is None:
            return 'kbd_type(0, %d, %s);' % (len(modifiers), ', '.join(modifiers))

        key = self.get_key_from_str(string)
        if key is not None:
            if len(modifiers) == 0:
                return 'kbd_type(%s);' % key
            return 'kbd_type(%s, %d, %s);' % (key, len(modifiers), ', '.join(modifiers))

        string = '"%s"' % string.replace('\\', r'\\').replace('"', r'\"')
        if self.flash_macro:
            string = 'F(%s)' % string
        return 'kbd_print(%s);' % string

    def indent_block(self, block, level, indent='    '):
        result = ''
        for line in block.split('\n'):
            if len(line) == 0 or line.isspace():
                result += '\n'
            else:
                result += (indent * level) + line + '\n'

        return result

    def get_key_from_str(self, key):
        ascii_name_map = {
            '-': 'MINUS',
            '=': 'EQUAL',
            '{': 'LEFT_BRACE',
            '}': 'RIGHT_BRACE',
            '\\': 'BACKSLASH',
            ';': 'SEMICOLON',
            "'": 'QUOTE',
            '~': 'TILDE',
            ',': 'COMMA',
            '.': 'PERIOD',
            '/': 'SLASH'
        }

        if key[0] in 'Ff' and (len(key) == 2 or len(key) == 3):
            try:
                num = int(key[1:])
                if num >= 1 and num <= 24:
                    return 'KEY_' + key
                return None
            except ValueError:
                return None

        if len(key) == 1:
            if self.convert_type == TYPE_ARDUINO:
                return "'%s'" % key.upper()

            key = ascii_name_map.get(key, key)
            return 'KEY_' + key

        key = KEYS_UNPRINTABLE_REPLACE.get(key, key)
        if key in KEYS_UNPRINTABLE:
            return 'KEY_' + key

        return None

    def translate_from_stream(self, stream):
        translations = []
        linenum = 0

        for line in stream:
            linenum += 1

            if len(line.strip()) == 0:
                translations.append(None)
                continue

            translations.append(self.translate_line(line.rstrip('\n')))

        return translations

    def convert_to_file(self, inf, outf):
        outf.write(file_template.HEADER[self.convert_type])

        outf.write('''
void setup()
{
'''
        )

        outf.write(self.indent_block(
            file_template.setup_keyboard(
                self.convert_type,
                keyboard_init_wait=self.keyboard_init_wait,
                led_pin=self.led_pin,
            ),
            1
        ))

        translations = self.translate_from_stream(inf)

        for line in translations:
            if line is None:
                outf.write('\n')
                continue

            outf.write(self.indent_block(line, 1))
            outf.write('\n')

            if self.global_delay > 0:
                outf.write(self.indent_block('delay(%d);' % self.global_delay, 1))

        outf.write(self.indent_block(
            file_template.unsetup_keyboard(
                self.convert_type,
                led_pin=self.led_pin
            ),
            1
        ))

        if self.led_pin is not None:
            outf.write(
'''\
}

void loop()
{
    digitalWrite(%s, HIGH);
    delay(500);
    digitalWrite(%s, LOW);
    delay(500);
}

''' % (self.led_pin, self.led_pin)
            )
        else:
            outf.write(
'''\
}

void loop() {}

'''
            )

        outf.write(file_template.kbd_type(
            self.convert_type,
            press_delay=self.press_delay
        ))

        return True


def main(argv):
    aparser = argparse.ArgumentParser(
        description='Converts duckyscript code to Arduino/Teensy code'
    )

    group = aparser.add_mutually_exclusive_group()
    group.add_argument('-a', '--arduino',
        dest='convert_type', action='store_const', const=TYPE_ARDUINO, default=TYPE_ARDUINO,
        help='convert to Arduino-style code (default)'
    )
    group.add_argument('-d', '--digispark',
        dest='convert_type', action='store_const', const=TYPE_DIGISPARK,
        help='convert to Digispark-style code'
    )
    group.add_argument('-t', '--teensy',
        dest='convert_type', action='store_const', const=TYPE_TEENSY,
        help='convert to Teensy-style code'
    )

    aparser.add_argument('-w', '--wait',
        metavar='MSEC', action='store', type=int, default=2000,
        help='time to wait for initial keyboard recognition (default 2000)'
    )
    aparser.add_argument('-p', '--press-delay',
        metavar='MSEC', action='store', type=int, default=0,
        help='delay between key press and release'
    )
    aparser.add_argument('-l', '--led',
        metavar='PIN', action='store', default=None,
        help='turn on LED when typing, blink when done, use built-in pin with "LED_BUILTIN"'
    )
    aparser.add_argument('-f', '--flash',
        action='store_true', default=False,
        help='use the F() macro for storing strings in flash'
    )
    aparser.add_argument('files',
        metavar='FILE', action='store', nargs=2
    )

    argspace = aparser.parse_args(argv)

    if argspace.led is not None and not is_valid_led_pin(argspace.led):
        raise ValueError('invalid led pin name: %s' % argspace.led)

    if argspace.files[0] != '-':
        infile = open(argspace.files[0], 'r')
    else:
        infile = sys.stdin

    if argspace.files[1] != '-':
        outfile = open(argspace.files[1], 'w')
    else:
        outfile = sys.stdout

    duck = Converter(
        convert_type=argspace.convert_type,
        keyboard_init_wait=argspace.wait,
        press_delay=argspace.press_delay,
        led_pin=argspace.led,
        flash_macro=argspace.flash
    )

    try:
        duck.convert_to_file(infile, outfile)
    finally:
        if infile != sys.stdin:
            infile.close()
        if outfile != sys.stdout:
            outfile.close()

def is_valid_led_pin(led_pin):
    return re.fullmatch(
        r'[A-Z_a-z][0-9A-Z_a-z]*|0x[0-9A-Fa-f]+|[0-9]+L?',
        led_pin
    ) is not None

if __name__ == '__main__': #pragma: no cover
    main(sys.argv[1:])
