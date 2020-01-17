from .base import *
from .simple import *
from engine.client.keys import *
from engine import *

class VirtualLayoutW(BaseWidget):
	def set_visible_area(self, screen_map):
		pass

class VertLayoutW(VirtualLayoutW):
	def __init__(self, *kargs, spacing=0, force_width=False, anchor="top", h_align='left', **kwargs):
		self.spacing = spacing
		self.force_width = force_width
		self.anchor = anchor
		self.h_align = h_align
		super().__init__(*kargs, **kwargs)

	def compute_children_dims(self):
		if self.force_width:
			for child in self.children:
				child.resize((child.rel_size[0], 1.))

		space_top = 0
		for child in self.children:
			col = 0
			if self.h_align == 'right':
				col = self.size[1] - child.size[1]
			if self.h_align == 'center':
				col = (self.size[1] - child.size[1])//2
			child.rel_pos = (space_top, col)
			space_top += self.spacing + child.size[0]
		space_top -= self.spacing

		delta = 0
		if self.anchor == "bottom":
			delta = self.size[0] - space_top
		elif self.anchor == "center":
			delta = (self.size[0] - space_top) // 2

		if delta:
			for child in self.children:
				child.rel_pos = add_coords(child.rel_pos, (delta, 0))

class HorLayoutW(VirtualLayoutW):
	def __init__(self, *kargs, spacing=0, force_height=False, anchor="left", v_align='top', **kwargs):
		self.spacing = spacing
		self.force_height = force_height
		self.anchor = anchor
		self.v_align = v_align
		super().__init__(*kargs, **kwargs)

	def compute_children_dims(self):
		if self.force_height:
			for child in self.children:
				child.resize((1., child.rel_size[1]))

		space_left = 0
		for child in self.children:
			row = 0
			if self.v_align == 'bottom':
				row = self.size[0] - child.size[0]
			if self.v_align == 'center':
				row = (self.size[0] - child.size[0])//2
			child.rel_pos = (row, space_left)
			space_left += self.spacing + child.size[1]
		space_left -= self.spacing

		delta = 0
		if self.anchor == "right":
			delta = self.size[1] - space_left
		elif self.anchor == "center":
			delta = (self.size[1] - space_left) // 2

		if delta:
			for child in self.children:
				child.rel_pos = add_coords(child.rel_pos, (0, delta))

########## Scroll

class ScrollTextW(TextW):
	FOCUSABLE = True
	BORDER_FOCUSED_STYLE = "text_scroll_focused"

	def __init__(self, *kargs, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.scroll_pos = 0

	def is_char_allowed(self, key):
		return key.is_char_allowed()

	def scroll(self, delta):
		self.scroll_pos += delta
		inner_size = self.get_inner_size()

		n_lines = len(super().get_broke_text(inner_size[1]))
		in_haut = inner_size[0]
		self.scroll_pos = min(self.scroll_pos, n_lines-in_haut)
		self.scroll_pos = max(0, self.scroll_pos)

	def keypress(self, key):
		if not self.focused:
			return False
		if key.check(KeyVal.ARROW_UP):
			self.scroll(-1)
		elif key.check(KeyVal.ARROW_DOWN):
			self.scroll(1)
		return True

	def get_broke_text(self, larg):
		txt = super().get_broke_text(larg)
		return txt[self.scroll_pos:]