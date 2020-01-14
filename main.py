from engine import *
from game.client import GameClient

def main():
	try:
		game_client = GameClient()
	except BaseLoadError as e:
		print(FORE["red"] + "[ERROR LOADING] " + e.message + DEF_FORMAT)
		return
	game_client.start()

if __name__ == '__main__':
	main()