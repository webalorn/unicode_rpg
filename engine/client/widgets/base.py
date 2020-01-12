from engine import *

class BaseWidget:
	FOCUSABLE = False

	def __init__(self, pos=(0, 0), size=(1, 1), add=[], inv_side=(False, False), modal=False, format=None):
		self.rel_pos = pos # Coords can be : +x , -x, "center"
		self.pos = tuple([k if type(k) == int else 0 for k in to_tuple(pos)])
		self.format = format
		self.displayed_format = None
		self.focused = False

		self.rel_size = (0, 0)
		self.size = (0, 0)
		self.resize(size)

		self.parent = None
		self.children = []
		self.add(add)

		self.inv_side = inv_side
		self.padding = ((0, 0), (0, 0))
		self.modal = modal # Block keys for other widgets

	########## Draw

	def clear_grid(self):
		self.grid = [[None for _ in range(self.size[1])] for _ in range(self.size[0])]

	def set_display_format(self, format, area=0):
		if self.parent:
			self.displayed_format = inherit_union(self.parent.displayed_format, self.format)
		if format != self.format:
			self.displayed_format = inherit_union(self.displayed_format, format)
		if format != None:
			self.format_map.set(area, self.displayed_format)

	def draw_before(self):
		self.clear_grid()
		self.set_display_format(self.format)
		# if self.parent:
		# 	self.displayed_format = inherit_union(self.parent.displayed_format, self.format)
		# if self.format != None:
		# 	self.format_map.set(0, self.displayed_format)

	def draw_after(self):
		pass

	def get_real_padding(self):
		return self.padding

	def get_real_coord(self, grid_size):
		coords = []
		for x, sub_l, grid_l, inv in zip(to_tuple(self.rel_pos), self.size, grid_size, to_tuple(self.inv_side)):
			if x in ("center", "c"):
				x = (grid_l-sub_l)//2
			elif type(x) == float:
				x = int(grid_l*x - sub_l/2)
			elif type(x) != int:
				raise Exception("Invalid coord", x)
			if inv:
				x = grid_l - x - sub_l
			coords.append(x)
		return tuple(coords)

	def draw(self, main_grid, format_map):
		self.format_map = format_map
		self.draw_before()

		padding = self.get_real_padding()
		inner_size = self.get_inner_size()
		sub_grid = extract_grid(self.grid, padding)
		sub_map = FormatMapRel(format_map, (padding[0][0], padding[1][0]), inner_size)

		for child in self.children:
			child.draw(sub_grid, FormatMapRel(sub_map, child.pos, child.size))
		if has_non_nul(padding):
			paint_on_grid(self.grid, sub_grid, (padding[0][0], padding[1][0]))

		self.draw_after()
		paint_on_grid(main_grid, self.grid, self.pos)

	def in_grid(self, r, c):
		return 0 <= r < self.size[0] and 0 <= c < self.size[1]

	########## Children

	def add(self, widget):
		if type(widget) == list:
			for w in widget:
				self.add(w)
		elif widget:
			self.children.append(widget)
			widget.parent = self
		return widget

	def remove(self, widget):
		if type(widget) == list:
			for w in widget:
				self.remove(w)
		elif widget:
			self.children = [w for w in self.children if id(w) != id(widget)]
		return widget

	def explore_focusable(self, focus_list): # return True if a modal has been seen, to stop exploration
		for child in self.children[::-1]:
			if child.explore_focusable(focus_list):
				return True
		if self.FOCUSABLE:
			focus_list.append(self)
		return self.modal

	########## Dimensions

	def resize(self, new_size):
		new_size = to_tuple(new_size)
		if new_size != self.rel_size:
			self.rel_size = new_size
			self.size = tuple([k if type(k) == int else 0 for k in new_size])
			self.clear_grid()

	def get_inner_size(self):
		padding = self.get_real_padding()
		return minus_coords(self.size, (sum(padding[0]), sum(padding[1])))

	def compute_dims(self, parent_size):
		if self.size != self.rel_size:
			new_size = []
			for rel, parent in zip(self.rel_size, parent_size):
				if type(rel) == int and rel >= 0: new_size.append(rel)
				elif type(rel) == int: new_size.append(parent + rel) # -5 means 100% - 5 cells
				elif type(rel) == float: new_size.append(round(parent*rel))
				elif rel in [None, "auto"]: new_size.append(parent)
				else: raise Error("Unknown dim type", rel)
			self.size = tuple(new_size)

		self.pos = self.get_real_coord(parent_size)
		
		padding = self.get_real_padding()
		inner_size = self.get_inner_size()
		for child in self.children:
			child.compute_dims(inner_size)

	########## Key events

	def keypress(self, key):
		return False

	def fire_key(self, key):
		for child in self.children[::-1]: # Last child tested first
			if child.fire_key(key): # The key has been used
				return True
		if self.keypress(key) or self.modal:
			return True
		return False