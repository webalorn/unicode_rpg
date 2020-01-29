# This file contains global variables shared by all the program,
# And the functions that need to run before everything else

from enum import Enum
import platform, os, sys

OS_NAME = platform.system() # In ['Linux', 'Darwin', 'Windows']
OS_WITH_TERM = OS_NAME in ['Linux', 'Darwin']


########## Client specific
class G: # G : contain general variables (objet to allow variable to be modified after imports)
	CLIENT = None
	WINDOW = None
	CLIENT_STEPS = 0

def get_cycle_val(cycle_time, modul=2):
	return (G.CLIENT_STEPS // cycle_time) % modul

# I allowed these functions to bypass encapsulation for speed efficiency
def to_skin_char(code):
	return G.CLIENT.skin.data["char"].get(code, '?')

def get_charset(name):
	return G.CLIENT.skin.data["charset"].get(name, '?')

def get_skin_format(name):
	while isinstance(name, str):
		name =  G.CLIENT.skin.data["format"].get(name, None)
	return name

########## Setting and cleaning up

class DispelMagic:
	_INSTANCES = []
	def __init__(self):
		super().__init__()
		self._INSTANCES.append(self)

	def pleaseCleanUpYourMess(self):
		pass # I you dont do any mess, why are you here? Only to not beeing garbage collected? You fool!

	def pleaseCleanUpYourMessLate(self):
		pass # Because we still need to log before

	@classmethod
	def releaseAll(cls):
		for inst in cls._INSTANCES:
			inst.pleaseCleanUpYourMess()
		for inst in cls._INSTANCES:
			inst.pleaseCleanUpYourMessLate()
		cls._INSTANCES.clear()

	def __del__(self):
		self.__class__.releaseAll()

########## Main functions

def init_client_globals(client):
	G.CLIENT = client
	G.WINDOW = client.window

def client_make_step():
	G.CLIENT_STEPS += 1

def mark_dims_changed():
	if G.WINDOW:
		G.WINDOW.dims_changed = True