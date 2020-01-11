import data.consts as C

def to_tuple(t, n=2):
	if type(t) == tuple: return t
	elif type(t) == list: return tuple(t)
	else: return tuple([t]*n)

########################## Collections

def has_non_nul(s):
	r = False
	if type(s) in [list, tuple]:
		for k in s:
			r = r or has_non_nul(k)
	else:
		r = bool(s)
	return r

def paint_on_grid(grid, to_paint, pos):
	for i_row, row in enumerate(to_paint):
		for i_col, val in enumerate(row):
			r, c = i_row + pos[0], i_col + pos[1]
			if 0 <= r < len(grid) and 0 <= c < len(grid[r]) and val != None:
				grid[r][c] = val

def extract_grid(grid, cut_sides):
	if has_non_nul(cut_sides):
		grid = grid[cut_sides[0][0]:len(grid)-cut_sides[0][1]]
		for i, l in enumerate(grid):
			grid[i] = l[cut_sides[1][0]:len(l)-cut_sides[1][1]]
	return grid

########################## Coords

def add_coords(*l):
	return tuple([sum(k) for k in zip(*l)])

def minus_coords(a, b):
	return tuple([x-y for x, y in zip(a, b)])

def is_pos_in_grid(pos, grid):
	return 0 <= pos[0] < len(grid) and 0 <= pos[1] < len(grid[0])

def enumerate_grid(grid, only_coords=False):
	for row, l in enumerate(grid):
		for col, val in enumerate(l):
			if only_coords:
				yield row, col
			else:
				yield (row, col), val

########################## Text