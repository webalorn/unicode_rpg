import termios, fcntl, sys, os, time, select
from engine import *
from .keys import *

class Keyboard:
	def get_keys(self):
		return []

class KeyboardTerm(Keyboard):
	def __init__(self):
		self.fd = sys.stdin.fileno()
		self.oldterm = termios.tcgetattr(self.fd)
		self.newattr = termios.tcgetattr(self.fd)

		self.newattr[3] = self.newattr[3] & ~termios.ICANON & ~termios.ECHO
		termios.tcsetattr(self.fd, termios.TCSANOW, self.newattr)
		# termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.newattr)
		
	def get_keys(self):
		keys = []
		try:
			self.orig_fl = fcntl.fcntl(self.fd, fcntl.F_GETFL)
			fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl | os.O_NONBLOCK)
			
			while True:
				c = sys.stdin.read(1)
				if c:
					# print("Got character", repr(c))
					log("Got character", repr(c))
					keys.append(c)
				else:
					break
		except IOError:
			pass
		finally:
			fcntl.fcntl(self.fd, fcntl.F_SETFL, self.orig_fl)
		keys = Key.input_to_keys_term(keys)
		return keys

	def __exit__():
		termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.oldterm)