import engine.consts as C
import json

class Skin:
	def __init__(self, name='default'):
		self.name = name
		skin_file = open(C.SKINS_PATH[name], 'r')
		self.skin_data = json.load(skin_file)

	def get_in_data(self, path, data):
		return data if not path else self.get_in_data(path[1:], data[path[0]])

	def to_char(self, c):
		if c in C.QUICK_CHARS:
			c = C.QUICK_CHARS[c]
		if type(c) == str and len(c) <= 1:
			return c
		elif type(c) == str:
			return self.get_in_data(c.split("."), self.skin_data)
		else:
			raise Exception("Char code invalid", c)