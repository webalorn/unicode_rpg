from .util import *
from .exceptions import *
from .log import log

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
		**{ k : "38;5;{}".format(k) for k in range(256) }, # 256 colors mode
		**{ v : str(i+30) for i, v in enumerate(NAMES) }, # 16 colors mode
		**{ "light_" + v : str(i+90) for i, v in enumerate(NAMES) }, # 16 colors mode
		**{
			"light_gray" : "37",
			"white" : "97",
			"text" : "30",
		},
	}

	BACK = {
		**{ k : "48;5;{}".format(k) for k in range(256) }, # 256 colors mode
		**{ v : str(i+40) for i, v in enumerate(NAMES) }, # 16 colors mode
		**{ "light_" + v : str(i+100) for i, v in enumerate(NAMES) }, # 16 colors mode
		**{
			"light_gray" : "47",
			"white" : "107",
			"back" : "107",
		},
	}

	F_STYLE = {
		"reset" : "0",
		"bold" : "1",
		"dim" : "2",
		"underlined" : "4",
		"blink" : "5",
		"reversed" : "7",
		"hidden" : "8",
	}

	@classmethod
	def format_to_code(cls, form):
		if len(form) != 3:
			raise Error("Invalid format code", form)
			return ""
		fg, back, styles = form
		styles = ["reset"] + (sorted(styles) or [])

		# fg = cls.FORE["text"] if fg is None else cls.FORE[fg]
		# back = cls.BACK["back"] if back is None else cls.BACK[back]
		fg = None if fg is None else cls.FORE[fg]
		back = None if back is None else cls.BACK[back]
		styles = ";".join([cls.F_STYLE[s] for s in styles])
		return (styles, fg, back)

	@classmethod
	def get_default_format(cls):
		return cls.format_to_code(("text", "back", []))

	@classmethod
	def add(cls, name, code):
		if isinstance(code, str):
			code = (cls.FORE.get(code, 'black'), cls.BACK.get(code, 'white'))
		elif isinstance(code, int):
			code = ("38;5;{}".format(code), "48;5;{}".format(code))
		elif isinstance(code, (list, tuple)) and len(code) == 3: # True colors mode
			code = ("38;2;{};{};{}".format(*code), "48;2;{};{};{}".format(*code))
		else:
			log("Unknown code type", code, err=True)
			return
		cls.FORE[name] = code[0]
		cls.BACK[name] = code[1]

	@classmethod
	def convert_map(cls, grid, config):
		default = COLORS.get_default_format()
		if not config.get("main", "colors"):
			for row in grid:
				row[:] = ['']*len(row)
			grid[0][0] = "\033[{}m".format(";".join(default))
			return

		last_format = (None, None, None)
		for i_row, row in enumerate(grid):
			for i_col, format in enumerate(row):
				format = default if format is None else (format[0] or default[0], format[1] or default[1], format[2] or default[2])
				if format[0] != last_format[0]: # To ensure text and background color are set
					to_print = ";".join(format)
				else:
					r = [] if format[1] == last_format[1] else [format[1]]
					if format[2] != last_format[2]:
						r.append(format[2])
					to_print = ";".join(r)
				if to_print:
					to_print = "\033[" + to_print + "m"
				grid[i_row][i_col] = to_print
				last_format = format

COLORS = ColorManager