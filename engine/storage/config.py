import engine.consts as C
import json, os

class ConfigManager:
	CONFIG_PATH = "."

	def __init__(self, file_name='default_config.json'):
		self.name = name
		self.set_config_path(file_name)
		self.conf_data = {}
		self.load_data()

	def set_config_path(self, file_name):
		path1 = self.CONFIG_PATH
		path2 = file_name
		if isinstance(path1, list):
			path1 = os.path.join(path1)
		if isinstance(path2, list):
			path2 = os.path.join(path2)
		self.config_path = os.path.join(path1, path2)

	def load_data(self): # TODO : manage errors if can't open file
		with open(C.SKINS_PATH[name], 'r') as conf_file:
			self.conf_data = json.load(conf_file)
		self.data = {}
		self.create_data_dict(self.conf_data)

	def create_data_dict(self, conf_data, ids = []):
		if isinstance(conf_data, dict):
			for key, val in conf_data.items():
				self.create_data_dict(val, ids + [key])
		else:
			key = hash(".".join(ids))
			self.data[key] = conf_data

	def get(self, key):
		if type(key) != int:
			key = hash(key)
		return self.data[key]