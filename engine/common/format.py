from .util import *

# TODO : for other platformes, for 8-16 bits terminal

_colors_names = ["black", "red", "green", "yellow", "blue", "magenta", "cyan"]

FORE = {
	**{ k : "\u001b[38;5;{}m".format(str(k)) for k in range(256) }, # 256 colors mode
	**{ v : "\u001b[{}m".format(str(i+30)) for i, v in enumerate(_colors_names) },
	**{ "light_" + v : "\u001b[{}m".format(str(i+90)) for i, v in enumerate(_colors_names) },
	**{
		"light_gray" : "\u001b[37m",
		"white" : "\u001b[97m",
	},
}

BACK = {
	**{ k : "\u001b[48;5;{}m".format(str(k)) for k in range(256) }, # 256 colors mode
	**{ v : "\u001b[{}m".format(str(i+40)) for i, v in enumerate(_colors_names) },
	**{ "light_" + v : "\u001b[{}m".format(str(i+100)) for i, v in enumerate(_colors_names) },
	**{
		"light_gray" : "\u001b[47m",
		"white" : "\u001b[107m",
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

if True: # TODO : if 256 color mode ok
	BACK["black"] = BACK[233]
	FORE["white"] = FORE[254]



DEF_FORMAT = F_STYLE["reset"] + FORE["white"] + BACK["black"]
EMPTY_FORMAT = (None, None, []) # None means 'do nothing', EMPTY_FORMAT will reset the style

def format_to_code(form):
	fg, back, styles = form
	style = styles or []
	l = []
	if fg != None: l.append(FORE[fg])
	if back != None: l.append(BACK[back])
	for s in styles:
		l.append(F_STYLE[s])
	return "".join(l)

class FormatMap:
	def __init__(self, size):
		self.size = size
		self.map = [['' for _ in range(self.size[1])] for _ in range(self.size[0])]

	def set(self, rect, form): # Possible optim : manage each line with a list / set
		if form == None:
			return
		code = format_to_code(form)
		(row1, col1), (row2, col2) = rect
		for row in range(row1, row2):
			for col in range(col1, col2):
				self.map[row][col] = code

	def get_final_map(self):
		for l in self.map:
			for i in range(len(l)-1, -1, -1):
				code = l[i]
				if (i == 0 or l[i-1] != code):
					l[i] = DEF_FORMAT + l[i]
				else:
					l[i] = ""
		return self.map

class FormatMapRel:
	def __init__(self, format_map, rel_pos, area_size):
		self.pos = rel_pos
		self.area = (rel_pos, add_coords(rel_pos, area_size))

		self.format_map = format_map
		while isinstance(self.format_map, FormatMapRel):
			move = self.format_map.pos
			# print("MOVE", self.pos, self.area, "DE", move)
			
			self.pos = add_coords(self.pos, move)
			area = (add_coords(self.area[0], move), add_coords(self.area[1], move))
			self.area = intersect_rects(
				(add_coords(self.area[0], move), add_coords(self.area[1], move)),
				self.format_map.area
			)
			# print(self.pos, self.area, "AREA", area, "INTER", self.format_map.area)

			self.format_map = self.format_map.format_map

	def set(self, rect, form):
		rect = (add_coords(rect[0], self.pos), add_coords(rect[1], self.pos))
		rect = intersect_rects(rect, self.area)
		self.format_map.set(rect, form)