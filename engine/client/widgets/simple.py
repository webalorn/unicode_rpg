from .base import *
import data.consts as C
from engine.client.keys import *
from engine import *

class BoxW(BaseWidget):
	def __init__(self, *kargs, border=0, background=None, fusion=False, **kwargs):
		self.border = border
		self.background = background
		self.fusion = fusion
		super().__init__(*kargs, **kwargs)

	def get_real_padding(self):
		(a, b), (c, d) = super().get_real_padding()
		return ((a+self.border, b+self.border), (c+self.border, d+self.border))

	def clear_grid(self):
		self.grid = [[self.background for _ in range(self.size[1])] for _ in range(self.size[0])]

	def draw_border(self):
		border = min(self.border, self.size[0], self.size[1])
		nr, nc = self.size
		if border and self.fusion:
			for decal in range(border):
				for row in range(nr):
					self.grid[row][decal] = 2
					self.grid[row][-1-decal] = 2
				self.grid[decal] = [2] * nc
				self.grid[-1-decal] = [2] * nc
		elif border:
			for decal in range(border):
				for row in range(nr):
					self.grid[row][decal] = "border.vert"
					self.grid[row][-1-decal] = "border.vert"
				self.grid[decal] = ["border.hor"] * nc
				self.grid[-1-decal] = ["border.hor"] * nc
				self.grid[0][0] = "border.down_right"
				self.grid[0][-1] = "border.down_left"
				self.grid[-1][0] = "border.up_right"
				self.grid[-1][-1] = "border.up_left"

	def draw_after(self):
		self.draw_border()

class SimpleTextW(BoxW):
	def __init__(self, text, *kargs, align="left", w_break=False, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.set_text(text)
		self.align = align
		self.w_break = w_break

	def set_text(self, text):
		self.text = list(text) # To allow append / pop

	def get_displayed_text_list(self):
		return self.text

	def get_real_text():
		return "".join(self.text)

	def get_broke_text(self, larg):
		txt = self.get_displayed_text_list()
		if self.w_break:
			return [txt[k:k+self.size[1]] for k in range(0, len(txt), self.size[1])]
		else:
			cuts = [0]
			for i, v in enumerate(txt):
				if v == "\n":
					cuts.append(i)
			cuts.append(len(txt))
			splited = ["".join(txt[i:j]).split() for i, j in zip(cuts, cuts[1:])]

			lines = [[]]
			for i_w_list, words in enumerate(splited):
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
				if i_w_list != len(splited)-1:
					lines.append([])
			return lines


	def draw_before(self):
		self.clear_grid()
		padd = self.get_real_padding()
		size = self.get_inner_size()
		if self.size[1] >= 1:
			lines = self.get_broke_text(size[1])
			for row, l in enumerate(lines):
				if self.align == "center":
					l = [' '] * ((size[1] - len(l))//2) + l
				elif self.align == "right":
					l = [' '] * (size[1] - len(l)) + l

				for col, val in enumerate(l):
					r, c = row+padd[0][0], col + padd[0][1]
					if self.in_grid(r, c):
						self.grid[r][c] = val