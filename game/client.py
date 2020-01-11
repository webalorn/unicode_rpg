from engine.client.window import *
from engine.client.widgets import *
from engine.client.client import Client
import data.consts as C
import time
from engine import *

class GameClient(Client):
	def __init__(self):
		super().__init__()

		txt = SimpleTextW("abcdefghijklmnopqrstuvwxyz", size=(4, 16))
		box = BoxW(add=txt, size=(6, 18), pos=5, border=1)
		self.window.add(box)

		txt2 = TextInputW("abc defg", size=(3, 16), w_break=True, border=1)
		box2 = BoxW(add=txt2, size=(6, 18), pos=6, border=1, background=0)
		self.window.add(box2)

		menu = self.window.add(MenuVertW(size=(30, 20), border=1, pos="center", col_size=2))
		menu.add(MenuItem("Bonjour. Ceci est un test de GUI avec mon truc un peu mal foutu"))
		def f():
			raise ExitException("END")
		menu.add(MenuItem("there it is, coucou", call=f))
		menu.add(MenuItem("test", align="right"))
