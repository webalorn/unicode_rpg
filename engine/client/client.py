from engine.storage.skin import SkinManager
from engine.storage.config import ConfigManager
from engine.client.window import *
from engine.client.widgets import *
from engine.client.keys.keyboard import *
import engine.consts as C
from engine import *
import time

class ClientWorker(MagicThread):
	def __init__(self, client):
		super().__init__()
		self.client = client

	def thread_loop(self):
		t1 = time.time()
		PROFILER.start("main loop")

		client_make_step()
		keys = self.client.input_manager.get_keys_gui()
		self.client.window.update(keys)

		PROFILER.end("main loop")
		t2 = time.time()
		
		# log("Main loop done in : {}ms".format(str(int((t2-t1)*1000))))
		delta = C.LOOP_TIME + t1 - t2
		if delta > 1e-6:
			time.sleep(delta)
		# raise ExitException

class Client:
	def __init__(self):
		self.load_config()
		self.open_window()
		init_client_globals(self)

		# self.main_loop_thread = Thread(target=self.run_main_loop)
		self.input_manager = InputManager()
		self.keyboard = self.window.get_keyboard_interface(self.input_manager)
		self.worker = ClientWorker(self)

	def open_window(self): # TODO : support other modes
		self.window = WindowText(self)

	def load_config(self):
		try:
			self.config = ConfigManager('user.json')
			self.skin = SkinManager(self.config.get("main", "skin"))
		except BaseLoadError as e:
			raise e
		except Exception as e:
			raise BaseLoadError("Can't load config because : ", str(e))

	def start(self):
		"""
			This function start the main loops and wait.
			When it returns, everything should have been cleaned
		"""
		self.keyboard.start()
		self.worker.start()

		try:
			self.worker.end_spell(join=True)
			self.keyboard.end_spell()
		except KeyboardInterrupt:
			self.worker.KILL_ME_PLEASE.set()
			self.worker.join()

		DispelMagic.releaseAll()

	# def run_main_loop(self):
	# 	try:
	# 		while True:
	# 			t1 = time.time()
	# 			PROFILER.start("main loop")

	# 			client_make_step()
	# 			keys = self.input_manager.get_keys_gui()
	# 			self.window.update(keys)

	# 			PROFILER.end("main loop")
	# 			t2 = time.time()
				
	# 			# log("Main loop done in : {}ms".format(str(int((t2-t1)*1000))))
	# 			time.sleep(max(0, C.LOOP_TIME + t1 - t2))
	# 			# raise ExitException
	# 	except ExitException: # Clean exit
	# 		pass