from engine.client.client import Scene
from engine.client.widgets import *
from engine.storage.skin import SkinManager
from game.client.widgets import *
from engine import *

class MainMenuScene(Scene):
	OPTIONS_IN_WIN = False

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
		about_message = ("\nThis project is WIP\n"
			+ "\nDeveloped by @webalorn\n"
			+ "Contact me at webalorn+urpg@gmail.com\n"
		)

		win = self.root.add(ButtonsPopup(about_message, v_align="top"))
		win.add(WebLinkW("Github page", "https://github.com/webalorn/unicode_rpg", pos=("center", "center")))

	def start(self):
		self.client.audio.loop("main_menu")

		self.root.add(AnimationW("flame_anim_51_28.cbi", tile_size=(51, 28), framerate=1,
			pos=(0, 0), inv_side=(True, False)))
		self.root.add(AnimationW("flame_anim_51_28.cbi", tile_size=(51, 28), framerate=1,
			pos=(0, 0), inv_side=(True, True)))

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
		menu = self.new_panel(BoxW(size=(1., 50), border=((0, 1), 0)))
		menu_keys = menu.add(VertScrollFromW(size=(-1, 1.), pos=(1, 0), side_margin=2))

		help_text = " [ENTER] to change                [{}/X] to clear ".format(KEYS_SYMB[KeyVal.BACK])
		menu.add(TextW(help_text, text_format="dim_text", size=(1, 1.), pos=(0, 0)))

		for key_name, key_text in self.CONFIG_KEYS:
			menu_keys.add(KeySetterW(key_name, key_text, size=(3, 1.)))

	def open_apperance_panel(self):
		menu = self.new_panel(BoxW(size=(1., 70), border=((0, 1), 0)))
		menu_text = menu.add(VertScrollFromW(size=(-1, 1.), pos=(1, 0), side_margin=2))

		### Music

		text_sound = "Enable / Disable music"
		menu_text.add(TextW(text_sound, size=(1, 1.), padding=((0, 0), (2, 0)), text_format="scene.conf.area_title"))

		music_box = menu_text.add(BoxW(size=(3, 1.), border=0))
		check_music = music_box.add(CheckBoxW(G.CLIENT.config.get("main", "music"), pos=(1, 2)))
		music_state = music_box.add(TextW("---", size=(1, -4), pos=(1, 10)))

		def on_change_music():
			if check_music.checked:
				music_state.set_text("Music enabled", format="scene.conf.on_state")
			else:
				music_state.set_text("Music disabled", format="scene.conf.off_state")
			G.CLIENT.config.set("main", "music", check_music.checked)
		check_music.ev_change.on(on_change_music)
		on_change_music()

		### Skin

		if not self.client.force_skin: # If the skin is forced, we can't change it
			menu_text.add(TextW("Change the game skin", padding=((0, 0), (2, 2)), size=(2, 1.),
				text_format="scene.conf.area_title"))

			text_intro = "To change the size of the game elements, change the font size in your terminal settings. A smaller font size will allow more elements on screen, but will make the game slower. If you experience slowness issues, try to set a bigger font-size, or the resize the window to make it smaller. It will decrease the number of cells the game needs to update each frame."
			menu_text.add(TextW(text_intro, text_format="dim_text", size=(7, 1.), padding=((0, 0), (2,0))))

			b = menu_text.add(BoxW(size=(5, 1.)))
			skin_list = b.add(SelectListW(self.get_skin_list(), pos=(0, 2),
				start_id=self.client.config.get("main", "skin")))

			def on_change_skin():
				new_skin = skin_list.get_selected_key()
				self.client.config.set("main", "skin", new_skin)
				self.client.reload_skin()

			skin_list.ev_changed.on(on_change_skin)

	def open_other_panel(self):
		menu = self.new_panel(BoxW(size=(1., 70), border=((0, 1), 0)))
		menu_scroll = menu.add(VertScrollFromW(size=(-1, 1.), pos=(1, 0), side_margin=2))

		danger_area_title = menu_scroll.add(BoxW(size=(1, 1.)))
		danger_area_title.add(SymbW("symb.danger", pos=(0, 0)))
		danger_area_title.add(TextW(" Reset all settings", pos=(0, 3), size=(1, -4),
			text_format="scene.conf.danger_area"))

		def reset_settings_confirm():
			def on_confirm():
				self.client.config.reset()
				self.client.reload_skin()
				self.close_panel()
			txt = "Are you sure you want to reset all settings ? All your changes to the configuration will be erased."
			w = G.WINDOW.add(ConfirmPopupW(txt, call=on_confirm))
			w.buttons[-1].FORMAT_FOCUSED = "button_danger_focused"

		menu_scroll.add(ButtonW("Reset settings", size=12, big=True, call=reset_settings_confirm))

	def open_main_panel(self):
		menu = self.new_panel(BoxMenuVertW(size=(1., 50), border=((0, 1), 0)))

		menu.add(BoxMenuItemW("KEYS", call=self.open_keys_panel))
		menu.add(BoxMenuItemW("SOUND & APPEARANCE", call=self.open_apperance_panel))
		menu.add(BoxMenuItemW("OTHER", call=self.open_other_panel))
		menu.add(BoxMenuItemW("HELP", call=None))
		menu.add(BoxMenuItemW("BACK", call=self.close_panel))

	########## Mains

	def start(self):
		self.canvas = self.root
		if self.in_win:
			self.canvas = self.root.add(BiGWinW())
		self.container = self.canvas.add(HorScrollLayoutW(size=1., side_margin=2))

		# self.open_main_panel()
		self.open_apperance_panel()

		self.canvas.add(TextW(" [ESC] to close             [TAB] to switch           Arrows to move",
			text_format="dim_text"))

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