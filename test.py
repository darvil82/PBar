"""
This is a shitty test file.
"""

from typing import Any
from random import choice, randint, choices
import string
from time import sleep
import pbar


termSize = pbar.Term.size()

def repeatFunc(times):
	def wrapper(func):
		def inner():
			for _ in range(times):
				func()
		return inner
	return wrapper

def randomString():
	return "".join(choices(string.ascii_letters + string.digits, k=randint(0, 250)))

def getConstAttrs(obj) -> list[tuple[str, Any]]:
	return [(x, getattr(obj, x)) for x in dir(obj) if x == x.upper()]

def animate(bar):
	pbar.animate(bar, delay=0.005)
	# sleep(0.1)
	bar.clear()









def default():
	b = pbar.PBar()
	animate(b)


@repeatFunc(30)
def fullyRandom():
	b = pbar.PBar(
		(randint(0, 200), randint(0, 200)),
		randomString(),
		(randint(0, termSize[0]), randint(0, termSize[1])),
		(randint(0, termSize[0]), randint(0, termSize[1])),
		choice(getConstAttrs(pbar.ColorSet))[1],
		choice(getConstAttrs(pbar.CharSet))[1],
		choice(getConstAttrs(pbar.FormatSet))[1],
		contentg=choice(pbar.ContentGens.getGens()),
		inverted=choice([True, False]),
	)

	animate(b)



def modifySizeAndPos():
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



def tryAllSets():
	print(pbar.Term.margin(2) + pbar.Term.clear() + f"COLORSET\tCHARSET\t\tFORMATSET\n{'-'*50}")

	b = pbar.PBar(prange=(1, 3))
	for cname, cvalue in getConstAttrs(pbar.ColorSet):
		b.colorset = cvalue
		for chrname, chrvalue in getConstAttrs(pbar.CharSet):
			b.charset = chrvalue
			for fname, fvalue in getConstAttrs(pbar.FormatSet):
				print(f"{cname:<15}{chrname:<15}{fname}")
				b.formatset = fvalue
				b.draw()
				sleep(.01)
				b.clear()
	animate(b)



@repeatFunc(30)
def condtionals():
	conds = (	# lol!
		pbar.Cond(f"percentage == {randint(0, 100)}", choice(getConstAttrs(pbar.ColorSet))[1], choice(getConstAttrs(pbar.CharSet))[1], choice(getConstAttrs(pbar.FormatSet))[1]),
		pbar.Cond(f"prange1 >= {randint(0, 100)}", choice(getConstAttrs(pbar.ColorSet))[1], choice(getConstAttrs(pbar.CharSet))[1], choice(getConstAttrs(pbar.FormatSet))[1]),
		pbar.Cond(f"prange1 >= {randint(0, 100)}", choice(getConstAttrs(pbar.ColorSet))[1], choice(getConstAttrs(pbar.CharSet))[1], choice(getConstAttrs(pbar.FormatSet))[1], choice(pbar.ContentGens.getGens())),
		pbar.Cond(f"prange1 >= {randint(0, 100)}", choice(getConstAttrs(pbar.ColorSet))[1], choice(getConstAttrs(pbar.CharSet))[1], choice(getConstAttrs(pbar.FormatSet))[1]),
		pbar.Cond(f"text == '{randomString()}'"),
	)
	b = pbar.PBar(size=(20, 10), conditions=conds)
	animate(b)



@pbar.taskWrapper
def taskWr(bar, something, another_thing):
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





def main():
	with pbar.Term.SeqMgr():
		default()
		modifySizeAndPos()
		fullyRandom()
		tryAllSets()
		condtionals()
		taskWr(pbar.PBar(), something="Something", another_thing="Another thing")


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		pass
