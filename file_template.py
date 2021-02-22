TYPE_ARDUINO = 'arduino'
TYPE_DIGISPARK = 'digispark'
TYPE_TEENSY = 'teensy'

HEADER_ARDUINO = '''\
#include <stdarg.h>

#include <Keyboard.h>

#define KEY_SPACE ' '

#define KEY_PRINTSCREEN 0xce
#define KEY_SCROLL_LOCK 0xcf
#define KEY_PAUSE 0xd4
#define KEY_NUM_LOCK 0xdb
#define KEY_MENU 0xed

#define KEY_UP KEY_UP_ARROW
#define KEY_DOWN KEY_DOWN_ARROW
#define KEY_LEFT KEY_LEFT_ARROW
#define KEY_RIGHT KEY_RIGHT_ARROW
#define KEY_ENTER KEY_RETURN
'''

HEADER_DIGISPARK = '''\
#include "DigiKeyboard.h"

#define KEY_ESC 41
#define KEY_BACKSPACE 42
#define KEY_TAB 43
#define KEY_MINUS 45
#define KEY_EQUAL 46
#define KEY_LEFT_BRACE 47
#define KEY_RIGHT_BRACE 48
#define KEY_BACKSLASH 49

#define KEY_SEMICOLON 51
#define KEY_QUOTE 52
#define KEY_TILDE 53
#define KEY_COMMA 54
#define KEY_PERIOD 55
#define KEY_SLASH 56
#define KEY_CAPS_LOCK 57

#define KEY_PRINTSCREEN 70
#define KEY_SCROLL_LOCK 71
#define KEY_PAUSE 72
#define KEY_INSERT 73
#define KEY_HOME 74
#define KEY_PAGE_UP 75
#define KEY_DELETE 76
#define KEY_END 77
#define KEY_PAGE_DOWN 78
#define KEY_ARROW_RIGHT 79

#define KEY_ARROW_DOWN 81
#define KEY_ARROW_UP 82
#define KEY_NUM_LOCK 83
#define KEYPAD_SLASH 84
#define KEYPAD_ASTERIX 85
#define KEYPAD_MINUS 86
#define KEYPAD_PLUS 87
#define KEYPAD_ENTER 88
#define KEYPAD_1 89
#define KEYPAD_2 90
#define KEYPAD_3 91
#define KEYPAD_4 92
#define KEYPAD_5 93
#define KEYPAD_6 94
#define KEYPAD_7 95
#define KEYPAD_8 96
#define KEYPAD_9 97
#define KEYPAD_0 98
#define KEYPAD_PERIOD 99

#define KEY_MENU 101

#define KEY_F13 104
#define KEY_F14 105
#define KEY_F15 106
#define KEY_F16 107
#define KEY_F17 108
#define KEY_F18 109
#define KEY_F19 110
#define KEY_F20 111
#define KEY_F21 112
#define KEY_F22 113
#define KEY_F23 114
#define KEY_F24 115

#define KEY_UP KEY_ARROW_UP
#define KEY_DOWN KEY_ARROW_DOWN
#define KEY_LEFT KEY_ARROW_LEFT
#define KEY_RIGHT KEY_ARROW_RIGHT
'''

HEADER_TEENSY = '''\
#include <stdarg.h>
'''

HEADER = {
    TYPE_ARDUINO: HEADER_ARDUINO,
    TYPE_DIGISPARK: HEADER_DIGISPARK,
    TYPE_TEENSY: HEADER_TEENSY
}


def setup_keyboard(convert_type, **kwargs):
    keyboard_init_wait = kwargs.get('keyboard_init_wait', 2000)
    led_pin = kwargs.get('led_pin')

    code_keyboard = ''

    if convert_type == TYPE_ARDUINO:
        code_keyboard += 'Keyboard.begin();\n'

    if led_pin is not None:
        code_keyboard += (
'''\
pinMode(%s, OUTPUT);

// wait for keyboard initialization
for (int i = 0; i < %d; i++)
{
    digitalWrite(%s, HIGH);
    delay(75);
    digitalWrite(%s, LOW);
    delay(75);
}
''' % (led_pin, keyboard_init_wait // 150, led_pin, led_pin)
        )

        if keyboard_init_wait % 150 != 0:
            code_keyboard += 'delay(%d);\n' % (keyboard_init_wait % 150)

        code_keyboard += 'digitalWrite(%s, HIGH);\n' % led_pin
    else:
        code_keyboard += (
'''\
// wait for keyboard initialization
delay(%d);
''' % keyboard_init_wait
        )

    if convert_type == TYPE_DIGISPARK:
        code_keyboard += (
'''\
DigiKeyboard.sendKeyStroke(0);
DigiKeyboard.delay(100);
'''
        )

    return code_keyboard

def unsetup_keyboard(convert_type, **kwargs):
    code_keyboard = ''

    if convert_type == TYPE_ARDUINO:
        code_keyboard += 'Keyboard.end();'

    return code_keyboard

def type_key(convert_type, **kwargs):
    press_delay = kwargs.get('press_delay', 0)
    code_typekey = '''\
void typeKey(int key, int mcount, ...)
{
    va_list args;
    va_start(args, mcount);
'''

    if press_delay > 0:
        code_delay = 'delay(%d);' % press_delay
    else:
        code_delay = '// delay(0);'

    if convert_type == TYPE_ARDUINO:
        code_typekey += (
'''
    for (int i = 0; i < mcount; i++)
        Keyboard.press(va_arg(args, int));
    %s

    if(key != 0)
        Keyboard.write(key);
    %s

    Keyboard.releaseAll();
''' % (code_delay, code_delay)
        )
    elif convert_type == TYPE_TEENSY:
        code_typekey += (
'''
    int modifier = 0;
    for (int i = 0; i < mcount; i++)
        modifier |= va_arg(args, int);

    Keyboard.set_modifier(modifier);
    Keyboard.send_now();
    %s

    if(key != 0)
    {
        Keyboard.set_key1(key);
        Keyboard.send_now();
        %s
        Keyboard.set_modifier(0);
        Keyboard.set_key1(0);
        Keyboard.send_now();
    }else
    {
        Keyboard.set_modifier(0);
        Keyboard.send_now();
    }
''' % (code_delay, code_delay)
        )
    elif convert_type == TYPE_DIGISPARK:
        code_typekey += (
'''
    int modifier = 0;
    for (int i = 0; i < mcount; i++)
        modifier |= va_arg(args, int);

    DigiKeyboard.sendKeyStroke(key, modifier);
'''
        )

    code_typekey += '''\
    va_end(args);
}
'''
    return code_typekey
