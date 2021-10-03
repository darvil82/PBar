"""
![logo_small](https://user-images.githubusercontent.com/48654552/134991429-1109ad1d-92fa-423f-8ce1-3b777471cb3d.png)

### PBar module for displaying custom progress bars for Python 3.9+

GitHub Repository:		https://github.com/DarviL82/PBar
"""

__all__ = ("PBar", "VT100", "ColorSet", "CharSet", "FormatSet", "taskWrapper")
__author__ = "David Losantos (DarviL)"
__version__ = "1.5.0-1"

from typing import Any, Optional, SupportsInt, TypeVar, Union, Callable
from os import get_terminal_size as _get_terminal_size, system as _runsys
from time import time as _time
from inspect import getsourcelines as _srclines


_runsys("")		# We need to do this, otherwise Windows won't display special VT100 sequences


_IGNORE_CHARS = "\x1b\n\r\b\a\f\v"

# Type Aliases
Color = Optional[Union[tuple[int, int, int], str, None]]
ColorSetEntry = dict[str, Union["ColorSetEntry", Color]]
CharSetEntry = dict[str, Union["CharSetEntry", str]]
FormatSetEntry = dict[str, Union["FormatSetEntry", str]]
Position = tuple[Union[str, int], Union[str, int]]



Num = TypeVar("Num", int, float)

def _capValue(value: Num, max: Optional[Num] = None, min: Optional[Num] = None) -> Num:
	"""Clamp a value to a minimum and/or maximum value."""

	if max is not None and value > max:
		return max
	elif min is not None and value < min:
		return min
	else:
		return value


def _getComment(string: str) -> Optional[str]:
	"""Returns the comment got from the string supplied. Returns None if there is no comment."""
	try:
		cnt = string.index("#") + 1
		return string[cnt:].strip()
	except ValueError:
		return


def _convertClrs(clr: ColorSetEntry, type: str) -> Union[str, tuple, dict, None]:
	"""Convert color values to HEX and vice-versa
	@clr:	Color value to convert.
	@type:	Type of conversion to do ('RGB' or 'HEX')"""

	if isinstance(clr, dict):
		return {key: _convertClrs(value, type) for key, value in clr.items()}

	if type == "RGB":
		if not isinstance(clr, str) or not clr.startswith("#"):
			return clr

		clrs = clr.lstrip("#")

		if len(clrs) == 3:
			clrs = "".join(c*2 for c in clrs)

		try:
			return tuple(int(clrs[i:i+2], 16) for i in (0, 2, 4))
		except ValueError:
			return clr
	elif type == "HEX":
		if not isinstance(clr, (tuple, list)) or len(clr) != 3: return clr

		capped = tuple(_capValue(value, 255, 0) for value in clr)
		return f"#{capped[0]:x}{capped[1]:x}{capped[2]:x}"


def _chkSeqOfLen(obj: object, length: int):
	"""Check if an object is a Sequence and has the length specified. If not, raises exceptions."""
	if not isinstance(obj, (tuple, list)):
		raise TypeError(f"Value {obj!r} ({type(obj)}) is not Sequence")
	elif len(obj) != length:
		raise ValueError(f"Sequence {obj} must have {length} items")
	return True




class VT100:
	"""Class for using VT100 sequences a bit easier"""

	@staticmethod
	def pos(pos: Optional[tuple[SupportsInt, SupportsInt]], offset: tuple[SupportsInt, SupportsInt] = (0, 0)):
		"""Position of the cursor on the terminal.
		@pos: This tuple can contain either ints, or strings with the value `center` to specify the center of the terminal.
		@offset: Offset applied to `pos`. (Can be negative)
		"""
		_chkSeqOfLen(pos, 2)

		position = (int(pos[0]) + int(offset[0]),
					int(pos[1] + int(offset[1])))

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

		crgb = [_capValue(value, 255, 0) for value in rgb]

		type = 48 if bg else 38
		return f"\x1b[{type};2;{crgb[0]};{crgb[1]};{crgb[2]}m"


	@staticmethod
	def moveHoriz(dist: SupportsInt):
		"""Move the cursor horizontally `dist` characters (supports negative numbers)."""
		dist = int(dist)
		return f"\x1b[{abs(dist)}{'D' if dist < 0 else 'C'}"


	@staticmethod
	def moveVert(dist: SupportsInt):
		"""Move the cursor vertically `dist` lines (supports negative numbers)."""
		dist = int(dist)
		return f"\x1b[{abs(dist)}{'A' if dist < 0 else 'B'}"


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
	CLEAR_SCROLL =	"\x1b[3J"
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


class _BaseSet(dict):
	"""Base class for all the customizable sets for the bar (colorset, charset, formatset)"""

	EMPTY: dict = {}
	DEFAULT: dict = {}

	def __init__(self, newSet: dict) -> None:
		if not newSet:
			newSet = self.DEFAULT
		elif not isinstance(newSet, dict):
			raise TypeError(f"newSet type ({type(newSet)}) is not dict")

		super().__init__(self._populate(self.EMPTY | newSet))


	def __repr__(self) -> str:
		return f"{self.__class__.__name__}({dict(self)})"


	def _populate(self, currentSet: dict) -> dict:		# ?: Needs a proper rewrite
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


	def iterValues(self, val: dict[dict, tuple[Optional[list[Any]], Optional[dict]]], func: Callable) -> dict:		# !thanks MithicSpirit. Still doesnt work with dicts inside dicts.
		"""
		Return dict with all values in it used as args for a function that will return a new value.
		@val: This represents the dictionary which contains a key for the dict to process, and a tuple containing
			  the *args and *kwargs.
		"""
		newSet = {}
		for key, value in val.items():
			if isinstance(value, dict):
				raise NotImplementedError	# !: Using workarounds everywhere.
				#newSet[key] = self.iterValues(value, func)
			#else:
			args = value[0] or ()
			kwargs = value[1] or {}
			newSet[key] = func(*args, *kwargs)
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
		self = CharSet._strip(self)


	@staticmethod
	def _strip(setdict: dict):
		"""Converts empty values to spaces, and makes sure there's only one character"""
		if not setdict:
			return

		newset = {}
		for key, value in setdict.items():
			if isinstance(value, dict):
				newset[key] = CharSet._strip(value)
				continue

			if len(value) > 1:
				value = value[0]

			if value in _IGNORE_CHARS+"\t":
				value = "?"
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
		"text":	{
			"right":	(15, 219, 162),
			"title":	(247, 111, 152),
			"subtitle":	(247, 111, 152),
			"left":		(15, 219, 162),
			"inside":	(15, 219, 162)
		}
	}

	ERROR: ColorSetEntry = {
		"empty":	(100, 0, 0),
		"full":		(255, 0, 0),
		"vert":		(255, 100, 100),
		"horiz":	(255, 100, 100),
		"corner":	(255, 100, 100),
		"text":		(255, 100, 100)
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
		'text':	{
			"inside":	(255, 197, 0),
			"right":	(255, 197, 0),
			"left":		(255, 197, 0),
			"title":	(199, 3, 24),
			"subtitle":	(199, 3, 24)
		}
	}


	def __init__(self, newSet: ColorSetEntry) -> None:
		super().__init__(_convertClrs(newSet, "RGB"))	# Convert all hex values to rgb tuples


	def parsedValues(self, bg = False) -> dict[str, Union[dict, str]]:
		"""Convert all values in the ColorSet to parsed color sequences"""
		# newset = {key: ((value, bg), None) for key, value in self.items()}
		# return ColorSet(self.iterValues(newset, VT100.color))
		return {
		    key: ColorSet.parsedValues(value, bg)
		    if isinstance(value, dict) else VT100.color(value, bg)
		    for key, value in self.items()
		}




class UnknownFormattingKeyError(BaseException):
	"""Unknown formatting key used in a formatset string"""
	def __init__(self, string, indices) -> None:
		start, end = indices
		value = string[start:end]
		super().__init__(
			f"Unknown formatting key {value!r} ('"
			+ string[:start]
			+ VT100.color((150, 0, 0), True) + string[start:end] + VT100.RESET
			+ string[end:] + "')"
		)


class UnexpectedEndOfStringError(BaseException):
	"""Unexpected end of string when parsing a formatting key"""
	def __init__(self, string) -> None:
		super().__init__(
			f"Unexpected end of string ('{string}"
			+ VT100.color((150, 0, 0), True)
			+ VT100.BOLD + "◄ Expected '>'" + VT100.RESET + "')"
		)


class FormatSet(_BaseSet):
	"""Container for the formatting sets."""

	EMPTY: FormatSetEntry = {
		"inside":	"",
		"right":	"",
		"left":		"",
		"title":	"",
		"subtitle":	""
	}

	DEFAULT: FormatSetEntry = {
		"right":	"<percentage>%",
		"title":	"<text>"
	}

	DESCRIPTIVE: FormatSetEntry = {
		"right":	"E. Time: <etime>s.",
		"title":	"<text>",
		"subtitle":	"<range1> of <range2>",
		"inside":	"<percentage>%"
	}

	LEFT_RIGHT: FormatSetEntry = {
		"left":		"<range1>/<range2>",
		"right":	"<text>: <percentage>%"
	}

	ONLY_PERCENTAGE: FormatSetEntry = {
		"inside":	"<percentage>%",
	}

	SIMPLE: FormatSetEntry = {
		"title":	"<text>",
		"subtitle":	"<range1>/<range2>"
	}

	E_TIME: FormatSetEntry = {
		"title":	"<text>",
		"subtitle":	"Elapsed <etime> seconds"
	}

	TITLE_SUBTITLE: FormatSetEntry = {
		"title":	"<text> (<range1>/<range2>)",
		"subtitle":	"<percentage>%, (<etime>s)"
	}

	CLASSIC: FormatSetEntry = {
		"right":	"<text>: <percentage>% (<range1>/<range2>) [<etime>s]"
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
	def _parseString(cls: "PBar", string: str) -> str:
		"""Parse a string that may contain formatting keys"""
		if string is None: return ""

		foundOpen = False		# Did we find a '<'?
		foundBackslash = False	# Did we find a '\'?
		tempStr = ""			# String that contains the current value inside < >
		endStr = ""				# Final string that will be returned
		text = FormatSet._rmPoisonChars(string)

		# Convert the keys to a final string
		for index, char in enumerate(text):
			if not foundOpen:
				if foundBackslash:
					# Also skip the character next to the slash
					foundBackslash = False
					endStr += char
					continue
				elif char == "\\":
					# Found backslash, skip it
					foundBackslash = True
					continue

			if foundOpen:
				# Found '<'. Now we add every char to tempStr until we find a '>'.
				if char == ">":
					# Found '>'. Now just add the formatting keys.
					if tempStr == "percentage":
						endStr += str(cls.percentage)
					elif tempStr == "range1":
						endStr += str(cls._range[0])
					elif tempStr == "range2":
						endStr += str(cls._range[1])
					elif tempStr == "etime":
						endStr += str(cls.etime)

					elif tempStr == "text":
						if cls._text:	endStr += FormatSet._rmPoisonChars(cls._text)
					else:
						raise UnknownFormattingKeyError(text, (index - len(tempStr), index))

					foundOpen = False
					tempStr = ""
				else:
					# No '>' encountered, we can just add another character.
					tempStr += char.lower()
			elif char == "<":
				foundOpen = True
			# elif char == " ":
			# 	endStr += VT100.moveHoriz(1)	# ?: Maybe in a future
			else:
				# It is just a normal character that doesn't belong to any formatting key, so just append it to the end string.
				endStr += char

		if foundOpen:	raise UnexpectedEndOfStringError(text)
		return endStr


	def parsedValues(self, cls: "PBar") -> "FormatSet":
		"""Returns a new FormatSet with all values parsed with the properties of the PBar object specified"""
		newset = {key: ((cls, value), None) for key, value in self.items()}
		return FormatSet(self.iterValues(newset, self._parseString))


	@staticmethod
	def cleanedValues(val: "FormatSet") -> "FormatSet":
		"""Convert all values in the FormatSet to strings with spaces of the same size."""
		return FormatSet({
		    key: FormatSet.cleanedValues(value)
		    if isinstance(value, dict) else " " * len(value)
		    for key, value in val.items()
		})




def _genShape(position: tuple[int, int], size: tuple[int, int], charset: CharSet, parsedColorset: dict, filled: Optional[str] = " ") -> str:
	"""Generates a basic rectangular shape that uses a charset and a parsed colorset"""
	width, height = _capValue(size[0], min=3) + 2, _capValue(size[1], min=0) + 1

	charVert = parsedColorset["vert"] + charset["vert"]
	charHoriz = charset["horiz"]
	charCorner = (
		parsedColorset["corner"]["tleft"] + charset["corner"]["tleft"],
		parsedColorset["corner"]["tright"] + charset["corner"]["tright"],
		parsedColorset["corner"]["bleft"] + charset["corner"]["bleft"],
		parsedColorset["corner"]["bright"] + charset["corner"]["bright"]
	)

	endStr: str = (
		VT100.pos((position))
		+ charCorner[0]
		+ parsedColorset["horiz"] + charHoriz*width
		+ charCorner[1]
	)

	for row in range(1, height):
		endStr += (
			VT100.pos((position), (0, row))
			+ charVert
			+ (VT100.moveHoriz(width) if filled is None else filled[0]*width)
			+ charVert
		)

	endStr += (
		VT100.pos((position), (0, height))
		+ charCorner[2]
		+ parsedColorset["horiz"] + charHoriz*width
		+ charCorner[3]
	)

	return endStr




def _genBarContent(position: tuple[int, int], size: tuple[int, int], charset: CharSet, parsedColorset: ColorSet,
				   rangeValue: tuple[int, int]) -> str:
	"""Generates the progress shape with a parsed colorset and a charset specified"""
	width, height = _capValue(size[0], min=3), _capValue(size[1], min=0) + 1
	SEGMENTS_FULL = int((_capValue(rangeValue[0], rangeValue[1], 0) / _capValue(rangeValue[1], min=1))*width)	# Number of character for the full part of the bar
	SEGMENTS_EMPTY = width - SEGMENTS_FULL

	charFull = charset["full"]
	charEmpty = charset["empty"]

	return "".join((
			VT100.pos((position), (0, row))
			+ parsedColorset["full"] + charFull*SEGMENTS_FULL
			+ parsedColorset["empty"] + charEmpty*SEGMENTS_EMPTY
		) for row in range(1, height))




def _genBarText(position: tuple[int, int], size: tuple[int, int], parsedColorset: dict[str, Union[dict, str]], formatset: FormatSet) -> str:
	"""Generates all text for the bar"""
	width, height = _capValue(size[0], min=3) + 3, _capValue(size[1], min=0) + 1

	def stripText(string: str, maxlen: int):
		"""Return a string stripped if the len of it is larger than the maxlen specified"""
		maxlen = _capValue(maxlen, min=3)
		return string[:maxlen-3] + "..." if len(string) > maxlen else string

	txtMaxWidth = width - 1
	txtSubtitle = stripText(formatset["subtitle"], txtMaxWidth)
	txtInside = stripText(formatset["inside"], txtMaxWidth-4)
	txtTitle = stripText(formatset["title"], txtMaxWidth)

	textTitle = (
		VT100.pos(position, (1, 0))
		+ parsedColorset["text"]["title"]
		+ txtTitle
	)

	textSubtitle = (
		VT100.pos(position, (width - len(txtSubtitle), height))
		+ parsedColorset["text"]["subtitle"]
		+ txtSubtitle
	)

	textRight = (
		VT100.pos(position, (width + 2, height/2))
		+ parsedColorset["text"]["right"]
		+ formatset["right"]
		+ VT100.CLEAR_RIGHT
	) if formatset["right"] else ""

	textLeft = (
		VT100.pos(position, (-len(formatset["left"]) - 1, height/2))
		+ VT100.CLEAR_LEFT
		+ parsedColorset["text"]["left"]
		+ formatset["left"]
	) if formatset["left"] else ""

	txtInside = (
		VT100.pos(position, (width/2 - len(txtInside)/2 + 1, height/2))
		+ parsedColorset["text"]["inside"]
		+ txtInside
	)

	return textTitle + textSubtitle + textRight + textLeft + txtInside




class PBar():
	"""
	# PBar - Progress bar

	Object for managing a progress bar.

	---

	## Methods

	- PBar.draw()
	- PBar.step()
	- PBar.clear()
	- PBar.resetETime()
	- PBar.fromConfig()

	---

	## Properties

	- PBar.percentage
	- PBar.text
	- PBar.range
	- PBar.length
	- PBar.position
	- PBar.charset
	- PBar.colorset
	- PBar.formatset
	- PBar.enabled
	- PBar.etime
	- PBar.config
	"""
	def __init__(self,
			range: tuple[int, int] = (0, 1),
			text: str = None,
			size: tuple[int, int] = (20, 1),
			position: tuple[Union[str, int], Union[str, int]] = ("center", "center"),
			charset: Optional[CharSetEntry] = None,
			colorset: Optional[ColorSetEntry] = None,
			formatset: Optional[FormatSetEntry] = None
		) -> None:
		"""
		### Detailed descriptions:
		@range: This tuple will specify the range of two values to display in the progress bar.

		---

		@text: String to show in the progress bar.

		---

		@size: Tuple that specifies the width and height of the bar.

		---

		@position: Tuple containing the position (X and Y axles of the center) of the progress bar on the terminal.

		- If an axis value is `center`, the bar will be positioned at the center of the terminal on that axis.
		- Negative values will position the bar at the other side of the terminal.

		---

		@charset: Set of characters to use when drawing the progress bar.

		To use one of the included sets, use any of the constant values in `pbar.CharSet`. Keep in mind that some fonts might not have
		the characters used in some charsets.

		Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom characters.
		- Custom character set dictionary:

				![image](https://user-images.githubusercontent.com/48654552/127887419-acee1b4f-de1b-4cc7-a1a6-1be75c7f97c9.png)

			Note: It is not needed to specify all the keys and values.

		---

		@colorset: Set of colors to use when drawing the progress bar.

		To use one of the included sets, use any of the constant values in `pbar.ColorSet`.

		Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom colors.
		- Custom color set dictionary:

				![image](https://user-images.githubusercontent.com/48654552/134371850-1d858a6e-8003-40da-a5ff-f36bd06a5b07.png)

			Note: It is not needed to specify all the keys and values.

			Note: The colors can also be specified as HEX in a string.

		---

		@formatset: Formatting used when displaying the strings in different places around the bar.

		To use one of the included sets, use any of the constant values in `pbar.FormatSet`.

		Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom formatting.
		- Custom formatset dictionary:

				![image](https://user-images.githubusercontent.com/48654552/134372064-2abd9fab-37dd-4334-8d30-26e2f0967313.png)

			Note: It is not needed to specify all the keys and values.

		- Available formatting keys:
			- `<percentage>`:	Percentage of the bar.
			- `<range1>`:		First value of the range.
			- `<range2>`:		Second value of the range.
			- `<text>`:			Text selected in the `text` property/arg.
			- `<etime>`:		Elapsed time since the bar created.
		"""
		self._requiresClear = False		# This controls if the bar needs to clear its old position before drawing.
		self._enabled = True			# If disabled, the bar will never draw.
		self._time = _time()			# The elapsed time since the bar created.

		self._range = PBar._getRange(range)
		self._text = FormatSet._rmPoisonChars(text) if text is not None else ""
		self._formatset = FormatSet(formatset)
		self._size = PBar._getSize(size)
		self._charset = CharSet(charset)
		self._colorset = ColorSet(colorset)
		self._pos = self._getPos(position)

		self._oldValues = [self._pos, self._size]	# This values are used when clearing the old position of the bar (when self._requiresClear is True)


	# --------- Properties / Methods the user should use. ----------


	def draw(self):
		"""Print the progress bar on screen."""

		if self._requiresClear:
			# Clear the bar at the old position and length
			self._printStr(self._genClearedBar(self._oldValues))
			self._oldValues = [self._pos, self._size]	# Reset the old values

		# Draw the bar
		self._printStr(self._genBar())

		self._requiresClear = False


	def step(self, steps: int = 1, text=None):
		"""
		Add `steps` to the first value in range, then draw the bar.
		@steps: Value to add to the first value in range.
		@text: Text to be displayed on the bar.
		"""
		self.range = (self._range[0] + steps, self._range[1])
		if text is not None: self.text = text
		self.draw()


	def clear(self):
		"""Clear the progress bar."""
		bar = self._genClearedBar((self._pos, self._size))
		self._printStr(bar)


	def resetETime(self):
		"""Reset the elapsed time counter."""
		self._time = _time()	# Just set _time to the current time.


	@classmethod
	def fromConfig(cls, other: Union["PBar", dict]) -> "PBar":
		"""Return a PBar object created with the configuration of the PBar/dict object given."""
		pb = PBar()
		pb.config = other.config if isinstance(other, PBar) else other
		return pb


	@property
	def percentage(self):
		"""Percentage of the progress of the current range."""
		return int((self._range[0]*100) / self._range[1])


	@property
	def text(self):
		"""Text to be displayed on the bar."""
		return self._text
	@text.setter
	def text(self, text: str):
		self._text = FormatSet._rmPoisonChars(text)


	@property
	def range(self) -> tuple[int, int]:
		"""Range for the bar progress."""
		return (self._range[0], self._range[1])
	@range.setter
	def range(self, range: tuple[int, int]):
		self._range = PBar._getRange(range)


	@property
	def charset(self) -> CharSet:
		"""Set of characters for the bar."""
		return self._charset
	@charset.setter
	def charset(self, charset: CharSetEntry):
		self._charset = CharSet(charset)


	@property
	def colorset(self) -> ColorSet:
		"""Set of colors for the bar."""
		return self._colorset
	@colorset.setter
	def colorset(self, colorset: ColorSetEntry):
		self._colorset = ColorSet(colorset)


	@property
	def formatset(self) -> FormatSet:
		"""Formatting used for the bar."""
		return self._formatset
	@formatset.setter
	def formatset(self, formatset: FormatSetEntry):
		self._formatset = FormatSet(formatset)


	@property
	def size(self):
		"""Size of the progress bar."""
		return self._size
	@size.setter
	def size(self, size: tuple[int, int]):
		newsize = PBar._getSize(size)
		self._requiresClear = newsize != self._size
		self._oldValues[1] = self._size
		self._size = newsize


	@property
	def position(self):
		"""Position of the progress bar."""
		return self._pos
	@position.setter
	def position(self, position: Position):
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
	def etime(self) -> float:
		"""Time elapsed since the bar created."""
		return round(_time() - self._time, 2)


	@property
	def config(self) -> dict:
		"""All the values of the progress bar stored in a dict."""
		return {
			"range":		self._range,
			"text":			self._text,
			"size":			self._size,
			"position":		self._pos,
			"charset":		self._charset,
			"colorset":		_convertClrs(self._colorset, "HEX"),
			"formatset":	self._formatset,
			"enabled":		self._enabled
		}
	@config.setter
	def config(self, config: dict[str, Any]):
		if not isinstance(config, dict):
			raise TypeError(f"config value type ({type(config)}) is not dictionary")
		for key in {"range", "text", "size", "position", "charset", "colorset", "formatset", "enabled"}:
			# Iterate through every key in the dict and populate the config of the class with its values
			if key not in config:
				raise ValueError(f"config dict is missing the {key!r} key")
			setattr(self, key, config[key])


	# --------- ///////////////////////////////////////// ----------


	def _getPos(self, position: Position) -> tuple[int, int]:
		"""Get and process new position requested"""
		_chkSeqOfLen(position, 2)

		TERM_SIZE: tuple[int, int] = _get_terminal_size()
		newpos = []

		for index, value in enumerate(position):
			if value == "center":
				value = int(TERM_SIZE[index] / 2)
			elif not isinstance(value, (int, float)):
				raise TypeError(f"Type of value {value} ({type(value)}) is not int/float")

			if value < 0:
				value = TERM_SIZE[index] + value

			if index == 0:
				value = _capValue(value, TERM_SIZE[0] - self._size[0]/2 + 2, self._size[0] / 2 + 2)
			else:
				value = _capValue(value, TERM_SIZE[1] - self._size[1]/2, 1 + self._size[1]/2)

			newpos.append(int(value))
		return tuple(newpos)


	@staticmethod
	def _getSize(size: Optional[tuple[SupportsInt, SupportsInt]]) -> tuple[int, int]:
		"""Get and process new length requested"""
		_chkSeqOfLen(size, 2)
		return (int(_capValue(size[0], min=0)),
				int(_capValue(size[1], min=0)))


	@staticmethod
	def _getRange(range: tuple[SupportsInt, SupportsInt]) -> tuple[int, int]:
		"""Return a capped range"""
		_chkSeqOfLen(range, 2)
		return (int(_capValue(range[0], range[1], 0)),
				int(_capValue(range[1], min=1)))


	def _genClearedBar(self, values: tuple[tuple[int, int], tuple[int, int]]) -> str:
		"""Generate a cleared progress bar. `values[0]` is the position, and `values[1]` is the size"""
		size = values[1]
		pos = values[0]
		parsedColorSet = ColorSet.parsedValues(ColorSet.EMPTY)

		POSITION = (pos[0] + int(size[0] / -2),
					pos[1] + int(size[1] / -2))

		barShape = _genShape(
			POSITION,
			size,
			CharSet.EMPTY,
			parsedColorSet
		)

		barText = _genBarText(
			POSITION,
			size,
			parsedColorSet,
			FormatSet.cleanedValues(self._formatset.parsedValues(self))
		)

		return (
			VT100.CURSOR_SAVE + VT100.CURSOR_HIDE
			+ barText
			+ barShape
			+ VT100.CURSOR_LOAD + VT100.CURSOR_SHOW
		)


	def _genBar(self) -> str:
		"""Generate the progress bar"""
		POSITION = (self._pos[0] + int(self._size[0] / -2),
					self._pos[1] + int(self._size[1] / -2))

		parsedColorSet = self._colorset.parsedValues()

		# Build all the parts of the progress bar
		barShape = _genShape(
			POSITION,
			self._size, self._charset, parsedColorSet
		)

		barContent = _genBarContent(
			(POSITION[0] + 2, POSITION[1]),
			self._size, self._charset, parsedColorSet, self._range
		)

		barText = _genBarText(
			POSITION,
			self._size, parsedColorSet, self._formatset.parsedValues(self)
		)

		return (
			VT100.CURSOR_SAVE + VT100.CURSOR_HIDE
			+ barShape
			+ barContent
			+ barText
			+ VT100.CURSOR_LOAD + VT100.CURSOR_SHOW
		)


	def _printStr(self, barString: str):
		"""Prints string to stream"""
		if not self._enabled: return
		print(barString, flush=True, end="")




def taskWrapper(pbarObj: PBar, scope: dict, titleComments = False, overwriteRange = True):
	"""
	Use as a decorator. Takes a PBar object, sets its range depending on the quantity of
	statements inside the decorated function, and `steps` the bar over after every function statement.
	Note: Multi-line expressions are not supported.

	@pbarObj: PBar object to use.
	@scope: Dictionary containing the scope local variables.
	@titleComments: If True, comments on a statement will be treated as titles for the progress bar.
	@overwriteRange: If True, overwrites the range of the bar.
	"""
	def wrapper(func):
		lines = _srclines(func)[0][2:]	# Get the source lines of code

		pbarObj.range = (0, len(lines)) if overwriteRange else pbarObj.range

		for inst in lines:	# Iterate through every statement
				instComment = _getComment(inst)
				if titleComments and instComment:	pbarObj.text = instComment
				pbarObj.draw()
				try:
					eval(inst, scope)	# yep, this uses evil()
				except SyntaxError:
					raise RuntimeError("Multi-line expressions are not supported inside functions decorated with taskWrapper")
				pbarObj.step()

	return wrapper