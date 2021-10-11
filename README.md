<img width=50% src="https://user-images.githubusercontent.com/48654552/136713737-aebdd652-061b-428a-b750-2faa29cd60b3.png"><br>

<a href="https://github.com/DarviL82/PBar/pulls"> <img src="https://img.shields.io/badge/contributions-welcome-brightgreen?style=flat-square"> </a>
<a href="https://pypi.org/project/PBar2/"> <img src="https://img.shields.io/badge/PyPI-available-blue?style=flat-square"> </a>

---

### PBar is a small work in progress Python package to display customizable progress bars on the terminal easily. Contributions are welcome!



https://user-images.githubusercontent.com/48654552/136842704-53542e3a-2953-4d73-8057-3a3349b84a04.mp4


<details>
	<summary><b> More examples <b></summary>

https://user-images.githubusercontent.com/48654552/134776865-c7516cf1-0c66-44da-ae2c-f2cbedd2527c.mp4

Source available [here.](https://github.com/DarviL82/PBar/blob/main/resources/examples/anim.py)

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

- **prange**: This tuple will specify the range of two values to display in the progress bar.

  	- `PBar.prangeFromFile()` will get the range from the number of lines of a file.


- **text**: String to show in the progress bar.


- **size**: Tuple that specifies the width and height of the bar.


- **position**: Tuple containing the position (X and Y axles of the center) of the progress bar on the terminal.

	- If an axis value is `center`, the bar will be positioned at the center of the terminal on that axis.
	- Negative values will position the bar at the other side of the terminal.
	- `pbar.barHelper()` can be useful for deciding the position.

- **charset**: Set of characters to use when drawing the progress bar.

	- To use one of the included sets, use any of the constant values in `pbar.CharSet`. Keep in mind that some fonts might not have
	the characters used in some charsets.

	- Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom characters.
	- Custom character set dictionary:

		```py
		CharSetEntry = {
			"empty":	" ",
			"full":		" ",
			"vert": {
				"right":	" ",
				"left":		" "
			},
			"horiz": {
				"top":		" ",
				"bottom":	" "
			},
			"corner": {
				"tleft":	" ",
				"tright":	" ",
				"bleft":	" ",
				"bright":	" "
			}
		}
		```

		Note: It is not needed to specify all the keys and values.


- **colorset**: Set of colors to use when drawing the progress bar.

	- To use one of the included sets, use any of the constant values in `pbar.ColorSet`.

	- Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom colors.
	- Custom color set dictionary:

		```py
		ColorSetEntry = {
			"empty":	None,
			"full":		None,
			"vert":	{
				"left":		None,
				"right":	None
			},
			"horiz": {
				"top":		None,
				"bottom":	None
			},
			"corner": {
				"tleft":	None,
				"tright":	None,
				"bleft":	None,
				"bright":	None
			},
			"text":	{
				"inside":	None,
				"right":	None,
				"left":		None,
				"title":	None,
				"subtitle":	None
			}
		}
		```

		Note: It is not needed to specify all the keys and values.

		Note: The colors can also be specified as a string with a HEX value (`#1af` | `#a0b1c2`), or an HTML color name (`red`, `yellow`, `turquoise`, etc...).


- **formatset**: Formatting used when displaying the strings in different places around the bar.

	- To use one of the included sets, use any of the constant values in `pbar.FormatSet`.

	- Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom formatting.
	- Custom formatset dictionary:

		```py
		FormatSetEntry = {
			"inside":	"",
			"right":	"",
			"left":		"",
			"title":	"",
			"subtitle":	""
		}
		```

		Note: It is not needed to specify all the keys and values.

	- Available formatting keys:
		- `<percentage>`:	Percentage of the bar.
		- `<range1>`:		First value of the prange.
		- `<range2>`:		Second value of the prange.
		- `<text>`:			Text selected in the `text` property/arg.
		- `<etime>`:		Elapsed time since the bar created.

Do note that this arguments are also available as object properties:
```py
mybar = pbar.PBar(prange=(0, 10), formatset=pbar.FormatSet.TITLE_SUBTITLE)
mybar.colorset = pbar.ColorSet.DARVIL
mybar.text = "Doing stuff!"
```

In order to control the way the bar behaves on the screen, use the next methods:

- `PBar.draw()`:		Prints the progress bar on screen.
- `PBar.step()`:		Add a specified step number to the first value in prange of the bar, then draw the bar.
- `PBar.clear()`:	Clears the progress bar from the screen.

The PBar object also counts the time that passed since the object constructed. This elapsed time can be displayed on the bar itself (by using FormatSets that use it), and can be obtained with the `PBar.etime` property, which returns a float.

This elapsed time counter can be resetted by calling the `PBar.resetETime()` method.

There's a **classmethod** available:
- `PBar.fromConfig()`:	Return a PBar object created with the configuration of the PBar/dict object given.


<br><hr>

## **taskWrapper function decorator**
The `taskWrapper` decorator will automatically change the prange of the progress bar depending on the number of function calls inside the decorated function. This will also call the `PBar.step()` method after each function call processed. Example:
```py
@taskWrapper(PBar(), locals())
def myTasks():
	getReq()
	processReq()
	prntText()
	testMgr()
```
In this example, there are four function calls inside the decorated function. `taskWrapper` will set the `prange` of the progress bar as `(0, 4)`. Then, after each of the functions finished processing, a `PBar.step()` call will be done.

Function arguments:
- **pbarObj (required)**: PBar object to use.
- **scope (required)**: Dictionary containing the scope local variables.
- **titleComments**: If True, comments on a statement will be treated as titles for the progress bar.
- **overwriteRange**: If True, overwrites the prange of the bar.

When setting `titleComments` as `True`, we can use Python comments with the "bTitle:" prefix to tell the wrapper to take that as a the value `PBar.text` will have for each call. For example:
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


## Installation
PBar is available in the Python Package Index:

`pip install pbar2`

You can also install this package through GitHub:

`pip install git+https://github.com/DarviL82/PBar`

For uninstalling:

`pip uninstall pbar2`


## Additional Credits
| User       | Task          |
|------------|---------------|
| DrMeepster | Type Checking |
