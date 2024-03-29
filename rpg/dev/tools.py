import time
from engine.common.log import log
from engine.common.all import G, DispelMagic

class Profiler(DispelMagic):
	def __init__(self):
		super().__init__()
		self.inits = {}
		self.sums = {}
		self.to_log = {}

	def start(self, name):
		self.inits[name] = time.time()

	def end(self, name):
		t = time.time()
		if not name in self.sums:
			self.sums[name] = 0
		if name in self.inits:
			self.sums[name] += t - self.inits[name]

	def log_task_start(self, name):
		self.to_log[name] = time.time()

	def log_task_end(self, name):
		t = time.time() - self.to_log[name]
		del self.to_log[name]
		log("# {} took {}ms to execute".format(name, round(t*1000 / G.CLIENT_STEPS, 2)))

	def next(self, old_name, new_name):
		self.end(old_name)
		self.start(new_name)

	def pleaseCleanUpYourMess(self):
		log("Time taken by tasks per cycle [average] : ")
		for name, t in sorted(list(self.sums.items())):
			log("    - {} : {}ms".format(name, round(t*1000 / G.CLIENT_STEPS, 2)))

PROFILER = Profiler()