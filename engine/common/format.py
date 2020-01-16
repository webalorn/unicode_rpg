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

class FormatMap:
	def __init__(self, size):
		self.size = size
		def_format = COLORS.get_default_format()
		self.map = [[def_format for _ in range(self.size[1])] for _ in range(self.size[0])]

	def set(self, rect, code): # Possible optim : manage each line with a list / set
		if code is None:
			return
		code = COLORS.format_to_code(code)
		(row1, col1), (row2, col2) = rect
		for row in range(row1, row2):
			for col in range(col1, col2):
				self.map[row][col] = code

	def set_point(self, point, code):
		if not code is None:
			code = COLORS.format_to_code(code)
			row, col = point
			self.map[row][col] = code

	def get_final_map(self):
		real_map = [[] for _ in range(len(self.map))]
		for i_line, l in enumerate(self.map):
			for i in range(len(l)-1, -1, -1):
				if i != 0 and l[i-1] == l[i]:
					l[i] = ""
			real_map[i_line] = l
		return real_map

class FormatMapRel:
	def __init__(self, format_map, rel_pos, area_size):
		self.pos = rel_pos
		self.area = (rel_pos, add_coords(rel_pos, area_size))

		self.format_map = format_map
		while isinstance(self.format_map, FormatMapRel):
			move = self.format_map.pos
			
			self.pos = add_coords(self.pos, move)
			area = (add_coords(self.area[0], move), add_coords(self.area[1], move))
			self.area = intersect_rects(
				(add_coords(self.area[0], move), add_coords(self.area[1], move)),
				self.format_map.area
			)

			self.format_map = self.format_map.format_map

	def set(self, rect, form):
		if not rect:
			rect = self.area
		else:
			rect = (add_coords(rect[0], self.pos), add_coords(rect[1], self.pos))
			rect = intersect_rects(rect, self.area)
		self.format_map.set(rect, form)

	def set_point(self, point, form):
		row, col = add_coords(point, self.pos)
		if self.area[0][0] <= row < self.area[1][0] and self.area[0][1] <= col < self.area[1][1]:
			self.format_map.set_point((row, col), form)		


COLORS = ColorManager