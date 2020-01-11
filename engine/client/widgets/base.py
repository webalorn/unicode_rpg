from engine import *

class BaseWidget:
	def __init__(self, pos=(0, 0), size=(1, 1), add=[], inv_side=(False, False), modal=False):
		self.pos = pos # Coords can be : +x , -x, "center"
		self.size = size
		self.clear_grid()
		self.children = []
		self.add(add)
		self.inv_side = inv_side
		self.padding = ((0, 0), (0, 0))
		self.modal = modal

	########## Draw

	def clear_grid(self):
		self.grid = [[None for _ in range(self.size[1])] for _ in range(self.size[0])]

	def draw_before(self):
		self.clear_grid()

	def draw_after(self):
		pass

	def get_real_padding(self):
		return self.padding

	def get_real_coord(self, grid_size):
		coords = []
		for x, sub_l, grid_l, inv in zip(to_tuple(self.pos), self.size, grid_size, to_tuple(self.inv_side)):
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

	def draw(self, main_grid):
		self.draw_before()

		padding = self.get_real_padding()
		sub_grid = extract_grid(self.grid, padding)
		for child in self.children:
			child.draw(sub_grid)
		if has_non_nul(padding):
			paint_on_grid(self.grid, sub_grid, (padding[0][0], padding[1][0]))
		self.draw_after()

		pos = self.get_real_coord((len(main_grid), len(main_grid[0])))
		paint_on_grid(main_grid, self.grid, pos)

	def in_grid(self, r, c):
		return 0 <= r < self.size[0] and 0 <= c < self.size[1]

	########## Children

	def add(self, widget):
		if type(widget) == list:
			for w in widget:
				self.add(w)
		elif widget:
			self.children.append(widget)
		return widget

	def remove(self, widget):
		if type(widget) == list:
			for w in widget:
				self.remove(w)
		elif widget:
			self.children = [w for w in self.widget if id(w) != id(widget)]
		return widget

	########## Dimensions

	def resize(self, new_size):
		self.size = new_size
		self.clear_grid()

	def get_inner_size(self):
		padding = self.get_real_padding()
		return minus_coords(self.size, (sum(padding[0]), sum(padding[1])))

	def compute_dims(self, parent_size):
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