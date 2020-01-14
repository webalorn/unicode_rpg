from engine.client.window import *
from engine.client.widgets import *
from engine.client.client import Client
import time
from engine import *

class GameClient(Client):
	def __init__(self):
		super().__init__()

		def call_button():
			self.window.add(TextPopupW("Bouton cliqué"))

		self.window.add(ButtonW("coucou", size=12, big=True, call=call_button))
		self.window.add(BarInputW(1, size=30, format=('white', 'yellow', []), maxi=50, step=1, pos=(5, 4)))

		col = self.window.add(VertLayoutW(size=(1., 30), force_width=False, anchor="center", h_align="center"))
		# col = self.window.add(HorLayoutW(size=(20, 1.), force_height=False, anchor="right"))

		for _ in range(3):
			txt = SimpleTextW("abcdefghijklmnopqrstuvwxyz", size=(4, 16))
			box = BoxW(add=txt, size=(6, 24), pos=5, border=1)
			col.add(box)

		txt2 = TextInputW("abc defg", size=(3, 14), w_break=True, border=1)
		box2 = BoxW(add=txt2, size=(6, 18), pos=6, border=1, background=0)
		col.add(box2)


		txt = SimpleTextW("Super boite", size=(4, 16))
		self.window.add(BoxW(add=txt, size=(6, 24), pos=(12, 5), border=1, background=0))

		def f():
			raise ExitException("END")

		def g():
			self.window.add(TextPopupW("Coucou, ça va ?"))
		form = ("red", None, ["bold"])

		menu = self.window.add(MenuVertW(size=(15, 15), border=1, pos="center", col_size=2, scroll=True, format=form))
		menu.add(MenuItem("Bonjour. Ceci est un test de GUI avec mon truc un peu mal foutu", call=g, text_format=('yellow', 'inherit', 'inherit')))
		menu.add(MenuItem("there it is, coucou", call=f))
		menu.add(MenuItem("test", align="center"))
		menu.add(MenuItem("test", align="center"))
		menu.add(MenuItem("test", align="center"))
		menu.add(MenuItem("test", align="center"))
		menu.add(MenuItem("test", align="center"))
		menu.add(MenuItem("test", align="center"))
		menu.add(MenuItem("test", align="center"))