import data.consts as C
from engine.common.util import *
from engine import *

def draw_borders(grid):
	todo = [[None] * len(grid[0]) for _ in range(len(grid))]
	for (row, col), val in enumerate_grid(grid):
		if val == 2:
			sides = [0, 0, 0, 0]
			for i_move, m in enumerate(C.SIDE_MOVES):
				r2, c2 = add_coords((row, col), m)
				if is_pos_in_grid((r2, c2), grid) and grid[r2][c2] == 2:
					sides[i_move] = 1
			code = "".join([str(k) for k in sides])
			todo[row][col] = "border." + C.BORDER_CODE[code]
		elif type(val) == str and val[:7] == "border.":
			code = [int(c) for c in C.BORDER_TO_CODE[val[7:]]]
			for i_move, m in enumerate(C.SIDE_MOVES):
				r2, c2 = add_coords((row, col), m)
				if ( code[i_move] == 0 and is_pos_in_grid((r2, c2), grid)
					and type(grid[r2][c2]) == str and grid[r2][c2][:7] == "border." ):
					code2 = list(C.BORDER_TO_CODE[grid[r2][c2][7:]])
					if code2[(i_move+2)%4] == '1':
						code[i_move] = 1

			code = "".join([str(k) for k in code])
			todo[row][col] = "border." + C.BORDER_CODE[code]

	for (row, col), val in enumerate_grid(todo):
		if val:
			grid[row][col] = val
	return grid