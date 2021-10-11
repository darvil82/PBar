#!/bin/env python3.9

import pbar
from time import sleep


mybar = pbar.PBar(
	prange=(0, 67),							# Range displayed as the progress
	text="Loading",							# Some text to be displayed
	charset=pbar.CharSet.ROUNDED,			# Characters that the bar will use
	size=(30, 1),							# Width and height
	formatset=pbar.FormatSet.TITLE_SUBTITLE	# Text that will be displayed on the different places

)


print("Printing bar... ", end="")


try:
	while mybar.percentage < 100:
		sleep(0.1)
		mybar.colorset |= {		# Merge with our own dict
			"full":		(0, mybar.percentage*2, 100),
			"empty":	(255 - mybar.percentage*2, 100, 0),
			"text":	{
				"title":	(0, mybar.percentage*2, 100),
				"subtitle":	(255 - mybar.percentage*2, 100, 0),
			}
		}
		mybar.step()			# Step over the prange and draw bar
	else:
		mybar.text = "Done!"	# Change the text of the bar
		mybar.colorset |= {
			"text":		(0, 255, 0)
		}

except KeyboardInterrupt:
	mybar.text = "Interrupted!"
	mybar.colorset = pbar.ColorSet.ERROR


mybar.draw()
sleep(1)
mybar.clear()

print("Finished!")				# The cursor stays at the same position