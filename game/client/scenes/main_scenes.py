from engine.client.client import Scene
from engine.client.widgets import *
from game.client.widgets import *
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
			option_scene = OptionsScene(self.client, self.root, in_win=True)
			option_scene.start()
		else:
			self.client.load_scene(OptionsScene)
		
	def on_about(self):
		self.root.add(ButtonsPopup("This project is WIP"))

	def start(self):
		self.title = self.root.add(ImageW("title.cbi", pos=(0, "center")))

		self.menu = self.root.add(MenuVertW(
			size=(-12, 26), border=(1, 0), pos=(12, "center"), col_size=2,
			format="scene.main_menu.menu", v_align="center"
		))
		self.menu.add(MenuItem("CONTINUE", call=self.on_continue))
		self.menu.add(MenuItem("NEW GAME", call=self.on_new_game))
		self.menu.add(MenuItem("LOAD GAME", call=self.on_load_game))
		self.menu.add(MenuItem("OPTIONS", call=self.on_options))
		self.menu.add(MenuItem("ABOUT", call=self.on_about))
		self.menu.add(MenuItem("QUIT", call=self.raise_exit))
		

class OptionsScene(Scene):
	CONFIG_KEYS = [
		("game.move_up", "Move up"),
		("game.move_down", "Move down"),
		("game.move_left", "Move left"),
		("game.move_right", "Move right"),
	]

	def __init__(self, *kargs, in_win=False, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.in_win = in_win
		self.panels = []

	########## panels

	def open_keys_panel(self):
		menu = self.new_panel(KeyInputContainer(size=(1., 50), border=((0, 1), 0)))

		for i_key, (key_name, key_text) in enumerate(self.CONFIG_KEYS):
			menu.add(KeySetter(key_name, key_text, size=(3, 1.), pos=(i_key*3, 0)))

	def open_main_panel(self):
		menu = self.new_panel(BoxMenuVertW(size=(1., 50), border=((0, 1), 0)))

		menu.add(BoxMenuItem("KEYS", call=self.open_keys_panel))
		menu.add(BoxMenuItem("SOUND", call=None))
		menu.add(BoxMenuItem("TEXT", call=None))
		menu.add(BoxMenuItem("OTHER", call=None))
		menu.add(BoxMenuItem("BACK", call=self.close_panel))

	########## Mains

	def start(self):
		self.canvas = self.root
		if self.in_win:
			self.canvas = self.root.add(BiGWinW())
			self.canvas.ev_key.on(self.keypress)

		self.open_main_panel()
		# self.open_keys_panel()

		self.canvas.add(TextW("[ESC] to close", text_format="dim_text"))

		# self.canvas.add(KeyInputW("Move forward", size=(3, 30), pos="center", format=(None, "black", [])))

	def stop(self):
		self.client.config.save()
		super().stop()

	def keypress_intercept(self, key):
		if key.check(KeyVal.ESCAPE):
			self.close_panel()
			return True
		return False

	########## Utility functions

	def get_panel_right(self):
		if not self.panels:
			return 0
		return self.panels[-1].pos[1] + self.panels[-1].size[1]

	def new_panel(self, panel_widget):
		self.canvas.add(panel_widget)
		panel_widget.move_to((0, self.get_panel_right()))
		self.panels.append(panel_widget)
		return panel_widget

	def quit_options_panel(self):
		if self.in_win:
			self.stop()
		else:
			self.client.load_scene(MainMenuScene)

	def close_panel(self):
		if self.panels:
			self.panels[-1].delete()
			self.panels.pop()
		if not self.panels:
			self.quit_options_panel()