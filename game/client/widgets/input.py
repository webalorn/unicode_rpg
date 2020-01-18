from engine.client.widgets import *
from engine import *

class KeyInputW(TextW):
	FOCUSABLE = True
	FORMAT_FOCUSED = "game.input.key_input"

	def __init__(self, text, *kargs, v_align="center", padding=((0, 0), (2, 1)), **kwargs):
		self.text = text
		super().__init__(text, *kargs, v_align=v_align, padding=padding, **kwargs)
		self.add(KeyDisplayW("X", pos=("center", 0), inv_side=(False, True)))

class KeySetter(KeyInputW):
	def __init__(self, key_tag, *kargs, **kwargs):
		self.key_tag = key_tag
		super().__init__(*kargs, **kwargs)

class KeyInputContainer(FormLayout): # TODO : Follow scroll
	pass