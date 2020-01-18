from engine import *
from engine.client.common.drawing import *

class BaseWidget:
	FOCUSABLE = False
	FORMAT = None
	FORMAT_FOCUSED = None

	def __init__(self, pos=(0, 0), size=(1, 1), add=[], inv_side=(False, False), modal=False,
				format=None, focused_format=None, padding=((0, 0), (0, 0))):
		super().__init__()
		self.rel_pos = "-" # Coords can be : +x , -x, "center"
		self.move_to(pos)
		self.format = self.parse_format(format)
		self.focused_format = self.parse_format(focused_format)
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
		self.padding = padding
		self.modal = modal # Block keys for other widgets
		self.ev_key_intercept = KeyPressEvent()
		self.ev_key_discarded = KeyPressEvent()
		self.ev_key = KeyPressEvent()

	def parse_format(self, format):
		if isinstance(format, str) and format != "inherit":
			return get_skin_format(format)
		return format

	########## Draw

	def clear_grid(self):
		self.grid = [[" "]*self.size[1] for _ in range(self.size[0])]
		self.format_map = [[None]*self.size[1] for _ in range(self.size[0])]

	def set_display_format(self, format, area=0):
		if self.parent:
			self.displayed_format = inherit_union(self.parent.displayed_format, self.format)
		if format != self.format:
			self.displayed_format = inherit_union(self.displayed_format, format)
		if self.displayed_format != None:
			area = area or ((0, 0), self.size)
			set_area_format(self.format_map, area, self.displayed_format)

	def is_displayed_focused(self):
		return self.focused

	def get_format(self):
		if self.is_displayed_focused():
			form = self.focused_format or get_skin_format(self.FORMAT_FOCUSED)
			if form:
				return form
		return self.format or get_skin_format(self.FORMAT)

	def need_draw(self):
		return (not self.keep_drawn_grid)

	def draw_widget(self):
		# We will need to draw again after the focus is lost
		self.keep_drawn_grid = True
		self.clear_grid()
		self.set_display_format(self.get_format())
		for child in self.children:
			child.keep_drawn_grid = False

	def draw(self):
		if self.need_draw():
			if G.WINDOW:
				G.WINDOW.keep_drawn_grid = False
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
			mark_dims_changed()
			self.children.append(widget)
			widget.parent = self
		return widget

	def remove(self, widget):
		if isinstance(widget, list):
			for w in widget:
				self.remove(w)
		elif widget:
			mark_dims_changed()
			self.children = [w for w in self.children if id(w) != id(widget)]
		return widget

	def delete(self):
		if self.parent:
			self.parent.remove(self)
		else:
			raise Error("Can't delete a widget without parent")

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
			mark_dims_changed()
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

	def compute_real_size(self, parent_size):
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

	def compute_dims(self, parent_size, parent_screen_map):
		import engine.client.utility_cls as u_cls
		
		self.compute_real_size(parent_size)
		self.pos = self.get_real_coord(parent_size)
		padding = self.get_real_padding()
		inner_size = self.get_inner_size()

		self.absolute_pos = (0, 0)
		if self.parent:
			sup_pad = self.parent.get_real_padding()
			self.absolute_pos = add_coords(self.parent.absolute_pos, self.pos, (sup_pad[0][0], sup_pad[1][0]))

		screen_map = u_cls.ScreenMapRel(parent_screen_map, self.pos, self.size)
		self.set_visible_area(screen_map)
		
		sub_map = u_cls.ScreenMapRel(screen_map, (padding[0][0], padding[1][0]), inner_size)

		self.compute_children_dims()

		for child in self.children:
			child.compute_dims(inner_size, sub_map)

	########## Key events

	def keypress(self, key):
		return False

	def fire_key(self, key):
		if self.ev_key_intercept.fire(key):
			return True
		for child in self.children[::-1]: # Last child tested first
			key_usage = child.fire_key(key)
			if key_usage: # The key has been used or discarded
				if key_usage == -1 and not self.ev_key_discarded.fire(key):
					return -1
				return True
		if self.keypress(key) or self.ev_key.fire(key):
			return True
		if self.modal: # Discard the key
			return -1
		return False

class ContainerW(BaseWidget):
	"""
		This widget can't be displayed and is only here to contain other widgets in the tree,
		for organization purposes
	"""
	def __init__(self, *args, size=(1., 1.), **kwargs):
		super().__init__(*args, size=size, **kwargs)

	def clear_grid(self):
		pass

	def need_draw(self):
		pass

	def set_visible_area(self, screen_map):
		pass

class SceneRootW(ContainerW):
	"""
		This widget allow the widget to be recognized as the root of a scene.
	"""
	def __init__(self, scene, *args, **kwargs):
		self.scene = scene
		super().__init__(*args, **kwargs)