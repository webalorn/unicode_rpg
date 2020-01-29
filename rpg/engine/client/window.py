from engine.client.widgets import *
from engine.client.keys.keyboard import *
from engine import *
import os, sys, shutil
from operator import add
from .cursor import CursorTerminal
from .utility_cls import ScreenMap

class WindowManager(BaseWidget, DispelMagic):
	def __init__(self, client, size=None):
		self.screen_cleared = True
		self.keyboard = None
		super().__init__((0, 0), size or (C.DEF_ROWS, C.DEF_COLS), format=EMPTY_FORMAT)

		self.client = client
		self.focused_el = None
		self.focusable_list = []
		self.displayed_format = EMPTY_FORMAT
		self.dims_changed = True
		
		self.ev_draw_begin = UIEvent()
		self.last_writen_stdout = None

	def get_keyboard_interface(self, input_manager):
		return Keyboard(input_manager)

	def resize(self, new_size):
		if new_size == self.rel_size:
			return
		self.dims_changed = True
		
		if self.keyboard:
			with self.keyboard.io_lock:
				self.clear_screen(hard=True)
		else:
			self.clear_screen(hard=True)
		super().resize(new_size)

	def set_visible_area(self, screen_map):
		pass

	def print_screen(self):
		raise Exception("Not implemented")

	def need_draw(self):
		return False

	def get_focus_id(self):
		i_focus = 0 if self.focusable_list else -1
		for i, w in enumerate(self.focusable_list):
			if w.focused:
				i_focus = i
		return i_focus

	def set_focus(self, el):
		for e in self.focusable_list:
			if e.focused:
				e.keep_drawn_grid = False
				e.focused = False
		el.focused = True
		el.keep_drawn_grid = False

	def focus_element(self):
		PROFILER.start("focus_element")
		self.focusable_list = []
		self.explore_focusable(self.focusable_list)
		self.focusable_list = self.focusable_list[::-1]

		i = self.get_focus_id()
		if i != -1:
			self.set_focus(self.focusable_list[i])
		PROFILER.end("focus_element")

	def next_focus(self, steps=1, rotate=True):
		if self.focusable_list:
			i = self.get_focus_id()
			n = len(self.focusable_list)
			if rotate:
				i = (i + steps % n + n) % n
			else:
				i = max(min(n-1, i+steps), 0)
			self.set_focus(self.focusable_list[i])

	def detect_keys(self, keys_pressed):
		PROFILER.start("detect_keys")
		for key in keys_pressed:
			if key.check("\t") and self.focusable_list:
				self.next_focus()
			elif key.check(KeyVal.REV_TAB) and self.focusable_list:
				self.next_focus(-1)
			else:
				self.fire_key(key)
		PROFILER.end("detect_keys")

	def update(self, keys):
		self.focus_element()
		self.detect_keys(keys)
		self.focus_element()
		self.print_screen()

class WindowText(WindowManager):
	def __init__(self, *kargs, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.cursor = CursorTerminal()

	def get_keyboard_interface(self, input_manager):
		return KeyboardTerm(input_manager)

	def compute_dims(self, *kargs):
		cols, rows = shutil.get_terminal_size(fallback=(35, 100))
		self.resize((rows, cols))

		if self.dims_changed:
			self.screen_map = ScreenMap(self.size)
			super().compute_dims(self.size, self.screen_map)
			self.dims_changed = False

	def clear_screen(self, hard=False):
		# sys.stdout.write("\r")
		# sys.stdout.write("\033[K")
		if not self.screen_cleared:
			self.screen_cleared = True
			if hard:
				sys.stdout.write("\033[K")
			for i in range(self.size[0]-1):
				sys.stdout.write("\033[F") # Up one line [if not on last line]
				if hard:
					sys.stdout.write("\033[K")

	def print_screen(self):
		PROFILER.start("win - 0 - print_screen")
		PROFILER.start("win - 1 - compute_dims")
		self.compute_dims()

		PROFILER.next("win - 1 - compute_dims", "win - 2 - format map, draw")
		self.ev_draw_begin.fire()
		self.draw()

		PROFILER.next("win - 2 - format map, draw", "win - 3 - process maps - 1")

		char_map = self.screen_map.get_char_map()
		format_map = self.screen_map.get_format_map()
		PROFILER.next("win - 3 - process maps - 1", "win - 3 - process maps - 2")
		COLORS.convert_map(format_map)

		PROFILER.next("win - 3 - process maps - 2", "win - 4 - compute grid chars")
		char_map = [self.client.skin.list_to_char(l) for l in char_map]

		PROFILER.next("win - 4 - compute grid chars", "win - 5 - compute grid string")
		printed_grid_string = "\n".join([
			"".join(map(add, format_map[i_row], row))
			for i_row, row in enumerate(char_map)
		])

		PROFILER.next("win - 5 - compute grid string", "win - 6 - write grid")
		grid_hash = hash(printed_grid_string)
		if self.last_writen_stdout != grid_hash:
			self.last_writen_stdout = grid_hash
			with self.client.keyboard.io_lock:
				self.clear_screen()
				self.screen_cleared = False

				sys.stdout.write(printed_grid_string)
				sys.stdout.flush()
		
		PROFILER.end("win - 6 - write grid")
		PROFILER.end("win - 0 - print_screen")

	def pleaseCleanUpYourMess(self):
		if self.client.keyboard:
			with self.client.keyboard.io_lock:
				sys.stdout.write("\033[0m")
				self.clear_screen(True)
				sys.stdout.flush()
				self.cursor.show()