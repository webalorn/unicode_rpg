# Main, and time
PROG_NAME = "Unicode RPG"
VERSION = "0.0.0-dev"
LOOP_TIME = 0.2
CURSOR_BLINK = 3

DEF_ROWS = 10
DEF_COLS = 20

# Coords
SIDE_MOVES = [(-1, 0), (0, 1), (1, 0), (0, -1)]

# Text and input
ALLOWED_CHARS = {
	"input" : "\n !\"`'#$%&()*+,-./:;<=>?@[\\]^_{|}~¿",
	"name" : " .-_",
	"password" : " !\"`'#$%&()*+,-./:;<=>?@[\\]^_{|}~¿",
	"mapable" : " !\"`'#$%&()*+,-./:;<=>?@[\\]^_{|}~¿\n"
}

# Storage
DEBUG_LOG = "debug.log"
ERR_LOG = "error.log"
DEBUG_DM_LOG = "debug_dm.log"
ERR_DM_LOG = "error_dm.log"

SKINS_PATH = "data/skins"
CONFIG_PATH = "data/config"
IMG_PATH = "data/img"
AUDIO_PATH = "data/audio"

QUICK_CHARS = { None : ' ', 0 : ' ', 1 : "block", -1 : '', 2 : "border"}

BORDER_CODE = {
	"0000" : "simple",
	"0001" : "left",
	"0010" : "down",
	"0011" : "down_left",
	"0100" : "right",
	"0101" : "hor",
	"0110" : "down_right",
	"0111" : "down_left_right",
	"1000" : "up",
	"1001" : "up_left",
	"1010" : "vert",
	"1011" : "up_down_left",
	"1100" : "up_right",
	"1101" : "up_left_right",
	"1110" : "up_down_right",
	"1111" : "all",
}
BORDER_TO_CODE = { b: a for a, b in BORDER_CODE.items()}