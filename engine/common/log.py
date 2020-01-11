import data.consts as C
from datetime import datetime

def log(*args, end="\n", sep=" ", err=False):
	with open(C.DEBUG_LOG if not err else C.ERR_LOG, 'a') as f:
		f.write(sep.join([str(a) for a in args]) + end)

# Clear (TODO : only 'cut' file ?)
# for fname in [C.DEBUG_LOG, C.ERR_LOG]: 
for fname in [C.DEBUG_LOG]:
	with open(fname, 'w') as f:
		f.write('')
date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
debug_line = "============================== " + str(datetime)
log(debug_line, "[DEBUG]")
log(debug_line, "[ERROR]", err=True)