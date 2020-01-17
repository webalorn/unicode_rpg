from threading import Thread, Event, Lock
from .exceptions import ExitException
from .log import log

class MagicThread(Thread):
	KILL_ME_PLEASE = Event()
	EXTERN_EXIT = Event()

	def __init__(self, *kargs, **kwargs):
		super().__init__(*kargs, **kwargs)
		self.exception = None

	def run(self):
		try:
			while not self.KILL_ME_PLEASE.is_set():
				self.thread_loop()
		except KeyboardInterrupt as e:
			self.EXTERN_EXIT.set()
		except ExitException as e:
			self.KILL_ME_PLEASE.set()
		except Exception as e:
			log("Exception in thread {} :".format(str(self.__class__.__name__)), str(e), err=True)
			self.KILL_ME_PLEASE.set()
			self.exception = e

	def thread_loop(self):
		pass

	def end_spell(self, join=False):
		if join:
			self.join()
		if self.exception:
			e = self.exception
			self.exception = None
			raise e