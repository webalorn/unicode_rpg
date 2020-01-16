import engine.consts as C
import json, os
from pathlib import Path
from engine.common.exceptions import *
from collections import defaultdict

class ConfigManager:
	"""
	Config file format : {"import" : [..], "category_1" : {...}, "category2": {"sub_cat": {...}, ...}}
	"""

	MAIN_PATH = C.CONFIG_PATH

	def __init__(self, file_path='default.json'):
		self.set_config_path(file_path)
		self.conf_data = {}
		self.load_data()
		self.cfg_id = hash(self.config_path)

	def set_config_path(self, file_path):
		self.config_path = (Path(self.MAIN_PATH) / file_path).resolve()

	def import_data(self, import_path):
		return ConfigManager(import_path).data

	def load_data(self): # TODO : manage errors if can't open file
		try:
			with open(str(self.config_path), 'r') as conf_file:
				self.conf_data = json.load(conf_file)
		except Exception as e:
			raise BaseLoadError("Can't open file config file : ", self.config_path, "because : ", str(e))

		self.data = defaultdict(lambda : {})
		if "import" in self.conf_data:
			for import_path in self.conf_data["import"]:
				for category, content in self.import_data(import_path).items():
					self.data[category].update(content)

		for category, content in self.conf_data.items():
			if category != "import":
				self.create_data_flat_dict(content, [], self.data[category])

	def create_data_flat_dict(self, conf_data, ids, dest):
		if isinstance(conf_data, dict):
			for key, val in conf_data.items():
				self.create_data_flat_dict(val, ids + [key], dest)
		else:
			key = ".".join(ids)
			dest[key] = conf_data

	def get(self, category, key):
		return self.data.get(category, {}).get(key, None)