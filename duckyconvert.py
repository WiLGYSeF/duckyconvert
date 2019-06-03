import re
import sys

AUTHOR = "WiLGYSeF"
VERSION = 1.2

g_globaldelay = 0

unprintablelist = [
	"ENTER", "ESC", "BACKSPACE", "TAB", "SPACE", "CAPS_LOCK", "PRINTSCREEN", "SCROLL_LOCK",
	"PAUSE", "INSERT", "HOME", "PAGE_UP", "DELETE", "END", "PAGE_DOWN", "RIGHT",
	"LEFT", "DOWN", "UP", "NUM_LOCK",

	"F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
	"F13", "F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22", "F23", "F24"
]

replaceunprintablemap = {
	"RETURN": "ENTER",
	"ESCAPE": "ESC",
	"CAPSLOCK": "CAPS_LOCK",
	"PRINTSCR": "PRINTSCREEN",
	"PRTSC": "PRINTSCREEN",
	"SCROLLLOCK": "SCROLL_LOCK",
	"BREAK": "PAUSE",
	"PAGEUP": "PAGE_UP",
	"PAGEDOWN": "PAGE_DOWN",
	"RIGHTARROW": "RIGHT",
	"LEFTARROW": "LEFT",
	"DOWNARROW": "DOWN",
	"UPARROW": "UP",
	"NUMLOCK": "NUM_LOCK"
}

modkeymap = {
	"CONTROL": "MODIFIERKEY_CTRL",
	"CTRL": "MODIFIERKEY_CTRL",
	"SHIFT": "MODIFIERKEY_SHIFT",
	"ALT": "MODIFIERKEY_ALT",
	"GUI": "MODIFIERKEY_GUI",
	"SUPER": "MODIFIERKEY_GUI",
	"WINDOWS": "MODIFIERKEY_GUI",
}

arduinoconvertmap = {
	"MODIFIERKEY_ALT": "KEY_LEFT_ALT",
	"MODIFIERKEY_CTRL": "KEY_LEFT_CTRL",
	"MODIFIERKEY_GUI": "KEY_LEFT_GUI",
	"MODIFIERKEY_SHIFT": "KEY_LEFT_SHIFT",
	"UP": "UP_ARROW",
	"DOWN": "DOWN_ARROW",
	"LEFT": "LEFT_ARROW",
	"RIGHT": "RIGHT_ARROW",
	"ENTER": "RETURN",
}

digisparkconvertmap = {
	"MODIFIERKEY_ALT": "MOD_ALT_LEFT",
	"MODIFIERKEY_CTRL": "MOD_CONTROL_LEFT",
	"MODIFIERKEY_GUI": "MOD_GUI_LEFT",
	"MODIFIERKEY_SHIFT": "MOD_SHIFT_LEFT",
	"UP": "ARROW_UP",
	"DOWN": "ARROW_DOWN",
	"LEFT": "ARROW_LEFT",
	"RIGHT": "ARROW_RIGHT"
}

helpstring = '''
Usage: duckyconvert.py [options] [input file] [output file]
Converts duckyscript code to Arduino/Teensy code

  -h, --help                    shows this help menu
  -a, --arduino                 convert to Arduino-style code (default)
  -t, --teensy                  convert to Teensy-style code
  -d, --digispark               convert to Digispark-style code
  -w, --wait [ms]               time to wait for initial keyboard recognition
  -p, --press-delay [ms]        delay between key press and release
                                  (default: 0)
  -l, --led [pin]               LED HIGH when typing, blink when done
                                  use built-in pin with "LED_BUILTIN"
'''

def main(argv):
	infname = None
	outfname = None

	keyboardinitwait = 2000
	convertType = "Arduino"
	ledpin = None
	pressdelay = 0

	literalarg = False

	i = 1
	while i < len(argv):
		if argv[i] == "--" and not literalarg:
			literalarg = True
			i += 1
			continue

		wasArg = not literalarg
		if not literalarg:
			if argv[i] == "-h" or argv[i] == "--help":
				print(helpstring)
				exit(0)

			elif argv[i] == "-a" or argv[i] == "--arduino":
				convertType = "Arduino"
			elif argv[i] == "-t" or argv[i] == "--teensy":
				convertType = "Teensy"
			elif argv[i] == "-d" or argv[i] == "--digispark":
				convertType = "Digispark"
			elif argv[i] == "-w" or argv[i] == "--wait":
				if i == len(argv) - 1:
					print(helpstring)
					exit(1)

				keyboardinitwait = int(argv[i + 1])
				if keyboardinitwait < 0:
					keyboardinitwait = 0

				i += 1
			elif argv[i] == "-l" or argv[i] == "--led":
				if i == len(argv) - 1:
					print(helpstring)
					exit(1)

				ledpin = argv[i + 1]
				if re.match(r'^([0-9]+|[A-Za-z_][A-Za-z0-9_]*)$', ledpin) is None:
					print("Error: invalid LED pin number", file=sys.stderr)
					print(helpstring)
					exit(1)
				i += 1
			elif argv[i] == "-p" or argv[i] == "--press-delay":
				if i == len(argv) - 1:
					print(helpstring)
					exit(1)

				pressdelay = int(argv[i + 1])
				if pressdelay < 0:
					pressdelay = 0

				i += 1
			elif argv[i][0] == "-":
				print(helpstring)
				exit(1)
			else:
				wasArg = False

		if not wasArg:
			if infname is None:
				infname = argv[i]
			elif outfname is None:
				outfname = argv[i]
			else:
				print(helpstring)
				exit(1)
		i += 1

	if infname is None:
		print(helpstring)
		exit(1)

	if not literalarg:
		if infname == "-":
			infname = None
		if outfname == "-":
			outfname = None

	inf = sys.stdin
	if infname is not None:
		inf = open(infname, "r")

	outf = sys.stdout
	if outfname is not None:
		outf = open(outfname, "w")

	status = convertToFile(inf, outf, {
		"keyboardinitwait": keyboardinitwait,
		"convertType": convertType,
		"ledpin": ledpin,
		"pressdelay": pressdelay
	})

	if infname is not None:
		inf.close()
	if outfname is not None:
		outf.close()

	if not status:
		exit(1)

def convertToFile(inf, outf, options={}):
	outf.write("//Generated by DuckyConvert v" + str(VERSION) + ", written by " + AUTHOR + "\n")

	if options["convertType"] == "Teensy":
		outf.write(
'''
#include <stdarg.h>

void setup()
{'''
		)
	elif options["convertType"] == "Arduino":
		outf.write(
'''
#include <stdarg.h>

#include <Keyboard.h>

#define KEY_SPACE ' '

#define KEY_PRINTSCREEN 0xce
#define KEY_SCROLL_LOCK 0xcf
#define KEY_PAUSE 0xd4
#define KEY_NUM_LOCK 0xdb
#define KEY_MENU 0xed

void setup()
{
	Keyboard.begin();
'''
		)
	elif options["convertType"] == "Digispark":
		outf.write(
'''
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

void setup()
{
'''
		)

	if options["ledpin"] is not None:
		outf.write(
'''
	pinMode(%s, OUTPUT);

	//wait for keyboard initialization
	for (int i = 0; i < %d; i++)
	{
		digitalWrite(%s, HIGH);
		delay(75);
		digitalWrite(%s, LOW);
		delay(75);
	}
''' % (options["ledpin"], options["keyboardinitwait"] // 150, options["ledpin"], options["ledpin"])
		)

		if options["keyboardinitwait"] % 150 != 0:
			outf.write(
'''
	delay(%d);
''' % (options["keyboardinitwait"] % 150)
			)

		outf.write(
'''
	digitalWrite(%s, HIGH);

''' % options["ledpin"]
		)
	else:
		outf.write(
'''
	//wait for keyboard initialization
	delay(%d);

''' % options["keyboardinitwait"]
		)

	if options["convertType"] == "Digispark":
		outf.write(
'''
	DigiKeyboard.sendKeyStroke(0);
	DigiKeyboard.delay(100);
'''
		)

	lastcmd = [None, None]
	linenum = 0

	for line in inf:
		linenum += 1

		if len(line.strip()) == 0:
			outf.write("\n")
			continue

		s, r, lastcmd = translateLine(line.rstrip("\n"), lastcmd, options)
		if r == 1:
			print("Error: could not translate line " + str(linenum) + ": " + line, file=sys.stderr)
			return False

		if s is not None:
			outf.write(indentStr(s, 1))

		if r != 2 and g_globaldelay > 0:
			outf.write(indentStr("delay(" + str(g_globaldelay) + ");", 1))

	if options["convertType"] == "Arduino":
		outf.write(
'''
	Keyboard.end();
'''
		)

	if options["ledpin"] is not None:
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
''' % (options["ledpin"], options["ledpin"])
		)
	else:
		outf.write(
'''\
}

void loop() {}
'''
		)

	outf.write(
'''
void keycombo(int key, int mcount, ...)
{
	va_list args;
	va_start(args, mcount);
'''
	)

	if options["convertType"] == "Teensy":
		outf.write(
'''
	int modifier = 0;
	for (int i = 0; i < mcount; i++)
		modifier |= va_arg(args, int);

	Keyboard.set_modifier(modifier);
	Keyboard.send_now();
'''
		)

		if options["pressdelay"] > 0:
			outf.write(
'''\
	delay(%d);
''' % (options["pressdelay"])
			)
		outf.write(
'''
	if(key != 0)
	{
		Keyboard.set_key1(key);
		Keyboard.send_now();
'''
		)

		if options["pressdelay"] > 0:
			outf.write(
'''\
		delay(%d);
''' % (options["pressdelay"])
			)

		outf.write(
'''
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
'''
		)
	elif options["convertType"] == "Arduino":
		outf.write(
'''
	for (int i = 0; i < mcount; i++)
		Keyboard.press(va_arg(args, int));

	if(key != 0)
		Keyboard.press(key);
'''
		)

		if options["pressdelay"] > 0:
			outf.write(
'''\
	delay(%d);
''' % (options["pressdelay"])
			)

		outf.write(
'''
	Keyboard.releaseAll();
}
'''
		)
	elif options["convertType"] == "Digispark":
		outf.write(
'''
	int modifier = 0;
	for (int i = 0; i < mcount; i++)
		modifier |= va_arg(args, int);

	DigiKeyboard.sendKeyStroke(key, modifier);

	va_end(args);
}
'''
		)

	if options["convertType"] == "Digispark":
		outf.write(
'''
void typekey(int key)
{
	DigiKeyboard.sendKeyStroke(key);
}
'''
		)
	else:
		outf.write(
'''
void typekey(int key)
{
	Keyboard.press(key);
'''
		)

		if options["pressdelay"] > 0:
			outf.write(
'''\
	delay(%d);
''' % (options["pressdelay"])
			)

		outf.write(
'''\
	Keyboard.release(key);
}
'''
		)

	return True

def translateLine(line, lastcmd, options={}):
	cmd = line
	val = None

	idx = line.find(" ")
	if idx != -1:
		cmd = line[0:idx]
		val = line[idx + 1:]

	return translateCmd(cmd, val, lastcmd, options)

def translateCmd(cmd, val, lastcmd, options={}):
	global g_globaldelay

	"""
	status:
	0 - success
	1 - failed
	2 - success, do not delay
	"""

	string = None
	status = 0

	failed = (None, 1, None)

	if cmd == "REM":
		if val is not None:
			string = "//" + val
		else:
			string = "//"
		status = 2
	elif cmd == "DEFAULT_DELAY" or cmd == "DEFAULTDELAY":
		if val is None:
			print("Error: expecting value for " + cmd, file=sys.stderr)
			return failed

		val = val.strip()
		g_globaldelay = int(val)
		status = 2
	elif cmd == "DELAY":
		if val is None:
			print("Error: expecting value for " + cmd, file=sys.stderr)
			return failed

		val = val.strip()
		string = "delay(" + str(int(val)) + ");"
		status = 2
	elif cmd == "STRING":
		if val is None:
			print("Error: expecting value for " + cmd, file=sys.stderr)
			return failed

		v = val.replace("\\", "\\\\").replace("\"", "\\\"")
		if options["convertType"] == "Digispark":
			string = "DigiKeyboard.print(\"" + v + "\");"
		else:
			string = "Keyboard.print(\"" + v + "\");"
	elif cmd.startswith("CONTROL") or cmd.startswith("CTRL") or cmd.startswith("SHIFT") or cmd.startswith("ALT") or cmd.startswith("GUI") or cmd.startswith("SUPER") or cmd.startswith("WINDOWS"):
		if val is not None:
			val = val.strip()

		#if the command is CTRL-SHIFT, etc.
		cspl = cmd.split("-")
		if len(cspl) > 1:
			cidx = 0
			while cidx < len(cspl):
				if cspl[cidx] not in modkeymap:
					break
				cidx += 1

			if cidx != 0:
				cmd = cspl[0]
				if val is None:
					val = " ".join(cspl[1:])
				else:
					val = " ".join(cspl[1:]) + " " + val

		string = getcombo(cmd, val, options)
		if string is None:
			print("Error: invalid key for " + cmd + ": " + val, file=sys.stderr)
			return failed
	elif cmd == "APP" or cmd == "MENU":
		string = "typekey(KEY_MENU);"
		"""
		#old code for context menu
		tstr, tstat, tlast = translateCmd("SHIFT", "F10", lastcmd, options)
		if tstat != 1:
			string = tstr
		"""
	elif cmd == "REPEAT":
		if lastcmd[0] is None:
			print("Error: no command to repeat", file=sys.stderr)
			return failed

		if val is not None:
			try:
				val = val.strip()
				rcount = int(val)

				if rcount <= 0:
					raise Exception
			except:
				print("Error: invalid repeat count: " + val, file=sys.stderr)
				return failed
		else:
			rcount = 1

		if rcount > 1:
			string = '''
for (int _repeat = 0; _repeat < %s; _repeat++)
{
''' % (rcount)

			tstr, tstat, tlast = translateCmd(lastcmd[0], lastcmd[1], lastcmd, options)
			if tstat == 1:
				return failed

			string += indentStr(tstr, 1)

			if g_globaldelay > 0:
				string += indentStr("delay(" + str(g_globaldelay) + ");", 1)

			string += "}\n"
		else:
			tstr, tstat, tlast = translateCmd(lastcmd[0], lastcmd[1], lastcmd, options)
			if tstat == 1:
				return failed

			string = tstr
		status = 2
	elif cmd in replaceunprintablemap or cmd in unprintablelist:
		c = cmd
		if c in replaceunprintablemap:
			c = replaceunprintablemap[c]

		if options["convertType"] == "Arduino":
			if c in arduinoconvertmap:
				c = arduinoconvertmap[c]
		elif options["convertType"] == "Digispark":
			if c in digisparkconvertmap:
				c = digisparkconvertmap[c]

		string = "typekey(KEY_" + c + ");"
	else:
		print("Error: unknown command: " + cmd, file=sys.stderr)
		return failed

	if cmd not in ["REM", "DEFAULT_DELAY", "DEFAULTDELAY", "REPEAT"]:
		lastcmd = [cmd, val]
	return (string, status, lastcmd)

def getcombo(cmd, key, options={}):
	if cmd not in modkeymap:
		return None

	modifiers = [modkeymap[cmd]]

	if key is not None and key != "":
		kspl = key.split(" ")
		i = 0

		while i < len(kspl):
			k = kspl[i]
			if k not in modkeymap:
				break

			modifiers.append(modkeymap[k]);
			i += 1
		key = " ".join(kspl[i:])

	if options["convertType"] == "Arduino":
		modifiers = list(map(lambda x: arduinoconvertmap[x], modifiers))
	elif options["convertType"] == "Digispark":
		modifiers = list(map(lambda x: digisparkconvertmap[x], modifiers))

	if key is not None and key != "":
		keyconst = getkeyfromstr(key, options)
		if keyconst is None:
			return None
	else:
		keyconst = "0"

	return "keycombo(" + keyconst + ", " + str(len(modifiers)) + ", " + ", ".join(modifiers) + ");"

def indentStr(s, indent):
	r = ""
	for line in s.split("\n"):
		r += ("\t" * indent) + line + "\n"

	return r

def getkeyfromstr(key, options={}):
	asciinamemap = {
		"-": "MINUS",
		"=": "EQUAL",
		"{": "LEFT_BRACE",
		"}": "RIGHT_BRACE",
		"\\": "BACKSLASH",
		";": "SEMICOLON",
		"\"": "QUOTE",
		"~": "TILDE",
		",": "COMMA",
		".": "PERIOD",
		"/": "SLASH"
	}

	key = key.upper()
	if key[0] == 'F' and (len(key) == 2 or len(key) == 3):
		try:
			n = int(key[1:])
			if n >= 1 and n <= 24:
				return "KEY_" + key
			return None
		except:
			return None

	if len(key) == 1:
		if key.isalpha() or key.isdigit() or key in asciinamemap:
			if options["convertType"] == "Teensy" or options["convertType"] == "Digispark":
				return "KEY_" + key
			elif options["convertType"] == "Arduino":
				return "'" + key + "'"

	if key in replaceunprintablemap:
		key = replaceunprintablemap[key]

	if key in unprintablelist:
		if options["convertType"] == "Arduino":
			if key in arduinoconvertmap:
				key = arduinoconvertmap[key]
		elif options["convertType"] == "Digispark":
			if key in digisparkconvertmap:
				key = digisparkconvertmap[key]
		return "KEY_" + key

	return None

if __name__ == "__main__":
	main(sys.argv)
