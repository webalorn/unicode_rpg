from engine.storage.skin import SkinManager
from engine.storage.config import GameConfig
from engine.client.window import *
from engine.client.widgets import *
from engine.client.keys.keyboard import *
from .utility_cls import ScreenMap, ScreenMapRel, Scene, DungeonScene
import engine.consts as C
from engine import *
from .audio import SoundPlayer
import time

class ClientWorker(MagicThread):
	def __init__(self, client):
		super().__init__()
		self.client = client

	def thread_loop(self):
		t1 = time.time()
		PROFILER.start("main loop")

		client_make_step()

		if self.EXTERN_EXIT.is_set():
			self.EXTERN_EXIT.clear()
			if self.client.scene:
				self.client.scene.ask_exit()
			else:
				self.KILL_ME_PLEASE.set()

		keys = self.client.input_manager.get_keys_gui()
		self.client.window.update(keys)

		PROFILER.end("main loop")
		t2 = time.time()
		
		delta = C.LOOP_TIME + t1 - t2
		if delta > 1e-6:
			time.sleep(delta)

class Client:
	def __init__(self, config_file="user.json", force_skin=None):
		self.cmd_args = {}
		self.keyboard = None
		self.force_skin = force_skin
		self.load_config(config_file)
		self.open_window()
		init_client_globals(self)

		self.audio = SoundPlayer()
		self.input_manager = InputManager()
		self.keyboard = self.window.get_keyboard_interface(self.input_manager)
		self.worker = ClientWorker(self)
		self.scene = None

	def open_window(self): # TODO : support other modes
		self.window = WindowText(self)

	def load_config(self, config_file):
		try:
			self.config = GameConfig(config_file)
			self.skin = SkinManager(self.force_skin or self.config.get("main", "skin"))
			self.dev_mode = self.config.get("main", "dev_mode")
		except BaseLoadError as e:
			raise e
		except Exception as e:
			raise BaseLoadError("Can't load config because : ", str(e))

	def reload_skin(self):
		self.skin = SkinManager(self.force_skin or self.config.get("main", "skin"))
		def reload_tree(node):
			node.keep_drawn_grid = False
			for child in node.children:
				reload_tree(child)
		if self.window:
			reload_tree(self.window)

	def load_scene(self, scene_cls, **scene_args):
		if self.scene:
			self.scene.stop()
		self.audio.stop() # Because we load a new main scene
		self.scene = scene_cls(self, **scene_args)
		self.scene.start()

	def start_first_scene(self, scene):
		"""
			Need to be overwriten with self.load_scene(scene_class)
		"""
		pass

	def keyboard_interrupt(self):
		if self.dev_mode:
			self.worker.KILL_ME_PLEASE.set()
		else:
			self.worker.EXTERN_EXIT.set()

	def start(self, scene=None):
		"""
			This function start the main loops and wait.
			When it returns, everything should have been cleaned
		"""
		try:
			self.start_first_scene(scene)
			self.keyboard.start()
			self.worker.start()

			# Wait until the end of the processes
			while self.worker.is_alive():
				try:
					self.worker.end_spell(join=True)
					self.keyboard.end_spell()
				except KeyboardInterrupt:
					self.keyboard_interrupt()
		finally:
			DispelMagic.releaseAll()