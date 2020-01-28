from .simple import *
from engine.client.keys import *
from engine import *
from .layouts import *
from .wins import *

########## Selection

class ListItemW(MenuItemW):
	FORMAT = "select.list_item"
	FORMAT_FOCUSED = "select.list_item_focused"

class SelectListWinW(BaseWinW):
	def __init__(self, list_widget, *kargs, size=None, **kwargs):
		if size == None:
			size = (min(G.WINDOW.size[0]-4, 30), 30)
		super().__init__(*kargs, size=size, **kwargs)

		self.add(TextW("Please select an option", align="center", v_align="center", size=(3, 1.),
			format="select.list_text"))
		self.choices = self.add(MenuVertW(scroll=True, v_align="top", size=(-3, 1.), pos=(3, 0), col_size=0))

		for i_el, (key, text) in enumerate(list_widget.select_list):
			def ev_closure(i_el, self):
				def called_on_select():
					list_widget.set_selected(i_el)
					self.close()
				return called_on_select
			self.choices.add(ListItemW(text, call=ev_closure(i_el, self)))
		self.choices.move_cursor(list_widget.selected_id)

class SelectListW(ButtonW):
	BORDER_FOCUSED = "border"

	def __init__(self, select_list, start_id=0, size=20, border=1, align="left", win_args={}, **kwargs):
		self.select_list = self.get_list_option(select_list)
		self.win_args = win_args
		kwargs["text"] = ""
		if isinstance(size, int):
			kwargs["size"] = (3, size)
		super().__init__(border=border, big=True, align=align, **kwargs)

		self.ev_changed = UIEvent()
		self.set_selected(start_id)

	def set_selected(self, i):
		if not isinstance(i, int):
			for j, (key, val) in enumerate(self.select_list):
				if key == i:
					i = j
					break
		self.selected_id = i
		self.set_text(self.select_list[i][1])
		self.ev_changed.fire()

	def draw_widget(self):
		super().draw_widget()
		self.grid[self.size[0]//2][-3] = "select.down"

	def get_real_padding(self):
		(a, b), (c, d) = super().get_real_padding()
		return ((a, b), (c+1, d+3))

	def get_selected_key(self):
		return self.select_list[self.selected_id][0]

	def keypress(self, key):
		if self.focused and key.check(["\n", " "]):
			G.WINDOW.add(SelectListWinW(self, **self.win_args))
			return True
		return False

	@staticmethod
	def get_list_option(select_list):
		"""
			Return a list [("key", "displayed text"), ...]
		"""
		if not select_list:
			raise Error("SelectListW without elements")
		if isinstance(select_list, dict):
			return list(select_list.items())
		elif isinstance(select_list, list) and isinstance(select_list[0], tuple):
			return select_list
		else:
			return list(enumerate(select_list))