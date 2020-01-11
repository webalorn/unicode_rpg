import data.consts as C
from datetime import datetime

# Clear (TODO : only 'cut' file ?)
for fname in [C.DEBUG_LOG]: # [C.DEBUG_LOG, C.ERR_LOG]:
	with open(fname, 'w') as f:
		f.write('')
date_time_start_log = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
debug_line = "============================== " + str(date_time_start_log)

ERR_WRITEN = False

def log(*args, end="\n", sep=" ", err=False):
	global ERR_WRITEN
	if err and not ERR_WRITEN:
		ERR_WRITEN = True
		log(debug_line, "[ERROR]", err=True)
	if err:
		log("[ERROR]", *args, end=end, sep=sep)

	with open(C.DEBUG_LOG if not err else C.ERR_LOG, 'a') as f:
		f.write(sep.join([str(a) for a in args]) + end)

log(debug_line, "[DEBUG]")
