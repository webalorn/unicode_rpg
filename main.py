from engine import *
from game.client import GameClient
import engine.consts as C
import argparse

def get_args():
	description = 'Start {}'.format(C.PROG_NAME)
	version = "{}, {}".format(C.PROG_NAME, C.VERSION)
	parser = argparse.ArgumentParser(description=description)

	parser.add_argument('--config', '-c', help='an integer for the accumulator', default="user")
	parser.add_argument('-v', '--version', action='version', version=version,
		help="Print version and exit")

	return  parser.parse_args()

def main():
	parser = get_args()
	try:
		game_client = GameClient(parser.config + ".json")
		game_client.start()
	except BaseLoadError as e:
		print("\033[31m", "[ERROR LOADING]", e.message, "\033[0m")
		return

if __name__ == '__main__':
	main()
