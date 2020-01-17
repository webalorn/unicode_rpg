import engine.consts as C
import json, os
from pathlib import Path
from engine.common.exceptions import *
from engine.common.log import *
from collections import defaultdict

class ConfigManager:
	"""
	Config file format : {"import" : [..], "category_1" : {...}, "category2": {"sub_cat": {...}, ...}}
	"""

	MAIN_PATH = C.CONFIG_PATH
	DEFAULT_CONFIG = {"import" : ["default.json"]}

	def __init__(self, file_path='default.json', main_config=True):
		self.main_config = main_config
		self.set_config_path(file_path)
		self.conf_data = {}
		self.load_data()
		if main_config:
			self.data_loaded_action()
		self.cfg_id = hash(self.config_path)

	def set_config_path(self, file_path):
		self.config_path = Path(self.MAIN_PATH) / file_path

	def import_data(self, import_path):
		return self.__class__(import_path, main_config=False).data

	def load_data(self):
		try:
			if self.main_config and not self.config_path.exists():
				self.config_path.parent.mkdir(parents=True, exist_ok=True)
				with open(str(self.config_path), 'w') as conf_file:
					json.dump(self.DEFAULT_CONFIG, conf_file)

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

	def data_loaded_action(self):
		pass

	def create_data_flat_dict(self, conf_data, ids, dest):
		if isinstance(conf_data, dict):
			for key, val in conf_data.items():
				self.create_data_flat_dict(val, ids + [key], dest)
		else:
			key = ".".join(ids)
			dest[key] = conf_data

	def get(self, category, key):
		return self.data.get(category, {}).get(key, None)

	def put_int_conf(self, conf_obj, path, value):
		if len(path) == 0:
			raise Exception("Empty config key")
		elif len(path) == 1:
			conf_obj[path[0]] = value
		else:
			self.put_int_conf(conf_obj.setdefault(path[0], {}), path[1:], value)

	def set(self, category, key, value):
		self.data[category][key] = value
		self.put_int_conf(self.conf_data, [category] + key.split("."), value)
		log(self.conf_data)

	def save(self):
		try:
			with open(str(self.config_path), 'w') as conf_file:
				json.dump(self.conf_data, conf_file)
		except e:
			log("Can't save config because", e, err=True)
			raise e