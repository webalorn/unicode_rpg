import time
from engine.common.log import log
import engine.common.all as A


class Profiler():
	def __init__(self):
		self.inits = {}
		self.sums = {}

	def start(self, name):
		self.inits[name] = time.time()

	def end(self, name):
		t = time.time()
		if not name in self.sums:
			self.sums[name] = 0
		if name in self.inits:
			self.sums[name] += t - self.inits[name]

	def next(self, old_name, new_name):
		self.end(old_name)
		self.start(new_name)

	def __del__(self):
		print("Time taken by tasks per cycle [average] : ")
		for name, t in sorted(list(self.sums.items())):
			print("    - {} : {}ms".format(name, int(t*1000 / A.CLIENT_STEPS)))

PROFILER = Profiler()