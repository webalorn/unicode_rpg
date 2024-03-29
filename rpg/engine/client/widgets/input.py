from .simple import *
from engine.client.keys import *
from engine import *
import copy

########## Text & buttons

class TextareaW(TextW):
	FOCUSABLE = True

	def __init__(self, *kargs, limit=None, strip_lines=False, **kwargs):
		self.cursor_pos = 0
		super().__init__(*kargs, strip_lines=strip_lines, **kwargs)
		self.limit = limit

	def set_text(self, *args, **kwargs):
		if super().set_text(*args, **kwargs):
			self.cursor_pos = len(self.text)

	def draw_widget(self):
		self.anchor_down = self.focused
		super().draw_widget()

	def is_char_allowed(self, key):
		return key.is_char_allowed()

	def get_cur_pos(self):
		self.cursor_pos = min(max(self.cursor_pos, 0), len(self.text))
		return self.cursor_pos

	def keypress(self, key):
		if not self.focused:
			return False
		if self.is_char_allowed(key):
			if self.limit:
				l = self.limit
				if l == "auto":
					r, c = self.get_inner_size()
					l = r*c
				if len(self.text) >= l:
					return True
				# while len(self.text) > l:
				# 	self.text.pop()
			# self.text.append(key.key)
			c = self.get_cur_pos()
			self.text = self.text[:c] + [key.key] + self.text[c:]
			self.cursor_pos += 1
		elif key.check(KeyVal.BACK):
			c = self.get_cur_pos()
			if c:
				self.text.pop(c-1)
				self.cursor_pos -= 1
		elif key.check(KeyVal.ARROW_RIGHT):
			self.cursor_pos += 1
			self.get_cur_pos()
		elif key.check(KeyVal.ARROW_LEFT):
			self.cursor_pos -= 1
			self.get_cur_pos()
		elif key.check(KeyVal.ARROW_UP):
			size = self.get_inner_size()
			self.cursor_pos -= size[1]
			self.get_cur_pos()
		elif key.check(KeyVal.ARROW_DOWN):
			size = self.get_inner_size()
			self.cursor_pos += size[1]
			self.get_cur_pos()
		reset_steps('cursor')
		return True

	def get_broke_text(self, larg):
		txt = super().get_broke_text(larg)
		if self.focused:
			txt = copy.deepcopy(txt)
			cur_p = self.get_cur_pos()
			i = 0
			self._grid_cur = None
			for i_line, l in enumerate(txt):
				for i_col, c in enumerate(l):
					while i < len(self.text) and self.text[i] != c:
						i += 1
					if i >= cur_p:
						self._grid_cur = (i_line, i_col)
						break
					i += 1
				if self._grid_cur:
					break
			if not self._grid_cur:
				if not txt:
					txt = [[" "]]
				elif len(txt[-1]) >= larg:
					txt.append([" "])
				else:
					txt[-1].append(" ")
				self._grid_cur = (len(txt)-1, len(txt[-1])-1)
			if not get_cycle_val(C.CURSOR_BLINK, name='cursor'):
				txt[self._grid_cur[0]][self._grid_cur[1]] = to_skin_char("cursor")

			haut = self.get_inner_size()[0]
			cur_l = self._grid_cur[0]
			if len(txt) - cur_l > haut:
				txt = txt[:haut+cur_l-len(txt)]
		return txt

	# def get_broke_text(self, larg):
	# 	txt = super().get_broke_text(larg)
	# 	if self.focused:
	# 		cursor = to_skin_char("cursor") if get_cycle_val(C.CURSOR_BLINK) else " "
	# 		if txt and len(txt[-1]) < self.get_inner_size()[1]:
	# 			txt = txt[:-1] + [txt[-1] + [cursor]]
	# 		else:
	# 			txt = txt + [cursor]
	# 	return txt

class TextInputW(TextareaW):
	def get_displayed_text_list(self):
		if not self.focused:
			return self.text
		else:
			txt = self.text + [" "]
			if not get_cycle_val(C.CURSOR_BLINK, name='cursor'):
				txt[self.get_cur_pos()] = to_skin_char("cursor")
			return txt

	def get_broke_text(self, larg):
		if self.focused:
			l = self.get_displayed_text_list()
			c = self.get_cur_pos()
			if c == 0:
				return [l[:larg]]
			elif len(l)-c > larg-1:
				l = l[:larg+c-1-len(l)]
			return [l[-larg:]]
		return [self.get_displayed_text_list()[:larg]]

	def is_char_allowed(self, key):
		return not key.check("\n") and key.is_char_allowed()

class PasswordW(TextInputW):
	def get_displayed_text_list(self):
		pass_chars = get_charset("password")
		n = len(pass_chars)
		txt = [pass_chars[i%n] for i in range(len(self.text))]

		cursor = to_skin_char("cursor")
		if not get_cycle_val(C.CURSOR_BLINK, name='cursor') and self.focused:
			return txt + [cursor]
		return txt + [" "] if self.focused else txt # Space to replace cursor

class ButtonW(TextW):
	FOCUSABLE = True
	FORMAT = 'button'
	FORMAT_FOCUSED = 'button_focused'
	BORDER = "button"
	BORDER_FOCUSED = "button_focused"

	SOUND_PRESS = "pressed"

	def __init__(self, text, *kargs, big=True, border=0, call=None, size=None, align="center", **kwargs):
		best_h = 3 if big else 1
		if size is None:
			size = (best_h, len(text)+2)
		elif isinstance(size, (int, float)):
			size = (best_h, size)

		kwargs['v_align'] = 'center'
		super().__init__(text, *kargs, align=align, size=size, **kwargs)
		self.big = big

		self.ev_pressed = UIEvent(call)

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

class MenuItemW(TextW):
	def __init__(self, *kargs, align="center", call=None, **kwargs):
		super().__init__(*kargs, align=align, **kwargs)
		self.ev_pressed = UIEvent(call)
		self.selected = False

	def compute_real_size(self, parent_size):
		larg = parent_size[1]
		n_rows = len(self.get_broke_text(larg))
		self.resize((n_rows, larg))

		super().compute_real_size(parent_size)

	def pressed(self):
		self.ev_pressed.fire()

	def is_displayed_focused(self):
		return self.focused or self.selected

class MenuVertW(BoxW):
	FOCUSABLE = True
	CURSOR_CHAR = ["select_left", "select_right"]
	SOUND_MOVE = "menu_move"
	SOUND_SELECT = "menu_select"

	def __init__(self, col_size=1, spacing=1, scroll=False, v_align="top", *kargs, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.col_size = col_size
		self.spacing = spacing
		self.cursor_pos = 0
		self.scroll = scroll
		self.v_align = v_align

	def get_real_padding(self):
		padd = super().get_real_padding()
		return (padd[0], add_coords(padd[1], (self.col_size, self.col_size)))

	def set_children_selected(self, state):
		if 0 <= self.cursor_pos < len(self.children):
			self.children[self.cursor_pos].selected = state
			self.children[self.cursor_pos].keep_drawn_grid = False

	def move_cursor(self, rel):
		self.set_children_selected(False)
		self.cursor_pos += rel
		self.cursor_pos = min(max(self.cursor_pos, 0), len(self.children)-1)
		self.set_children_selected(True)
		mark_dims_changed()

	def compute_children_dims(self):
		space_top = 0
		inner_size = self.get_inner_size()
		for child in self.children:
			child.compute_real_size(inner_size)
			child.rel_pos = (space_top, 0)
			space_top += self.spacing + child.size[0]
		space_top -= self.spacing

		if self.scroll and self.children:
			mid = self.get_inner_size()[0] // 2
			s_child = self.children[self.cursor_pos]
			pos_mid_selected = s_child.rel_pos[0] + s_child.size[0] // 2
			delta = mid - pos_mid_selected

			for child in self.children:
				child.rel_pos = add_coords(child.rel_pos, (delta, 0))
		elif self.children:
			delta = 0
			if self.v_align == "bottom":
				delta = inner_size[0] - space_top
			elif self.v_align == "center":
				delta = (inner_size[0] - space_top)//2

			for child in self.children:
				child.rel_pos = add_coords(child.rel_pos, (delta, 0))

	def keypress(self, key):
		if not self.focused:
			return False
		if key.check("\n"):
			self.children[self.cursor_pos].pressed()
		elif key.check(KeyVal.ARROW_UP):
			self.move_cursor(-1)
		elif key.check(KeyVal.ARROW_DOWN):
			self.move_cursor(1)
		else:
			return False
		return True

	def draw_widget(self):
		super().draw_widget()
		self.set_children_selected(True)
		if self.children and self.focused and self.col_size:
			padd = self.get_real_padding()
			child = self.children[self.cursor_pos]

			row = child.pos[0] + padd[0][0] + child.size[0] // 2
			if row < len(self.grid) and row >= 0 and self.size[1]:
				self.grid[row][padd[1][0]-1] = self.CURSOR_CHAR[0]
				self.grid[row][-padd[1][1]] = self.CURSOR_CHAR[1]

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
		else:
			return False
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
		self.ev_change = UIEvent()

	def resize(self, new_size):
		super().resize((1, 3))

	def draw_widget(self):
		super().draw_widget()
		charset = get_charset(self.CHARSET)
		center = charset[-1] if self.checked else charset[-2]
		self.grid = [[charset[0], center, charset[1]]]
		if self.checked:
			center_format = get_skin_format(self.CHECKED_CENTER_STYLE)
			center_format = inherit_union(self.displayed_format, center_format)
			set_point_format(self.format_map, (0, 1), center_format)

	def press(self):
		self.checked = not self.checked
		self.ev_change.fire()

	def keypress(self, key):
		if not self.focused:
			return False
		if key.check(["\n", " "]):
			self.press()
		else:
			return False
		return True

class RadioGroupW(BoxW):
	def reset_checked(self, node=None):
		if node is None:
			node = self
		for child in node.children:
			if isinstance(child, RadioW):
				child.checked = False
				child.keep_drawn_grid = False
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