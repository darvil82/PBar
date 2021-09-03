#!/bin/env python3.9

import pbar
from time import sleep


mybar = pbar.PBar(
	range=(14, 67),
	text="Loading",
	charset={
		"empty":	"H",
		"full":		"X",
		"corner":	"O"
	},
	colorset=pbar.ColorSet.DARVIL,
	format=pbar.FormatSet.MIXED,
	length=30
)


print("Printing bar... ", end="")


mybar.draw()