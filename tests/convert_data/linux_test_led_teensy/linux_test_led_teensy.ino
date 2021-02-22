#include <stdarg.h>

#define kbd_print(x) Keyboard.print(x)
#define kbd_println(x) Keyboard.println(x)

void setup()
{
    pinMode(LED_BUILTIN, OUTPUT);

    // wait for keyboard initialization
    for (int i = 0; i < 13; i++)
    {
        digitalWrite(LED_BUILTIN, HIGH);
        delay(75);
        digitalWrite(LED_BUILTIN, LOW);
        delay(75);
    }
    delay(50);
    digitalWrite(LED_BUILTIN, HIGH);



    // spawn terminal

    delay(25);
    kbd_type(KEY_T, 2, MODIFIERKEY_CTRL, MODIFIERKEY_ALT);

    delay(25);
    delay(300);

    delay(25);

    // move to bottom corner of screen

    delay(25);
    kbd_type(KEY_F7, 1, MODIFIERKEY_ALT);

    delay(25);
    kbd_type(KEY_DOWN, 1, MODIFIERKEY_SHIFT);

    delay(25);

    for (int _repeat = 0; _repeat < 3; _repeat++)
    {
        kbd_type(KEY_DOWN, 1, MODIFIERKEY_SHIFT);
        delay(25);
    }


    delay(25);
    kbd_type(KEY_ENTER);

    delay(25);

    // payload

    delay(25);
    kbd_print("echo \"If you can read this, you are in big trouble\"");

    delay(25);
    kbd_type(KEY_ENTER);

    delay(25);

}

void loop()
{
    digitalWrite(LED_BUILTIN, HIGH);
    delay(500);
    digitalWrite(LED_BUILTIN, LOW);
    delay(500);
}

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

    Keyboard.set_modifier(modifier);
    Keyboard.send_now();
    // delay(0);

    if(key != 0)
    {
        Keyboard.set_key1(key);
        Keyboard.send_now();
        // delay(0);
        Keyboard.set_modifier(0);
        Keyboard.set_key1(0);
        Keyboard.send_now();
    }else
    {
        Keyboard.set_modifier(0);
        Keyboard.send_now();
    }
    va_end(args);
}
