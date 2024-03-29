from engine import *
from engine.client.common.drawing import *
from engine.client.widgets import *
from engine.client.keys.keyboard import *
from engine.dm.dm import DungeonMaster
from threading import Lock

########## Screen map classes : map screen cells to widgets

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
		return [
			[
				" " if not widget else widget.grid[i_row - widget.absolute_pos[0]][i_col - widget.absolute_pos[1]]
				for i_col, widget in enumerate(row)
			]
			for i_row, row in enumerate(self.map)
		]

	def get_format_map(self):
		return [
			[
				None if not widget else widget.format_map[i_row - widget.absolute_pos[0]][i_col - widget.absolute_pos[1]]
				for i_col, widget in enumerate(row)
			]
			for i_row, row in enumerate(self.map)
		]

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

	def set_point(self, point, widget):
		self.set((point, add_coords(point, (1, 1))), widget)

########## Scene : containers for widgets

class Scene:
	def __init__(self, client, root=None):
		"""
			The root must be an widget, or the window for the root scene
		"""
		self.client = client
		self.window = client.window

		root_parent = client.window if root is None else root
		self.root = root_parent.add(SceneRootW(self))

		self.ev_stop = UIEvent()
		self.ev_draw_begin = UIEvent()

		self.root.ev_key_intercept.on(self.keypress_intercept)
		self.root.ev_key_discarded.on(self.keypress_discarded)
		self.window.ev_draw_begin.on(self.ev_draw_begin.fire)
		self.root.ev_key.on(self.unhandled_keypress)

	def start(self):
		"""
			Create all widgets for the scene
		"""
		pass

	def stop(self): # 
		"""
			Clean up your stuff
		"""
		self.root.scene = None
		self.ev_stop.fire()
		self.try_stop_subscenes(self.root)
		self.root.delete()

		self.root.ev_key_intercept.off(self.keypress_intercept)
		self.root.ev_key_discarded.off(self.keypress_discarded)
		self.window.ev_draw_begin.off(self.ev_draw_begin.fire)
		self.root.ev_key.off(self.unhandled_keypress)

	def try_stop_subscenes(self, node):
		for child in node.children:
			if isinstance(child, SceneRootW) and node.scene:
				node.scene.stop()
			else:
				self.try_stop_subscenes(child)

	def raise_exit(self):
		self.stop()
		raise ExitException

	def ask_exit(self):
		text_exit = "Do you really want to exit {}?".format(C.PROG_NAME)
		w = G.WINDOW.add(ConfirmPopupW(text_exit, buttons=["Cancel", " Exit "], call=self.raise_exit))
		w.buttons[-1].FORMAT_FOCUSED = "button_danger_focused"

	def keypress_intercept(self, key):
		"""
			Called before all the widgets if all the scene added after rejected the key
		"""
		return False

	def unhandled_keypress(self, key):
		"""
			Called if an input key has not been handled by the scene widgets
		"""
		return False

	def keypress_discarded(self, key):
		"""
			Called if an input key has not been handled by the scene widgets
			Default is to call unhandled_keypress
		"""
		return self.unhandled_keypress(key)

class DungeonScene(Scene):
	"""
		Base scene to create a game server
	"""
	def __init__(self, *kargs, serv_args={}, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.dm = self.create_game_serv(**serv_args)
		self.dm_lock = Lock()

	def create_game_serv(self, **serv_args):
		""" Should be overwride """
		return DungeonMaster(**serv_args)

	def test_dm_state(self):
		if self.dm.DEAD.is_set():
			raise ExitException("DM is dead")

	def send_dm(self, *messages):
		with self.dm_lock:
			for m in messages:
				self.dm.ext_pipe.send(m)

	def get_from_dm(self):
		with self.dm_lock:
			return get_pipe_messages(self.dm.ext_pipe)

	def start(self):
		self.dm.start()
		self.client.input_manager.clear_prio()
		self.client.input_manager.register_prio(self)
		self.ev_draw_begin.on(self.test_dm_state)

	def stop(self):
		self.client.input_manager.clear_prio()
		self.dm.close_dm_ext()
		super().stop()

	def accept_prio_key(self, key):
		return False # Overwride to send keys directly to the DM