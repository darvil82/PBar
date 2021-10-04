<img width=50% src="resources/logo.png">

---

### PBar is a small work in progress python module to display customizable progress bars on the terminal easily. Contributions are welcome!

https://user-images.githubusercontent.com/48654552/134776865-c7516cf1-0c66-44da-ae2c-f2cbedd2527c.mp4


<details>
	<summary><b>See the code of this example</b></summary>

```py
import pbar
from time import sleep


mybar = pbar.PBar(
	range=(0, 67),							# Range displayed as the progress
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

print("Finished!")				# The cursor stays at the same position
```
</details>

<br><br>

# Main Features
## **PBar Object**
The main part of this module, the PBar object, which will let us manage and customize the progress bars however we want. In order to create a new progress bar, create a new instance of the object.

```py
import pbar
mybar = pbar.PBar()
```

Note that the object constructor provides many arguments (all optional) for configuring the bar when constructing it:

- **range**: This tuple will specify the range of two values to display in the progress bar.


- **text**: String to show in the progress bar.


- **size**: Tuple that specifies the width and height of the bar.


- **position**: Tuple containing the position (X and Y axles of the center) of the progress bar on the terminal.

	- If an axis value is `center`, the bar will be positioned at the center of the terminal on that axis.
	- Negative values will position the bar at the other side of the terminal.


- **charset**: Set of characters to use when drawing the progress bar.

	- To use one of the included sets, use any of the constant values in `pbar.CharSet`. Keep in mind that some fonts might not have
	the characters used in some charsets.

	- Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom characters.
	- Custom character set dictionary:

		![image](https://user-images.githubusercontent.com/48654552/127887419-acee1b4f-de1b-4cc7-a1a6-1be75c7f97c9.png)

		Note: It is not needed to specify all the keys and values.


- **colorset**: Set of colors to use when drawing the progress bar.

	- To use one of the included sets, use any of the constant values in `pbar.ColorSet`.

	- Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom colors.
	- Custom color set dictionary:

		![image](https://user-images.githubusercontent.com/48654552/134371850-1d858a6e-8003-40da-a5ff-f36bd06a5b07.png)

		Note: It is not needed to specify all the keys and values.

		Note: The colors can also be specified as HEX in a string.


- **formatset**: Formatting used when displaying the strings in different places around the bar.

	- To use one of the included sets, use any of the constant values in `pbar.FormatSet`.

	- Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom formatting.
	- Custom formatset dictionary:

		![image](https://user-images.githubusercontent.com/48654552/134372064-2abd9fab-37dd-4334-8d30-26e2f0967313.png)

		Note: It is not needed to specify all the keys and values.

	- Available formatting keys:
		- `<percentage>`:	Percentage of the bar.
		- `<range1>`:		First value of the range.
		- `<range2>`:		Second value of the range.
		- `<text>`:			Text selected in the `text` property/arg.
		- `<etime>`:		Elapsed time since the bar created.

Do note that this arguments are also available as object properties:
```py
mybar = pbar.PBar(range=(0, 10), formatset=pbar.FormatSet.TITLE_SUBTITLE)
mybar.colorset = pbar.ColorSet.DARVIL
mybar.text = "Doing stuff!"
```

In order to control the way the bar behaves on the screen, use the next methods:

- `PBar.draw()`:		Prints the progress bar on screen.
- `PBar.step()`:		Add a specified step number to the first value in range of the bar, then draw the bar.
- `PBar.clear()`:	Clears the progress bar from the screen.

The PBar object also counts the time that passed since the object constructed. This elapsed time can be displayed on the bar itself (by using FormatSets that use it), and can be obtained with the `PBar.etime` property, which returns a float.

This elapsed time counter can be resetted by calling the `PBar.resetETime()` method.

<br><hr>

## **taskWrapper function decorator**
The `taskWrapper` decorator will automatically change the range of the progress bar depending on the number of function calls inside the decorated function. This will also call the `PBar.step()` method after each function call processed. Example:
```py
@taskWrapper(PBar(), locals())
def myTasks():
	getReq()
	processReq()
	prntText()
	testMgr()
```
In this example, there are four function calls inside the decorated function. `taskWrapper` will set the `range` of the progress bar as `(0, 4)`. Then, after each of the functions finished processing, a `PBar.step()` call will be done.

Function arguments:
- **pbarObj (required)**: PBar object to use.
- **scope (required)**: Dictionary containing the scope local variables.
- **titleComments**: If True, comments on a statement will be treated as titles for the progress bar.
- **overwriteRange**: If True, overwrites the range of the bar.

When setting `titleComments` as `True`, we can use Python comments with the "bTitle:" prefix to tell the wrapper to take that as a the value `PBar.title` will have for each call. For example:
```py
@taskWrapper(PBar(), locals(), titleComments=True)
def myTasks():
	getReq()	#bTitle: Getting requests
	processReq()	#bTitle: Processing requests
	prntText()	#bTitle: Printing
	testMgr()	#bTitle: Testing
```
Each of those comments will be displayed on the progress bar.

> **Note:** Multi-line statements are not supported inside a function decorated by `taskWrapper`.

<br>

### As a minor note, pbar provides a very simple `VT100` class for using terminal escape sequences. (This is what the module uses for printing the bar)

<br><br><hr>




## Requirements
Python 3.9+


## Additional Credits
| User       | Task          |
|------------|---------------|
| DrMeepster | Type Checking |
