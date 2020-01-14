from engine import DispelMagic
import platform, os, sys

########## Cursor (adapted from https://github.com/GijsTimmers/cursor/blob/master/cursor/cursor.py)

if os.name == 'nt':
	import ctypes

	class _CursorInfo(ctypes.Structure):
		_fields_ = [("size", ctypes.c_int),
					("visible", ctypes.c_byte)]

class CursorTerminal:
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
		super().__init__()
		self.hide()