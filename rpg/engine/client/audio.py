from threading import Thread
from queue import Queue
from collections import defaultdict
import simpleaudio
import time, wave, struct, array
from engine import *
import engine.consts as C
from pathlib import Path

class SoundPlayer:
	def __init__(self, start_with=None, volume=1):
		if abs(volume-1) < 0.001:
			volume = 1

		self.cache = {}
		self.loop = False
		self.volume = volume
		self.cur_sound = None
		self.last_path = None
		if start_with:
			self.start(start_with)

	def stop(self):
		if self.cur_sound:
			self.cur_sound.stop()
			self.cur_sound = None
			self.loop = False
			self.last_path = None

	def get_sound_obj(self, path):
		if not path in self.cache:
			if self.volume == 1:
				self.cache[path] = simpleaudio.WaveObject.from_wave_file(path)
			else:
				w = wave.open(path)
				p = w.getparams()
				sn = array.array('h')
				sn.frombytes(w.readframes(p[3]))
				sn = [min(32767, max(-32767, int(v*self.volume))) for v in sn]
				s1 = struct.pack('h'*len(sn), *sn)

				self.cache[path] = simpleaudio.WaveObject(s1, p.nchannels, p.sampwidth, p.framerate)
		return self.cache[path]

	def play(self, path, block=False):
		self.stop()
		o = self.get_sound_obj(path)
		self.last_path = path
		self.cur_sound = o.play()
		if block:
			self.cur_sound.wait_done()

	def restart_loop(self):
		if self.last_path and self.loop:
			self.play(self.last_path)
			self.loop = True

	def is_playing(self):
		return self.cur_sound and self.cur_sound.is_playing()

	@classmethod
	def stop_all(cls, path):
		simpleaudio.stop_all()

def play_sound(path, block=False):
	s = SoundPlayer()
	s.play(path, block)
	return s

class SoundThread(Thread):
	"""
		This manager ensures the sound is loaded without slowing down the UI
	"""
	def __init__(self):
		super().__init__(daemon=True)
		self.channels = defaultdict(lambda: SoundPlayer())
		self.play_q = Queue()

	def run(self):
		while True:
			try:
				for name, chan in self.channels.items():
					if chan.loop and not chan.is_playing():
						chan.restart_loop()
				while not self.play_q.empty():
					chan, path = self.play_q.get(block=False)
					if path == "stop":
						if chan == "all":
							for name, chan in self.channels.items():
								chan.stop()
						else:
							self.channels[chan].stop()
					elif path == "clear_cache":

						if chan == "all":
							for name, chan in self.channels.items():
								chan.cache = {}
						else:
							self.channels[chan].cache = {}
					else:
						self.channels[chan].play(path)
			except Exception as e:
				log("Got error in audio thread : ", e, err=True)
			time.sleep(0.01)

	def get_chan_volume(self, chan):
		return G.CLIENT.config.get_volume_multiplier(chan)

	def play_path(self, chan, path, loop=False):
		self.channels[chan].volume = self.get_chan_volume(chan)
		self.channels[chan].loop = loop
		self.play_q.put((chan, path))

	def play(self, chan, name, loop=False):
		# Skin path will be audio.chan.name
		path = G.CLIENT.skin.get("audio", ".".join([chan, name]))
		if path:
			path = Path(C.AUDIO_PATH) / chan / path
			self.play_path(chan, str(path), loop=loop)
		else:
			log("Sound name doesn't exists", name)

	def loop(self, chan, name):
		self.play(chan, name, True)

	def stop(self, chan):
		self.play_q.put((chan, "stop"))

	def stop_all(self):
		self.play_q.put(("all", "stop"))

	def clear_cache(self): # Needed if the volume change
		self.play_q.put(("all", "clear_cache"))