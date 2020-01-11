# This file contains global variables shared by all the program,
# And the functions that need to run before everything else

from enum import Enum
import platform, os, sys

OS_NAME = platform.system() # In ['Linux', 'Darwin', 'Windows']
OS_WITH_TERM = OS_NAME in ['Linux', 'Darwin']


########## Client specific

WINDOW, CLINT_OBJ, CURSOR = None, None, None
CLIENT_STEPS = 0

def to_skin_char(c):
	return WINDOW.skin.to_char(c)

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


def init_client_globals(client):
	global WINDOW, CLINT_OBJ, CURSOR
	CLINT_OBJ = client
	WINDOW = client.window
	CURSOR = Cursor()

def client_make_step():
	global CLIENT_STEPS
	CLIENT_STEPS += 1