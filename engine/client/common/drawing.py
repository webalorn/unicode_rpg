from engine.common.util import *
from engine import *

def draw_borders(grid):
	PROFILER.start("Draw borders")
	todo = [[None] * len(grid[0]) for _ in range(len(grid))]

	PROFILER.start("Draw borders - loop 1")
	for row in range(len(todo)):
		for col in range(len(todo[row])):
			val = grid[row][col]
			if val == 2:
				sides = [0, 0, 0, 0]
				for i_move, m in enumerate(C.SIDE_MOVES):
					r2, c2 = add_coords((row, col), m)
					if is_pos_in_grid((r2, c2), grid) and grid[r2][c2] == 2:
						sides[i_move] = 1
				code = "".join([str(k) for k in sides])
				todo[row][col] = "border." + C.BORDER_CODE[code]
			elif isinstance(val, str) and val[:7] == "border.":
				code = [int(c) for c in C.BORDER_TO_CODE[val[7:]]]
				for i_move, m in enumerate(C.SIDE_MOVES):
					r2, c2 = add_coords((row, col), m)
					if ( code[i_move] == 0 and is_pos_in_grid((r2, c2), grid)
						and isinstance(grid[r2][c2], str) and grid[r2][c2][:7] == "border." ):
						code2 = list(C.BORDER_TO_CODE[grid[r2][c2][7:]])
						if code2[(i_move+2)%4] == '1':
							code[i_move] = 1

				code = "".join([str(k) for k in code])
				todo[row][col] = "border." + C.BORDER_CODE[code]

	PROFILER.next("Draw borders - loop 1", "Draw borders - loop 2")
	for row in range(len(todo)):
		for col in range(len(todo[row])):
			val = todo[row][col]
			if val:
				grid[row][col] = val
	PROFILER.end("Draw borders - loop 2")
	PROFILER.end("Draw borders")
	return grid

def set_area(grid, area, val):
	r, c = get_dims(grid)
	(r0, c0), (r1, c1) = area
	for i_row in range(max(r0, 0), min(r, r1)):
		a, b = max(c0, 0), min(c, c1)
		grid[i_row][a:b] = [val]*(b-a)

def paint_on_grid(grid, to_paint, pos):
	if grid and to_paint:
		row_min, row_max = max(0, pos[0]), min(len(grid), pos[0]+len(to_paint))
		col_min, col_max = max(0, pos[1]), min(len(grid[0]), pos[1]+len(to_paint[0]))

		if col_max > col_min:
			def f(x, y) : return x if y is None else y
			c1, c2 = col_min-pos[1], col_max-pos[1]
			for i_row in range(row_min, row_max):
				grid[i_row][col_min:col_max] = map(f, grid[i_row][col_min:col_max], to_paint[i_row-pos[0]][c1:c2])

def set_area_format(grid, area, code):
	if code is not None:
		set_area(grid, area, COLORS.format_to_code(code))

def set_point_format(grid, point, code):
	if code is not None:
		code = COLORS.format_to_code(code)
		row, col = point
		grid[row][col] = code