# PBar
PBar is a small work in progress python module to display customizable progress bars on the terminal. Contributions are welcome!

## Example
### This code here...
```py
import pbar
from time import sleep


mybar = pbar.PBar(
	range=(0, 67),					# Range displayed as the progress
	text="Loading",					# Some text to be displayed
	charset=pbar.CharSet.TILTED,	# Characters that the bar will use
	size=(30, 1),					# Width and height
	formatset={						# Text that will be displayed on the different places
		"title":	"<text>",
		"subtitle":	"<range1> of <range2>"
	}
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
		mybar.step()			# Step over the range and draw bar
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

print("Finished!")		# The cursor stays at the same position
```
### ...will generate something like this:

https://user-images.githubusercontent.com/48654552/134509476-091b8d27-5d50-47a4-a0b6-37c587d27154.mp4


## Requirements
Python 3.9


## Additional Credits
| User       | Task          |
|------------|---------------|
| DrMeepster | Type Checking |
