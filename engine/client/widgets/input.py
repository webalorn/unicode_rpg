from .simple import *
import data.consts as C
from engine.client.keys import *
from engine import *

class TextInputW(SimpleTextW):
	def __init__(self, *kargs, limit="auto", **kwargs):
		super().__init__(*kargs, **kwargs)
		self.limit = limit

	def keypress(self, key):
		if key.is_char_allowed():
			self.text.append(key.key)
			if self.limit:
				l = self.limit
				if l == "auto":
					r, c = self.get_inner_size()
					l = r*c
				while len(self.text) > l:
					self.text.pop()
		elif key.check(KeyVal.BACK):
			if self.text:
				self.text.pop()
		else:
			return False
		return True

	def get_displayed_text_list(self):
		cursor = to_skin_char("cursor")
		return self.text + [cursor] if get_cycle_val(C.CURSOR_BLINK) else self.text

########## Menus

class MenuItem(SimpleTextW):
	def __init__(self, *kargs, align="center", call=None, **kwargs):
		super().__init__(*kargs, align=align, **kwargs)
		self.call = call

	def compute_dims(self, parent_size):
		n_char = len(self.text)
		larg = parent_size[1]
		n_rows = (n_char+larg-1)//larg
		self.resize((n_rows, larg))

		super().compute_dims(parent_size)

	def pressed(self):
		if self.call:
			self.call()

class MenuVertW(BoxW):
	def __init__(self, col_size=1, spacing=1, *kargs, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.col_size = col_size
		self.spacing = spacing
		self.cursor_pos = 0

	def get_real_padding(self):
		padd = super().get_real_padding()
		return (padd[0], add_coords(padd[1], (self.col_size, self.col_size)))

	def move_cursor(self, rel):
		self.cursor_pos += rel
		self.cursor_pos = min(max(self.cursor_pos, 0), len(self.children)-1)

	def compute_dims(self, parent_size):
		super().compute_dims(parent_size)

		space_top = 0
		for child in self.children:
			child.pos = (space_top, 0)
			space_top += self.spacing + child.size[0]

	def keypress(self, key):
		if key.check("\n"):
			self.children[self.cursor_pos].pressed()
		elif key.check(KeyVal.ARROW_UP):
			self.move_cursor(-1)
		elif key.check(KeyVal.ARROW_DOWN):
			self.move_cursor(1)
		else:
			return False
		return True

	def draw_after(self):
		super().draw_after()
		padd = self.get_real_padding()
		child = self.children[self.cursor_pos]

		row = child.pos[0] + padd[0][0] + child.size[0] // 2
		self.grid[row][padd[1][0]-1] = "select_left"
		self.grid[row][-padd[1][1]] = "select_right"