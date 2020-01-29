
from engine import *
import engine.consts as C

from multiprocessing import Process, Pipe, Event
from collections import defaultdict
import time, pathlib

class SoundPlayerProcess(Process):
	def __init__(self, start_with=None, hungry=False, auto_start=True):
		super().__init__(daemon=True)
		self.hungry = hungry
		self.sound_q_ext, self.sound_q_recv = Pipe()
		self.playing = Event()
		if auto_start:
			self.start()

	def run(self):
		# Import here because otherwise it cause a crash
		from engine.client.common.playsound import playsound

		action, paths = "simple", None
		while True:
			if action != "loop" or self.sound_q_recv.poll():
				action, paths = self.sound_q_recv.recv()

			if self.hungry:
				while self.sound_q_recv.poll():
					action, paths = self.sound_q_recv.recv()
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
	LONG_CHANNELS = ["music"]
	WAITER_CHANNELS = ["music"]
	INIT_CHANNELS = ["music", "ui"]

	def __init__(self):
		self.channels = {}
		self.preloaded_chans = {}

		for chan in self.LONG_CHANNELS:
			if self.is_channel_active(chan):
				self.init_chan(chan)
				self.preloaded_chans[chan] = self.channels[chan]
		self.channels = {}
		for chan in self.INIT_CHANNELS:
			self.init_chan(chan)

	def is_channel_active(self, chan):
		return True
		# return G.CLIENT.config.is_channel_active(chan)

	def init_chan(self, chan, force=False):
		if not chan in self.channels:
			hungry = chan not in self.WAITER_CHANNELS
			self.channels[chan] = SoundPlayerProcess(hungry=hungry)

		elif (chan in self.LONG_CHANNELS) or force and self.channels[chan].playing.is_set():
			self.channels[chan].terminate()
			del self.channels[chan]
			self.init_chan(chan)

			if chan in self.LONG_CHANNELS:
				self.channels[chan], self.preloaded_chans[chan] = self.preloaded_chans[chan], self.channels[chan]

	def play_path(self, chan, path, loop=False):
		if self.is_channel_active(chan):
			self.init_chan(chan)
			log("Start", path, "loop ?", loop)
			if loop:
				self.channels[chan].loop(path)
			else:
				self.channels[chan].queue(path)

	def play(self, chan, name, loop=False):
		# Skin path will be audio.chan.name
		log("Will play on {} the audio {}".format(chan, name))
		path = G.CLIENT.skin.get("audio", ".".join([chan, name]))
		if path:
			path = pathlib.Path(C.AUDIO_PATH) / chan / path
			self.play_path(chan, str(path), loop=loop)
		else:
			log("Sound name doesn't exists", name)

	def loop(self, chan, name):
		self.play(chan, name, True)

	def stop(self, chan):
		if chan in self.channels:
			self.init_chan(chan, froce=True)

	def stop_all(self):
		for name, chan in self.channels.items():
			self.stop(chan)