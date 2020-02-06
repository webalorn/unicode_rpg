from engine import *
import engine.consts as C
import argparse, textwrap

PROG_DESCRIPTION = """{}, version {}

The unicode RPG is game designed to work in a command-line environment, made with python3.

========== GENERAL INFORMATIONS ==========
This is the command to start the unicode RPG. To make sure it works properly, use a terminal emulator with a monoscpaced font and the right unicode characters size. In some terminals, some characters take a double width, and it leads to an unuseable display. The font you use must also support some non-ascii unicode characters. Don't use a transparent background if you don't want the game to be ugly. To change the display size, you can change the font size in your terminal settings.

However, if you experiences issues with the display and can't use another terminal emulator, you still have the following options :
- Use only plain ascii, with the "-s ascii" (it loads the ascii skin). Usefull if your font doesn't support a lot of unicode characters / if they have the wrong size in your terminal.
- Use a better terminal emulator. iTerm works well on macOS (but the default terminal don't without ascii mode).

To fix performance issues :
- Start the game with pypy3 instead of python3. It can make it twice faster.
- A bigger font size can make the game faster by reducing the number of characters to be update.
- Some terminals have faster output speed, you can try another terminal emulator.
- i7 cores are often faster than pentiums. Don't try 4K with a 10Mhz processor.

========== HELP ABOUT THE GAME ==========
You can navigate between elements with the arrow keys, and move the focus with the [TAB] key. Close windows and pannels with [ESCAPE], or using the buttons with [ENTER]. Knowing this, you will find every additional help needed in-game in the game itself.

========== ADDITIONAL HELP / BUGS ==========
You can ask for help or report bugs or any kind of problem to me on github : https://github.com/webalorn/unicode_rpg

Feel free to contact me at webalorn+urpg@gmail.com

"""

def get_game_app(*k, **kw):
	from game.client.client import GameClient
	return GameClient(*k, **kw)

def get_music_app(*k, **kw):
	from apps.music import MusicClient
	return MusicClient(*k, **kw)

APPS_GETTERS = {
	'game' : get_game_app,
	'music' : get_music_app,
}

def get_args():
	description = PROG_DESCRIPTION.format(C.PROG_NAME, C.VERSION)
	description = "\n".join(textwrap.fill(l, 85) for l in description.splitlines())

	def w(txt):
		return textwrap.fill(txt, 60)

	version = "{} {}".format(C.PROG_NAME, C.VERSION)
	parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)

	parser.add_argument('--config', '-c', help=w('Name of a config file in the data/config folder, without the ".json" extension. The default value is to use the "user" configuration file.'), default="user")
	parser.add_argument('--skin', '-s', help=w('Name of a skin in the data/skin folder, without the ".json" extension. Overwrite the skin given in the config file. The default value is defined by the configuration file, and can be changed with in-game settings.'), default=None)
	parser.add_argument('-v', '--version', action='version', version=version, help=w("Print version and exit"))
	parser.add_argument('-a', '--app', default='game', help=w("The application to start"), choices=list(APPS_GETTERS.keys()))
	parser.add_argument('-e', '--scene', default='main', help=w("The scene at wich the application should start. Default is 'main'. [INTENDED FOR DEV / DEBUG ONLY]"))
	parser.add_argument('-p', '--path', default=None, help=w("A path, can be used by some applications"))

	return  parser.parse_args()

def main():
	args = get_args()
	try:
		log("Located at {}".format(str(C.MAIN_PATH)))
		skin = args.skin + ".json" if args.skin else None
		game_client = APPS_GETTERS[args.app](args.config + ".json", force_skin=skin)
		game_client.cmd_args = args
		game_client.start(args.scene)
	except ErrorMessage as e:
		print("\033[31m", "[ERROR]", e.message, "\033[0m")
		return
	except BaseLoadError as e:
		print("\033[31m", "[ERROR LOADING]", e.message, "\033[0m")
		return

if __name__ == '__main__':
	main()