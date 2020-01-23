from engine.client.client import Client
from .scenes.test_scene import *
from .scenes.main_scenes import *
import engine.consts as C

class GameClient(Client):
	def start_first_scene(self):
		if G.CLIENT.config.get("main", "dev_start_scene"):
			# self.load_scene(OptionsScene)
			self.load_scene(TestScene)
		else:
			self.load_scene(MainMenuScene)
