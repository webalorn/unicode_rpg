import engine.consts as C
from .format import *

def to_tuple(t, n=2):
	if isinstance(t, tuple): return t
	elif isinstance(t, list): return tuple(t)
	else: return tuple([t]*n)

########################## Collections

def get_dims(grid):
	if not grid:
		return 0, 0
	return len(grid), len(grid[0])

def has_non_nul(s):
	r = False
	if isinstance(s, (list, tuple)):
		for k in s:
			r = r or has_non_nul(k)
	else:
		r = bool(s)
	return r

def extract_grid(grid, cut_sides):
	if has_non_nul(cut_sides):
		grid = grid[cut_sides[0][0]:len(grid)-cut_sides[0][1]]
		for i, l in enumerate(grid):
			grid[i] = l[cut_sides[1][0]:len(l)-cut_sides[1][1]]
	return grid

def inherit_union(parent, child):
	if child == 'inherit' or child == ('inherit', 'inherit', 'inherit') or child is None:
		return parent
	if parent is None:
		parent = EMPTY_FORMAT
	return tuple([a if b == 'inherit' else b for a, b in zip(parent, child)])


########################## Coords

def add_coords(*l):
	return tuple([sum(k) for k in zip(*l)])

def minus_coords(a, b):
	return tuple([x-y for x, y in zip(a, b)])

def is_pos_in_grid(pos, grid):
	return 0 <= pos[0] < len(grid) and 0 <= pos[1] < len(grid[0])

def intersect_rects(rect1, rect2):
	(_r1, _c1), (_r2, _c2) = rect1
	(r1, c1), (r2, c2) = rect2
	return ((max(r1, _r1), max(c1, _c1)), (min(r2, _r2), min(c2, _c2)))

########################## Text