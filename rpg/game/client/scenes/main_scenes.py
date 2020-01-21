from engine.client.client import Scene
from engine.client.widgets import *
from engine.storage.skin import SkinManager
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
		win = self.root.add(ButtonsPopup("\nThis project is WIP\n\n([TAB] to move focus)", v_align="top"))
		win.add(WebLinkW("Github page", "https://github.com/webalorn/unicode_rpg", pos=("center", "center")))

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
	CONFIG_SOUND = [
		("sound.main", "Main volume"),
		("sound.music", "Music volume"),
		("sound.effets", "Sound effets volume"),
	]
	MIN_PANEL_ARROW_CLOSE = 2

	def __init__(self, *kargs, in_win=False, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.in_win = in_win
		self.panels = []

	########## panels

	def open_keys_panel(self):
		menu = self.new_panel(BoxW(size=(1., 50), border=((0, 1), 0)))
		menu_keys = menu.add(VertScrollFromW(size=(-1, 1.), pos=(1, 0), side_margin=2))

		help_text = " [ENTER] to change                [{}/X] to clear ".format(KEYS_SYMB[KeyVal.BACK])
		menu.add(TextW(help_text, text_format="dim_text", size=(1, 1.), pos=(0, 0)))

		for key_name, key_text in self.CONFIG_KEYS:
			menu_keys.add(KeySetterW(key_name, key_text, size=(3, 1.)))

	def open_sound_panel(self): # TODO
		menu = self.new_panel(BoxW(size=(1., 50), border=((0, 1), 0)))
		menu_sound = menu.add(VertScrollFromW(size=(-1, 1.), pos=(1, 0), side_margin=5, h_align="center"))

		help_text = " Left/Right arrow to change the volume"
		menu.add(TextW(help_text, text_format="dim_text", size=(1, 1.), pos=(0, 0)))

		for vol_name, vol_text in self.CONFIG_SOUND:
			menu_sound.add(TextW(vol_text, size=(3, 48), v_align="center", padding=((0, 0), (2, 2))))
			menu_sound.add(VolumeSetterW(vol_name, size=(1, 47)))

	def open_text_panel(self):
		menu = self.new_panel(BoxW(size=(1., 70), border=((0, 1), 0)))
		menu_text = menu.add(VertScrollFromW(size=(-1, 1.), pos=(1, 0), side_margin=2))

		text_intro = "To change the size of the game elements, change the font size in your terminal settings. A smaller font size will allow more elements on screen, but will make the game slower. If you experience slowness issues, try to set a bigger font-size, or the resize the window to make it smaller. It will decrease the number of cells the game needs to update each frame."
		menu_text.add(TextW(text_intro, text_format="dim_text", size=(7, 1.), padding=((0, 0), (2,0))))

		if not self.client.force_skin: # If the skin is forced, we can't change it
			menu_text.add(TextW("Change the game skin", padding=((0, 0), (2, 2)), size=(2, 1.),
				text_format=(None, None, ["underlined"])))

			skin_list = menu_text.add(SelectListW(self.get_skin_list(), pos=(10, 3),
				start_id=self.client.config.get("main", "skin")))

			def on_change_skin():
				new_skin = skin_list.get_selected_key()
				self.client.config.set("main", "skin", new_skin)
				self.client.reload_skin()

			skin_list.ev_changed.on(on_change_skin)

	def open_main_panel(self):
		menu = self.new_panel(BoxMenuVertW(size=(1., 50), border=((0, 1), 0)))

		menu.add(BoxMenuItemW("KEYS", call=self.open_keys_panel))
		menu.add(BoxMenuItemW("SOUND", call=self.open_sound_panel))
		menu.add(BoxMenuItemW("APPEARANCE", call=self.open_text_panel))
		menu.add(BoxMenuItemW("OTHER", call=None))
		menu.add(BoxMenuItemW("HELP", call=None))
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

	@staticmethod
	def get_skin_list():
		l = SkinManager.get_available_list()
		return {el : "Skin " + el[:-5] for el in l}

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