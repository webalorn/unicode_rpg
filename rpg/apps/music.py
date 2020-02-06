from engine.client.client import Client
from engine.client.window import *
from engine.client.widgets import *
from engine.client.client import Scene
import engine.consts as C
from engine import *
import time, wave, math

try:
	import pyaudio
except:
	pyaudio = None

class AudioPlayer:
	def __init__(self, path=None):
		self.p = pyaudio.PyAudio()
		self.stream = None
		if path:
			self.play(path)

	def stop(self):
		if self.stream:
			self.stream.close()
		self.playing_path = None
		self.is_playing = False
		self.stream = None

	def toggle_pause(self):
		state1 = self.stream.is_active()
		if self.is_playing:
			self.stream.stop_stream()
			self.is_playing = False
		else:
			self.stream.start_stream()
			self.is_playing = True

	def ensure_playing_ok(self):
		if self.is_playing and not self.stream.is_active(): # Stream has ended, need restart
			self.play(self.playing_path)

	def _read_callback(self, in_data, frame_count, time_info, status):
		data = self.wf.readframes(frame_count)
		return (data, pyaudio.paContinue)

	def play(self, path):
		self.stop()
		self.wf = wave.open(str(path), 'rb')
		self.playing_path = path
		self.is_playing = True
		self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
				channels=self.wf.getnchannels(),
				rate=self.wf.getframerate(),
				output=True,
				stream_callback=self._read_callback)
		self.stream.start_stream()

	def set_pos(self, frac):
		self.ensure_playing_ok()
		self.wf.setpos(int(self.wf.getnframes() * frac))

	def duration(self):
		return math.ceil(self.wf.getnframes() / self.wf.getframerate())

	def get_time(self):
		return math.ceil(self.wf.tell() / self.wf.getframerate())

	def get_time_frac(self):
		return self.wf.tell() / self.wf.getnframes()

	@staticmethod
	def format_time(elp, min_parts=0):
		if elp < 60 and min_parts <= 1:
			return str(elp)
		elif elp < 60*60 and min_parts <= 2:
			return "{:02d}:{:02d}".format(elp//60, elp%60)
		else:
			return "{}h{:02d}:{:02d}".format(elp//3600, (elp//60)%60, elp%60)

	def get_times_formated(self, min_parts=0):
		return self.format_time(self.get_time(), min_parts), self.format_time(self.duration(), min_parts)

class FileExplorerW(BoxW):
	pass

class HorLine(BoxW):
	def __init__(self, *kargs, **kwargs):
		kwargs['size'] = (1, 1.)
		kwargs['border'] = ((0, 0), (1, 0))
		super().__init__(*kargs, **kwargs)

class MusicBarW(BarInputW):
	FOCUSABLE = False
	FORMAT = "apps.music.bar"

	def __init__(self, player, step=0.1, **kwargs):
		super().__init__(step=step, **kwargs)
		self.player = player

	def need_draw(self):
		return True

	def advance(self, nb_steps):
		super().advance(nb_steps)
		self.player.set_pos(self.value)
	
	def set(self, time):
		super().set(time)

	def keypress(self, key):
		self.focused = True
		r = super().keypress(key)
		self.focused = False
		return r

class MusicScene(Scene):
	DEFAULT_PATH = C.AUDIO_PATH / "music " / "heroic_demise_short.wav"

	def on_play_pause(self):
		self.player.toggle_pause()

	def on_restart(self):
		if not self.player.is_playing:
			self.player.toggle_pause()
		self.player.set_pos(0)

	def on_open(self):
		pass

	def on_open_recent(self):
		pass

	def set_correct_rendering(self):
		if self.music_path:
			if self.player.is_playing:
				self.pp_button.set_text("Pause")
			else:
				self.pp_button.set_text("Play")
			name = self.music_path.stem.replace('_', ' ').capitalize()
			self.music_name.set_text(name)
			self.music_bar.set(self.player.get_time_frac())
			left, right = self.player.get_times_formated(min_parts=2)
			self.time_left.set_text(left)
			self.time_right.set_text(right)

	def error_pop(self, msg):
		if self.music_path:
			self.root.add(ButtonsPopup(msg))
		else:
			self.root.add(ButtonsPopup(msg, call=[self.quit]))

	def play_path(self, path):
		path = Path(path)
		try:
			self.player.play(path)
		except FileNotFoundError:
			self.error_pop("The file '{}' doesn't exists".format(path))
		except IsADirectoryError:
			self.error_pop("'{}' is a directory, it must be a wave file".format(path))
		except wave.Error:
			self.error_pop("The file must be a wave file, and {} seems to not be a valid wave file.\nYou can convert a file with ffmpeg -i old_audio new_audio.wav".format(path))
		except Exception as e:
			self.error_pop("An error occured : {}".format(str(e)))
		else:
			self.music_path = path

	def start(self):
		super().start()

		if not pyaudio:
			self.root.add(ButtonsPopup("To play music, you must have the 'pyaudio' package installed.",
				call=[self.quit]))
			return

		self.music_path = None
		self.player = AudioPlayer()

		box = self.root.add(BoxW(size=(22, 1.), pos=(0.5, 0), border=0))
		self.music_name = box.add(TextW("music name", align='center', size=(3, 1.), pos=(0, 0.5), v_align='center'))
		box.add(HorLine(pos=(3, 0)))

		self.music_bar = box.add(MusicBarW(self.player, size=(1, 60), pos=(5, 0.5), start_at=0))
		time_bar = box.add(BoxW(size=(1, 60), pos=(6, 0.5)))
		self.time_left = time_bar.add(TextW("--:--", size=(1, 30)))
		self.time_right = time_bar.add(TextW("--:--", size=(1, 30), inv_side=(False, True), align="right"))

		buttons_box = box.add(BoxW(size=(10, 40), pos=(8, 0.5)))
		self.pp_button = buttons_box.add(ButtonW("----", size=17, big=True, call=self.on_play_pause,
			align="center"))
		buttons_box.add(ButtonW("Restart", size=17, big=True, call=self.on_restart,
			align="center", inv_side=(False, True)))
		buttons_box.add(ButtonW("Open", size=17, big=True, call=self.on_open,
			align="center", pos=(4, 0)))
		buttons_box.add(ButtonW("Open recent", size=17, big=True, call=self.on_open_recent,
			align="center", inv_side=(False, True), pos=(4, 0)))

		help_text = "[Q] : quit\n"
		help_text += "[P] : Play / Pause     [R] : Restart\n"
		help_text += "[O] : Open         [L] : Open recent"
		box.add(TextW(help_text, text_format="dim_text", v_align="center", size=(3, 1.), pos=(0, 0),
			inv_side=(True, False), align="center"))

		if self.client.cmd_args.path:
			if self.client.cmd_args.path == "42":
				self.play_path(C.AUDIO_PATH / "42.wav")
			else:
				self.play_path(self.client.cmd_args.path)
		else:
			self.play_path(self.DEFAULT_PATH)

		self.ev_draw_begin.on(self.set_correct_rendering)

	def unhandled_keypress(self, key):
		if key.check('Q'):
			self.quit()
		elif key.check('P') or key.check(' '):
			self.on_play_pause()
		elif key.check('R'):
			self.on_restart()
		elif key.check('O'):
			self.on_open()
		elif key.check('L'):
			self.on_open_recent()
		elif key.check(KeyVal.ARROW_DOWN):
			self.client.window.detect_keys([Key("\t")])
		elif key.check(KeyVal.ARROW_UP):
			self.client.window.detect_keys([Key(KeyVal.REV_TAB)])
		else:
			return False
		self.set_correct_rendering()
		return True

	def quit(self):
		self.stop()
		raise ExitException

class MusicClient(Client):
	def start_first_scene(self, scene):
		self.load_scene(MusicScene)