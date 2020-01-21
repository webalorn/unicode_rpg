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

class HorScrollLayoutW(HorLayoutW):
	"""
		Auto-scroll to show the rightmost element
		Only work if the children have a fixed width (int)
	"""

	def __init__(self, *kargs, side_margin=0, **kwargs):
		self.side_margin = side_margin
		super().__init__(*kargs, **kwargs)

	def compute_children_dims(self):
		super().compute_children_dims()
		if self.children:
			if self.anchor == "left":
				cur_margin = (self.size[1] - self.children[-1].rel_pos[1]
					- self.children[-1].rel_size[1] - self.side_margin
				)
				if cur_margin < 0:
					for child in self.children:
						child.rel_pos = (child.rel_pos[0], child.rel_pos[1]+cur_margin)
			elif self.anchor == "right":
				cur_margin = self.children[0].rel_pos[1] - self.side_margin
				if cur_margin < 0:
					for child in self.children:
						child.rel_pos = (child.rel_pos[0], child.rel_pos[1]-cur_margin)
			else:
				raise Error("HorScrollLayoutW can't work with {} anchor".format(self.anchor))

class VertScrollLayoutW(VertLayoutW):
	"""
		Auto-scroll to show the rightmost element
		Only work if the children have a fixed width (int)
	"""

	def __init__(self, *kargs, side_margin=0, **kwargs):
		self.side_margin = side_margin
		super().__init__(*kargs, **kwargs)

	def compute_children_dims(self):
		super().compute_children_dims()
		if self.children:
			if self.anchor == "bottom":
				cur_margin = (self.size[0] - self.children[-1].rel_pos[0]
					- self.children[-1].rel_size[0] - self.side_margin
				)
				if cur_margin < 0:
					for child in self.children:
						child.rel_pos = (child.rel_pos[0]+cur_margin, child.rel_pos[1])
			elif self.anchor == "top":
				cur_margin = self.children[0].rel_pos[0] - self.side_margin
				if cur_margin < 0:
					for child in self.children:
						child.rel_pos = (child.rel_pos[0]-cur_margin, child.rel_pos[1])
			else:
				raise Error("VertScrollLayoutW can't work with {} anchor".format(self.anchor))

########## Forms

class FormLayoutW(BoxW): # TODO : move focus
	"""
		An ordered form allow to switch between input widgets with arrow keys.
	"""
	def __init__(self, *kargs, modal=True, **kwargs):
		super().__init__(*kargs, modal=modal, **kwargs)

	def move_focus(self, steps):
		G.WINDOW.next_focus(steps, rotate=False)

	def keypress(self, key):
		if key.check(KeyVal.ARROW_UP):
			self.move_focus(-1)
		elif key.check(KeyVal.ARROW_DOWN):
			self.move_focus(1)
		else:
			return False
		return True

class VertScrollFromW(FormLayoutW, VertLayoutW):
	def __init__(self, *kargs, side_margin=2, **kwargs):
		self.side_margin = side_margin
		self.delta_row = 0
		super().__init__(*kargs, **kwargs)

	def set_visible_area(self, screen_map):
		pass

	def move_focus(self, steps):
		super().move_focus(steps)
		G.WINDOW.dims_changed = True

	def apply_delta(self, delta):
		for child in self.children:
			child.rel_pos = (child.rel_pos[0]+delta, child.rel_pos[1])

	def compute_children_dims(self):
		super().compute_children_dims()
		self.apply_delta(self.delta_row)

		focused_child = None
		for child in self.children:
			if child.focused:
				focused_child = child
		if focused_child:
			cur_margin_bottom = (self.size[0] - focused_child.rel_pos[0]
				- focused_child.rel_size[0] - self.side_margin
			)
			cur_margin_top = focused_child.rel_pos[0] - self.side_margin
			delta = 0
			if cur_margin_top < 0:
				delta = - cur_margin_top
			elif cur_margin_bottom < 0:
				delta = cur_margin_bottom

			if delta:
				self.apply_delta(delta)
				self.delta_row += delta