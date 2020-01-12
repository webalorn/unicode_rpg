from engine.storage.skin import Skin
from engine.client.widgets import BaseWidget
from engine.client.keys import *
from .drawing import *
from engine import *
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
		i_focus = 0 if self.focusable_list else -1
		for i, w in enumerate(self.focusable_list):
			if w.focused:
				i_focus = i
		return i_focus

	def set_focus(self, el):
		for e in self.focusable_list:
			e.focused = False
		el.focused = True

	def focus_element(self):
		self.focusable_list = []
		self.explore_focusable(self.focusable_list)
		self.focusable_list = self.focusable_list[::-1]

		i = self.get_focus_id()
		if i != -1:
			self.set_focus(self.focusable_list[i])

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
		PROFILER.start("win - 0 - print_screen")
		PROFILER.start("win - 1 - compute_dims")
		self.compute_dims(None) # takes 8

		PROFILER.next("win - 1 - compute_dims", "win - 2 - format map, draw")
		format_map = FormatMap(self.size)
		self.draw(self.grid, format_map)
		format_map = format_map.get_final_map()

		PROFILER.next("win - 2 - format map, draw", "win - 3 - clear screen")
		self.clear_screen()
		self.screen_cleared = False


		# takes 30
		# for i_row, row in enumerate(self.grid):
		# 	for i_col, v in enumerate(row):
		# 		sys.stdout.write(format_map[i_row][i_col])
		# 		sys.stdout.write(self.skin.to_char(v))
		# 	if i_row < self.size[0]-1:
		# 		sys.stdout.write("\n")

		PROFILER.next("win - 3 - clear screen", "win - 4 - compute grid chars")
		self.grid = [[self.skin.to_char(v) for v in l] for l in self.grid]

		PROFILER.next("win - 4 - compute grid chars", "win - 5 - compute grid string")
		printed_grid_string = "\n".join([
			"".join([format_map[i_row][i_col] + v for i_col, v in enumerate(row)])
			for i_row, row in enumerate(self.grid)
		])

		PROFILER.next("win - 5 - compute grid string", "win - 6 - write grid")
		sys.stdout.write(printed_grid_string)
		sys.stdout.write("\r")

		
		PROFILER.next("win - 5 - compute grid string", "win - 7 - flush grid")
		sys.stdout.flush()

		PROFILER.next("win - 5 - compute grid string", "win - 8 - clear grid")

		self.clear_grid() # takes 0-1
		PROFILER.end("win - 8 - clear grid")
		PROFILER.end("win - 0 - print_screen")

	def __del__(self):
		sys.stdout.write(F_STYLE["reset"])
		sys.stdout.flush()