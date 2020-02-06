class Error(Exception):
	pass

class ExitException(Exception):
	pass

class ErrorMessage(Error):
	def __init__(self, *args):
		self.message = " ".join([str(txt) for txt in args])

class BaseLoadError(ErrorMessage):
	pass