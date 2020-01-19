from engine.client.widgets import *
from engine import *

########## Generic menus

class BoxMenuItemW(MenuItemW):
	FORMAT = None
	FORMAT_FOCUSED = "game.menus.box_item_focused"

	def __init__(self, *args, v_align="center", **kwargs):
		super().__init__(*args, v_align=v_align, **kwargs)

	def compute_real_size(self, parent_size):
		larg = parent_size[1]
		n_rows = len(self.get_broke_text(larg)) + 2
		self.resize((n_rows, larg))

		super(MenuItemW, self).compute_real_size(parent_size)

class BoxMenuVertW(MenuVertW):
	def __init__(self, *args, v_align="center", col_size=0, border=(1, 0), spacing=0, modal=True, **kwargs):
		super().__init__(*args, v_align=v_align, col_size=col_size, border=border,
			modal=modal, spacing=spacing, **kwargs)