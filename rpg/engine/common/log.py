import engine.consts as C
from datetime import datetime
from .all import DispelMagic

class LogManagerFile(DispelMagic):
	def __init__(self, file_name, tag):
		super().__init__()
		date_time_start_log = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		self.debug_line = "============================== " + str(date_time_start_log) + " " + tag + "\n"
		self.writen = False
		self.file = None
		self.file_name = file_name

	def write(self, *args):
		if not self.writen:
			self.file = open(self.file_name, 'w')
			self.file.write(self.debug_line)
			self.writen = True
		self.file.write(*args)
		self.file.flush()

	def pleaseCleanUpYourMessLate(self):
		if self.file:
			self.file.close()

LOG_FILES = [LogManagerFile(f, tag) for f, tag in zip([C.DEBUG_LOG, C.ERR_LOG], ("[DEBUG]", "[ERROR]"))]
LOG_FILES_DM = [LogManagerFile(f, tag) for f, tag in zip([C.DEBUG_DM_LOG, C.ERR_DM_LOG], ("[DM DEBUG]", "[DM ERROR]"))]

def log(*args, end="\n", sep=" ", err=False):
	f = LOG_FILES[1] if err else LOG_FILES[0]
	f.write(sep.join([str(a) for a in args]) + end)

def log_dm(*args, end="\n", sep=" ", err=False):
	f = LOG_FILES_DM[1] if err else LOG_FILES_DM[0]
	f.write(sep.join([str(a) for a in args]) + end)
