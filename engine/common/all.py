# This file contains global variables shared by all the program,
# And the functions that need to run before everything else

from enum import Enum
import platform, os, sys

OS_NAME = platform.system() # In ['Linux', 'Darwin', 'Windows']
OS_WITH_TERM = ['Linux', 'Darwin']
WINDOW = None

def to_skin_char(c):
	return WINDOW.skin.to_char(c)

########## Steps : one step is added each time the main loop advance

CLIENT_STEPS = 0
def get_cycle_val(cycle_time, modul=2):
	return (CLIENT_STEPS // cycle_time) % 2

########## Cursor (adapted from https://github.com/GijsTimmers/cursor/blob/master/cursor/cursor.py)

if os.name == 'nt':
	import ctypes

	class _CursorInfo(ctypes.Structure):
		_fields_ = [("size", ctypes.c_int),
					("visible", ctypes.c_byte)]

class Cursor:
	def hide(self, stream=sys.stdout):
		if os.name == 'nt':
			ci = _CursorInfo()
			handle = ctypes.windll.kernel32.GetStdHandle(-11)
			ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
			ci.visible = False
			ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
		elif os.name == 'posix':
			stream.write("\033[?25l")
			stream.flush()

	def show(self, stream=sys.stdout):
		if os.name == 'nt':
			ci = _CursorInfo()
			handle = ctypes.windll.kernel32.GetStdHandle(-11)
			ctypes.windll.kernel32.GetConsoleCursorInfo(handle, ctypes.byref(ci))
			ci.visible = True
			ctypes.windll.kernel32.SetConsoleCursorInfo(handle, ctypes.byref(ci))
		elif os.name == 'posix':
			stream.write("\033[?25h")
			stream.flush()

	def __init__(self):
		self.hide()

	def __del__(self):
		self.show()

########## Run functions

CURSOR = Cursor()