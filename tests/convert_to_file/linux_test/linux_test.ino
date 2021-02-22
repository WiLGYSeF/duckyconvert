#include <stdarg.h>

#include <Keyboard.h>

#define kbd_print(x) Keyboard.print(x)
#define kbd_println(x) Keyboard.println(x)

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

void setup()
{
    Keyboard.begin();
    // wait for keyboard initialization
    delay(2000);


    // spawn terminal
    kbd_type('T', 2, KEY_LEFT_CTRL, KEY_LEFT_ALT);
    delay(25);
    delay(300);

    // move to bottom corner of screen
    kbd_type(KEY_F7, 1, KEY_LEFT_ALT);
    delay(25);
    kbd_type(KEY_DOWN, 1, KEY_LEFT_SHIFT);
    delay(25);

    for (int _repeat = 0; _repeat < 3; _repeat++)
    {
        kbd_type(KEY_DOWN, 1, KEY_LEFT_SHIFT);
        delay(25);
    }
    kbd_type(KEY_ENTER);
    delay(25);

    // payload
    kbd_print("echo \"If you can read this, you are in big trouble\"");
    delay(25);
    kbd_type(KEY_ENTER);
    delay(25);
    Keyboard.end();
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

    for (int i = 0; i < mcount; i++)
        Keyboard.press(va_arg(args, int));
    // delay(0);

    if(key != 0)
        Keyboard.write(key);
    // delay(0);

    Keyboard.releaseAll();
    va_end(args);
}
