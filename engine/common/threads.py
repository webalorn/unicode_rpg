from threading import Thread, Event, Lock
from .exceptions import ExitException
from .log import log

class MagicThread(Thread):
	KILL_ME_PLEASE = Event()

	def __init__(self, *kargs, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.exception = None

	def run(self):
		try:
			while not self.KILL_ME_PLEASE.is_set():
				self.thread_loop()
		except (ExitException, KeyboardInterrupt) as e:
			self.KILL_ME_PLEASE.set()
		except Exception as e:
			self.KILL_ME_PLEASE.set()
			self.exception = e

	def thread_loop(self):
		pass

	def end_spell(self, join=False):
		if join:
			self.join()
		if self.exception:
			raise self.exception