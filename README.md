# PBar
PBar is a small work in progress python module to display customizable progress bars on the terminal. Contributions are welcome!

## Example
### This code here...
```py
import pbar
from time import sleep


mybar = pbar.PBar(
	range=(0, 67),
	text="Loading",
	charset=pbar.CharSet.SLIM,
	length=30,
	colorset={
		"text": {
			"outside":	(255, 189, 0)
		}
	},
	format=pbar.FormatSet.MIXED
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
	mybar.colorset = pbar.ColorSet.ERROR


mybar.draw()
sleep(1)
mybar.clear()

print("Finished!")
```
### ...will generate something like this:

https://user-images.githubusercontent.com/48654552/130366455-55ddbbeb-3225-4431-9fe0-8d6b73187357.mp4


## Requirements
Python 3.9


## Additional Credits
| User       | Task          |
|------------|---------------|
| DrMeepster | Type Checking |
