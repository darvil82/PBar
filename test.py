"""
This is a shitty test file.
"""

from typing import Any
from random import choice, randint, choices
import string
from time import sleep
import pbar


term_size = pbar.Term.get_size()

def repeat_func(times):
	def wrapper(func):
		def inner():
			for _ in range(times):
				func()
		return inner
	return wrapper

def random_string():
	return "".join(choices(string.ascii_letters + string.digits, k=randint(0, 250)))

def get_const_attrs(obj) -> list[tuple[str, Any]]:
	return [(x, getattr(obj, x)) for x in dir(obj) if x == x.upper()]

def animate(bar):
	pbar.animate(bar, delay=0.005)
	# sleep(0.1)
	bar.clear()









def default():
	b = pbar.PBar()
	animate(b)


@repeat_func(30)
def fully_random():
	b = pbar.PBar(
		(randint(0, 200), randint(0, 200)),
		random_string(),
		(randint(0, term_size[0]), randint(0, term_size[1])),
		(randint(0, term_size[0]), randint(0, term_size[1])),
		choice(get_const_attrs(pbar.ColorSet))[1],
		choice(get_const_attrs(pbar.CharSet))[1],
		choice(get_const_attrs(pbar.FormatSet))[1],
		contentg=choice(pbar.ContentGens.get_gens()),
		inverted=choice([True, False]),
	)

	animate(b)


def modify_size_and_pos():
	h = 1
	b = pbar.PBar(prange=(0, 80))

	for p, w in enumerate(range(1, 81)):
		h += .5
		b.size = (w, h)
		b.position = (p*2, p)
		b.step()
		sleep(.05)

	b.percentage = 0
	for p, w in enumerate(range(100, 1, -1)):
		h -= .5
		b.size = (w, h)
		b.position = (p*2, p)
		b.step()
		sleep(.05)

	animate(b)


def try_all_sets():
	print(pbar.Term.margin(2) + pbar.Term.clear() + f"COLORSET\tCHARSET\t\tFORMATSET\n{'-'*50}")

	b = pbar.PBar()
	for cname, cvalue in get_const_attrs(pbar.ColorSet):
		b.colorset = cvalue
		for chrname, chrvalue in get_const_attrs(pbar.CharSet):
			b.charset = chrvalue
			for fname, fvalue in get_const_attrs(pbar.FormatSet):
				print(f"{cname:<15}{chrname:<15}{fname}")
				b.formatset = fvalue
				b.draw()
				sleep(.05)
	animate(b)


@repeat_func(30)
def condtionals():
	conds = (	# lol!
		pbar.Cond(f"percentage == {randint(0, 100)}", choice(get_const_attrs(pbar.ColorSet))[1], choice(get_const_attrs(pbar.CharSet))[1], choice(get_const_attrs(pbar.FormatSet))[1]),
		pbar.Cond(f"prange1 >= {randint(0, 100)}", choice(get_const_attrs(pbar.ColorSet))[1], choice(get_const_attrs(pbar.CharSet))[1], choice(get_const_attrs(pbar.FormatSet))[1]),
		pbar.Cond(f"prange1 >= {randint(0, 100)}", choice(get_const_attrs(pbar.ColorSet))[1], choice(get_const_attrs(pbar.CharSet))[1], choice(get_const_attrs(pbar.FormatSet))[1], choice(pbar.ContentGens.get_gens())),
		pbar.Cond(f"prange1 >= {randint(0, 100)}", choice(get_const_attrs(pbar.ColorSet))[1], choice(get_const_attrs(pbar.CharSet))[1], choice(get_const_attrs(pbar.FormatSet))[1]),
		pbar.Cond(f"text == '{random_string()}'"),
	)
	b = pbar.PBar(size=(20, 10), conditions=conds)
	animate(b)


@pbar.task_wrapper
def task_wr(bar, something, another_thing):
	print(pbar.Term.clear())
	sleep(.25)
	sleep(.25)
	sleep(.25)
	sleep(.25)
	print(something)
	sleep(.25)
	sleep(.25)
	sleep(.25)
	print(another_thing)
	sleep(.25)
	sleep(.25)
	sleep(.25)


def try_relative_positioning():
	with pbar.Term.SeqMgr(scroll_limit=3):
		for n in pbar.iter(range(2000), pbar.PBar(position=("r", "r1"), centered=False)):
			print(choice(string.ascii_letters), end="")
			if n % (term_size[0]//2) == 0:
				print()
			sleep(.005)


def main():
	with pbar.Term.SeqMgr(hide_cursor=True, new_buffer=True, home_cursor=True):
		try_relative_positioning()
		default()
		modify_size_and_pos()
		fully_random()
		try_all_sets()
		condtionals()
		task_wr(pbar.PBar(), something="Something", another_thing="Another thing")


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
