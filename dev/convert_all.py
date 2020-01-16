from pathlib import Path
from convert_image import make_conversion

def get_all_images_paths(path):
	files = list(path.iterdir())
	imgs = [p for p in files if p.is_file() and str(p)[-4:] in [".png", ".jpg"]]
	for d in files:
		if d.is_dir():
			imgs.extend(get_all_images_paths(d))
	return imgs

def main():
	source_path = Path("private/img")
	dest_path = Path("data/img")

	imgs = get_all_images_paths(source_path)
	imgs = [p.relative_to(source_path) for p in imgs]
	
	for p in imgs:
		(dest_path / p).parent.mkdir(parents=True, exist_ok=True)
		print("Converting:", p)
		make_conversion(str(source_path / p), str((dest_path / p).with_suffix(".cbi")))

if __name__ == '__main__':
	main()