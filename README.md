# duckyconvert
Converts duckyscript to Arduino/Teensy keyboard HID code.

## Duckyscript Syntax
A description of the different commands in duckyscript and how they convert.
Some commands have been extended from the [official specification](https://github.com/hak5darren/USB-Rubber-Ducky/wiki/Duckyscript) to add more capability.

### REM
Arguments: ANY

Insert a comment into the converted code

```
REM This is a comment
```

### DEFAULT_DELAY or DEFAULTDELAY
Arguments: Milliseconds (int)

Add a default delay after each command run if no delay is explicitly done.

```
DEFAULT_DELAY 100
```
Delays by 100ms after all further commands.

### DELAY
Arguments: Milliseconds (int)

Delay for n milliseconds.

```
DELAY 500
```
Delays for 500ms.

### STRING
Arguments: ANY

Type the argument string as a keyboard, automatically applies any SHIFT modifiers.

```
STRING This is a test, 123
```
Types "This is a test, 123".

### WINDOWS or GUI or SUPER<sup>+</sup>
Arguments: Key (char) or Unprintable Key (string), optional <sup>*</sup>

Press the WINDOWS/GUI/SUPER key if no argument.
Hold the WINDOWS/GUI/SUPER key and press the Key specified, then release.

```
GUI r
```
Presses GUI and R, opens the *Run* box on Windows.

<sup>+</sup> SUPER is not in the official specification.

<sup>*</sup> WINDOWS/GUI/SUPER supports more keys than in the official specification.

### MENU or APP
Arguments: NONE

```
MENU
```
Opens the context-menu.

Press the context-menu key (right click)

### SHIFT
Arguments: Key (char) or Unprintable Key (string), optional <sup>*</sup>

Press the SHIFT key if no argument.
Hold the SHIFT key and press the Key specified, then release.

```
SHIFT TAB
```
Presses SHIFT and TAB.

<sup>*</sup> SHIFT supports more keys than in the official specification.

### ALT
Arguments: Key (char) or Unprintable Key (string), optional <sup>*</sup>

Press the ALT key if no argument.
Hold the ALT key and press the Key specified, then release.

```
ALT F4
```
Presses ALT and F4, closes the currently opened window.

<sup>*</sup> ALT supports more keys than in the official specification.

### CONTROL or CTRL
Arguments: Key (char) or Unprintable Key (string), optional <sup>*</sup>

Press the CTRL key if no argument.
Hold the CTRL key and press the Key specified, then release.

```
CTRL S
```
Presses CTRL and S.

<sup>*</sup> CTRL supports more keys than in the official specification.

### REPEAT
Arguments: Times (int), optional

Repeat the last command n times. Default is once.

```
DOWN
REPEAT 5
```
Presses DOWN 6 times total.

### *Unprintable Key*
Arguments: NONE

Type the unprintable key.

```
NUM_LOCK
```
Toggles NUMLOCK.

## Unprintable Key List
 - ENTER <sup>*</sup>
 - ESC
 - BACKSPACE <sup>*</sup>
 - TAB
 - SPACE
 - CAPS_LOCK
 - F1, F2, ..., F24 <sup>*</sup>
 - PRINTSCREEN
 - SCROLL_LOCK
 - PAUSE
 - INSERT
 - HOME
 - PAGE_UP
 - DELETE
 - END
 - PAGE_DOWN
 - RIGHTARROW or RIGHT
 - LEFTARROW or LEFT
 - DOWNARROW or DOWN
 - UPARROW or UP
 - NUM_LOCK

<sup>*</sup> Not specified in the official documentation, but ENTER is used in the payload examples.

## Using Multiple Modifiers
To press keys with multiple modifiers, the converter supports different formats:
```
CTRL SHIFT F
CTRL-SHIFT F
CTRL-SHIFT-F
CTRL SHIFT ALT C
CTRL-SHIFT ALT C
CTRL-SHIFT-ALT C
SHIFT ALT ,       (types ALT <)
SHIFT-ALT .       (types ALT >)
```
Note that none of these are actually specified in the official documentation, but are used by multiple payload examples. Some formats are also mentioned in the [duckencode help menu](https://github.com/hak5darren/USB-Rubber-Ducky/blob/master/Encoder/README).
