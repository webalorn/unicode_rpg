from .util import *
from .exceptions import *

"""
	Format of format codes : (foreground, background, special) OR None
	None will return empty string (keep format)
	foreground and background are either :
	- None : default color
	- string : name of a color
	- int : code of a color
	special must be a list of keys of F_STYLE
"""

EMPTY_FORMAT = (None, None, []) # None means 'do nothing' while EMPTY_FORMAT will reset the style

class ColorManager:
	NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan"]

	FORE = {
		**{ k : "\u001b[38;5;{}m".format(k) for k in range(256) }, # 256 colors mode
		**{ v : "\u001b[{}m".format(i+30) for i, v in enumerate(NAMES) }, # 16 colors mode
		**{ "light_" + v : "\u001b[{}m".format(i+90) for i, v in enumerate(NAMES) }, # 16 colors mode
		**{
			"light_gray" : "\u001b[37m",
			"white" : "\u001b[97m",
			"text" : "\u001b[30m",
		},
	}

	BACK = {
		**{ k : "\u001b[48;5;{}m".format(k) for k in range(256) }, # 256 colors mode
		**{ v : "\u001b[{}m".format(i+40) for i, v in enumerate(NAMES) }, # 16 colors mode
		**{ "light_" + v : "\u001b[{}m".format(i+100) for i, v in enumerate(NAMES) }, # 16 colors mode
		**{
			"light_gray" : "\u001b[47m",
			"white" : "\u001b[107m",
			"back" : "\u001b[107m",
		},
	}

	F_STYLE = {
		"reset" : "\u001b[0m",
		"bold" : "\u001b[1m",
		"dim" : "\u001b[2m",
		"underlined" : "\u001b[4m",
		"blink" : "\u001b[5m",
		"reversed" : "\u001b[7m",
		"hidden" : "\u001b[8m",
	}

	@classmethod
	def format_to_code(cls, form):
		if len(form) != 3:
			raise Error("Invalid format code", form)
			return ""
		fg, back, styles = form
		style = styles or []
		l = [cls.F_STYLE["reset"]]
		l.append(cls.FORE["text"] if fg is None else cls.FORE[fg])
		l.append(cls.BACK["back"] if back is None else cls.BACK[back])
		for s in styles:
			l.append(cls.F_STYLE[s])
		return "".join(l)

	@classmethod
	def get_default_format(cls):
		return cls.F_STYLE["reset"] + cls.format_to_code(("text", "back", []))

	@classmethod
	def add(cls, name, code):
		if isinstance(code, str):
			code = (cls.FORE.get(code, 'black'), cls.BACK.get(code, 'white'))
		elif isinstance(code, int):
			code = ("\u001b[38;5;{}m".format(code), "\u001b[48;5;{}m".format(code))
		elif isinstance(code, (list, tuple)) and len(code) == 3: # True colors mode
			code = ("\x1b[38;2;{};{};{}m".format(*code), "\x1b[48;2;{};{};{}m".format(*code))
		else:
			log("Unknown code type", code, err=True)
			return
		cls.FORE[name] = code[0]
		cls.BACK[name] = code[1]

COLORS = ColorManager