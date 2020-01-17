from engine.client.window import *
from engine.client.widgets import *
from engine.client.client import Scene
from engine import *
import time

class StartScene(Scene):
	def on_continue(self):
		self.window.add(ButtonsPopup("The game does not yet exist"))
		
	def on_new_game(self):
		self.window.add(ButtonsPopup("The game does not yet exist"))
		
	def on_load_game(self):
		self.window.add(ButtonsPopup("The game does not yet exist"))
		
	def on_options(self):
		self.window.add(ButtonsPopup("Soon configure your non-game!"))
		
	def on_about(self):
		self.window.add(ButtonsPopup("This project is WIP"))
		
	def on_quit(self):
		raise ExitException

	def start(self):
		self.title = self.window.add(ImageW("title.cbi", pos=(0, "center")))

		form = ("scene.main_menu.color", None, ["bold"])
		self.menu = self.window.add(MenuVertW(
			size=(-12, 26), border=0, pos=(12, "center"), col_size=2, format=form, v_align="center"
		))
		self.menu.add(MenuItem("CONTINUE", call=self.on_continue))
		self.menu.add(MenuItem("NEW GAME", call=self.on_new_game))
		self.menu.add(MenuItem("LOAD GAME", call=self.on_load_game))
		self.menu.add(MenuItem("OPTIONS", call=self.on_options))
		self.menu.add(MenuItem("ABOUT", call=self.on_about))
		self.menu.add(MenuItem("QUIT", call=self.on_quit))
		