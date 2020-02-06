from engine.client.client import Client
from .scenes.test_scene import *
from .scenes.main_scenes import *
import engine.consts as C

class GameClient(Client):
	def start_first_scene(self, scene):
		SCENES = {
			"main" : MainMenuScene,
			"options" : OptionsScene,
		}
		DEV_SCENES = {
			"game_test" : GameTestScene,
			"test" : TestScene,
			"test_2" : TestScene,
		}
		if G.CLIENT.config.get("main", "dev_mode"):
			SCENES = {**SCENES, **DEV_SCENES}
		
		if scene in SCENES:
			self.load_scene(SCENES[scene])
		else:
			raise ErrorMessage("No scene named '{}', choose from {}".format(scene, str(list(SCENES.keys()))))