#!/bin/env python3.9

import pbar
from time import sleep


mybar = pbar.PBar(
	range=(0, 67),
	text="Loading",
	format=pbar.FormatSet.MIXED,
	charset=pbar.CharSet.SLIM,
	colorset=pbar.ColorSet.DARVIL,
	length=30,
	position=("a", "a")
)


print("Printing bar... ", end="")


mybar.draw()