from engine.client.window import *
from engine.client.widgets import *
import data.consts as C
import engine.common.all as all_global
from engine import *
import time

class Client:
	def __init__(self):
		self.window = WindowText()
		all_global.WINDOW = self.window

	def run_main(self):
		all_global.CLIENT_STEPS += 1
		self.window.detect_keys()
		self.window.print_screen()
		time.sleep(C.LOOP_TIME)

	def run(self):
		try:
			while True:
				self.run_main()
		except ExitException: # Clean exit
			pass