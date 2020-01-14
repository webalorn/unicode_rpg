from .simple import *
from engine.client.keys import *
from engine import *

class TextInputW(SimpleTextW):
	FOCUSABLE = True

	def __init__(self, *kargs, limit="auto", **kwargs):
		super().__init__(*kargs, **kwargs)
		self.limit = limit

	def keypress(self, key):
		if not self.focused:
			return False
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
		return True

	def get_displayed_text_list(self):
		cursor = to_skin_char("cursor")
		if get_cycle_val(C.CURSOR_BLINK) and self.focused:
			return self.text + [cursor]
		return self.text

class ButtonW(SimpleTextW):
	FOCUSABLE = True
	FORMAT = 'button'
	FORMAT_FOCUSED = 'button_focused'
	BORDER = "border"
	BORDER_FOCUSED = "border"

	def __init__(self, text, *kargs, big=False, border=0, call=None, size=None, **kwargs):
		best_h = 3 if big else 1
		if size is None:
			size = (best_h, len(text)+2)
		elif isinstance(size, (int, float)):
			size = (best_h, size)

		kwargs['align'] = 'center'
		kwargs['v_align'] = 'center'
		super().__init__(text, *kargs, size=size, **kwargs)
		self.call = call
		self.big = big

	def get_real_padding(self):
		(a, b), (c, d) = super().get_real_padding()
		if self.big:
			return ((a+1, b+1), (c+1, d+1))
		return ((a, b), (c+1, d+1))

	def keypress(self, key):
		if self.focused and key.check("\n"):
			if self.call:
				self.call()
			return True
		return False

	def draw_border(self):
		symbs = get_charset(self.BORDER_FOCUSED or self.BORDER if self.focused else self.BORDER)

		for row in range(self.size[0]):
			self.grid[row][0] = symbs[0]
			self.grid[row][-1] = symbs[0]
		if self.big and self.size[0] and self.size[1]:
			self.grid[0] = [symbs[1]] * self.size[1]
			self.grid[-1] = [symbs[1]] * self.size[1]
			self.grid[0][0] = symbs[2]
			self.grid[0][-1] = symbs[3]
			self.grid[-1][0] = symbs[4]
			self.grid[-1][-1] = symbs[5]

########## Menus

class MenuItem(SimpleTextW):
	def __init__(self, *kargs, align="center", call=None, **kwargs):
		super().__init__(*kargs, align=align, **kwargs)
		self.call = call

	def compute_dims(self, parent_size):
		larg = parent_size[1]
		n_rows = len(self.get_broke_text(larg))
		self.resize((n_rows, larg))

		super().compute_dims(parent_size)

	def draw_after(self):
		super().draw_after()

	def pressed(self):
		if self.call:
			self.call()

class MenuVertW(BoxW):
	FOCUSABLE = True

	def __init__(self, col_size=1, spacing=1, scroll=False, *kargs, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.col_size = col_size
		self.spacing = spacing
		self.cursor_pos = 0
		self.scroll = scroll

	def get_real_padding(self):
		padd = super().get_real_padding()
		return (padd[0], add_coords(padd[1], (self.col_size, self.col_size)))

	def move_cursor(self, rel):
		self.cursor_pos += rel
		self.cursor_pos = min(max(self.cursor_pos, 0), len(self.children)-1)
		G.WINDOW.dims_changed = True

	def compute_dims(self, parent_size):
		super().compute_dims(parent_size)

		space_top = 0
		for child in self.children:
			child.pos = (space_top, 0)
			space_top += self.spacing + child.size[0]

		if self.scroll and self.children:
			mid = self.get_inner_size()[0] // 2
			s_child = self.children[self.cursor_pos]
			pos_mid_selected = s_child.pos[0] + s_child.size[0] // 2
			delta = mid - pos_mid_selected

			for child in self.children:
				child.pos = add_coords(child.pos, (delta, 0))

	def keypress(self, key):
		if not self.focused:
			return False
		if key.check("\n"):
			self.children[self.cursor_pos].pressed()
		elif key.check(KeyVal.ARROW_UP):
			self.move_cursor(-1)
		elif key.check(KeyVal.ARROW_DOWN):
			self.move_cursor(1)
		return True

	def draw_after(self):
		super().draw_after()
		if self.children and self.focused:
			padd = self.get_real_padding()
			child = self.children[self.cursor_pos]

			row = child.pos[0] + padd[0][0] + child.size[0] // 2
			if row < len(self.grid) and self.size[1]:
				self.grid[row][padd[1][0]-1] = "select_left"
				self.grid[row][-padd[1][1]] = "select_right"

class BarInputW(BarW):
	FOCUSABLE = True
	FORMAT_FOCUSED = "bar_focused"

	def __init__(self, *kargs, step=0.1, **kwargs): 
		self.step = step
		super().__init__(*kargs, **kwargs)

	def advance(self, nb_steps):
		real_step = self.step
		if self.maxi and abs(real_step) < 1:
			real_step = real_step * maxi
		self.set(self.value + real_step * nb_steps)

	def keypress(self, key):
		if not self.focused:
			return False
		if key.check(KeyVal.ARROW_RIGHT):
			self.advance(1)
		elif key.check(KeyVal.ARROW_LEFT):
			self.advance(-1)
		return True