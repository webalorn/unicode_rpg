class Event:
	def __init__(self, events=[], one_shot=False):
		self.callbacks = []
		self.one_shot = one_shot
		self.on(events)

	def on(self, fct):
		if isinstance(fct, (list, tuple)):
			for f in fct:
				self.on(f)
		else:
			self.callbacks.append(fct)

	def off(self, fct):
		if isinstance(fct, (list, tuple)):
			for f in fct:
				self.off(f)
		elif fct:
			self.callbacks = [f for f in self.callbacks if f != fct]

	def clear(self):
		self.callbacks = []

	def fire(self, *args, **kwargs):
		for f in self.callbacks:
			if f:
				f(*args, **kwargs)

class KeyPressEvent(Event):
	def fire(self, key):
		for f in self.callbacks:
			if f and f(key):
				return True
		return False