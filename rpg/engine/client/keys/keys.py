from engine import *
from enum import IntEnum

class KeyVal(IntEnum):
	SPECIAL = -2
	OTHER = -1

	ARROW_UP = 0
	ARROW_RIGHT = 1
	ARROW_DOWN = 2
	ARROW_LEFT = 3

	BACK = 4
	ESCAPE = 5
	REV_TAB = 6

KEY_MAP = {
	'\x7f' : KeyVal.BACK,
	'\x1b' : KeyVal.ESCAPE,
}

SPECIAL_KEY_MAP = {
	'A' : KeyVal.ARROW_UP,
	'C' : KeyVal.ARROW_RIGHT,
	'B' : KeyVal.ARROW_DOWN,
	'D' : KeyVal.ARROW_LEFT,
	'Z' : KeyVal.REV_TAB,
}

KEYS_MAPABLE = [
	KeyVal.ARROW_UP, KeyVal.ARROW_RIGHT, KeyVal.ARROW_LEFT, KeyVal.ARROW_DOWN,
]

KEYS_SYMB = {
	"\n" : "ENTER", # "↵",
	"\t" : "TAB",
	" " : "SPACE",
	KeyVal.BACK : "⌫",
	KeyVal.ESCAPE : "ESC",
	KeyVal.ARROW_UP : "↑",
	KeyVal.ARROW_RIGHT : "→",
	KeyVal.ARROW_DOWN : "↓",
	KeyVal.ARROW_LEFT : "←",
}

class Key:
	def __init__(self, key):
		self.key = key

	def isalnum(self):
		return isinstance(self.key, str) and self.key.isalnum()

	def is_char(self):
		return isinstance(self.key, str)

	def is_meta(self):
		return isinstance(self.key, KeyVal)

	def check(self, val, norm=True):
		if isinstance(val, (list, tuple)):
			for k in val:
				if self.check(k, norm):
					return True
			return False
		if norm and isinstance(val, str) and self.is_char():
			return self.key.upper() == val.upper()
		return self.key == val

	def check_in_str(self, vals):
		return isinstance(self.key, str) and self.key in vals

	# Keys categories

	def is_char_allowed(self, category="input"):
		return isinstance(self.key, str) and (self.key.isalnum() or self.key in C.ALLOWED_CHARS[category])

	def is_key_mapable(self):
		return self.is_char_allowed("mapable") or (isinstance(self.key, KeyVal) and self.key in KEYS_MAPABLE)

	# Conversion

	def norm(self):
		if isinstance(self.key, str):
			return Key(self.key.upper())
		return self

	@classmethod
	def input_to_keys_term(cls, keys):
		n, i = len(keys), 0
		real_keys = []
		while i < n:
			if keys[i] in KEY_MAP:
				val = KEY_MAP[keys[i]]
				if val == KeyVal.ESCAPE and i + 2 < n and keys[i+1] == "[": # Composite key
					if keys[i+2] in SPECIAL_KEY_MAP:
						val = SPECIAL_KEY_MAP[keys[i+2]]
					else:
						log("Unknown special key", repr(keys[i+2]), err=True)
						val = KeyVal.OTHER
					i += 2

				real_keys.append(cls(val))
			else:
				real_keys.append(cls(keys[i]))
			i += 1

		return real_keys

	@classmethod
	def from_repr(cls, key):
		if isinstance(key, str):
			return Key(key)
		elif isinstance:
			return Key(KeyVal(key))
		else:
			raise Error("Key doesn't exist : ", key)

	def to_repr(self):
		if isinstance(self.key, str):
			return self.key
		return int(self.key)

	def get_repr_symb(self):
		if self.key in KEYS_SYMB:
			return KEYS_SYMB[self.key]
		elif isinstance(self.key, str):
			return self.key
		else:
			raise Error("Key withoud symbol :", self.key)