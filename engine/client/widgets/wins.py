from .simple import *
from .input import *
from .layouts import *
from engine.client.keys import *
from engine import *

class BaseWinW(BoxW):
	def __init__(self, *kargs, closeable=True, border=1, modal=True, pos="center", size=(15, 60),
				background=0, format=EMPTY_FORMAT, **kwargs):
		super().__init__(*kargs, border=border, modal=modal, pos=pos, size=size,
			background=background, format=format, **kwargs)
		self.closeable = closeable

	def close(self):
		if self.parent:
			self.parent.remove(self)
			self.parent = None

	def keypress(self, key):
		if self.closeable and key.check(KeyVal.ESCAPE):
			self.close()
		return super().keypress(key)

class BiGWinW(BaseWinW):
	def __init__(self, *kargs, free_space=1, **kwargs):
		kwargs["pos"] = (free_space, free_space*2)
		kwargs["size"] = (-free_space*2, -free_space*4)
		super().__init__(*kargs, **kwargs)

class TextPopupW(BaseWinW):
	def __init__(self, text, *kargs, align="center", v_align="center", text_format=None, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.add(TextW(text, align=align, v_align=v_align, size=(1., 1.)))

	def keypress(self, key):
		if key.check("\n"):
			self.close()
		return super().keypress(key)

class ButtonsPopup(TextPopupW):
	def __init__(self, *kargs, buttons=["Close"], call=["close"], always_remove=False, **kwargs):
		super().__init__(*kargs, **kwargs)

		self.children[0].size = (-3, 1.)
		v_box = self.add(HorLayoutW(size=(3, 1.), inv_side=(True, False), anchor="center", spacing=2))

		self.buttons = [v_box.add(ButtonW(message, big=True)) for message in buttons]
		for button, fct in zip(self.buttons, call):
			if fct == "close":
				fct = self.close
			elif always_remove:
				button.ev_pressed.on(self.close)
			button.ev_pressed.on(fct)

	def keypress(self, key):
		return False

class ConfirmPopupW(ButtonsPopup):
	def __init__(self, *kargs, buttons=["Cancel", "  Ok  "], call=None, always_remove=True, **kwargs):
		super().__init__(*kargs, buttons=buttons, call=["close", call], always_remove=always_remove, **kwargs)