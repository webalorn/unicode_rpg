from engine.client.window import *
from engine.client.widgets import *
from engine.client.client import Scene
from engine import *
import time

class TestScene(Scene):
	def start(self):
		def call2():
			self.window.add(TextPopupW("So be it"))

		def call_button():
			# self.window.add(ConfirmPopupW("Do you want to continue ?", call=call2))
			self.window.add(ButtonsPopup("Fenêtre avec des JOLIS boutons"))
			# self.window.add(TextPopupW("Bouton cliqué"))

		self.window.add(ButtonW("coucou", size=12, big=True, call=call_button))
		self.window.add(BarInputW(1, size=30, format=('white', 'yellow', []), maxi=50, step=1, pos=(7, 3)))
		self.window.add(CheckBoxW(False, pos=(4, 15)))


		group = self.window.add(RadioGroupW(pos=(4, 35), size=(12, 4)))
		layout_radio = group.add(VertLayoutW(size=(1.,1.)))
		layout_radio.add(RadioW())
		layout_radio.add(RadioW())
		layout_radio.add(RadioW())

		for _ in range(30):
			self.window.add(ImageW("shield.cbi", pos=(0, "center")))

		long_text = "Exercitation qui enim cillum duis labore aliquip amet laboris nostrud dolore dolore exercitation nisi deserunt irure amet labore aute incididunt tempor ad eu in irure aute officia labore laboris consectetur dolor reprehenderit nisi quis ea dolore fugiat ad nisi adipisicing aliqua amet aliquip et ut incididunt dolore irure ut ut qui nisi velit ut non incididunt sed voluptate aliquip proident sunt nisi pariatur anim ex excepteur culpa ex elit sint id in elit elit cillum aute esse amet laboris id officia ut consectetur esse veniam enim pariatur reprehenderit ut excepteur culpa ullamco cillum sit dolor minim dolore mollit ut ea nisi tempor officia et dolore proident sunt et labore veniam sit id enim nostrud duis sit in nulla est ullamco in in ullamco sed amet quis pariatur sed dolore elit reprehenderit minim ut deserunt nulla in magna exercitation aliquip ullamco pariatur aute culpa magna cillum ut duis dolor veniam consequat non et nostrud sunt laborum voluptate laborum do in est do consequat id non aliquip sunt dolore ut in eiusmod excepteur do tempor velit aliqua duis irure dolor mollit duis deserunt anim dolore esse nostrud velit adipisicing qui excepteur incididunt in adipisicing et commodo occaecat anim enim proident dolor eu dolore commodo magna eu dolore eu anim officia consequat veniam."

		col_right = self.window.add(VertLayoutW(size=(1., 45), anchor="center", h_align="center", inv_side=(False, True)))
		col_right.add(ScrollTextW(
			long_text,
			size=(10, 40), border=1, pos=("center", 0), inv_side=(False, True)
		))

		col_right.add(TextareaW(
			"Veniam magna incididunt esse exercitation aliquip sint eu pariatur elit cupidatat.",
			size=(10, 40), border=1, pos=("center", 0), inv_side=(False, True)
		))

		col = self.window.add(VertLayoutW(size=(1., 30), force_width=False, anchor="center", h_align="center"))
		# col = self.window.add(HorLayoutW(size=(20, 1.), force_height=False, anchor="right"))

		for _ in range(3):
			txt = TextW("Ea nisi reprehenderit sed dolore dolore", size=(4, 16))
			box = BoxW(add=txt, size=(6, 24), pos=5, border=1)
			col.add(box)

		txt2 = TextInputW("abc de 123 456 789 10", size=(3, 14), border=1, limit=0)
		box2 = BoxW(add=txt2, size=(6, 18), pos=6, border=1, background=0)
		col.add(box2)
		password = col.add(PasswordW("Guess me", size=(3, 16), border=1, limit=0))
		self.window.ev_draw_begin.on(lambda : txt.set_text("-> " + password.get_real_text()))


		super_txt = TextW("Super boite", size=(4, 16))
		self.window.add(BoxW(add=super_txt, size=(6, 24), pos=(12, 5), border=1, background=0))

		def f():
			raise ExitException("END")

		def g():
			self.window.add(TextPopupW("Coucou, ça va ?"))
		form = ("red", None, ["bold"])

		menu = self.window.add(MenuVertW(size=(15, 15), border=1, pos="center", col_size=2, scroll=True, format=form))
		menu.add(MenuItem("Ullamco voluptate eiusmod voluptate", call=g, text_format=('yellow', 'inherit', 'inherit')))
		menu.add(MenuItem("Hello there", call=f))
		menu.add(MenuItem("test", align="center"))
		menu.add(MenuItem("test", align="center"))
		menu.add(MenuItem("test", align="center"))
		menu.add(MenuItem("test", align="center"))
		menu.add(MenuItem("test", align="center"))
		menu.add(MenuItem("test", align="center"))
		menu.add(MenuItem("test", align="center"))