from .simple import *
from .input import *
from engine.client.keys import *
from engine import *

class BaseWinW(BoxW):
	def __init__(self, *kargs, closeable=True, border=1, modal=True, pos="center", size=(15, 30),
				background=0, format=EMPTY_FORMAT, **kwargs):
		super().__init__(*kargs, border=border, modal=modal, pos=pos, size=size,
			background=background, format=format, **kwargs)
		self.closeable = closeable

	def close(self):
		if self.parent:
			self.parent.remove(self)

	def keypress(self, key):
		if self.closeable and key.check(KeyVal.ESCAPE):
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
