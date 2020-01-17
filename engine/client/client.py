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

class Scene:
	def __init__(self, client, root=None):
		"""
			The root must be an widget, or the window for the root scene
		"""
		self.client = client
		root_parent = client.window if root is None else root
		self.root = root_parent.add(SceneRootW(self))
		self.ev_stop = Event()
		self.root.ev_key.on(self.keypress)

	def start(self):
		"""
			Create all widgets for the scene
		"""
		pass

	def stop(self): # 
		"""
			Clean up your stuff
		"""
		self.ev_stop.fire()
		self.try_stop_subscenes(self.root)
		self.root.parent.remove(self.root)

	def try_stop_subscenes(self, node):
		for child in node.children:
			if isinstance(child, SceneRootW):
				node.scene.stop()
			else:
				self.try_stop_subscenes(child)

	def raise_exit(self):
		raise ExitException

	def ask_exit(self):
		text_exit = "Do you really want to exit {}?".format(C.PROG_NAME)
		w = self.root.add(ConfirmPopupW(text_exit, buttons=["Cancel", " Exit "], call=self.raise_exit))
		w.buttons[-1].FORMAT_FOCUSED = "button_danger_focused"

	def keypress(self, key):
		return False

class Client:
	def __init__(self, config_file="user.json"):
		self.load_config(config_file)
		self.open_window()
		init_client_globals(self)

		self.input_manager = InputManager()
		self.keyboard = self.window.get_keyboard_interface(self.input_manager)
		self.worker = ClientWorker(self)
		self.scene = None

	def open_window(self): # TODO : support other modes
		self.window = WindowText(self)

	def load_config(self, config_file):
		try:
			self.config = ConfigManager(config_file)
			self.skin = SkinManager(self.config.get("main", "skin"))
			self.dev_mode = self.config.get("main", "dev_mode")
		except BaseLoadError as e:
			raise e
		except Exception as e:
			raise BaseLoadError("Can't load config because : ", str(e))

	def load_scene(self, scene_cls, **scene_args):
		if self.scene:
			self.scene.stop()
		self.scene = scene_cls(self, **scene_args)
		self.scene.start()

	def start_first_scene(self):
		"""
			Need to be overwriten with self.load_scene(scene_class)
		"""
		pass

	def keyboard_interrupt(self):
		if self.dev_mode:
			self.worker.KILL_ME_PLEASE.set()
		else:
			self.worker.EXTERN_EXIT.set()

	def start(self):
		"""
			This function start the main loops and wait.
			When it returns, everything should have been cleaned
		"""
		try:
			self.start_first_scene()
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