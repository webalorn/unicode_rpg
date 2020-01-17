from .base import *
from engine.client.keys import *
from engine import *
from pathlib import Path
import re

class BoxW(BaseWidget):
	BORDER = "border"
	BORDER_FOCUSED = "border"
	BORDER_STYLE = None
	BORDER_FOCUSED_STYLE = None

	def __init__(self, *kargs, border=0, **kwargs):
		self.border = border
		super().__init__(*kargs, **kwargs)

	def get_real_padding(self):
		(a, b), (c, d) = super().get_real_padding()
		return ((a+self.border, b+self.border), (c+self.border, d+self.border))

	def draw_border(self):
		border = min(self.border, self.size[0], self.size[1])
		nr, nc = self.size
		if border:
			symbs = get_charset(self.BORDER_FOCUSED or self.BORDER if self.focused else self.BORDER)
			style = (self.BORDER_FOCUSED_STYLE if self.focused else None) or self.BORDER_STYLE
			for decal in range(min(border, nr, nc)):
				for row in range(decal, nr-decal):
					self.grid[row][decal] = symbs[0]
					self.grid[row][-1-decal] = symbs[0]
				self.grid[decal][decal:nc-decal] = [symbs[1]] * (nc-decal*2)
				self.grid[-1-decal][decal:nc-decal] = [symbs[1]] * (nc-decal*2)
				self.grid[decal][decal] = symbs[2]
				self.grid[decal][-1-decal] = symbs[3]
				self.grid[-1-decal][decal] = symbs[4]
				self.grid[-1-decal][-1-decal] = symbs[5]

			if style:
				style = get_skin_format(style)
				set_area_format(self.format_map, ((0, 0), (border, nc)), style)
				set_area_format(self.format_map, ((nr-border, 0), (nr, nc)), style)
				set_area_format(self.format_map, ((0, 0), (nr, border)), style)
				set_area_format(self.format_map, ((0, nc-border), (nr, nc)), style)

	def draw_widget(self):
		super().draw_widget()
		self.draw_border()

class TextW(BoxW):
	RE_SPACE = re.compile(r'(\S+)')

	def __init__(self, text, *kargs, align="left", v_align="top", w_break=False,
				text_format=None, strip_lines=True, size=None, **kwargs):
		if size is None:
			size = (1, len(text))
		super().__init__(*kargs, size=size, **kwargs)
		self.set_text(text)
		self.align = align
		self.v_align = v_align
		self.w_break = w_break
		self.text_format = self.parse_format(text_format)
		self.anchor_down = False
		self.strip_lines = strip_lines

	def set_text(self, text):
		self.last_real_text = None
		self.text = list(text) # To allow append / pop

	def get_displayed_text_list(self):
		return self.text

	def get_real_text(self):
		return "".join(self.text)

	def get_broke_text(self, larg):
		PROFILER.start("get_broke_text")
		txt = self.get_displayed_text_list()
		txt_hash = hash("".join(txt))
		if self.last_real_text != None and self.last_real_text[1:] == (larg, txt_hash):
			return self.last_real_text[0]

		real_txt = []
		if self.w_break:
			real_txt = [txt[k:k+larg] for k in range(0, len(txt), larg)]
			
		else:
			joined_txt = "".join(txt)
			splited = [self.RE_SPACE.split(l) for l in joined_txt.splitlines()]
			if joined_txt and joined_txt[-1] == "\n":
				splited.append("") # Because splitlines ignore the last "\n"

			real_txt = []
			for i_w_list, words in enumerate(splited):
				real_txt.append([])
				for i_word, word in enumerate(words):
					if i_word%2:
						if real_txt and (not real_txt[-1] or len(real_txt[-1]) + len(word) <= larg):
							real_txt[-1].extend(list(word))
							while len(real_txt[-1]) > larg:
								w = real_txt.append(real_txt[-1][larg:])
								real_txt[-2] = real_txt[-2][:larg]
						else:
							real_txt.append(list(word))
					else:
						pass
						for c in word:
							if not real_txt or len(real_txt[-1]) >= larg:
								real_txt.append([])
							real_txt[-1].append(c)
		if self.strip_lines:
			real_txt = [list("".join(l).strip()) for l in real_txt]
		self.last_real_text = (real_txt, larg, txt_hash)
		PROFILER.end("get_broke_text")
		return real_txt

	def draw_widget(self):
		super().draw_widget()
		padd = self.get_real_padding()
		size = self.get_inner_size()
		if size[1] >= 1 and size[0] >= 1:
			lines = self.get_broke_text(size[1])
			if self.anchor_down:
				lines = lines[-size[0]:]

			if self.v_align == "bottom":
				lines = lines[-size[0]:]
				lines = [[]] * (size[0]-len(lines)) + lines
			elif self.v_align == "center":
				lines = lines[:size[0]]
				lines = [[]] * ((size[0] - len(lines))//2) + lines

			for row, l in enumerate(lines[:size[0]]):
				if self.align == "center":
					l = [' '] * ((size[1] - len(l))//2) + l
				elif self.align == "right":
					l = [' '] * (size[1] - len(l)) + l

				for col, val in enumerate(l):
					r, c = row+padd[0][0], col + padd[1][0]
					if self.in_grid(r, c):
						self.grid[r][c] = val

				c1, c2 = 0, len(l)
				while c1 < len(l) and l[c1] == ' ': c1 += 1
				while c2 > 0 and l[c2-1] == ' ': c2 -= 1
				r = row + padd[0][0]
				c1, c2 = c1 + padd[1][0], c2 + padd[1][0]
				format = inherit_union(self.displayed_format, self.text_format)
				set_area_format(self.format_map, ((r, c1), (r+1, c2)), format)

class BarW(BoxW): # TODO: use skin for drawing and colors + default skin + default skin focused
	FORMAT = "bar"

	def __init__(self, start_at=1, *kargs, size=9, maxi=0, **kwargs):
		self.maxi = max(0, maxi) # 0 : percentage [0 -> 1]. Otherwise, between 0 and maxi
		self.set(start_at)
		if isinstance(size, (int, float)):
			size = (1, size)
		super().__init__(*kargs, size=size, **kwargs)

	def set(self, value):
		if self.maxi:
			self.value = min(max(value, 0), self.maxi)
		else:
			self.value = min(max(value, 0), 1)

	def percent(self): # Between 0 and 1
		if self.maxi:
			return self.value / self.maxi
		return self.value

	def draw_widget(self):
		super().draw_widget()
		bar_chars = get_charset("bar")

		length = self.size[1]
		percent = self.percent()
		plain_l = int(length * percent)
		queue = None
		if plain_l < length:
			frac = length * percent - plain_l
			i_car = int(len(bar_chars) * frac)
			if i_car:
				queue = bar_chars[i_car]

		plain_char = bar_chars[-1]
		for row in self.grid:
			row[:plain_l] = plain_char * plain_l
			if queue:
				row[plain_l] = queue

class ImageW(BaseWidget):
	SOURCE_PATH = C.IMG_PATH

	def __init__(self, path, *kargs, back_color=None, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.back_color = back_color
		self.load(path)

	def load(self, path):
		path = Path(self.SOURCE_PATH) / path
		self.img = []
		try:
			with open(str(path), "r") as f:
				img = f.readlines()
				img = [[int(col) for col in row.split()] for row in img]
				if len(img)%2:
					img.append([-1]*len(img[0]))
				self.img = [list(zip(r1, r2)) for r1, r2 in zip(img[0::2], img[1::2])]

				nbcols = len(self.img[0]) if self.img else 0
				self.resize((len(self.img), nbcols))
		except OSError as e:
			log("Could not open/read file {} because {}".format(path, str(e)))

	def draw_widget(self):
		super().draw_widget()
		self.grid = [["▄"]*self.size[1] for _ in range(self.size[0])]
		back_color = 'back' if self.back_color is None else self.back_color
		for i_row, row in enumerate(self.img):
			for i_col, (back, front) in enumerate(row):
				if back == -1:
					back = back_color
				if front == -1:
					front = back_color
				set_point_format(self.format_map, (i_row, i_col), (front, back, []))
