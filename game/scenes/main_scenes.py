from engine.client.widgets import *
from engine.client.client import Scene
from engine import *

class MainMenuScene(Scene):
	OPTIONS_IN_WIN = True

	def on_continue(self):
		self.root.add(ButtonsPopup("The game does not yet exist"))
		
	def on_new_game(self):
		self.root.add(ButtonsPopup("The game does not yet exist"))
		
	def on_load_game(self):
		self.root.add(ButtonsPopup("The game does not yet exist"))
		
	def on_options(self):
		if self.OPTIONS_IN_WIN:
			option_scene = OptionsPanelScene(self.client, self.root, in_win=True)
			option_scene.start()
		else:
			self.client.load_scene(OptionsPanelScene)
		
	def on_about(self):
		self.root.add(ButtonsPopup("This project is WIP"))

	def start(self):
		self.title = self.root.add(ImageW("title.cbi", pos=(0, "center")))

		form = ("scene.main_menu.color", None, ["bold"])
		self.menu = self.root.add(MenuVertW(
			size=(-12, 26), border=0, pos=(12, "center"), col_size=2, format=form, v_align="center"
		))
		self.menu.add(MenuItem("CONTINUE", call=self.on_continue))
		self.menu.add(MenuItem("NEW GAME", call=self.on_new_game))
		self.menu.add(MenuItem("LOAD GAME", call=self.on_load_game))
		self.menu.add(MenuItem("OPTIONS", call=self.on_options))
		self.menu.add(MenuItem("ABOUT", call=self.on_about))
		self.menu.add(MenuItem("QUIT", call=self.raise_exit))
		

class OptionsPanelScene(Scene):
	def __init__(self, *kargs, in_win=False, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.in_win = in_win

	def start(self):
		self.canvas = self.root
		if self.in_win:
			self.canvas = self.root.add(BiGWinW())
			self.canvas.ev_key.on(self.keypress)

		self.canvas.add(TextW("[ESC] to close", text_format="dim_text"))
		self.canvas.add(TextW("The option page will be here soon", pos="center"))

	def quit_options_panel(self):
		if self.in_win:
			self.stop()
		else:
			self.client.load_scene(MainMenuScene)

	def stop(self):
		self.client.config.save()
		super().stop()

	def keypress(self, key):
		if key.check(KeyVal.ESCAPE):
			self.quit_options_panel()
			return True
		return False