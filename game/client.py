from engine.client.client import Client
from .scenes.test_scene import *

class GameClient(Client):
	START_SCENE = TestScene