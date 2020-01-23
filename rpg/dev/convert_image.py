from PIL import Image 
import sys
import os

color_path = os.path.join(os.path.dirname(__file__), "colors.txt")
palette = [tuple(map(int, l.split())) for l in open(color_path, "r").readlines()]
cols_computed = {}

def col_dist(x, y):
	return sum([abs(a-b)**2 for a, b in zip(x, y)])

def get_nearest_id(col):
	if col not in cols_computed:
		i_min, d_min = 0, 1e9
		for i, pal_col in enumerate(palette):
			d = col_dist(col, pal_col)
			if d < d_min:
				d_min = d
				i_min = i
		cols_computed[col] = i_min
	return cols_computed[col]

def convert(img):
	ncols, nrows = img.size
	img = [get_nearest_id(col[:3]) if col[-1] else -1 for col in list(img.getdata())]
	return [img[i*ncols:(i+1)*ncols] for i in range(nrows)]

def draw_img(img, background=0):
	if len(img)%2 and img:
		img = img + [[0]*len(img[0])]
	for row1, row2 in zip(img[0::2], img[1::2]):
		for up, down in zip(row1, row2):
			print("\u001b[48;5;{}m\u001b[38;5;{}m".format(up, down), end="")
			if up == -1:
				print("\u001b[48;5;{}m".format(background), end="")
			print("▄" if down != -1 else " ", end="")
		print("\u001b[0m")

def make_conversion(img_path, dest_path, show=False, background=0):
	img = convert(Image.open(img_path))
	open(dest_path, "w").write("\n".join([" ".join([str(col) for col in l]) for l in img]))
	if show:
		draw_img(img, background=background)

def main():
	if len(sys.argv) < 3:
		print("Usage : python3 <script_name.py> [original image path] [new image path]")
		print("Optional arg : background color")
	my_path, img_path, dest_path = sys.argv[:3]
	background = 0 if len(sys.argv) < 4 else sys.argv[3]
	make_conversion(img_path, dest_path, True, background)

if __name__ == '__main__':
	main()