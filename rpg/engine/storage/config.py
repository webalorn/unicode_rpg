import engine.consts as C
import json, os
from engine.common.exceptions import *
from engine.common.log import *
from collections import defaultdict
from engine.client.keys import Key

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
		self.cfg_id = hash(self.config_path)

	def set_config_path(self, file_path):
		self.config_path = self.MAIN_PATH / file_path

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

		if self.main_config:
			self.data_loaded_action()

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

	def get_parent_dict(self, conf_obj, path):
		if len(path) == 0:
			raise Exception("Empty config key")
		elif len(path) == 1:
			return conf_obj
		else:
			return self.get_parent_dict(conf_obj.setdefault(path[0], {}), path[1:])

	def set(self, category, key, value, force=False):
		if self.data[category].get(key, None) != value or force:
			self.data[category][key] = value
			key = [category] + key.split(".")
			self.get_parent_dict(self.conf_data, key)[key[-1]] = value

	def remove(self, category, key, value):
		try:
			key = [category] + key.split(".")
			self.get_parent_dict(self.conf_data, key).pop(key[-1])
			self.data[category].pop(key)
		except KeyError:
			pass # The key does not exist in the configuration. Don't remove if imported

	def save(self):
		try:
			with open(str(self.config_path), 'w') as conf_file:
				json.dump(self.conf_data, conf_file)
		except e:
			log("Can't save config because", e, err=True)
			raise e

	def reset(self):
		self.conf_data = self.DEFAULT_CONFIG
		self.save()
		self.load_data()

	@classmethod
	def get_available_list(cls):
		return [str(p.relative_to(cls.MAIN_PATH)) for p in cls.MAIN_PATH.iterdir() if p.is_file() and p.suffix == ".json"]

class GameConfig(ConfigManager):
	def get_key(self, key_name):
		key = self.get("keys", key_name)
		return Key.from_repr(key) if key is not None else None

	def set_key(self, key_name, key):
		self.set("keys", key_name, key.to_repr() if key is not None else None)

	def get_key_map(self):
		return {
			name : Key.from_repr(k) if k is not None else None for name, k in self.data["keys"]
		}

	def set_sound(self, sound_name, volume): # Volume must be an integer between 0 and 100
		self.set("sound", sound_name, max(0, min(int(volume), 100)))

	def get_sound(self, sound_name):
		volume = self.get("sound", sound_name)
		return volume if volume is not None else 20 # 100% if not set [20=100%]

	def get_volume_multiplier(self, sound_name):
		return self.get_sound(sound_name) / 20