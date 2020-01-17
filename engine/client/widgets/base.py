from engine import *
from .drawing import *

class ScreenMap:
	def __init__(self, size):
		self.size = size
		self.map = [[None]*size[1] for _ in range(self.size[0])]

	def set(self, area, widget):
		(row1, col1), (row2, col2) = area
		for row in range(row1, row2):
			for col in range(col1, col2):
				self.map[row][col] = widget

	def get_char_map(self):
		grid = [[" "]*self.size[1] for _ in range(self.size[0])]
		for i_row, row in enumerate(self.map):
			for i_col, widget in enumerate(row):
				if widget:
					r, c = minus_coords((i_row, i_col), widget.absolute_pos)
					grid[i_row][i_col] = widget.grid[r][c]
		return grid

	def get_format_map(self):
		default = COLORS.get_default_format()
		grid = [[None]*self.size[1] for _ in range(self.size[0])]

		for i_row, row in enumerate(self.map):
			for i_col, widget in enumerate(row):
				if widget:
					r, c = minus_coords((i_row, i_col), widget.absolute_pos)
					grid[i_row][i_col] = widget.format_map[r][c]
		for row in grid:
			for i_col, col in enumerate(row):
				if not col:
					row[i_col] = default
		return grid

class ScreenMapRel:
	def __init__(self, screen_map, rel_pos, area_size):
		self.pos = rel_pos
		self.area = (rel_pos, add_coords(rel_pos, area_size))

		self.screen_map = screen_map
		while isinstance(self.screen_map, ScreenMapRel):
			move = self.screen_map.pos
			
			self.pos = add_coords(self.pos, move)
			area = (add_coords(self.area[0], move), add_coords(self.area[1], move))
			self.area = intersect_rects(
				(add_coords(self.area[0], move), add_coords(self.area[1], move)),
				self.screen_map.area
			)

			self.screen_map = self.screen_map.screen_map

	def set(self, area, widget):
		if not area:
			area = self.area
		else:
			area = (add_coords(area[0], self.pos), add_coords(area[1], self.pos))
			area = intersect_rects(area, self.area)
		self.screen_map.set(area, widget)

class BaseWidget:
	FOCUSABLE = False
	FORMAT = None
	FORMAT_FOCUSED = None

	def __init__(self, pos=(0, 0), size=(1, 1), add=[], inv_side=(False, False), modal=False,
				format=None, focused_format=None):
		super().__init__()
		self.rel_pos = "-" # Coords can be : +x , -x, "center"
		self.move_to(pos)
		self.format = format
		self.focused_format = focused_format
		self.displayed_format = None
		self.focused = False
		self.keep_drawn_grid = False

		self.rel_size = "-"
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
		self.grid = [[" "]*self.size[1] for _ in range(self.size[0])]
		self.format_map = [[None]*self.size[1] for _ in range(self.size[0])]

	def set_display_format(self, format, area=0):
		if self.parent:
			self.displayed_format = inherit_union(self.parent.displayed_format, self.format)
		if format != self.format:
			self.displayed_format = inherit_union(self.displayed_format, format)
		if format != None:
			area = area or ((0, 0), self.size)
			set_area_format(self.format_map, area, self.displayed_format)

	def get_format(self):
		if self.focused:
			form = self.focused_format or get_skin_format(self.FORMAT_FOCUSED)
			if form:
				return form
		return self.format or get_skin_format(self.FORMAT)

	def need_draw(self):
		return (not self.keep_drawn_grid) or self.focused

	def draw_widget(self):
		# We will need to draw again after the focus is lost
		self.keep_drawn_grid = (not self.focused)
		self.clear_grid()
		self.set_display_format(self.get_format())

	def get_real_padding(self):
		return self.padding

	def get_real_coord(self, grid_size):
		coords = []
		for x, sub_l, grid_l, inv in zip(to_tuple(self.rel_pos), self.size, grid_size, to_tuple(self.inv_side)):
			if x in ("center", "c"):
				x = (grid_l-sub_l)//2
			elif isinstance(x, float):
				x = int(grid_l*x - sub_l/2)
			elif not isinstance(x, int):
				raise Exception("Invalid coord", x)
			if inv:
				x = grid_l - x - sub_l
			coords.append(x)
		return tuple(coords)

	def draw(self):
		if self.need_draw():
			self.draw_widget()
		for child in self.children:
			child.draw()

	def in_grid(self, r, c):
		return 0 <= r < self.size[0] and 0 <= c < self.size[1]

	########## Children

	def add(self, widget):
		if isinstance(widget, list):
			for w in widget:
				self.add(w)
		elif widget:
			self.children.append(widget)
			widget.parent = self
		return widget

	def remove(self, widget):
		if isinstance(widget, list):
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
			if G.WINDOW:
				G.WINDOW.dims_changed = True
			self.rel_size = new_size
			self.size = tuple([k if isinstance(k, int) and k>0 else 0 for k in new_size])

	def move_to(self, pos):
		if pos != self.rel_pos:
			if G.WINDOW:
				G.WINDOW.dims_changed = True
			self.rel_pos = pos
			self.absolute_pos = pos
			self.pos = tuple([k if isinstance(k, int) else 0 for k in to_tuple(pos)])

	def get_inner_size(self):
		padding = self.get_real_padding()
		return minus_coords(self.size, (sum(padding[0]), sum(padding[1])))

	def set_visible_area(self, screen_map):
		screen_map.set(None, self)

	def compute_children_dims(self):
		pass

	def compute_dims(self, parent_size, parent_screen_map):
		if self.size != self.rel_size:
			new_size = []
			for rel, parent in zip(self.rel_size, parent_size):
				if not rel or rel == "auto": new_size.append(parent)
				if isinstance(rel, int) and rel >= 0: new_size.append(rel)
				elif isinstance(rel, int): new_size.append(parent + rel) # -5 means 100% - 5 cells
				elif isinstance(rel, float): new_size.append(round(parent*rel))
				else: raise Error("Unknown dim type", rel)
			self.size = tuple(new_size)
			self.keep_drawn_grid = False

		self.pos = self.get_real_coord(parent_size)
		padding = self.get_real_padding()
		inner_size = self.get_inner_size()

		self.absolute_pos = (0, 0)
		if self.parent:
			sup_pad = self.parent.get_real_padding()
			self.absolute_pos = add_coords(self.parent.absolute_pos, self.pos, (sup_pad[0][0], sup_pad[1][0]))

		screen_map = ScreenMapRel(parent_screen_map, self.pos, self.size)
		self.set_visible_area(screen_map)
		
		sub_map = ScreenMapRel(screen_map, (padding[0][0], padding[1][0]), inner_size)

		self.compute_children_dims()

		for child in self.children:
			child.compute_dims(inner_size, sub_map)

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