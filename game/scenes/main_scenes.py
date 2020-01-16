from engine.client.window import *
from engine.client.widgets import *
from engine.client.client import Scene
from engine import *
import time

class StartScene(Scene):
	def start(self):
		self.window.add(TextW("Not build yet", size=(1, 30), align="center", pos="center"))