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
		self.menu.add(MenuItemW("CONTINUE", call=self.on_continue))
		self.menu.add(MenuItemW("NEW GAME", call=self.on_new_game))
		self.menu.add(MenuItemW("LOAD GAME", call=self.on_load_game))
		self.menu.add(MenuItemW("OPTIONS", call=self.on_options))
		self.menu.add(MenuItemW("ABOUT", call=self.on_about))
		self.menu.add(MenuItemW("QUIT", call=self.raise_exit))
		

class OptionsScene(Scene):
	CONFIG_KEYS = [
		("game.move_up", "Move up"),
		("game.move_down", "Move down"),
		("game.move_left", "Move left"),
		("game.move_right", "Move right"),
		("game.action", "Interact / Act"),
	]
	MIN_PANEL_ARROW_CLOSE = 2

	def __init__(self, *kargs, in_win=False, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.in_win = in_win
		self.panels = []

	########## panels

	def open_keys_panel(self):
		menu = self.new_panel(BoxW(size=(1., 50)))
		menu_keys = menu.add(KeyInputContainerW(size=(-1, 1.), pos=(1, 0), border=((0, 1), 0), side_margin=2))

		help_text = " [ENTER] to change                [{}/X] to clear ".format(KEYS_SYMB[KeyVal.BACK])
		menu.add(TextW(help_text, text_format="dim_text", size=(1, 1.), pos=(0, 0)))

		for i_key, (key_name, key_text) in enumerate(self.CONFIG_KEYS):
			menu_keys.add(KeySetterW(key_name, key_text, size=(3, 1.), pos=(i_key*3, 0)))

	def open_main_panel(self):
		menu = self.new_panel(BoxMenuVertW(size=(1., 50), border=((0, 1), 0)))

		menu.add(BoxMenuItemW("KEYS", call=self.open_keys_panel))
		menu.add(BoxMenuItemW("SOUND", call=None))
		menu.add(BoxMenuItemW("TEXT", call=None))
		menu.add(BoxMenuItemW("OTHER", call=None))
		menu.add(BoxMenuItemW("BACK", call=self.close_panel))

	########## Mains

	def start(self):
		self.canvas = self.root
		if self.in_win:
			self.canvas = self.root.add(BiGWinW())
		self.container = self.canvas.add(HorScrollLayoutW(size=1., side_margin=2))

		self.open_main_panel()

		self.canvas.add(TextW("[ESC] to close", text_format="dim_text"))

	def stop(self):
		self.client.config.save()
		super().stop()

	def unhandled_keypress(self, key):
		if (key.check(KeyVal.ESCAPE) or
			(key.check(KeyVal.ARROW_LEFT) and len(self.panels) >= self.MIN_PANEL_ARROW_CLOSE)):
			self.close_panel()
		elif key.check(KeyVal.ARROW_RIGHT):
			if self.panels:
				self.panels[-1].keypress(Key("\n"))
		else:
			return False
		return True

	########## Utility functions

	def new_panel(self, panel_widget):
		self.container.add(panel_widget)
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