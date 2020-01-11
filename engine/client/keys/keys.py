from engine import *
import data.consts as C

from enum import Enum

class KeyVal(Enum):
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

class Key:
	def __init__(self, key):
		self.key = key

	def isalnum(self):
		return isinstance(self.key, str) and self.key.isalnum()

	def is_char(self):
		return isinstance(self.key, str)

	def is_meta(self):
		return isinstance(self.key, KeyVal)

	def check(self, val):
		return self.key == val

	def check_in_str(self, vals):
		return isinstance(self.key, str) and self.key in vals

	def is_char_allowed(self):
		return isinstance(self.key, str) and (self.key.isalnum() or self.key in C.ALLOWED_CHARS)

	# Conversion

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