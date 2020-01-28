import termios, fcntl, sys, os, time, select
from queue import Queue
from engine import *
from .keys import *

class NonBlockingContext: 
	def __init__(self, fd):
		self.fd = fd

	def __enter__(self):
		self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
		fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
	
	def __exit__(self, exc_type, exc_value, exc_traceback):
		fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)

class InputManager():
	def __init__(self):
		self.keys_queue = Queue()
		self.prio_list = []

	def add_key(self, key):
		for prio in self.prio_list:
			if prio.accept_prio_key(key):
				return
		self.keys_queue.put(key)

	def get_keys_gui(self):
		keys = []
		while not self.keys_queue.empty():
			try:
				keys.append(self.keys_queue.get_nowait())
			except:
				break
		return keys

	def clear_prio(self):
		self.prio_list = []

	def register_prio(self, obj):
		self.prio_list.append(obj)

class Keyboard(MagicThread):
	def __init__(self, input_manager):
		super().__init__(daemon=True)
		self.input_manager = input_manager

	def get_keys(self):
		return []

	def thread_loop(self):
		keys = self.get_keys()
		for key in keys:
			self.input_manager.add_key(key)

class KeyboardTerm(Keyboard):
	def __init__(self, *kargs, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.fd = sys.stdin.fileno()
		self.oldterm = termios.tcgetattr(self.fd)
		self.newattr = termios.tcgetattr(self.fd)

		self.newattr[3] = self.newattr[3] & ~termios.ICANON & ~termios.ECHO
		termios.tcsetattr(self.fd, termios.TCSANOW, self.newattr)

		self.io_lock = Lock()
		self.non_block = NonBlockingContext(self.fd)

	def get_keys(self):
		keys = []
		try:
			last_char = sys.stdin.read(1)
			with self.io_lock, self.non_block:
				while last_char:
					# log("Got character", repr(last_char))
					keys.append(last_char)
					last_char = sys.stdin.read(1)
		except IOError:
			pass

		return Key.input_to_keys_term(keys)

	def __exit__():
		termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.oldterm)