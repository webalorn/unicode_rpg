
from engine import *
import engine.consts as C

from multiprocessing import Process, Pipe, Event
from collections import defaultdict
import time, pathlib

class SoundPlayerProcess(Process):
	def __init__(self, start_with=None, hungry=False):
		super().__init__(daemon=True)
		self.hungry = hungry
		self.sound_q_ext, self.sound_q_recv = Pipe()
		self.playing = Event()

	def run(self):
		# Import here because otherwise it cause a crash
		# print("I AM HERE " + str(self))
		from engine.client.common.playsound import playsound

		action, paths = "simple", None
		while True:
			# print("LOOP " + str(self))
			if action != "loop" or self.sound_q_recv.poll():
				action, paths = self.sound_q_recv.recv()

			if self.hungry:
				while self.sound_q_recv.poll():
					action, paths = self.sound_q_recv.recv()
			# print("OK FOR", action, paths)
			self.playing.set()
			if action == "simple":
				for p in paths:
					playsound(p)
			elif action == "loop":
				playsound(paths[0])
				paths = paths[1:] + [paths[0]]
			self.playing.clear()

	def send_to_proc(self, action, paths):
		self.sound_q_ext.send((action, paths if isinstance(paths, list) else [paths]))

	def queue(self, path):
		self.send_to_proc("simple", path)

	def loop(self, path):
		self.send_to_proc("loop", path)

class SoundManager:
	"""
		This manager ensures the sound is loaded without slowing down the UI
	"""

	def create_chan(self):
		log("CREATE")
		chan = SoundPlayerProcess()
		chan.start()
		return chan

	def __init__(self):
		self.chan = self.create_chan()
		self.preloaded_chan = self.create_chan()

	def is_sound_enabled(self):
		return G.CLIENT.config.get("main", "music")

	def queue_path(self, path, loop=False, stop=True):
		if stop:
			self.stop()
		if self.is_sound_enabled():
			log("queue", path, loop, self.chan, self.preloaded_chan)
			if loop:
				self.chan.loop(path)
			else:
				self.chan.queue(path)

	def play(self, name, loop=False, stop=True):
		path = G.CLIENT.skin.get("audio", name)
		log(name, path)
		if path:
			path = pathlib.Path(C.AUDIO_PATH) / path
			self.queue_path(str(path), loop=loop, stop=stop)
		else:
			log("Sound name doesn't exists", name)

	def loop(self, name, stop=True):
		self.play(name, True, stop)

	def stop(self):
		log("STOP", self.chan.playing.is_set(), self.chan.is_alive())
		if self.chan.playing.is_set():
			self.chan.terminate()
			self.chan.join()
			log(self.chan, self.chan.is_alive())
			self.chan = self.preloaded_chan
		self.preloaded_chan = self.create_chan()