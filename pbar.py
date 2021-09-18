"""
PBar module for displaying custom progress bars for Python 3.9+

GitHub Repository:		https://github.com/DarviL82/PBar
"""

__all__ = ("PBar", "VT100", "ColorSet", "CharSet", "FormatSet")
__author__ = "David Losantos (DarviL)"
__version__ = "0.10.1"

from typing import Any, Optional, SupportsInt, TypeVar, Union, cast, Sequence
from os import get_terminal_size as _get_terminal_size, system as _runsys


_runsys("")		# We need to do this, otherwise Windows won't display special VT100 sequences


_DEFAULT_RANGE = (0, 1)
_DEFAULT_POS = ("center", "center")
_DEFAULT_SIZE = (20, 1)
_IGNORE_CHARS = "\x1b\n\r\b\a\f\v"


Color = Optional[Union[tuple[int, int, int], str]]
ColorSetEntry = dict[str, Color]
CharSetEntry = dict[str, str]
FormatSetEntry = dict[str, str]



Num = TypeVar("Num", int, float)

def _capValue(value: Num, max: Optional[Num] = None, min: Optional[Num] = None) -> Num:
	"""Clamp a value to a minimum and/or maximum value."""

	if max is not None and value > max:
		return max
	elif min is not None and value < min:
		return min
	else:
		return value




def _formatError(string: str, start: int, end: int) -> str:
	"""Returns a colored string across the character indices specified."""

	return (
		string[:start] +
		VT100.UNDERLINE + VT100.color((255, 0, 0)) + string[start:end] + VT100.RESET +
		string[end:]
	)




def _convertClrs(clr: Union[str, tuple, dict], type: str) -> Union[str, tuple, dict, None]:
	"""Convert color values to HEX and vice-versa
	@clr:	Color value to convert.
	@type:	Type of conversion to do ('RGB' or 'HEX')"""

	if isinstance(clr, dict):
		return {key: _convertClrs(clr[key], type) for key in clr.keys()}

	if type == "RGB":
		if not isinstance(clr, str) or not clr.startswith("#"):
			return clr

		clr = clr.lstrip("#")
		try:
			return tuple(int(clr[i:i+2], 16) for i in (0, 2, 4))
		except ValueError:
			return
	elif type == "HEX":
		if not isinstance(clr, (tuple, list)) or len(clr) != 3: return clr

		capped = tuple(_capValue(value, 255, 0) for value in clr)
		return f"#{capped[0]:X}{capped[1]:X}{capped[2]:X}"








class VT100:
	"""Class for using VT100 sequences a bit easier"""

	@staticmethod
	def pos(pos: Optional[tuple[int, int]], offset: tuple[int, int] = (0, 0)):
		"""Position of the cursor on the terminal.
		@pos: This tuple can contain either ints, or strings with the value `center` to specify the center of the terminal.
		@offset: Offset applied to `pos`. (Can be negative)
		"""

		if not isinstance(pos, (tuple, list)):
			raise TypeError("Sequence must have 3 items")
		elif len(pos) != 2:
			raise TypeError(f"Type of position ({type(pos)}) is not Sequence")

		position = list((pos[0], pos[1]))
		for index, value in enumerate(position):
			if not isinstance(value, int):
				raise TypeError(f"Invalid type {type(value)} for position value")

			position[index] += int(offset[index])

		return f"\x1b[{position[1]};{position[0]}f"


	@staticmethod
	def color(rgb: Optional[tuple[int, int, int]], bg: bool = False):
		"""Color of the cursor.
		@rgb:	Tuple with three values from 0 to 255. (RED GREEN BLUE)
		@bg:	This color will be displayed on the background"""

		if not isinstance(rgb, (tuple, list)):
			return VT100.RESET
		elif len(rgb) != 3:
			raise ValueError("Sequence must have 3 items")

		rgb = [_capValue(value, 255, 0) for value in rgb]

		type = 48 if bg else 38
		return f"\x1b[{type};2;{rgb[0]};{rgb[1]};{rgb[2]}m"



	@staticmethod
	def moveHoriz(dist: SupportsInt):
		"""Move the cursor horizontally `dist` characters (supports negative numbers)."""
		dist = int(dist)
		if dist < 0:
			return f"\x1b[{abs(dist)}D"
		else:
			return f"\x1b[{dist}C"


	@staticmethod
	def moveVert(dist: SupportsInt):
		"""Move the cursor vertically `dist` lines (supports negative numbers)."""
		dist = int(dist)
		if dist < 0:
			return f"\x1b[{abs(dist)}A"
		else:
			return f"\x1b[{dist}B"


	# simple sequences that dont require parsing
	RESET =			"\x1b[0m"
	INVERT =		"\x1b[7m"
	NO_INVERT =		"\x1b[27m"
	BOLD =			"\x1b[1m"
	NO_BOLD =		"\x1b[21m"
	ITALIC =		"\x1b[3m"
	NO_ITALIC =		"\x1b[23m"
	BLINK =			"\x1b[5m"
	NO_BLINK =		"\x1b[25m"
	CLEAR_LINE =	"\x1b[2K"
	CLEAR_RIGHT =	"\x1b[0K"
	CLEAR_LEFT =	"\x1b[1K"
	CLEAR_DOWN =	"\x1b[0J"
	CLEAR_ALL =		"\x1b[2J"
	CURSOR_SHOW =	"\x1b[?25h"
	CURSOR_HIDE =	"\x1b[?25l"
	CURSOR_SAVE =	"\x1b7"
	CURSOR_LOAD =	"\x1b8"
	BUFFER_NEW =	"\x1b[?1049h"
	BUFFER_OLD =	"\x1b[?1049l"
	UNDERLINE =		"\x1b[4m"
	NO_UNDERLINE =	"\x1b[24m"
	CURSOR_HOME =	"\x1b[H"








class UnknownSetKeyError(BaseException):
	"""A key supplied in a dictionary is unknown for the set class that will use it"""
	def __init__(self, key, setcls) -> None:
		msg = f"Unknown key {key!r} for {setcls.__class__.__name__!r}"
		clsKeys = "', '".join(setcls.EMPTY.keys())
		super().__init__(f"{msg}. Available valid keys: '{clsKeys}'.")




class _BaseSet:
	"""Base class for all the customizable sets for the bar (colorset, charset, formatset)"""

	def __init__(self, newSet: dict) -> None:
		if not newSet:
			newSet = self.DEFAULT
		elif not isinstance(newSet, dict):
			raise TypeError(f"newSet type ({type(newSet)}) is not dict")

		self._newset = self._populate(self.EMPTY | newSet)


	def keys(self):
		return self._newset.keys()


	def __getitem__(self, item) -> dict:
		return self._newset[item]


	def __or__(self, other):
		new = dict(self._newset)
		new.update(other)
		return new


	def __ior__(self, other):
		dict.update(self._newset, other)
		return self._newset


	def __repr__(self) -> str:
		return f"{self.__class__.__name__}({self._newset})"


	def _populate(self, currentSet: dict) -> dict:
		"""Return a new set with all the necessary keys for drawing the bar, making sure that no keys are missing."""

		newSet = {}
		for key, currentValue in currentSet.items():
			if key not in self.EMPTY.keys():
				raise UnknownSetKeyError(key, self)
			else:
				defaultSetValue = self.EMPTY[key]

			if not isinstance(currentValue, dict) and isinstance(defaultSetValue, dict):
				newSet[key] = {subkey: currentValue for subkey in defaultSetValue.keys()}
			elif isinstance(currentValue, dict):
				newSet[key] = defaultSetValue | currentValue
			else:
				newSet[key] = currentValue

		return newSet




class CharSet(_BaseSet):
	"""Container for the character sets."""

	EMPTY: CharSetEntry = {
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
	}

	DEFAULT: CharSetEntry = {
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
	}

	BASIC: CharSetEntry = {
		"empty":	".",
		"full":		"#",
		"vert":		"│"
	}

	SLIM: CharSetEntry = {
		"empty":	"░",
		"full":		"█"
	}

	CIRCLES: CharSetEntry = {
		"empty":	"○",
		"full":		"●"
	}

	BASIC2: CharSetEntry = {
		"empty":	".",
		"full":		"#",
		"vert":		"|",
		"horiz":	"-",
		"corner":	"+"
	}

	FULL: CharSetEntry = {
		"empty":	"█",
		"full":		"█"
	}

	DIFF: CharSetEntry = {
		"full":		"+",
		"empty":	"-"
	}

	DOTS: CharSetEntry = {
		"full":		"⣿",
		"empty":	"⢸"
	}

	TRIANGLES: CharSetEntry = {
		"full":		"▶",
		"empty":	"◁"
	}

	BRICKS: CharSetEntry = {
		"full":		"█",
		"empty":	"▞",
		"vert":		"┋"
	}

	ROUNDED: CharSetEntry = {
		"full":		"█",
		"empty":	"▁",
		"horiz":	"─",
		"vert":		"│",
		"corner": {
			"tright":	"╮",
			"tleft":	"╭",
			"bleft":	"╰",
			"bright":	"╯"
		},
	}

	TILTED: CharSetEntry = {
		"full":		"🙽",
		"empty":	"🙽"
	}


	def __init__(self, newSet: CharSetEntry) -> None:
		super().__init__(newSet)
		self._newset = CharSet._strip(self._newset)


	@staticmethod
	def _strip(setdict: dict):
		"""Converts empty values to spaces, and makes sure there's only one character"""
		if not setdict:
			return

		IGNORE_CHARS = "\x1b\n\r\b\a\f\v\t"

		newset = {}
		for key, value in setdict.items():
			if isinstance(value, dict):
				value = CharSet._strip(value)
			elif value in IGNORE_CHARS or len(value) < 1:
				value = " "
			elif len(value) > 1:
				value = value[0]
			newset[key] = value

		return newset




class ColorSet(_BaseSet):
	"""Container for the color sets."""

	EMPTY: ColorSetEntry = {
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
			"right":	None,
			"left":		None,
			"title":	None,
			"subtitle":	None
		}
	}

	DEFAULT = EMPTY

	GREEN_RED: ColorSetEntry = {
		"empty":	(255, 0, 0),
		"full":		(0, 255, 0)
	}

	DARVIL: ColorSetEntry = {
		"empty":	(0, 103, 194),
		"full":		(15, 219, 162),
		"vert":		(247, 111, 152),
		"horiz":	(247, 111, 152),
		"corner":	(247, 111, 152),
		"text": {
			"outside":	(247, 111, 152)
		}
	}

	ERROR: ColorSetEntry = {
		"empty":	(100, 0, 0),
		"full":		(255, 0, 0),
		"vert":		(255, 100, 100),
		"horiz":	(255, 100, 100),
		"corner":	(255, 100, 100),
		"text": {
			"outside":	(255, 100, 100)
		}
	}

	YELLOW: ColorSetEntry = {
		'full':		(232, 205, 0),
		'empty':	(167, 114, 39),
		'horiz':	(218, 183, 123),
		'vert':		(218, 183, 123),
		'corner':	(218, 183, 123),
		'text':		(218, 183, 123)
	}

	FLAG_ES: ColorSetEntry = {
		'corner':	(199, 3, 24),
		'horiz':	(199, 3, 24),
		'vert':		(255, 197, 0),
		'full':		(255, 197, 0),
		'empty':	(154, 118, 0),
		'text':		(255, 197, 0)
	}


	def __init__(self, newSet: ColorSetEntry) -> None:
		super().__init__(_convertClrs(newSet, "RGB"))	# Convert all hex values to rgb tuples




class FormatSet(_BaseSet):
	"""Container for the formatting sets."""

	EMPTY: FormatSetEntry = {		# ! please remember to change this back
		"inside":	"INSIDE",
		"right":	"RIGHT",
		"left":		"LEFT",
		"title":	"TITLE",
		"subtitle":	"SUBTITLE"
	}

	DEFAULT: FormatSetEntry = {
		"inside":	"<percentage>%",
		"right":	"<text>"
	}

	ALL_OUT: FormatSetEntry = {
		"right":	"<percentage>%, <range1>/<range2>, <text>"
	}

	ALL_IN: FormatSetEntry = {
		"inside":	"<percentage>%, <range1>/<range2>, <text>"
	}

	MIXED: FormatSetEntry = {
		"inside":	"<percentage>%",
		"right":	"<text>: (<range1>/<range2>)"
	}


	def __init__(self, newSet: FormatSetEntry) -> None:
		super().__init__(newSet)


	@staticmethod
	def _rmPoisonChars(text: str) -> str:
		"""Remove "dangerous" characters and convert some"""
		endStr = ""
		for char in str(text):
			if char not in _IGNORE_CHARS:	# Ignore this characters entirely
				if char == "\t":
					char = "    "	# Convert tabs to spaces because otherwise we can't tell the length of the string properly
				endStr += char
		return endStr


	@staticmethod
	def _parseFormat(cls: "PBar", string: str) -> str:
		"""Parse a string that may contain formatting keys"""
		if string is None: return ""

		foundOpen = False		# Did we find a '<'?
		foundBackslash = False	# Did we find a '\'?
		tempStr = ""			# String that contains the current value inside < >
		endStr = ""				# Final string that will be returned
		text = FormatSet._rmPoisonChars(string)

		# Convert the keys to a final string
		for index, char in enumerate(text):
			if foundBackslash:
				# Also skip the character next to the slash
				foundBackslash = False
				endStr += char
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
						endStr += str(cls.percentage)
					elif tempStr == "range1":
						endStr += str(cls._range[0])
					elif tempStr == "range2":
						endStr += str(cls._range[1])

					elif tempStr == "text":
						if cls._text:
							endStr += FormatSet._rmPoisonChars(cls._text)
					else:
						raise RuntimeError(f"Unknown formatting key ('{_formatError(text, index - len(tempStr), index)}')")

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

			if index + 1 == len(text):
				# This is the last character, so add the temp str to the final string
				endStr += tempStr

		return endStr







def _genShape(position: tuple[int, int], size: tuple[int, int], charset: CharSet, colorset: ColorSet) -> str:
	"""Generates a basic rectangular shape that uses a charset and a colorset"""
	width, height = _capValue(size[0], min=3) + 2, _capValue(size[1], min=0) + 1

	charVert = VT100.color(colorset["vert"]) + charset["vert"]
	charHoriz = VT100.color(colorset["horiz"]) + charset["horiz"]
	charCorner = (
		VT100.color(colorset["corner"]["tleft"]) + charset["corner"]["tleft"],
		VT100.color(colorset["corner"]["tright"]) + charset["corner"]["tright"],
		VT100.color(colorset["corner"]["bleft"]) + charset["corner"]["bleft"],
		VT100.color(colorset["corner"]["bright"]) + charset["corner"]["bright"]
	)

	endStr: str = (
		VT100.pos((position))
		+ charCorner[0]
		+ charHoriz*width
		+ charCorner[1]
	)

	for row in range(1, height):
		endStr += (
			VT100.pos((position), (0, row))
			+ charVert
			+ VT100.moveHoriz(width)
			+ charVert
		)

	endStr += (
		VT100.pos((position), (0, height))
		+ charCorner[2]
		+ charHoriz*width
		+ charCorner[3]
	)

	return endStr






def _genBarContent(position: tuple[int, int], size: tuple[int, int], charset: CharSet, colorset: ColorSet,
				   rangeValue: tuple[int, int]) -> str:
	"""Generates the progress shape with a colorset and a charset specified"""
	width, height = _capValue(size[0], min=3), _capValue(size[1], min=0) + 1
	SEGMENTS_FULL = int((_capValue(rangeValue[0], rangeValue[1], 0) / _capValue(rangeValue[1], min=1))*width)	# Number of character for the full part of the bar
	SEGMENTS_EMPTY = width - SEGMENTS_FULL

	charFull = VT100.color(colorset["full"]) + charset["full"]
	charEmpty = VT100.color(colorset["empty"]) + charset["empty"]

	return "".join((
			VT100.pos((position), (0, row))
			+ charFull*SEGMENTS_FULL
			+ charEmpty*SEGMENTS_EMPTY
		) for row in range(1, height))





def _genBarText(position: tuple[int, int], size: tuple[int, int], colorset: ColorSet, formatset: FormatSet) -> str:
	"""Generates all text for the bar"""
	width, height = _capValue(size[0], min=3), _capValue(size[1], min=0) + 1
	textTitle = formatset["title"]

	return ""









class PBar():
	"""
	# PBar - Progress bar

	PBar is an object for managing progress bars in python.

	---

	## Initialization

	>>> mybar = PBar()

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
	- mybar.length
	- mybar.position
	- mybar.charset
	- mybar.colorset
	- mybar.formatset
	- mybar.enabled
	- mybar.config
	"""
	def __init__(self,
			range: tuple[int, int] = None,
			text: str = "",
			size: tuple[int, int] = None,
			position: tuple[Union[int, str], Union[int, str]] = None,
			charset: Optional[CharSetEntry] = None,
			colorset: Optional[ColorSetEntry] = None,
			formatset: Optional[FormatSetEntry] = None
		) -> None:
		"""
		### Detailed descriptions:
		@range: This tuple will specify the range of two values to display in the progress bar. Default value is `(0, 1)`.

		---

		@text: String to show in the progress bar.

		---

		@size: Tuple that specifies the width and height of the bar. Default value is `(20, 1)`.

		---

		@position: Tuple containing the position (X and Y axles of the center) of the progress bar on the terminal.
		If a value is `center`, the bar will be positioned at the center of the terminal on that axis. Default value is `("center", "center")`

		---


		@charset: Set of characters to use when drawing the progress bar.

		To use one of the included sets, use any of the constant values in `pbar.CharSet`.

		Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom characters:
		- Custom character set dictionary:

				![image](https://user-images.githubusercontent.com/48654552/127887419-acee1b4f-de1b-4cc7-a1a6-1be75c7f97c9.png)

			Note: It is not needed to specify all the keys and values.

		---

		@colorset: Set of colors to use when drawing the progress bar.

		To use one of the included sets, use any of the constant values in `pbar.ColorSet`.

		Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom colors:
		- Custom color set dictionary:

				![image](https://user-images.githubusercontent.com/48654552/127904550-15001058-cbf2-4ebf-a543-8d6566e9ef36.png)

			Note: It is not needed to specify all the keys and values.

			Note: The colors can also be specified as HEX in a string.

		---

		@formatset: Formatting used when displaying the values inside and outside the bar.

		To use one of the included sets, use any of the constant values in `pbar.FormatSet`.

		Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom formatting:
		- Custom formatset dictionary:

				![image](https://user-images.githubusercontent.com/48654552/127889950-9b31d7eb-9a52-442b-be7f-8b9df23b15ae.png)

			Note: It is not needed to specify all the keys and values.

		- Available formatting keys:
			- `<percentage>`
			- `<range1>`
			- `<range2>`
			- `<text>`
		"""
		self._requiresClear = False
		self._enabled = True

		self._range = PBar._getRange(range)
		self._text = FormatSet._rmPoisonChars(text)
		self._formatset = FormatSet(formatset)
		self._size = PBar._getSize(size)
		self._charset = CharSet(charset)
		self._colorset = ColorSet(colorset)
		self._pos = self._getPos(position)

		self._oldValues = [self._pos, self._size]




	# --------- Properties / Methods the user should use. ----------

	def draw(self):
		"""Print the progress bar on screen"""
		self._draw()


	def step(self, steps: int = 1):
		"""Add `steps` to the first value in range, then draw the bar"""
		self.range = (self._range[0] + steps, self._range[1])
		self._draw()


	def clear(self):
		"""Clear the progress bar"""
		self._clear([self._pos, self._size])


	@property
	def percentage(self):
		"""Percentage of the progress of the current range"""
		return int((self._range[0]*100) / self._range[1])


	@property
	def text(self):
		"""Text to be displayed on the bar"""
		return self._text
	@text.setter
	def text(self, text: str):
		self._text = FormatSet._rmPoisonChars(text)
		self._requiresClear = True


	@property
	def range(self) -> tuple[int, int]:
		"""Range for the bar progress"""
		return (self._range[0], self._range[1])
	@range.setter
	def range(self, range: tuple[int, int]):
		self._range = PBar._getRange(range)


	@property
	def charset(self) -> CharSet:
		"""Set of characters for the bar"""
		return self._charset
	@charset.setter
	def charset(self, charset: CharSetEntry):
		self._charset = CharSet(charset)


	@property
	def colorset(self) -> ColorSet:
		"""Set of colors for the bar"""
		return self._colorset
	@colorset.setter
	def colorset(self, colorset: ColorSetEntry):
		self._colorset = ColorSet(colorset)


	@property
	def formatset(self) -> FormatSet:
		"""Formatting used for the bar"""
		return self._formatset
	@formatset.setter
	def formatset(self, formatset: FormatSetEntry):
		self._formatset = FormatSet(formatset)


	@property
	def size(self):
		"""Size of the progress bar"""
		return self._size
	@size.setter
	def size(self, size: tuple[int, int]):
		newsize = PBar._getSize(size)
		if newsize != self._size:
			self._requiresClear = True		# since the bar is gonna be smaller, we need to redraw it.
		self._oldValues[1] = self._size
		self._size = newsize


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
			self._pos = newpos


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
			"range":		self._range,
			"text":			self._text,
			"size":			self._size,
			"position":		self._pos,
			"charset":		dict(self._charset),						# \
			"colorset":		_convertClrs(dict(self._colorset), "HEX"),	# |- Cast to dict when saving to make it easier to parse in a future.
			"formatset":	dict(self._formatset),						# /
			"enabled":		self._enabled
		}
	@config.setter
	def config(self, config: dict[str, Any]):
		if isinstance(config, dict):
			for key in {"range", "text", "size", "position", "charset", "colorset", "formatset", "enabled"}:
				# Iterate through every key in the dict and populate the config of the class with its values
				if key in config: setattr(self, key, config[key])


	# --------- ///////////////////////////////////////// ----------




	def _getPos(self, position: Optional[tuple[int, int]]) -> tuple[int, int]:
		"""Get and process new position requested"""
		if not position:
			position = _DEFAULT_POS
		elif not isinstance(position, (tuple, list)):
			raise TypeError(f"Type of position ({type(position)}) is not Sequence")
		elif len(position) != 2:
			raise ValueError("Sequence must have two items")

		newpos = []
		TERM_SIZE: tuple[int, int] = _get_terminal_size()

		for index, value in enumerate(position):
			if value == "center":
				value = int(TERM_SIZE[index] / 2)
			elif not isinstance(value, (int, float)):
				raise TypeError(f"Type of value {value} ({type(value)}) is not int/float")

			if index == 0:
				value = _capValue(value, TERM_SIZE[0] - self._size[0] / 2 + 2, self._size[0] / 2 + 2)
			else:
				value = _capValue(value, TERM_SIZE[1] - 3, 1)

			newpos.append(int(value))
		return tuple(newpos)




	@staticmethod
	def _getSize(size: Optional[tuple[int, int]]) -> tuple[int, int]:
		"""Get and process new length requested"""
		if size is None:
			return _DEFAULT_SIZE
		elif not isinstance(size, (tuple, list)):
			raise TypeError(f"Type of size ({type(size)}) is not Sequence")
		elif len(size) != 2:
			raise ValueError("Sequence must have two items")

		# tSize: tuple[int, int] = _get_terminal_size()
		# return _capValue(size, tSize[0] - 5, 5)
		return size




	@staticmethod
	def _getRange(range: tuple[int, int]) -> tuple[int, int]:
		"""Return a capped range"""
		if not range:
			return _DEFAULT_RANGE
		elif not isinstance(range, (tuple, list)):
			raise TypeError(f"Type of value {range!r} ({type(range)}) is not a tuple/list")

		for item in range:
			if not isinstance(item, int):
				raise TypeError(f"Type of value {item!r} ({type(item)}) in range is not int")

		if len(range) != 2:
			raise ValueError("Length of sequence is not 2")

		value1 = _capValue(range[0], range[1], 0)
		value2 = _capValue(range[1], min=1)
		return (value1, value2)




	def _clear(self, values: tuple[tuple[int, int], int]):		# TODO: Rework
		"""Clears the progress bar at the position and length specified. `values[0]` is the position, and `values[1]` is the length"""

		if not self._enabled: return

		pos = values[0]
		length = values[1]
		centerOffset = int((length + 2) / -2)		# Number of characters from the end of the bar to the center

		barShape = _genShape((pos[0] + centerOffset, pos[1]), (length, 1), CharSet.EMPTY, ColorSet.EMPTY)
		barContent = _genBarContent(
			(self._pos[0] + centerOffset + 2, self._pos[1]),
			self._size,
			CharSet.EMPTY,
			ColorSet.EMPTY,
			self._formatset,
			self._range
		)

		print(VT100.CURSOR_SAVE, barShape, barContent, VT100.CURSOR_LOAD, sep="", end="", flush=True)




	def _genBar(self) -> str:
		POSITION = (self._pos[0] + int(self._size[0] / -2),
					self._pos[1] + int(self._size[1] / -2))

		# Build all the parts of the progress bar
		barShape = _genShape(
			POSITION,
			self._size, self._charset, self._colorset
		)

		barContent = _genBarContent(
			POSITION,
			self._size, self._charset, self._colorset, self._range
		)

		barText = _genBarText(
			POSITION,
			self._size, self._colorset, self._formatset
		)


		return (
			VT100.CURSOR_SAVE + VT100.CURSOR_HIDE
			+ barShape
			+ barContent
			+ VT100.CURSOR_LOAD + VT100.CURSOR_SHOW
		)




	def _draw(self):
		"""Draw the progress bar"""

		if not self._enabled: return

		if self._requiresClear:
			# Clear the bar at the old position and length
			self._clear(self._oldValues)
			self._oldValues = [self._pos, self._size]


		# Draw the bar
		print(self._genBar(), flush=True, end="")

		self._requiresClear = False
