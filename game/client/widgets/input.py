from engine.client.widgets import *
from engine import *

class KeyInputW(TextW):
	FOCUSABLE = True
	FORMAT_FOCUSED = "game.input.key_input"

	def __init__(self, text, *kargs, v_align="center", padding=((0, 0), (2, 1)), **kwargs):
		self.text = text
		super().__init__(text, *kargs, v_align=v_align, padding=padding, **kwargs)
		self.key_w = self.add(KeyDisplayW(None, pos=("center", 0), inv_side=(False, True)))

class KeySetterW(KeyInputW):
	def __init__(self, key_tag, text, config_obj=None, **kwargs):
		self.key_tag = key_tag
		self.config_obj = config_obj if config_obj else G.CLIENT.config
		super().__init__(text, **kwargs)

		self.set_key(self.config_obj.get_key(key_tag))

	def set_key(self, key):
		self.key_w.set_key(key)
		self.config_obj.set_key(self.key_tag, key)

	def keypress(self, key):
		if not self.focused:
			return False
		if key.check("\n"):
			G.WINDOW.add(KeyPromptW(call=self.set_key))
		elif key.check([KeyVal.BACK, "X"]):
			self.set_key(None)
		else:
			return False
		return True

class KeyPromptW(BaseWinW):
	def __init__(self, *kargs, size=(10, 40), call=None, normalize=True, **kwargs):
		kwargs["closeable"] = False
		super().__init__(*kargs, modal=True, size=size, **kwargs)

		self.call = call
		self.normalize = normalize

		self.add(TextW("Press the key to record,\nor [ESC] to cancel", size=(3, -4), align="center", pos=(1, 2)))
		self.message = self.add(TextW("Waiting...", size=(3, -4), align="center", pos=(0, 2),
			inv_side=(True, False), format="dim_text"))

	def keypress(self, key):
		if key.check(KeyVal.ESCAPE):
			self.delete()
		if self.normalize:
			key = key.norm()

		if key.is_key_mapable():
			if self.call:
				self.call(key)
			self.delete()
		else:
			self.message.set_text("Key not valid\nChoose another one")
			self.message.format = self.message.parse_format("error_message")
		return True

class KeyInputContainerW(FormLayoutW, VertLayoutW):
	def __init__(self, *kargs, side_margin=2, **kwargs):
		self.side_margin = side_margin
		self.delta_row = 0
		super().__init__(*kargs, **kwargs)

	def move_focus(self, steps):
		super().move_focus(steps)
		G.WINDOW.dims_changed = True

	def apply_delta(self, delta):
		for child in self.children:
			child.rel_pos = (child.rel_pos[0]+delta, child.rel_pos[1])

	def compute_children_dims(self):
		super().compute_children_dims()
		self.apply_delta(self.delta_row)

		focused_child = None
		for child in self.children:
			if child.focused:
				focused_child = child
		if focused_child:
			cur_margin_bottom = (self.size[0] - focused_child.rel_pos[0]
				- focused_child.rel_size[0] - self.side_margin
			)
			cur_margin_top = focused_child.rel_pos[0] - self.side_margin
			delta = 0
			if cur_margin_top < 0:
				delta = - cur_margin_top
			elif cur_margin_bottom < 0:
				delta = cur_margin_bottom

			if delta:
				self.apply_delta(delta)
				self.delta_row += delta