#include "DigiKeyboard.h"

#define kbd_print(x) DigiKeyboard.print(x)
#define kbd_println(x) DigiKeyboard.println(x)
#define delay(x) DigiKeyboard.delay(x)

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

void setup()
{
    // wait for keyboard initialization
    delay(2000);
    DigiKeyboard.sendKeyStroke(0);
    DigiKeyboard.delay(100);


    // spawn terminal
    kbd_type(KEY_T, 2, MOD_CONTROL_LEFT, MOD_ALT_LEFT);
    delay(25);
    delay(300);

    // move to bottom corner of screen
    kbd_type(KEY_F7, 1, MOD_ALT_LEFT);
    delay(25);
    kbd_type(KEY_DOWN, 1, MOD_SHIFT_LEFT);
    delay(25);

    for (int _repeat = 0; _repeat < 3; _repeat++)
    {
        kbd_type(KEY_DOWN, 1, MOD_SHIFT_LEFT);
        delay(25);
    }
    kbd_type(KEY_ENTER);
    delay(25);

    // payload
    kbd_print("echo \"If you can read this, you are in big trouble\"");
    delay(25);
    kbd_type(KEY_ENTER);
    delay(25);

}

void loop() {}

void kbd_type(int key)
{
    kbd_type(key, 0);
}

void kbd_type(int key, int mcount, ...)
{
    va_list args;
    va_start(args, mcount);

    int modifier = 0;
    for (int i = 0; i < mcount; i++)
        modifier |= va_arg(args, int);

    DigiKeyboard.sendKeyStroke(key, modifier);
    va_end(args);
}
