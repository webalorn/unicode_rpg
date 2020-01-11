from engine.client.window import *
from engine.client.widgets import *
import data.consts as C
from engine import *
import time

class Client:
	def __init__(self):
		self.window = WindowText()
		# all_global.WINDOW = self.window
		init_client_globals(self)

	def run_main(self):
		t1 = time.time()
		client_make_step()
		self.window.update()
		t2 = time.time()
		
		# log("Main loop done in : {}s".format(str(time.time()-t2)))
		time.sleep(max(0, C.LOOP_TIME + t1 - t2))

	def run(self):
		try:
			while True:
				self.run_main()
		except ExitException: # Clean exit
			pass