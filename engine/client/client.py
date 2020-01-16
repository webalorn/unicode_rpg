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
		
		delta = C.LOOP_TIME + t1 - t2
		if delta > 1e-6:
			time.sleep(delta)

class Scene:
	def __init__(self, client):
		self.client = client
		self.window = client.window

	def start(self):
		"""
			Create all widgets for the scene
		"""
		pass

	def on_start_main_loop(self):
		"""
			Do you need to make an action before each turn of the main loop ?
		"""
		pass

	def stop(self): # 
		"""
			Clean your stuff
		"""
		self.window.children.clear()

class Client:
	START_SCENE = None

	def __init__(self):
		self.load_config()
		self.open_window()
		init_client_globals(self)

		self.input_manager = InputManager()
		self.keyboard = self.window.get_keyboard_interface(self.input_manager)
		self.worker = ClientWorker(self)
		self.scene = None

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

	def load_scene(self, scene_cls):
		if self.scene:
			self.scene.stop()
		self.scene = scene_cls(self)
		self.scene.start()

	def start(self):
		"""
			This function start the main loops and wait.
			When it returns, everything should have been cleaned
		"""
		try:
			self.load_scene(self.START_SCENE)
			self.keyboard.start()
			self.worker.start()

			# Wait until the end of the processes
			self.worker.end_spell(join=True)
			self.keyboard.end_spell()
		except KeyboardInterrupt:
			self.worker.KILL_ME_PLEASE.set()
			self.worker.join()
		finally:
			DispelMagic.releaseAll()