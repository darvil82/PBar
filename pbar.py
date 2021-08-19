"""
PBar module for displaying custom progress bars for Python 3.9+

GitHub Repository:		https://github.com/DarviL82/PBar
"""

from typing import Any, Optional, SupportsInt, Type, TypeVar, Union, cast, Sequence
from os import get_terminal_size as _get_terminal_size, system as _runsys

__all__ = ["PBar"]
__author__ = "David Losantos (DarviL)"
__version__ = "0.6.3"


_runsys("")		# We need to do this, otherwise Windows won't display special VT100 sequences


_DEFAULT_RANGE = (0, 1)
_DEFAULT_POS = ("center", "center")
_DEFAULT_LEN = 20

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
		"inside":	"<percentage>%",
		"outside":	"<text>"
	},

	"all-out": {
		"outside":	"<percentage>%, <range1>/<range2>, <text>"
	},

	"all-in": {
		"inside":	"<percentage>%, <range1>/<range2>, <text>"
	},

	"mixed": {
		"inside":	"<percentage>%",
		"outside":	"<text>: (<range1>/<range2>)"
	}
}




Num = TypeVar("Num", int, float)

def _capValue(value: Num, max: Optional[Num] = None, min: Optional[Num] = None) -> Num:
    """Clamp a value to a minimun and/or maximun value."""

    if max != None and value > max:
        return max
    elif min != None and value < min:
        return min
    else:
        return value








class VT100():
	"""Class for using VT100 sequences a bit easier"""

	@staticmethod
	def pos(pos: Optional[Sequence[Any]], offset: tuple[int, int] = (0, 0)):
		"""Position of the cursor on the terminal.
		@pos: This tuple can contain either ints, or strings with the value `center` to specify the center of the terminal.
		@offset: Offset applied to `pos`. (Can be negative)
		"""
		if pos and len(pos) == 2:
			position = list(pos)
			for index, value in enumerate(position):
				if isinstance(value, int):
					value = int(value)
					position[index] += offset[index]
				else:
					raise TypeError(f"Invalid type {type(value)} for position value")

			return f"\x1b[{position[1]};{position[0]}f"
		else:
			return ""

	@staticmethod
	def color(rgb: Optional[Sequence[int]], bg: bool = False):
		"""Color of the cursor.
		@rgb:	Tuple with three values from 0 to 255. (RED GREEN BLUE)
		@bg:	This color will be displayed on the background"""
		if rgb and len(rgb) == 3:
			rgb = [_capValue(value, 255, 0) for value in rgb]
			if bg:
				return f"\x1b[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m"
			else:
				return f"\x1b[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m"

		else:
			return ""

	@staticmethod
	def moveHoriz(pos: SupportsInt):
		"""Move the cursor horizontally `pos` characters (supports negative numbers)."""
		pos = int(pos)
		if pos < 0:
			return f"\x1b[{abs(pos)}D"
		else:
			return f"\x1b[{pos}C"

	@staticmethod
	def moveVert(pos: SupportsInt):
		"""Move the cursor vertically `pos` lines (supports negative numbers)."""
		pos = int(pos)
		if pos < 0:
			return f"\x1b[{abs(pos)}A"
		else:
			return f"\x1b[{pos}B"

	# simple sequences that dont require parsing
	reset =			"\x1b[0m"
	invert =		"\x1b[7m"
	noInvert =		"\x1b[27m"
	clearLine =		"\x1b[2K"
	clearRight =	"\x1b[0K"
	clearLeft =		"\x1b[1K"
	clearDown =		"\x1b[0J"
	cursorShow =	"\x1b[?25h"
	cursorHide =	"\x1b[?25l"
	cursorSave =	"\x1b7"
	cursorLoad =	"\x1b8"
	bufferNew =		"\x1b[?1049h"
	bufferOld =		"\x1b[?1049l"
	underline =		"\x1b[4m"
	noUnderline =	"\x1b[24m"








def _getCharset(charset: Any) -> CharSet:
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




def _getColorset(colorset: Any) -> ColorSet:
		"""Return a full valid color set"""
		if colorset:
			if isinstance(colorset, str):
				colorset = _DEFAULT_COLORSETS.get(colorset, _DEFAULT_COLORSETS["empty"])
			elif isinstance(colorset, dict):
				colorset = _convertClrs(colorset, "RGB")

				if "corner" in colorset.keys():
					if isinstance(colorset["corner"], (tuple, list)):
						colorset["corner"] = {
							"tleft": 	colorset["corner"],
							"tright": 	colorset["corner"],
							"bleft": 	colorset["corner"],
							"bright": 	colorset["corner"]
						}
					elif isinstance(colorset["corner"], dict):
						colorset["corner"] = _DEFAULT_COLORSETS["empty"]["corner"] | colorset["corner"]
					else:
						raise ValueError(f"Invalid type ({type(colorset['corner'])}) for colorset")

				if "text" in colorset.keys():
					if isinstance(colorset["text"], (tuple, list)):
						colorset["text"] = {
							"inside":	colorset["text"],
							"outside":	colorset["text"]
						}
					elif isinstance(colorset["text"], dict):
						colorset["text"] = _DEFAULT_COLORSETS["empty"]["text"] | colorset["text"]
					else:
						raise ValueError(f"Invalid type ({type(colorset['text'])}) for colorset")

			else:
				raise ValueError(f"Invalid type ({type(colorset)}) for colorset")

			set: ColorSet = _DEFAULT_COLORSETS["empty"] | colorset
		else:
			set = _DEFAULT_COLORSETS["empty"]

		return set




def _getFormat(formatset: Any) -> FormatSet:
		"""Return a full valid formatting set"""
		if formatset:
			if isinstance(formatset, str):
				formatset = _DEFAULT_FORMATTING.get(formatset, _DEFAULT_FORMATTING["empty"])
			elif isinstance(formatset, dict):
				pass
			else:
				raise ValueError(f"Invalid type ({type(formatset)}) for formatset")
			set: FormatSet = _DEFAULT_FORMATTING["empty"] | formatset
		else:
			set = _DEFAULT_FORMATTING["default"]

		return set




def _getRange(range: tuple[int, int]) -> tuple[int, int]:
	if range:
		if isinstance(range, (tuple, list)):
			for item in range:
				if not isinstance(item, int):
					raise TypeError(f"Type of value '{item}' ({type(item)}) in range is not int")

			if len(range) == 2:
				value1 = _capValue(range[0], range[1], 0)
				value2 = _capValue(range[1], min=1)
				return (value1, value2)
			else:
				raise ValueError("Length of sequence is not 2")
		else:
			raise TypeError(f"Type of value '{range}' ({type(range)}) is not a tuple/list")
	else:
		return _DEFAULT_RANGE




def _convertClrs(clr: Union[str, tuple, dict], type: str) -> Union[str, tuple, dict]:
	"""Convert color values to HEX and vice-versa
	@clr:	Color value to convert.
	@type:	Type of conversion to do ('RGB' or 'HEX')"""

	if isinstance(clr, dict):
		endDict = {}
		for key in clr.keys():
			endDict[key] = _convertClrs(clr[key], type)
		return endDict

	if type == "RGB":
		if isinstance(clr, str) and clr.startswith("#"):
			clr = clr.lstrip("#")
			try:
				return tuple(int(clr[i:i+2], 16) for i in (0, 2, 4))
			except ValueError:
				return
		else:
			return clr

	elif type == "HEX":
		if isinstance(clr, (tuple, list)) and len(clr) == 3:
			capped = tuple(_capValue(value, 255, 0) for value in clr)
			return f"#{capped[0]:02x}{capped[1]:02x}{capped[2]:02x}"
		else:
			return clr








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
	- mybar.enabled
	- mybar.config
	"""
	def __init__(self,
			range: tuple[int, int] = None,
			text: str = "",
			length: int = None,
			position: Union[str, tuple[int, int]] = None,
			charset: Union[None, str, dict[str, str]] = None,
			colorset: Union[None, str, dict[str, tuple[int, int, int]]] = None,
			format: Union[None, str, dict[str, str]] = None,
			inherit: "PBar" = None
		) -> None:
		"""
		### Detailed descriptions:
		@range: This tuple will specify the range of two values to display in the progress bar. Default value is `(0, 1)`.

		---

		@text: String to show in the progress bar.

		---

		@length: Intenger that specifies how long the bar will be. Default value is `20`.

		---

		@charset: Set of characters to use when drawing the progress bar.
		This value can either be a string which will specify a default character set to use, or a dictionary, which should specify the custom characters:
		- Available default character sets: `empty`, `normal`, `basic`, `basic2`, `slim`, `circles` and `full`.
		- Custom character set dictionary:

				![image](https://user-images.githubusercontent.com/48654552/127887419-acee1b4f-de1b-4cc7-a1a6-1be75c7f97c9.png)

			Note: It is not needed to specify all the keys and values.

		---

		@colorset: Set of colors to use when drawing the progress bar.
		This value can either be a string which will specify a default color set to use, or a dictionary, which should specify the custom colors:
		- Available default color sets: `empty`, `green-red` and `darvil`.
		- Custom color set dictionary:

				![image](https://user-images.githubusercontent.com/48654552/127904550-15001058-cbf2-4ebf-a543-8d6566e9ef36.png)

			Note: It is not needed to specify all the keys and values.

			Note: The colors can also be specified as HEX in a string.

		---

		@position: Tuple containing the position (X and Y axles of the center) of the progress bar on the terminal.
		If a value is `center`, the bar will be positioned at the center of the terminal on that axis. Default value is `("center", "center")`

		---

		@format: Formatting used when displaying the values inside and outside the bar.
		This value can either be a string which will specify a default formatting set to use, or a dictionary, which should specify the custom formats:
		- Available default formatting sets: `empty`, `default`, `all-out`, `all-in` and `mixed`.
		- Custom color set dictionary:

				![image](https://user-images.githubusercontent.com/48654552/127889950-9b31d7eb-9a52-442b-be7f-8b9df23b15ae.png)

			Note: It is not needed to specify all the keys and values.

		- Available formatting keys:
			- `<percentage>`
			- `<range1>`
			- `<range2>`
			- `<text>`

		---

		@inherit: Inherits all properties from the PBar object specified.
		"""
		self._requiresClear = False
		self._enabled = True

		self._range = list(_getRange(range))
		self._text = str(text)
		self._format = _getFormat(format)
		self._length = self._getLength(length)
		self._charset = _getCharset(charset)
		self._colorset = _getColorset(colorset)
		self._pos = self._getPos(position)

		self._oldValues = [self._pos, self._length]

		if inherit:
			if isinstance(inherit, PBar):
				self.config = inherit.config	# Get config from the object to inherit from, and apply it to ours
				if range:		self.range = range
				if text:		self.text = text
				if format:		self.format = format
				if length:		self.length = length
				if charset:		self.charset = charset
				if colorset:	self.colorset = colorset
				if position:	self.position = position
			else:
				raise TypeError(f"Type {type(inherit)} is not a PBar object")




	# --------- Properties / Methods the user should use. ----------

	def draw(self):
		"""Print the progress bar on screen"""
		self._draw()


	def step(self, steps: int = 1):
		"""Add `steps` to the first value in range, then draw the bar"""
		if not self._range[0] >= self._range[1]:
			self._range[0] += _capValue(steps, self._range[1] - self._range[0])
		self._draw()


	def clear(self):
		"""Clear the progress bar"""
		self._clear([self._pos, self._length])


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
		self._requiresClear = True


	@property
	def range(self) -> tuple[int, int]:
		"""Range for the bar progress"""
		return (self._range[0], self._range[1])
	@range.setter
	def range(self, range: tuple[int, int]):
		self._range = list(_getRange(range))


	@property
	def charset(self) -> CharSet:
		"""Set of characters for the bar"""
		return self._charset
	@charset.setter
	def charset(self, charset: Any):
		self._charset = _getCharset(charset)


	@property
	def colorset(self) -> ColorSet:
		"""Set of colors for the bar"""
		return self._colorset
	@colorset.setter
	def colorset(self, colorset: Any):
		self._colorset = _getColorset(colorset)


	@property
	def format(self):
		"""Formatting used for the bar"""
		return self._format
	@format.setter
	def format(self, format: Any):
		self._format = _getFormat(format)


	@property
	def length(self):
		"""Length of the progress bar"""
		return self._length
	@length.setter
	def length(self, length: int):
		newlen = self._getLength(length)
		if newlen < self._length:
			self._requiresClear = True		# since the bar is gonna be smaller, we need to redraw it.
		self._oldValues[1] = self._length
		self._length = newlen


	@property
	def position(self):
		"""Position of the progress bar"""
		return self._pos
	@position.setter
	def position(self, position: Union[None, str, tuple[int, int]]):
		newpos = self._getPos(position)
		# we dont need to update the position and ask to redraw if the value supplied is the same
		if newpos != self._pos:
			self._oldValues[0] = self._pos
			self._requiresClear = True		# Position has been changed, we need to clear the bar at the old position
			self._pos = self._getPos(position)


	@property
	def enabled(self):
		"""Will the bar draw on the next `draw` calls?"""
		return self._enabled
	@enabled.setter
	def enabled(self, state: bool):
		self._enabled = state


	@property
	def config(self) -> dict:
		"""All the values of the progress bar stored in a dict"""
		return {
			"range":	self._range,
			"text":		self._text,
			"length":	self._length,
			"position":	self._pos,
			"charset":	self._charset,
			"colorset":	_convertClrs(self._colorset, "HEX"),
			"format":	self._format,
			"enabled":	self._enabled
		}
	@config.setter
	def config(self, config: dict[str, Any]):
		if isinstance(config, dict):
			for key in {"range", "text", "length", "position", "charset", "colorset", "format", "enabled"}:
				# Move through every key in the dict and populate the config of the class with its values
				if key in config.keys(): setattr(self, key, config[key])


	# --------- ///////////////////////////////////////// ----------


	@property
	def _charsetCorner(self) -> dict[str, str]:
		"""type checker does not understand that CharSet["corner"] is always dict[str, str]"""
		return cast(dict[str, str], self._charset["corner"])

	def _char(self, key: str) -> str:
		assert(key != "corner")

		return cast(str, self._charset[key])


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





	def _getPos(self, position: Optional[Sequence[Any]]) -> tuple[int, int]:
		"""Get and process new position requested"""
		if not position: position = _DEFAULT_POS
		if len(position) == 2:
			newpos = []
			tSize: tuple[int, int] = _get_terminal_size()

			if isinstance(position, (tuple, list)):
				for index, value in enumerate(position):
					if isinstance(value, str) and value == "center":
						value = int(tSize[index] / 2)
					elif isinstance(value, (int, float)):
						if index == 0:
							value = _capValue(value, tSize[0] - self._length / 2 + 2, self._length / 2 + 2)
						else:
							value = _capValue(value, tSize[1] - 3, 1)

						value = int(value)
					else:
						raise Exception(f"Invalid position value type ({type(value)})")
					newpos.append(value)
				return newpos
		else:
			raise ValueError("Position must be a Sequence")




	def _getLength(self, length: int):
		"""Get and process new length requested"""
		if length != None:
			tSize: tuple[int, int] = _get_terminal_size()
			return _capValue(length, tSize[0] - 5, 5)
		else:
			return _DEFAULT_LEN




	def _parseFormat(self, string: str) -> str:
		"""Parse a string that may contain formatting keys"""
		foundOpen = False					# Did we find a '<'?
		foundBackslash = False				# Did we find a '\'?
		ignoreChars = "\x1b\n\r\b\a\f\v"	# Ignore this characters entirely
		tempStr = ""						# String that contains the current value inside < >
		endStr = ""							# Final string that will be returned

		for char in str(string):
			if char in ignoreChars:
				continue
			elif char == "\t":
				# Convert tabs to spaces because otherwise we can't
				# tell the length of the string properly
				endStr += "    "
				continue

			if foundBackslash:
				# Also skip the character next to the slash
				endStr += char
				foundBackslash = False
				continue
			elif char == "\\":
				# Found backslash, skip it
				foundBackslash = True
				continue

			elif foundOpen:
				# Found '<'. Now we add every char to tempStr until we find a '>'.
				if char == ">":
					# Found '>'. Now just add the formatting keys.
					if tempStr == "percentage":
						endStr += str(self.percentage)
					elif tempStr == "range1":
						endStr += str(self._range[0])
					elif tempStr == "range2":
						endStr += str(self._range[1])

					elif tempStr == "text":
						if self._text:
							if self._text is string:
								# We prevent a recursion exception here, because the user can use the format key '<text>' in the text parameter.
								endStr += ":)"
							else:
								endStr += self._parseFormat(self._text)	# We want to parse the text too, because it can also have keys or other characters
					else:
						raise ValueError(f"Unknown formatting key '{tempStr}'")

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




	def _clear(self, values: tuple[Sequence[int], int]):
		"""Clears the progress bars at the position and length specified"""

		if not self._enabled: return

		pos = values[0]
		length = values[1]
		centerOffset = int((length + 2) / -2)		# Number of characters from the end of the bar to the center

		top = VT100.pos(pos, (centerOffset, 0)) + " " * (length + 4)
		middle = VT100.pos(pos, (centerOffset, 1)) + " " * (length + 5 + len(self._parseFormat(self._format["outside"])))
		bottom = VT100.pos(pos, (centerOffset, 2)) + " " * (length + 4)

		print(VT100.cursorSave, top, middle, bottom, VT100.cursorLoad, sep="", end="")




	def _draw(self):
		"""Draw the progress bar"""

		if not self._enabled: return

		if self._requiresClear:
			# Clear the bar at the old position and length
			self._clear(self._oldValues)
			self._oldValues = [self._pos, self._length]

		centerOffset = int((self._length + 2) / -2)		# Number of characters from the end of the bar to the center
		segments = int((_capValue(self._range[0], self._range[1], 0) / _capValue(self._range[1], min=1)) * self._length)	# Number of character for the full part of the bar



		# Build all the parts of the progress bar
		def buildTop() -> str:
			left = VT100.color(self._colorsetCorner["tleft"]) + self._charsetCorner["tleft"] + VT100.reset
			middle = VT100.color(self._color("horiz")) + self._char("horiz") * (self._length + 2) + VT100.reset
			right = VT100.color(self._colorsetCorner["tleft"]) + self._charsetCorner["tright"] + VT100.reset

			return VT100.pos(self._pos, (centerOffset, 0)) + left + middle + right



		def buildMid() -> str:
			segmentsFull = segments
			segmentsEmpty = self._length - segmentsFull

			vert = VT100.color(self._color("vert")) + self._char("vert") + VT100.reset
			middle = VT100.color(self._color("full")) + self._char("full") * segmentsFull + VT100.reset + VT100.color(self._color("empty")) + self._char("empty") * segmentsEmpty + VT100.reset

			# ---------- Build the content outside the bar ----------
			extra = self._parseFormat(self._format["outside"])
			extraFormatted = VT100.clearRight + VT100.color(self._colorsetText["outside"]) + extra + VT100.reset


			# ---------- Build the content inside the bar ----------
			info = self._parseFormat(self._format["inside"])
			if len(info) > self._length - 3:
				# if the text is bigger than the size of the bar, we just cut it and add '...' at the end
				info = info[:self._length - 5] + "... "
			infoFormatted = VT100.color(self._colorsetText["inside"])


			if self.percentage < 50:
				if self._charset["empty"] == "█":	infoFormatted += VT100.invert
				if not self._colorsetText["inside"]:	infoFormatted += VT100.color(self._color("empty"))
			else:
				if self._charset["full"] == "█":	infoFormatted += VT100.invert
				if not self._colorsetText["inside"]:	infoFormatted += VT100.color(self._color("full"))


			infoFormatted += info + VT100.reset
			# ---------- //////////////////////////////// ----------

			return (
				VT100.pos(self._pos, (centerOffset, 1)) + vert + " " + middle + " " + vert + " " + extraFormatted +
				VT100.moveHoriz(centerOffset - len(info) / 2 - 2 - len(extra)) + infoFormatted
			)


		def buildBottom() -> str:
			left = VT100.color(self._colorsetCorner["bleft"]) + self._charsetCorner["bleft"] + VT100.reset
			middle = VT100.color(self._color("horiz")) + self._char("horiz") * (self._length + 2) + VT100.reset
			right = VT100.color(self._colorsetCorner["bright"]) + self._charsetCorner["bright"] + VT100.reset

			return VT100.pos(self._pos, (centerOffset, 2)) + left + middle + right



		# Draw the bar
		print(
			VT100.cursorSave,
			buildTop(),
			buildMid(),
			buildBottom(),
			VT100.cursorLoad,

			sep="",
			end=""
		)

		self._requiresClear = False