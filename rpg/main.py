from engine import *
from game.client.client import GameClient
import engine.consts as C
import argparse

def get_args():
	description = 'Start {}'.format(C.PROG_NAME)
	version = "{}, {}".format(C.PROG_NAME, C.VERSION)
	parser = argparse.ArgumentParser(description=description)

	parser.add_argument('--config', '-c', help='an integer for the accumulator', default="user")
	parser.add_argument('--skin', '-s', help='Name of a skin in the data/skin folder. Overwrite the skin given in the config file', default=None)
	parser.add_argument('-v', '--version', action='version', version=version,
		help="Print version and exit")

	return  parser.parse_args()

def main():
	parser = get_args()
	try:
		game_client = GameClient(parser.config + ".json", force_skin=parser.skin)
		game_client.start()
	except BaseLoadError as e:
		print("\033[31m", "[ERROR LOADING]", e.message, "\033[0m")
		return

if __name__ == '__main__':
	main()