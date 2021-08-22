#!/bin/env python3.9

from pbar import PBar
from time import sleep


mybar = PBar(
	range=(0, 67),
	text="Loading",
	charset="slim",
	length=30,
	colorset={
		"text": {
			"outside":	(255, 189, 0)
		}
	},
	format={
		"inside":	"<percentage>%!",
		"outside":	"[<range1>/<range2>] -><text>\<-"
	}
)


print("Printing bar... ", end="")


try:
	while mybar.percentage < 100:
		sleep(0.1)
		mybar.colorset |= {
			"full":		(0, mybar.percentage * 2, 100),
			"empty":	(255 - mybar.percentage * 2, 100, 0)
		}
		mybar.step()
	else:
		mybar.text = "Done!"
		mybar.colorset |= {
			"text": {"outside":	(0, 255, 0)}
		}

except KeyboardInterrupt:
	mybar.text = "Interrupted!"
	mybar.colorset = "error"


mybar.draw()
sleep(1)
mybar.clear()


print("Finished!")