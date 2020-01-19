import engine.consts as C
from datetime import datetime
from .all import DispelMagic

class LogManagerFile(DispelMagic):
	def __init__(self, file_name, tag):
		super().__init__()
		self.file = open(file_name, 'w')
		date_time_start_log = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
		self.debug_line = "============================== " + str(date_time_start_log) + " " + tag + "\n"
		self.writen = False

	def write(self, *args):
		if not self.writen:
			self.file.write(self.debug_line)
			self.writen = True
		self.file.write(*args)
		self.file.flush()

	def pleaseCleanUpYourMessLate(self):
		self.file.close()

LOG_FILES = [LogManagerFile(f, tag) for f, tag in zip([C.DEBUG_LOG, C.ERR_LOG], ("[DEBUG]", "[ERROR]"))]

def log(*args, end="\n", sep=" ", err=False):
	f = LOG_FILES[1] if err else LOG_FILES[0]
	f.write(sep.join([str(a) for a in args]) + end)
