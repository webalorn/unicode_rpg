from .base import *
from engine.client.keys import *
from engine import *

class VertLayoutW(BaseWidget):
	def __init__(self, *kargs, spacing=0, force_width=False, anchor="top", h_align='left', **kwargs):
		self.spacing = spacing
		self.force_width = force_width
		self.anchor = anchor
		self.h_align = h_align
		super().__init__(*kargs, **kwargs)

	def compute_dims(self, parent_size):
		if self.force_width:
			for child in self.children:
				child.resize((child.rel_size[0], 1.))

		super().compute_dims(parent_size)

		space_top = 0
		for child in self.children:
			col = 0
			if self.h_align == 'right':
				col = self.size[1] - child.size[1]
			if self.h_align == 'center':
				col = (self.size[1] - child.size[1])//2
			child.pos = (space_top, col)
			space_top += self.spacing + child.size[0]
		space_top -= self.spacing

		delta = 0
		if self.anchor == "bottom":
			delta = self.size[0] - space_top
		elif self.anchor == "center":
			delta = (self.size[0] - space_top) // 2

		if delta:
			for child in self.children:
				child.pos = add_coords(child.pos, (delta, 0))

class HorLayoutW(BaseWidget):
	def __init__(self, *kargs, spacing=0, force_height=False, anchor="left", v_align='top', **kwargs):
		self.spacing = spacing
		self.force_height = force_height
		self.anchor = anchor
		self.v_align = v_align
		super().__init__(*kargs, **kwargs)

	def compute_dims(self, parent_size):
		if self.force_height:
			for child in self.children:
				child.resize((1., child.rel_size[1]))

		super().compute_dims(parent_size)

		space_left = 0
		for child in self.children:
			row = 0
			if self.v_align == 'bottom':
				row = self.size[0] - child.size[0]
			if self.v_align == 'center':
				row = (self.size[0] - child.size[0])//2
			child.pos = (row, space_left)
			space_left += self.spacing + child.size[1]
		space_left -= self.spacing

		delta = 0
		if self.anchor == "right":
			delta = self.size[1] - space_left
		elif self.anchor == "center":
			delta = (self.size[1] - space_left) // 2

		if delta:
			for child in self.children:
				child.pos = add_coords(child.pos, (0, delta))