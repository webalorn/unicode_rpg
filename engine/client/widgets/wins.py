from .simple import *
from .input import *
import data.consts as C
from engine.client.keys import *
from engine import *

class BaseWinW(BoxW):
	def __init__(self, *kargs, escape_close=True, border=1, modal=True, pos="center", size=(15, 30), background=0, **kwargs):
		super().__init__(*kargs, border=border, modal=modal, pos=pos, size=size, background=background, **kwargs)
		self.escape_close = escape_close

	def close(self):
		if self.parent:
			self.parent.remove(self)

	def keypress(self, key):
		if self.escape_close and key.check(KeyVal.ESCAPE):
			self.close()
		return super().keypress(key)

class TextPopupW(BaseWinW):
	def __init__(self, text, *kargs, align="center", v_align="center", text_format=None, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.add(SimpleTextW(text, align=align, v_align=v_align, size=(1., 1.)))

	def keypress(self, key):
		if key.check("\n"):
			self.close()
		return super().keypress(key)
