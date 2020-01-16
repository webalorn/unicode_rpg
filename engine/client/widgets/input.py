from .simple import *
from engine.client.keys import *
from engine import *

class TextareaW(SimpleTextW):
	FOCUSABLE = True

	def __init__(self, *kargs, limit=None, strip_lines=False, **kwargs):
		super().__init__(*kargs, strip_lines=strip_lines, **kwargs)
		self.limit = limit

	def draw_before(self):
		self.anchor_down = self.focused
		super().draw_before()

	def is_char_allowed(self, key):
		return key.is_char_allowed()

	def keypress(self, key):
		if not self.focused:
			return False
		if self.is_char_allowed(key):
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

	def get_broke_text(self, larg):
		txt = super().get_broke_text(larg)
		if self.focused:
			cursor = to_skin_char("cursor") if get_cycle_val(C.CURSOR_BLINK) else " "
			if txt and len(txt[-1]) < self.get_inner_size()[1]:
				txt = txt[:-1] + [txt[-1] + [cursor]]
			else:
				txt = txt + [cursor]
		return txt


class TextInputW(TextareaW):
	def get_displayed_text_list(self):
		cursor = to_skin_char("cursor")
		if get_cycle_val(C.CURSOR_BLINK) and self.focused:
			return self.text + [cursor]
		return self.text + [" "] if self.focused else self.text # Space to replace cursor

	def get_broke_text(self, larg):
		if self.focused:
			return [self.get_displayed_text_list()[-larg:]]
		return [self.get_displayed_text_list()[:larg]]

	def is_char_allowed(self, key):
		return not key.check("\n") and key.is_char_allowed()

class PasswordW(TextInputW):
	def get_displayed_text_list(self):
		pass_chars = get_charset("password")
		n = len(pass_chars)
		txt = [pass_chars[i%n] for i in range(len(self.text))]

		cursor = to_skin_char("cursor")
		if get_cycle_val(C.CURSOR_BLINK) and self.focused:
			return txt + [cursor]
		return txt + [" "] if self.focused else txt # Space to replace cursor

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
		self.big = big

		self.ev_pressed = Event(call)

	def get_real_padding(self):
		(a, b), (c, d) = super().get_real_padding()
		if self.big:
			return ((a+1, b+1), (c+1, d+1))
		return ((a, b), (c+1, d+1))

	def keypress(self, key):
		if self.focused and key.check("\n"):
			self.ev_pressed.fire()
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
		self.ev_pressed = Event(call)

	def compute_dims(self, parent_size):
		larg = parent_size[1]
		n_rows = len(self.get_broke_text(larg))
		self.resize((n_rows, larg))

		super().compute_dims(parent_size)

	def pressed(self):
		self.ev_pressed.fire()

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

########## Other

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

class CheckBoxW(BaseWidget):
	FOCUSABLE = True
	FORMAT = "checkbox"
	FORMAT_FOCUSED = "checkbox_focused"
	CHECKED_CENTER_STYLE = "checkbox_cross"
	CHARSET = "checkbox"

	def __init__(self, checked=False, *kargs, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.checked = checked

	def resize(self, new_size):
		super().resize((1, 3))

	def draw_before(self):
		super().draw_before()
		charset = get_charset(self.CHARSET)
		center = charset[-1] if self.checked else charset[-2]
		self.grid = [[charset[0], center, charset[1]]]
		if self.checked:
			center_format = get_skin_format(self.CHECKED_CENTER_STYLE)
			center_format = inherit_union(self.displayed_format, center_format)
			self.format_map.set_point((0, 1), center_format)

	def press(self):
		self.checked = not self.checked

	def keypress(self, key):
		if not self.focused:
			return False
		if key.check(["\n", " "]):
			self.press()
		return True

class RadioGroupW(BoxW):
	def reset_checked(self, node=None):
		if node is None:
			node = self
		for child in node.children:
			if isinstance(child, RadioW):
				child.checked = False
			else:
				self.reset_checked(child)

class RadioW(CheckBoxW):
	FORMAT = "radio"
	FORMAT_FOCUSED = "radio_focused"
	CHARSET = "radio"

	def press(self):
		parent = self.parent
		while parent and not isinstance(parent, RadioGroupW):
			parent = parent.parent
		if parent:
			parent.reset_checked()
		else:
			log("Radio button without group", err=True)
		self.checked = True