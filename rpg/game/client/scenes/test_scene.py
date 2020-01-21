from engine.client.window import *
from engine.client.widgets import *
from engine.client.client import Scene
from engine import *
import time

class TestScene(Scene):
	def start(self):
		self.start_2()

	def start_2(self):
		def call_button():
			self.root.add(TextPopupW("---------"))

		self.root.add(ButtonW("Button", size=12, big=True, call=call_button))

		l = ["value1", "value2", "value2", "Obi-Wan Kenobi"]
		self.root.add(SelectListW(l, pos=(10, 3)))

		self.root.add(WebLinkW("Github page", "https://github.com/webalorn/unicode_rpg", pos=(5, 3)))


	def start_1(self):
		def call2():
			self.root.add(TextPopupW("So be it"))

		def call_button():
			# self.root.add(ConfirmPopupW("Do you want to continue ?", call=call2))
			self.root.add(ButtonsPopup("Fenêtre avec des JOLIS boutons"))

		self.root.add(ButtonW("coucou", size=12, big=True, call=call_button))
		self.root.add(BarInputW(1, size=30, format=('white', 'yellow', []), maxi=50, step=1, pos=(7, 3)))
		self.root.add(CheckBoxW(False, pos=(4, 15)))


		group = self.root.add(RadioGroupW(pos=(4, 35), size=(12, 4)))
		layout_radio = group.add(VertLayoutW(size=(1.,1.)))
		layout_radio.add(RadioW())
		layout_radio.add(RadioW())
		layout_radio.add(RadioW())


		self.root.add(ImageW("shield.cbi", pos=(0, "center")))
		# for i in range(60):
		# 	self.root.add(ImageW("shield.cbi", pos=((i//10)*8, (i%10)*16)))

		long_text = "Exercitation qui enim cillum duis labore aliquip amet laboris nostrud dolore dolore exercitation nisi deserunt irure amet labore aute incididunt tempor ad eu in irure aute officia labore laboris consectetur dolor reprehenderit nisi quis ea dolore fugiat ad nisi adipisicing aliqua amet aliquip et ut incididunt dolore irure ut ut qui nisi velit ut non incididunt sed voluptate aliquip proident sunt nisi pariatur anim ex excepteur culpa ex elit sint id in elit elit cillum aute esse amet laboris id officia ut consectetur esse veniam enim pariatur reprehenderit ut excepteur culpa ullamco cillum sit dolor minim dolore mollit ut ea nisi tempor officia et dolore proident sunt et labore veniam sit id enim nostrud duis sit in nulla est ullamco in in ullamco sed amet quis pariatur sed dolore elit reprehenderit minim ut deserunt nulla in magna exercitation aliquip ullamco pariatur aute culpa magna cillum ut duis dolor veniam consequat non et nostrud sunt laborum voluptate laborum do in est do consequat id non aliquip sunt dolore ut in eiusmod excepteur do tempor velit aliqua duis irure dolor mollit duis deserunt anim dolore esse nostrud velit adipisicing qui excepteur incididunt in adipisicing et commodo occaecat anim enim proident dolor eu dolore commodo magna eu dolore eu anim officia consequat veniam."

		col_right = self.root.add(VertLayoutW(size=(1., 45), anchor="center", h_align="center", inv_side=(False, True)))
		col_right.add(ScrollTextW(
			long_text,
			size=(10, 40), border=1, pos=("center", 0), inv_side=(False, True)
		))

		col_right.add(TextareaW(
			"Veniam magna incididunt esse exercitation aliquip sint eu pariatur elit cupidatat.",
			size=(10, 40), border=1, pos=("center", 0), inv_side=(False, True)
		))

		col = self.root.add(VertLayoutW(size=(1., 30), force_width=False, anchor="center", h_align="center"))

		for _ in range(3):
			txt = TextW("Ea nisi reprehenderit sed dolore dolore", size=(4, 16))
			box = BoxW(add=txt, size=(6, 24), pos=5, border=1)
			col.add(box)

		txt2 = TextInputW("abc de 123 456 789 10", size=(3, 14), border=1, limit=0)
		box2 = BoxW(add=txt2, size=(6, 18), pos=6, border=1)
		col.add(box2)
		password = col.add(PasswordW("Guess me", size=(3, 16), border=1, limit=0))
		self.window.ev_draw_begin.on(lambda : txt.set_text("-> " + password.get_real_text()))


		super_txt = TextW("Super boite", size=(4, 16))
		self.root.add(BoxW(add=super_txt, size=(6, 24), pos=(12, 5), border=1))

		def f():
			raise ExitException("END")

		def g():
			self.root.add(TextPopupW("Coucou, ça va ?"))
		form = ("red", None, ["bold"])

		menu = self.root.add(MenuVertW(size=(15, 15), border=1, pos="center", col_size=2, scroll=True, format=form))
		menu.add(MenuItemW("Ullamco voluptate eiusmod voluptate", call=g, text_format=('yellow', 'inherit', 'inherit')))
		menu.add(MenuItemW("Hello there", call=f))
		for _ in range(7):
			menu.add(MenuItemW("test", align="center"))