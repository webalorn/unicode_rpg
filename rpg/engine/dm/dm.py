from multiprocessing import Process, Pipe
from multiprocessing import Event as EventMultiProc
from engine import *
from .messages import *
import time

class DungeonMaster(Process):
	"""
		Abstract class for game servers
	"""
	def __init__(self):
		super().__init__(daemon=True)

		self.ext_pipe, self._entry_pipe = Pipe()
		self.DEAD = EventMultiProc()
		self.serv = None
		self._thread_pool = []

	def run(self):
		try:
			while True:
				if self.DEAD.is_set():
					break
				for th in self._thread_pool:
					if th.KILL_ME_PLEASE.is_set() or self.serv.EXTERN_EXIT.is_set(): # In case of error
						raise ExitException(self.serv, "killed")
				messages = get_pipe_messages(self._entry_pipe)
				for m in messages:
					if isinstance(m, CloseServer):
						break
				self.main_loop(messages)
		except Exception as e:
			self.DEAD.set()
			raise e
		finally:
			self._in_close()

	def main_loop(self, messages):
		for m in messages:
			log_dm("Got message", m)
		time.sleep(0.1)

	def _in_close(self):
		"""
			Can be used to save datas, etc...
		"""
		pass

	def close_dm_ext(self):
		"""
			Used by external functions to ask the DM to stop itself
		"""
		self.ext_pipe.send(CloseServer())