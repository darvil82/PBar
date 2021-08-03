#!/bin/python3.9

from collections.abc import Sequence
from typing import Any, Optional, SupportsInt, TypeVar, Union, cast
from os import get_terminal_size as _get_terminal_size



__all__ = ["PBar"]
__author__ = "David Losantos (DarviL)"
__version__ = "0.1"


CharSetEntry = Union[str, dict[str, str]]
CharSet = dict[str, Union[str, CharSetEntry]]

_DEFAULT_CHARSETS: dict[str, CharSet] = {
	"empty": {
		"empty":	" ",
		"full":		" ",
		"vert":		" ",
		"horiz":	" ",
		"corner": {
			"tleft":	" ",
			"tright":	" ",
			"bleft":	" ",
			"bright":	" "
		}
	},

	"normal": {
		"empty":	"░",
		"full":		"█",
		"vert":		"│",
		"horiz":	"─",
		"corner": {
			"tleft":	"┌",
			"tright":	"┐",
			"bleft":	"└",
			"bright":	"┘"
		}
	},

	"basic": {
		"empty":	".",
		"full":		"#",
		"vert":		"│"
	},

	"slim": {
		"empty":	"░",
		"full":		"█"
	},

	"circles": {
		"empty":	"○",
		"full":		"●"
	},

	"basic2": {
		"empty":	".",
		"full":		"#",
		"vert":		"|",
		"horiz":	"-",
		"corner": {
			"tleft":	"+",
			"tright":	"+",
			"bleft":	"+",
			"bright":	"+"
		}
	},

	"full": {
		"empty":	"█",
		"full":		"█"
	},
}

Color = Optional[tuple[int, int, int]]
ColorSet = dict[str, Union[Color, dict[str, Color]]]

_DEFAULT_COLORSETS: dict[str, ColorSet] = {
	"empty": {
		"empty":	None,
		"full":		None,
		"vert":		None,
		"horiz":	None,
		"corner": {
			"tleft":	None,
			"tright":	None,
			"bleft":	None,
			"bright":	None,
		},
		"text":	{
			"inside":	None,
			"outside":	None,
		}
	},

	"green-red": {
		"empty":	(255, 0, 0),
		"full":		(0, 255, 0)
	},

	"darvil": {
		"empty":	(0, 103, 194),
		"full":		(15, 219, 162),
		"vert":		(247, 111, 152),
		"horiz":	(247, 111, 152),
		"corner":	{
			"tleft":	(247, 111, 152),
			"tright":	(247, 111, 152),
			"bleft":	(247, 111, 152),
			"bright":	(247, 111, 152)
		},
		"text": {
			"outside":	(247, 111, 152),
			"inside":	None
		}
	}
}


FormatSet = dict[str, str]

_DEFAULT_FORMATTING: dict[str, FormatSet] = {
	"empty": {
		"inside":	"",
		"outside":	""
	},

	"default": {
		"inside":	"<percentage>",
		"outside":	"<text>"
	},

	"all-out": {
		"outside":	"<percentage>, <range>, <text>"
	},

	"all-in": {
		"inside":	"<percentage>, <range>, <text>"
	}
}




Num = TypeVar("Num", int, float)

def _capValue(value: Num, max: Optional[Num]=None, min: Optional[Num]=None) -> Num:
    """Clamp a value to a minimun and/or maximun value."""

    if max and value > max:
        return max
    elif min and value < min:
        return min
    else:
        return value








class VT100():
	"""Class for using VT100 sequences a bit easier"""

	@staticmethod
	def pos(pos: Optional[Sequence[Any]], offset: tuple[int, int] = (0, 0)):
		if pos and len(pos) == 2:
			position = list(pos)
			for index, value in enumerate(position):
				if isinstance(value, str):
					if value == "center":
						position[index] = int(_get_terminal_size()[index] / 2)
					else:
						return ""
				elif isinstance(value, int):
					value = int(value)
				else:
					raise TypeError("Invalid type for position value")

				if isinstance(position[index], int):
					position[index] += offset[index]

			return f"\x1b[{position[1]};{position[0]}f"
		else:
			return ""

	@staticmethod
	def color(RGB: Optional[Sequence[int]]):
		if RGB and len(RGB) == 3:
			RGB = [_capValue(value, 255, 0) for value in RGB]
			return f"\x1b[38;2;{RGB[0]};{RGB[1]};{RGB[2]}m"
		else:
			return ""

	@staticmethod
	def moveHoriz(pos: SupportsInt):
		pos = int(pos)
		if pos < 0:
			return f"\x1b[{abs(pos)}D"
		else:
			return f"\x1b[{pos}C"

	@staticmethod
	def moveVert(pos: SupportsInt):
		pos = int(pos)
		if pos < 0:
			return f"\x1b[{abs(pos)}A"
		else:
			return f"\x1b[{pos}B"


	reset = "\x1b[0m"
	invert = "\x1b[7m"
	revert = "\x1b[27m"
	clearLine = "\x1b[2K"
	clearRight = "\x1b[0K"
	clearLeft = "\x1b[1K"
	cursorShow = "\x1b[?25h"
	cursorHide = "\x1b[?25l"
	cursorSave = "\x1b7"
	cursorLoad = "\x1b8"








class PBar():
	"""
	# pBar - Progress bar

	pBar is an object for managing progress bars in python.

	---

	## Initialization

	>>> mybar = pBar()

	- A progress bar will be initialized with all the default values. For customization, use the arguments or the properties available.

	---

	## Methods

	- mybar.draw()
	- mybar.step()
	- mybar.clear()

	---

	## Properties

	- mybar.percentage
	- mybar.text
	- mybar.range
	- mybar.charset
	- mybar.colorset
	- mybar.format
	"""

	def __init__(self,
			range: tuple[int, int] = (0, 1),
			text: str = "",
			length: int = 20,
			charset: Union[None, str, dict[str, str]] = None,
			colorset: Union[None, str, dict[str, tuple[int, int, int]]] = None,
			position: Optional[tuple[int, int]] = None,
			format: Union[None, str, dict[str, str]] = None
		) -> None:
		"""
		>>> range: tuple[int, int]:

		- This tuple will specify the range of two values to display in the progress bar.
		---

		>>> text: str:

		- String to show in the progress bar.
		---

		>>> length: int:

		- Intenger that specifies how long the bar will be.
		---

		>>> charset: Union[None, str, dict[str, str]]:

		- Set of characters to use when drawing the progress bar. This value can either be a
		string which will specify a default character set to use, or a dictionary, which should specify the custom characters:
			- Available default character sets: `empty`, `normal`, `basic`, `basic2`, `slim`, `circles` and `full`.
			- Custom character set dictionary:

				![image](https://user-images.githubusercontent.com/48654552/127887419-acee1b4f-de1b-4cc7-a1a6-1be75c7f97c9.png)

			Note: It is not needed to specify all the keys and values.

		---

		>>> colorset: Union[None, str, dict[str, tuple[int, int, int]]]:

		- Set of colors to use when drawing the progress bar. This value can either be a
		string which will specify a default character set to use, or a dictionary, which should specify the custom characters:
			- Available default color sets: `empty`, `green-red` and `darvil`.
			- Custom color set dictionary:

				![image](https://user-images.githubusercontent.com/48654552/127904550-15001058-cbf2-4ebf-a543-8d6566e9ef36.png)

			Note: It is not needed to specify all the keys and values.

		---

		>>> position: Optional[tuple[int, int]]:

		- Tuple containing the position (X and Y axles of the center) of the progress bar on the terminal.
		If a value is `center`, the bar will be positioned at the center of the terminal on that axis.
		---

		>>> format: Union[None, str, dict[str, str]]:

		- Formatting used when displaying the values inside and outside the bar. This value can either be a
		string which will specify a default formatting set to use, or a dictionary, which should specify the custom formats:
			- Available default formatting sets: `empty`, `default`, `all-out` and `all-in`.
			- Custom color set dictionary:

				![image](https://user-images.githubusercontent.com/48654552/127889950-9b31d7eb-9a52-442b-be7f-8b9df23b15ae.png)

			Note: It is not needed to specify all the keys and values.

		- Available formatting keys: `<percentage>`, `<range>` and `<text>`.
		"""

		self._range = list(range)
		self._text = str(text)
		self._length = _capValue(length, 255, 5)
		self._charset = self._getCharset(charset)
		self._colorset = self._getColorset(colorset)
		self._pos = position
		self._format = self._getFormat(format)

		self._drawtimes = 0
		self._requiresClear = False
		# self._draw()




	# --------- Properties / Methods the user should use. ----------

	def draw(self):
		"""Print the progress bar on screen"""
		self._draw(self._requiresClear)


	def step(self, steps: int = 1):
		"""Add `steps` to the first value in range, then draw the bar"""
		if not self._range[0] >= self._range[1]:
			self._range[0] += _capValue(steps, self._range[1] - self._range[0])
		self._draw(self._requiresClear)


	def clear(self):
		"""Clear the progress bar"""
		# well this is kinda hacky or ugly, but it's probably the easiest way to do it (just switch to the empty sets temporary)
		prevsets = (self._charset, self._colorset, self._format)
		self._charset, self._colorset, self._format = _DEFAULT_CHARSETS["empty"], _DEFAULT_COLORSETS["empty"], _DEFAULT_FORMATTING["empty"]
		self._draw()
		self._charset, self._colorset, self._format = prevsets



	@property
	def percentage(self):
		"""Percentage of the progress of the current range"""
		return int((self._range[0] * 100) / self._range[1])


	@property
	def text(self):
		"""Text to be displayed on the bar"""
		return self._text
	@text.setter
	def text(self, text: str):
		self._text = str(text)


	@property
	def range(self) -> tuple[int, int]:
		"""Range for the bar progress"""
		return self._range[0], self._range[1]
	@range.setter
	def range(self, range: tuple[int, int]):
		self._range = list(range)


	@property
	def charset(self) -> CharSet:
		"""Set of characters for the bar"""
		return self._charset
	@charset.setter
	def charset(self, charset: Any):
		self._charset = self._getCharset(charset)


	@property
	def colorset(self) -> ColorSet:
		"""Set of colors for the bar"""
		return self._colorset
	@colorset.setter
	def colorset(self, colorset: Any):
		self._colorset = self._getColorset(colorset)


	@property
	def format(self):
		"""Formatting used for the bar"""
		return self._format
	@format.setter
	def format(self, format: Any):
		self._format = self._getFormat(format)


	@property
	def length(self):
		"""Length of the progress bar"""
		return self._length
	@length.setter
	def length(self, length: int):
		newlen = _capValue(length, 255, 5)
		if newlen < self._length:
			# since the bar is gonna be smaller, we need to redraw it while clearing everything at the sides.
			self._requiresClear = True
		self._length = newlen

	# --------- ///////////////////////////////////////// ----------



	def _getCharset(self, charset: Any) -> CharSet:
		"""Return a full valid character set"""

		def stripCharset(charset: CharSet) -> CharSet:
			"""Converts empty values to spaces, and makes sure there's only one character"""
			newset = dict({})
			for key in charset.keys():
				value = charset[key]

				if isinstance(value, dict):
					value = stripCharset(value)
				elif len(value) > 1:
					value = value[0]
				elif len(value) == 0:
					value = " "

				newset[key] = value
			return newset


		if charset:
			if isinstance(charset, str):
				# it is a string, so we just get the default character set with that name
				charset = _DEFAULT_CHARSETS.get(charset, _DEFAULT_CHARSETS["normal"])
			elif isinstance(charset, dict):
				# it is a dict
				charset = stripCharset(charset)

				if "corner" in charset.keys():
					if isinstance(charset["corner"], str):	# this is only a str, so we just make all corners the value of this str
						charset["corner"] = {
							"tleft":	charset["corner"],
							"tright":	charset["corner"],
							"bleft":	charset["corner"],
							"bright":	charset["corner"]
						}
					elif isinstance(charset["corner"], dict):
						charset["corner"] = _DEFAULT_CHARSETS["empty"]["corner"] | charset["corner"]	# Merge corners into default dict
			else:
				raise ValueError(f"Invalid type ({type(charset)}) for charset")

			set: CharSet = _DEFAULT_CHARSETS["empty"] | charset		# merge charset into default dict
		else:
			set = _DEFAULT_CHARSETS["normal"]

		return set

	@property
	def _charsetCorner(self) -> dict[str, str]:
		"""type checker does not understand that CharSet["corner"] is always dict[str, str]"""
		return cast(dict[str, str], self._charset["corner"])

	def _char(self, key: str) -> str:
		assert(key != "corner")

		return cast(str, self._charset[key])


	def _getColorset(self, colorset: Any) -> ColorSet:
		"""Return a full valid color set"""
		if colorset:
			if isinstance(colorset, str):
				colorset = _DEFAULT_COLORSETS.get(colorset, _DEFAULT_COLORSETS["empty"])
			elif isinstance(colorset, dict):
				if "corner" in colorset.keys():
					if isinstance(colorset["corner"], list):
						colorset["corner"] = {
							"tleft": 	colorset["corner"],
							"tright": 	colorset["corner"],
							"bleft": 	colorset["corner"],
							"bright": 	colorset["corner"]
						}
					elif isinstance(colorset["corner"], dict):
						colorset["corner"] = _DEFAULT_COLORSETS["empty"]["corner"] = colorset["corner"]
				if "text" in colorset.keys():
					if isinstance(colorset["text"], list):
						colorset["text"] = {
							"inside":	colorset["text"],
							"outside":	colorset["text"]
						}
					elif isinstance(colorset["text"], dict):
						colorset["text"] = _DEFAULT_COLORSETS["empty"]["text"] | colorset["text"]
			else:
				raise ValueError(f"Invalid type ({type(colorset)}) for colorset")

			set: ColorSet = _DEFAULT_COLORSETS["empty"] | colorset
		else:
			set = _DEFAULT_COLORSETS["empty"]

		return set

	@property
	def _colorsetCorner(self) -> dict[str, Color]:
		"""type checker does not understand that ColorSet["corner"] is always dict[str, Color]"""
		return cast(dict[str, Color], self._colorset["corner"])

	@property
	def _colorsetText(self) -> dict[str, Color]:
		"""type checker does not understand that ColorSet["text"] is always dict[str, Color]"""
		return cast(dict[str, Color], self._colorset["text"])

	def _color(self, key: str) -> Color:
		assert(key != "corner" and key != "text")

		return cast(Color, self._colorset[key])


	def _getFormat(self, formatset: Any) -> FormatSet:
		"""Return a full valid formatting set"""
		if formatset:
			if isinstance(formatset, str):
				formatset = _DEFAULT_FORMATTING.get(formatset, _DEFAULT_FORMATTING["empty"])

			set: FormatSet = _DEFAULT_FORMATTING["empty"] | formatset
		else:
			set = _DEFAULT_FORMATTING["default"]

		return set








	def _draw(self, clearAll: bool = False):
		"""Draw the progress bar. clearAll will clear the lines used by the bar."""
		centerOffset = int((self._length + 2) / -2)		# Number of characters from the end of the bar to the center
		segments = int((_capValue(self._range[0], self._range[1], 0) / _capValue(self._range[1], min=1)) * self._length)	# Number of character for the full part of the bar


		def parseFormat(type: str) -> str:
			"""Parse a string that may contain formatting keys"""
			string = self._format[type]
			foundOpen = False	# Did we find a '<'?
			tempStr = ""		# String that contains the current value inside < >
			endStr = ""			# Final string that will be returned

			for char in string:
				if foundOpen:
					# Found '<'. Now we add every char to tempStr until we find a '>'.
					if char == ">":
						# Found '>'. Now just add the formatting keys.
						if tempStr == "percentage":
							endStr += f"{str(self.percentage)}%"
						elif tempStr == "range":
							endStr += f"{self._range[0]}/{self._range[1]}"
						elif tempStr == "text":
							if self._text:
								endStr += self._text

						foundOpen = False
						tempStr = ""
					else:
						# No '>' encountered, we can just add another character.
						tempStr += char.lower()
				elif char == "<":
					foundOpen = True
				else:
					# It is just a normal character that doesn't belong to any formatting key, so just append it to the end string.
					endStr += char

			return endStr



		# Build all the parts of the progress bar
		def buildTop() -> str:
			left = VT100.color(self._colorsetCorner["tleft"]) + self._charsetCorner["tleft"] + VT100.reset
			middle = VT100.color(self._color("horiz")) + self._char("horiz") * (self._length + 2) + VT100.reset
			right = VT100.color(self._colorsetCorner["tleft"]) + self._charsetCorner["tright"] + VT100.reset

			rtnExtra = ""
			if clearAll: rtnExtra = VT100.clearLine

			return rtnExtra + VT100.pos(self._pos, (centerOffset, 0)) + left + middle + right



		def buildMid() -> str:
			segmentsFull = segments
			segmentsEmpty = self._length - segmentsFull

			vert = VT100.color(self._color("vert")) + self._char("vert") + VT100.reset
			middle = VT100.color(self._color("full")) + self._char("full") * segmentsFull + VT100.reset + VT100.color(self._color("empty")) + self._char("empty") * segmentsEmpty + VT100.reset

			# ---------- Build the content outside the bar ----------
			extra = parseFormat("outside")
			extraFormatted = VT100.clearRight + VT100.color(self._colorsetText["outside"]) + extra + VT100.reset


			# ---------- Build the content inside the bar ----------
			info = parseFormat("inside")
			infoFormatted = VT100.color(self._colorsetText["inside"])

			if self.percentage < 50:
				if self._charset["empty"] == "█":
					infoFormatted += VT100.invert
				infoFormatted += VT100.color(self._color("empty"))
			else:
				if self._charset["full"] == "█":
					infoFormatted += VT100.invert
				infoFormatted += VT100.color(self._color("full"))

			infoFormatted += parseFormat("inside") + VT100.reset
			# ---------- //////////////////////////////// ----------

			rtnExtra = ""
			if clearAll: rtnExtra = VT100.clearLine

			return (
				rtnExtra + VT100.pos(self._pos, (centerOffset, 1)) + vert + " " + middle + " " + vert + " " + extraFormatted +
				VT100.moveHoriz(centerOffset - len(info) / 2 - 2 - len(extra)) + infoFormatted
			)


		def buildBottom() -> str:
			left = VT100.color(self._colorsetCorner["bleft"]) + self._charsetCorner["bleft"] + VT100.reset
			middle = VT100.color(self._color("horiz")) + self._char("horiz") * (self._length + 2) + VT100.reset
			right = VT100.color(self._colorsetCorner["bright"]) + self._charsetCorner["bright"] + VT100.reset

			rtnExtra = ""
			if clearAll: rtnExtra = VT100.clearLine

			return rtnExtra + VT100.pos(self._pos, (centerOffset, 2)) + left + middle + right



		# Draw the bar
		print(
			VT100.cursorSave + buildTop(),
			buildMid(),
			buildBottom(),

			sep="\n",
			end="\n"
		)

		print(VT100.cursorLoad, end="")

		self._drawtimes += 1
		self._requiresClear = False























if __name__ == "__main__":
	from time import sleep

	mybar = PBar(
		range=(0, 25),
		text="Loading...",
		charset="normal",
		length=50,
		position=("center", "center")
	)

	print("BEFORE")

	while mybar.percentage < 100:
		sleep(0.1)
		mybar.colorset = {
			"full":		(0, mybar.percentage * 2, 0),
			"empty":	(255 - mybar.percentage * 2, 0, 0)
		}
		mybar.step()
	else:
		mybar.text = "Done!"
		mybar.colorset |= {
			"text": {"outside":		(0, 255, 0)}
		}
		mybar.step()

		sleep(1)
		mybar.clear()

	print("AFTER")