from engine import *
import engine.consts as C

from threading import Thread
from queue import Queue
import time, pathlib

try:
	import simpleaudio
except: # If the package is not installed
	simpleaudio = False

class SoundPlayer(Thread):
	FAKE = False
	def __init__(self):
		super().__init__(daemon=True)

		self.cache = {}
		self.cur_sound = None
		self.last_path = None
		self.play_q = Queue()

		self.start()

	def get_sound_obj(self, path):
		if not path in self.cache:
			self.cache[path] = simpleaudio.WaveObject.from_wave_file(path)
		return self.cache[path]

	def _in_play(self, path):
		o = self.get_sound_obj(path)
		self.last_path = path
		self.cur_sound = o.play()

	def run(self):
		paths = []
		while True:
			new_paths = False
			while not self.play_q.empty() or (self.cur_sound == None and not new_paths):
				paths = self.play_q.get()
				new_paths = True

			if new_paths or not self.cur_sound.is_playing():
				if paths and paths[0] == None:
					paths = []
				if self.cur_sound:
					self.cur_sound.stop()
					self.cur_sound = None
				if paths:
					self._in_play(paths[0])
					paths = paths[1:] + [paths[0]]

			# if self.cur_sound and self.cur_sound.is_playing():
			# 	time.sleep(0.05)
			time.sleep(0.01)

	def stop(self):
		self.play_q.put([])

	def play_path(self, paths):
		if G.CLIENT.config.get("main", "music"):
			self.play_q.put(paths if isinstance(paths, list) else [paths])

	def name2path(self, name, force_list=False):
		if isinstance(name, (list, tuple)):
			return [name2path(n) for n in name]
		path = G.CLIENT.skin.get("audio", name)
		if path:
			path = pathlib.Path(C.AUDIO_PATH) / path
			return [str(path)] if force_list else str(path)
		else:
			log("Sound name doesn't exists", name)
			return ""

	def play(self, name):
		self.play_path(self.name2path(name))

	def play_oneshot(self, name):
		self.play_path([self.name2path(name, force_list=True)] + [None])

	def is_playing(self):
		return self.cur_sound and self.cur_sound.is_playing()

class FakeSoundPlayer:
	FAKE = True

	def stop(*args, **kwargs):
		pass
	def play_path(*args, **kwargs):
		pass
	def name2path(*args, **kwargs):
		return ""
	def play(*args, **kwargs):
		pass
	def play_oneshot(*args, **kwargs):
		pass
	def is_playing(*args, **kwargs):
		return False

if not simpleaudio:
	SoundPlayer = FakeSoundPlayer