class Error(Exception):
	pass

class ExitException(Exception):
	pass

class BaseLoadError(Exception):
	def __init__(self, *args):
		self.message = " ".join([str(txt) for txt in args])