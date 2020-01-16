from engine import *
from game.client import GameClient

def main():
	try:
		game_client = GameClient()
		game_client.start()
	except BaseLoadError as e:
		print(COLORS.FORE["red"], "[ERROR LOADING]", e.message, COLORS.F_STYLE["reset"])
		return

if __name__ == '__main__':
	main()