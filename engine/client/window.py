from engine.storage.skin import Skin
from engine.client.widgets import BaseWidget
from engine.client.keys import *
from .drawing import *
import data.consts as C
import os, sys

class WindowManager(BaseWidget):
	def __init__(self, size=None, skin_name='default'):
		self.screen_cleared = True
		super().__init__((0, 0), size or (C.DEF_ROWS, C.DEF_COLS), format=EMPTY_FORMAT)

		self.set_skin(skin_name)
		self.keyboard = Keyboard()
		self.focused_el = None
		self.focusable_list = []
		self.displayed_format = EMPTY_FORMAT

	def resize(self, new_size):
		if new_size == self.size:
			return
		self.clear_screen() # Clear before resizing
		super().resize(new_size)
		self.clear_grid()

	def clear_screen(self):
		sys.stdout.write("\033[K")
		if not self.screen_cleared:
			self.screen_cleared = True
			for i in range(self.size[0]-1):
				sys.stdout.write("\033[F") # Up one line [if not on last line]

	def print_screen(self):
		raise Exception("Not implemented")

	def set_skin(self, skin_name):
		self.skin = Skin(skin_name)

	def draw_after(self):
		draw_borders(self.grid)

	def get_focus_id(self):
		i_focus = -1
		for i, w in enumerate(self.focusable_list):
			if id(w) == id(self.focused_el):
				i_focus = i
		return i_focus

	def set_focus(self, el):
		if self.focused_el:
			self.focused_el.focused = False
		self.focused_el = el
		if self.focused_el:
			self.focused_el.focused = True

	def focus_element(self):
		self.focusable_list = []
		self.explore_focusable(self.focusable_list)
		self.focusable_list = self.focusable_list[::-1]

		if self.focused_el == None or self.get_focus_id() == -1:
			self.set_focus(self.focusable_list[0] if self.focusable_list else None)

	def next_focus(self, steps=1):
		if self.focusable_list:
			i = self.get_focus_id()
			n = len(self.focusable_list)
			i = (i + steps % n + n) % n
			self.set_focus(self.focusable_list[i])

	def detect_keys(self):
		keys_pressed = self.keyboard.get_keys()
		for key in keys_pressed:
			if key.check("\t"):
				self.next_focus()
			elif key.check(KeyVal.REV_TAB):
				self.next_focus(-1)
			else:
				self.fire_key(key)

	def update(self):
		self.focus_element()
		self.detect_keys()
		self.print_screen()

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
		format_map = FormatMap(self.size)
		self.draw(self.grid, format_map)
		format_map = format_map.get_final_map()

		self.clear_screen()
		self.screen_cleared = False

		for i_row, row in enumerate(self.grid):
			for i_col, v in enumerate(row):
				sys.stdout.write(format_map[i_row][i_col])
				sys.stdout.write(self.skin.to_char(v))
			if i_row < self.size[0]-1:
				sys.stdout.write("\n")
		sys.stdout.write("\r")
		sys.stdout.flush()
		self.clear_grid()

	def __del__(self):
		sys.stdout.write(F_STYLE["reset"])
		sys.stdout.flush()