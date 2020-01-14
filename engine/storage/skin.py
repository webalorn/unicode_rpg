import engine.consts as C
import json
from .config import ConfigManager

class SkinManager(ConfigManager):
	MAIN_PATH = C.SKINS_PATH

	def to_char(self, code):
		if code in C.QUICK_CHARS:
			code = C.QUICK_CHARS[code]
		if isinstance(code, str) and len(code) <= 1:
			return code
		elif isinstance(code, str):
			return self.get("char", code) or "?"
		else:
			raise Exception("Char code invalid", code)

	def list_to_char(self, l):
		# return [code if isinstance(code, str) and len(code) == 1 else self.to_char(code) for code in l]
		return [
			' ' if code in [None, 0] else
			code if isinstance(code, str) and len(code) == 1
			else self.to_char(code)
		for code in l ]

	def get_charset(self, name):
		return self.get("charset", name) or "?"

	def get_skin_format(self, name):
		return self.get("format", name)