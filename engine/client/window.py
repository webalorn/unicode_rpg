from engine.storage.skin import Skin
from engine.client.widgets import BaseWidget
from engine.client.keys import *
from .drawing import *
import data.consts as C
import os, sys

class WindowManager(BaseWidget):
	def __init__(self, size=None, skin_name='default'):
		super().__init__((0, 0), size or (C.DEF_ROWS, C.DEF_COLS))
		self.keyboard = Keyboard()
		self.screen_cleared = True
		self.set_skin(skin_name)

	def resize(self, new_size):
		if new_size == self.size:
			return
		self.clear_screen() # Clear before resizing
		self.size = new_size
		self.clear_grid()

	def clear_screen(self):
		sys.stdout.write("\033[K")
		if not self.screen_cleared:
			self.screen_cleared = True
			for i in range(self.size[0]):
				if i: sys.stdout.write("\033[F") # Up one line [if not on last line]
				# sys.stdout.write("\033[K") # Clear line

	def print_screen(self):
		raise Exception("Not implemented")

	def set_skin(self, skin_name):
		self.skin = Skin(skin_name)

	def draw_after(self):
		draw_borders(self.grid)

	def detect_keys(self):
		pass

class WindowText(WindowManager):
	def __init__(self, *kargs, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.keyboard =  KeyboardTerm()

	def compute_dims(self, _ignored_):
		s = tuple(map(int, os.popen('stty size', 'r').read().split()))
		self.resize(s)
		super().compute_dims(self.size)

	def draw_before(self):
		pass

	def print_screen(self):
		self.compute_dims(None)
		self.draw(self.grid)
		self.clear_screen()
		self.screen_cleared = False

		for i_row, row in enumerate(self.grid):
			for v in row:
				sys.stdout.write(self.skin.to_char(v))
			if i_row < self.size[0]-1:
				sys.stdout.write("\n")
		sys.stdout.write("\r")
		sys.stdout.flush()
		self.clear_grid()

	def detect_keys(self):		
		keys_pressed = self.keyboard.get_keys()
		for key in keys_pressed:
			self.fire_key(key)