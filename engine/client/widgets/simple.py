from .base import *
from engine.client.keys import *
from engine import *

class BoxW(BaseWidget):
	BORDER = "border"
	BORDER_FOCUSED = "border"

	def __init__(self, *kargs, border=0, background=None, **kwargs):
		self.border = border
		self.background = background
		super().__init__(*kargs, **kwargs)

	def get_real_padding(self):
		(a, b), (c, d) = super().get_real_padding()
		return ((a+self.border, b+self.border), (c+self.border, d+self.border))

	def clear_grid(self):
		self.grid = [[self.background for _ in range(self.size[1])] for _ in range(self.size[0])]

	def draw_border(self):
		border = min(self.border, self.size[0], self.size[1])
		nr, nc = self.size
		if border:
			symbs = get_charset(self.BORDER_FOCUSED or self.BORDER if self.focused else self.BORDER)
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

	def draw_after(self):
		self.draw_border()

class SimpleTextW(BoxW):
	def __init__(self, text, *kargs, align="left", v_align="top", w_break=False,
				text_format=None, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.set_text(text)
		self.align = align
		self.v_align = v_align
		self.w_break = w_break
		self.text_format = text_format

	def set_text(self, text):
		self.last_real_text = None
		self.text = list(text) # To allow append / pop

	def get_displayed_text_list(self):
		return self.text

	def get_real_text():
		return "".join(self.text)

	def get_broke_text(self, larg):
		PROFILER.start("get_broke_text")
		txt = self.get_displayed_text_list()
		txt_hash = hash("".join(txt))
		if self.last_real_text != None and self.last_real_text[1:] == (larg, txt_hash):
			return self.last_real_text[0]

		if self.w_break:
			self.last_real_text = ([txt[k:k+self.size[1]] for k in range(0, len(txt), self.size[1])], larg, txt_hash)
		else:
			splited = [l.split() for l in "".join(txt).splitlines()]

			lines = []
			for i_w_list, words in enumerate(splited):
				if i_w_list:
					lines.append([])
				for word in words:
					if lines and (not lines[-1] or len(lines[-1]) + 1 + len(word) <= larg):
						if lines[-1]:
							lines[-1].append(" ")
						lines[-1].extend(list(word))
						while len(lines[-1]) > larg:
							w = lines.append(lines[-1][larg:])
							lines[-2] = lines[-2][:larg]
					else:
						lines.append(list(word))
			self.last_real_text = (lines, larg, txt_hash)
		PROFILER.end("get_broke_text")
		return self.last_real_text[0]


	def draw_before(self):
		super().draw_before()
		padd = self.get_real_padding()
		size = self.get_inner_size()
		if self.size[1] >= 1:
			lines = self.get_broke_text(size[1])

			if self.v_align == "bottom":
				lines = lines[-size[0]:]
				lines = [[]] * (size[0]-len(lines)) + lines
			elif self.v_align == "center":
				lines = lines[:size[0]]
				lines = [[]] * ((size[0] - len(lines))//2) + lines

			for row, l in enumerate(lines):
				if self.align == "center":
					l = [' '] * ((size[1] - len(l))//2) + l
				elif self.align == "right":
					l = [' '] * (size[1] - len(l)) + l

				for col, val in enumerate(l): # TODO : Optim
					r, c = row+padd[0][0], col + padd[1][0]
					if self.in_grid(r, c):
						self.grid[r][c] = val

				c1, c2 = 0, len(l)
				while c1 < len(l) and l[c1] == ' ': c1 += 1
				while c2 > 0 and l[c2-1] == ' ': c2 -= 1
				format = inherit_union(self.displayed_format, self.text_format)
				self.format_map.set(((row, c1), (row+1, c2)), format)

class BarW(BoxW): # TODO: use skin for drawing and colors + default skin + default skin focused
	FORMAT = "bar"

	def __init__(self, start_at=1, *kargs, size=9, background=0, maxi=0, **kwargs):
		self.maxi = max(0, maxi) # 0 : percentage [0 -> 1]. Otherwise, between 0 and maxi
		self.set(start_at)
		if isinstance(size, (int, float)):
			size = (1, size)
		super().__init__(*kargs, size=size, background=background, **kwargs)

	def set(self, value):
		if self.maxi:
			self.value = min(max(value, 0), self.maxi)
		else:
			self.value = min(max(value, 0), 1)

	def percent(self): # Between 0 and 1
		if self.maxi:
			return self.value / self.maxi
		return self.value

	def draw_before(self):
		super().draw_before()
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