from engine.client.client import Client
from engine.client.window import *
from engine.client.widgets import *
from engine.client.client import Scene
import engine.consts as C
from engine import *
import time, wave, math, mimetypes, base64

########## Audio tools

try:
	import pyaudio
except:
	pyaudio = None

class AudioPlayer:
	def __init__(self, path=None):
		self.p = pyaudio.PyAudio()
		self.stream = None
		self.stop()
		if path:
			self.play(path)

	def stop(self):
		if self.stream:
			self.stream.close()
		self.playing_path = None
		self.is_playing = False
		self.stream = None

	def pause(self):
		if self.is_playing:
			self.toggle_pause()

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
		self.pause()
		self.wf = wave.open(str(path), 'rb')
		self.stop()
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

########## Widgets

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

class FileItemW(MenuItemW):
	FORMAT = "apps.files.item.default"
	FORMAT_FOCUSED = "apps.files.item.selected"

	def __init__(self, flist, path, filename=None, v_align="left", align="left", **kwargs):
		self.flist = flist
		self.path = path
		symb = to_skin_char("directory") if path.is_dir() else to_skin_char("file")
		filename = filename or path.name
		text = " {} | {}".format(symb, filename)
		super().__init__(text, v_align=v_align, align=align, **kwargs)

	def pressed(self):
		super().pressed()
		if self.path.is_dir():
			self.flist.set_path(self.path)
		else:
			self.flist.select_file(self.path)

class FileListW(MenuVertW):
	def __init__(self, path=Path(), col_size=0, spacing=0, format="apps.files.list",
		files_filter=None, scroll=True, **kwargs):
		super().__init__(col_size=col_size, format=format, spacing=spacing, **kwargs)
		self.path = None
		self.ev_changed = UIEvent()
		self.ev_select_file = UIEvent()
		self.files_filter = files_filter or (lambda x:x)
		self.set_path(path)

	def update_file_list(self):
		self.clear_children_list()
		self.add(FileItemW(self, self.path.parent, ".."))

		key_file = lambda p : p.name
		dir_list = list(self.path.iterdir())
		files = sorted([f for f in dir_list if f.is_dir()], key=key_file)
		files.extend(sorted(self.files_filter([f for f in dir_list if not f.is_dir()]), key=key_file))
		for f in files:
			self.add(FileItemW(self, f))

	def select_file(self, file):
		self.ev_select_file.fire()

	def get_selected_path(self):
		if 0 <= self.cursor_pos < len(self.children):
			return self.children[self.cursor_pos].path
		return self.path

	def move_cursor(self, rel):
		super().move_cursor(rel)
		self.ev_changed.fire()

	def set_path(self, path):
		p = Path(path).resolve()
		if p != self.path:
			self.path = p
			self.update_file_list()
			self.cursor_pos = 0
			self.set_children_selected(True)
		self.ev_changed.fire()

	def keypress(self, key):
		if not self.focused:
			return False
		if key.check(KeyVal.ARROW_RIGHT):
			self.children[self.cursor_pos].pressed()
		elif key.check(KeyVal.ARROW_LEFT):
			self.set_path(self.path.parent)
		elif key.check("H"):
			self.set_path(self.path.home())
		else:
			return super().keypress(key)
		return True

	def compute_children_dims(self):
		space_top = 0
		inner_size = self.get_inner_size()
		for child in self.children:
			child.compute_real_size(inner_size)
			child.rel_pos = (space_top, 0)
			space_top += self.spacing + child.size[0]
		space_top -= self.spacing

		if self.children:
			s_child = self.children[self.cursor_pos]
			pos_end_selected = s_child.rel_pos[0] + s_child.size[0]

			delta = inner_size[0] - 1 - pos_end_selected
			if delta < 0:
				for child in self.children:
					child.rel_pos = add_coords(child.rel_pos, (delta, 0))

class FilePromptW(BiGWinW):
	def __init__(self, *kargs, path=Path(), call=None, files_filter=None, **kwargs):
		super().__init__(*kwargs, **kwargs)

		if isinstance(files_filter, list):
			f = lambda l : [x for x in l if x.suffix in files_filter]
		else:
			f = files_filter

		self.scene = FileExplorerScene(G.CLIENT, self, path=path, files_args={"files_filter" : f})
		self.scene.start()
		self.call = [] if not call else (call if isinstance(call, list) else [call])
		self.scene.files.ev_select_file.on(self.on_file_selected)

	def on_file_selected(self):
		for f in self.call:
			f(self.scene.files.get_selected_path())
		self.close()

	def close(self):
		self.scene.stop()
		super().close()

########## Scenes

# TODO : 4 arrows, enter, scroll list, show path, side column

class FileExplorerScene(Scene):
	HELP_TEXT = "Arrows to move | [H] : Home | [ENTER] | [ESCAPE]"
	CODE_EXTS = [".spec", ".gitignore"]
	def __init__(self, *kargs, path=Path(), files_args={}, **kwargs):
		self.open_path = path
		self.mime = mimetypes.MimeTypes()
		self.files_args = files_args
		super().__init__(*kargs, **kwargs)

	def get_file_image(self, path):
		if path.is_dir():
			return "files/folder.cbi"
		m_type = self.mime.guess_type(str(path))[0]
		main_type, sub_type = m_type.split("/") if m_type else (None, None)

		if main_type in ["audio"]:
			return "files/music.cbi"
		if main_type in ["image"] or path.suffix in [".cbi"]:
			return "files/image.cbi"
		if sub_type and sub_type[:2] == "x-" or path.suffix in self.CODE_EXTS or path.name in self.CODE_EXTS:
			return "files/code.cbi"
		return "files/file.cbi"

	def get_file_size_string(self, path):
		if path.is_file():
			s = path.stat().st_size
			exts = ["bytes", "Kb", "Mb", "Gb", "Tb"]
			while s > 1000 and len(exts) > 1:
				s /= 1000
				exts = exts[1:]
			return "{} {}".format(round(s, 1), exts[1])
		return ""

	def update_files_view(self):
		self.pathw.set_text(str(self.files.path))
		self.info_title.set_text(self.files.path.name)
		path = self.files.get_selected_path()
		self.info_img.load(self.get_file_image(path))
		self.info_size.set_text(self.get_file_size_string(path))

	def start(self):
		super().start()
		self.pathw = self.root.add(TextW("-", format="apps.files.path",
			size=(1, 1.), padding=((0, 0), (2, 2))))

		COL_SIZE = 40
		self.info_col = self.root.add(BoxW(format="apps.files.info_col", size=(-2, COL_SIZE),
			inv_side=(False, True), pos=(1, 0)))

		self.info_title = self.info_col.add(TextLineW("---", pos=(1, 0.5), size=(1, COL_SIZE-4), align="center"))
		self.info_img = self.info_col.add(ImageW(self.get_file_image(self.open_path),
			pos=(3, "center"), back_color="files_col_back"))
		self.info_size = self.info_col.add(TextLineW("000", pos=(21, 0.5), size=(1, COL_SIZE-4), align="center"))

		self.help_bar = self.root.add(TextW(self.HELP_TEXT, format="apps.files.help",
			size=(1, 1.), padding=((0, 0), (2, 2)), inv_side=(True, False)))

		self.files = self.root.add(FileListW(size=(-2, -COL_SIZE), pos=(1, 0), **self.files_args))
		self.files.ev_changed.on(self.update_files_view)
		self.files.set_path(self.open_path)

class MusicScene(Scene):
	DEFAULT_PATH = C.AUDIO_PATH / "music" / "heroic_demise.wav"
	ANSWER_PATH = (C.AUDIO_PATH / "42.wav").resolve()

	def on_play_pause(self):
		self.player.toggle_pause()

	def on_restart(self):
		if not self.player.is_playing:
			self.player.toggle_pause()
		self.player.set_pos(0)

	def on_open(self):
		self.root.add(FilePromptW(path=self.music_path.parent, call=self.play_path,
			files_filter=['.wav', '.wave']))

	def on_open_recent(self):
		recent_names = [p.name for p in self.recent[::-1]]
		self.root.add(SelectListPromptW(recent_names, call=self.on_open_recent_selected,
			win_args={"banner_text": "Recent musics", "size" : (min(G.WINDOW.size[0]-4, 35), 70)}))

	def on_open_recent_selected(self, i):
		self.play_path(self.recent[-1-i])

	def set_correct_rendering(self):
		if self.music_path:
			if self.player.is_playing:
				self.pp_button.set_text("Pause")
			else:
				self.pp_button.set_text("Play")
			name = self.music_path.stem.replace('_', ' ').capitalize()
			if self.music_path == self.ANSWER_PATH:
				name = get_cycle_val(10) and base64.b64decode(b'WW91IGhhdmUgYmVlbiBSaWNrIFJvbGxlZCAh').decode('ascii') or ''
			self.music_name.set_text(name)
			self.music_bar.set(self.player.get_time_frac())
			left, right = self.player.get_times_formated(min_parts=2)
			self.time_left.set_text(left)
			self.time_right.set_text(right)

	def error_pop(self, msg):
		log("ERROR MUSIC PLAYER : {}".format(msg), err=True)
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
			if path in self.recent:
				self.recent.remove(path)
			self.recent.append(path)

	def start(self):
		super().start()

		if not pyaudio:
			self.root.add(ButtonsPopup("To play music, you must have the 'pyaudio' package installed.",
				call=[self.quit]))
			return

		self.music_path = None
		self.player = AudioPlayer()
		self.recent = []

		box = self.root.add(ContainerW(size=(22, 1.), pos=(0.5, 0)))
		self.music_name = box.add(TextW("music name", align='center', size=(3, 1.), pos=(0, 0.5), v_align='center'))
		box.add(HorLine(pos=(3, 0)))

		self.music_bar = box.add(MusicBarW(self.player, size=(1, 60), pos=(5, 0.5), start_at=0))
		time_bar = box.add(ContainerW(size=(1, 60), pos=(6, 0.5)))
		self.time_left = time_bar.add(TextW("--:--", size=(1, 30)))
		self.time_right = time_bar.add(TextW("--:--", size=(1, 30), inv_side=(False, True), align="right"))

		buttons_box = box.add(ContainerW(size=(10, 40), pos=(8, 0.5)))
		self.pp_button = buttons_box.add(ButtonW("----", size=17, big=True, call=self.on_play_pause,
			align="center"))
		buttons_box.add(ButtonW("Restart", size=17, big=True, call=self.on_restart,
			align="center", inv_side=(False, True)))
		buttons_box.add(ButtonW("Open", size=17, big=True, call=self.on_open,
			align="center", pos=(4, 0)))
		buttons_box.add(ButtonW("Open recent", size=17, big=True, call=self.on_open_recent,
			align="center", inv_side=(False, True), pos=(4, 0)))

		help_text =  "[TAB] / Arrows            [Q] : quit\n"
		help_text += "[P] : Play / Pause     [R] : Restart\n"
		help_text += "[O] : Open         [L] : Open recent"
		box.add(TextW(help_text, text_format="dim_text", v_align="center", size=(3, 1.), pos=(0, 0),
			inv_side=(True, False), align="center"))

		if self.client.cmd_args.path:
			if self.client.cmd_args.path == "42":
				self.play_path(self.ANSWER_PATH)
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