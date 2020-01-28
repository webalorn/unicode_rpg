class PipeMessage:
	"""
		Base class for messages with complex structure
	"""
	def __init__(self, *kargs, **kwargs):
		self.list_args = kargs
		self.dict_args = kwargs

class CloseServer(PipeMessage):
	pass