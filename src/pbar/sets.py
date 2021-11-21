from typing import Optional, Callable, Union
from . utils import *
from . import bar


Color = Optional[Union[tuple[int, int, int], str, None]]
ColorSetEntry = dict[str, Union["ColorSetEntry", Color]]	# type: ignore
CharSetEntry = dict[str, Union["CharSetEntry", str]]		# type: ignore
FormatSetEntry = dict[str, Union["FormatSetEntry", str]]	# type: ignore


_IGNORE_CHARS = "\x1b\n\r\b\a\f\v"


class UnknownSetKeyError(Exception):
	"""A key supplied in a dictionary is unknown for the set class that will use it"""
	def __init__(self, key, setcls) -> None:
		msg = f"Unknown key {key!r} for {setcls.__class__.__name__!r}"
		clsKeys = "', '".join(setcls.EMPTY)
		super().__init__(f"{msg}. Available valid keys: '{clsKeys}'.")


class _BaseSet(dict):
	"""Base class for all the customizable sets for the bar (colorset, charset, formatset)"""
	EMPTY: dict = {}

	def __init__(self, newSet: dict) -> None:
		chkInstOf(newSet, dict, name="newSet")
		super().__init__(self._populate(self.EMPTY | newSet))


	def __repr__(self) -> str:
		return f"{self.__class__.__name__}({dict(self)})"


	def _populate(self, currentSet: dict) -> dict:		# ?: Needs a proper rewrite if we end up needing more subdicts
		"""Return a new set with all the necessary keys for drawing the bar, making sure that no keys are missing."""
		newSet = {}
		for key, currentValue in currentSet.items():
			if key not in self.EMPTY:
				raise UnknownSetKeyError(key, self)

			defaultSetValue = self.EMPTY[key]

			if not isinstance(currentValue, dict) and isinstance(defaultSetValue, dict):
				newSet[key] = {subkey: currentValue for subkey in defaultSetValue}
			elif isinstance(currentValue, dict) and isinstance(defaultSetValue, dict):
				newSet[key] = defaultSetValue | currentValue
			else:
				newSet[key] = currentValue

		return newSet


	def mapValues(self, func: Callable) -> dict:
		"""Return a dict mapped the values of the set to a function."""
		return mapDict(self, func)




class CharSet(_BaseSet):
	"""Container for the character sets."""

	EMPTY: CharSetEntry = {
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
		"vert":	{
			"left":		"[",
			"right":	"]"
		}
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

	DOUBLE: CharSetEntry = {
		"empty":	"░",
		"full":		"█",
		"vert":		"║",
		"horiz":	"═",
		"corner": {
			"tleft":	"╔",
			"tright":	"╗",
			"bleft":	"╚",
			"bright":	"╝"
		}
	}


	def __init__(self, newSet: CharSetEntry) -> None:
		super().__init__(newSet or self.DEFAULT)
		self |= self._strip()	# we update with the stripped strings


	def _strip(self) -> "CharSet":
		def clean(value) -> str:
			if len(value) > 1:
				value = value[0]	# if the string is larger than one, just get the first char
			if value in _IGNORE_CHARS+"\t":
				return "?"	# we just return a "?" if the char is invalid.
			return value

		return self.mapValues(lambda val: clean(val))	# map the new dict





class ColorSet(_BaseSet):
	"""Container for the color sets."""

	EMPTY: ColorSetEntry = {
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

	DEFAULT: ColorSetEntry = {
		"full":		"#15F28D",
		"empty":	"#FF4D4D",
		"horiz":	"white",
		"vert":		"white",
		"corner":	"white",
		"text":		"white"
	}

	DARVIL: ColorSetEntry = {
		'empty':	'#0067c2',
		'full':		'springGreen',
		'vert':		'#f76f98',
		'horiz':	'#f76f98',
		'corner':	'#f76f98',
		'text': {
			'right':	'springGreen',
			'title':	'#f76f98',
			'subtitle':	'#f76f98',
			'left':		'springGreen',
			'inside':	'springGreen'
		}
	}

	RED: ColorSetEntry = {
		'empty':	'darkRed',
		'full':		'red',
		'vert':		'#ff6464',
		'horiz':	'#ff6464',
		'corner':	'#ff6464',
		'text':		'#ff6464'
	}

	GREEN: ColorSetEntry = {
		"full":		"lime",
		"empty":	"green",
		"horiz":	"paleGreen",
		"corner":	"paleGreen",
		"vert":		"paleGreen",
		"text":		"lime"
	}

	YELLOW: ColorSetEntry = {
		'full':		"yellow",
		'empty':	"#a77227",
		'horiz':	"#dab77b",
		'vert':		"#dab77b",
		'corner':	"#dab77b",
		'text':		"#dab77b"
	}

	FLAG_ES: ColorSetEntry = {
		'corner':	"red",
		'horiz':	"red",
		'vert':		"yellow",
		'full':		"yellow",
		'empty':	"#9a7600",
		'text':	{
			"inside":	"yellow",
			"right":	"yellow",
			"left":		"yellow",
			"title":	"red",
			"subtitle":	"red"
		}
	}

	FLAG_LESBIAN: ColorSetEntry = {		# Author: ShygalCoco
		"empty":        "#777",
		"full":         "#fff",
		"vert":			"#fff",
		"horiz": {
			"top":      "#ff9879",
			"bottom":   "#e57bb9"
		},
		"corner": {
			"tleft":    "#ff9879",
			"tright":   "#ff9879",
			"bleft":    "#e57bb9",
			"bright":   "#e57bb9"
		},
		"text": {
			"inside":   "#fff",
			"right":    "#fff",
			"left":     "#fff",
			"title":    "#ff9879",
			"subtitle": "#e57bb9"
		}
	}


	def __init__(self, newSet: ColorSetEntry) -> None:
		super().__init__(convertClrs(newSet or self.DEFAULT, "RGB"))	# Convert all hex values to rgb tuples


	def parsedValues(self, bg=False) -> dict[str, Union[dict, str]]:
		"""Convert all values in the ColorSet to parsed color sequences for the terminal"""
		return self.mapValues(lambda val: Term.color(val, bg))




class UnknownFormattingKeyError(Exception):
	"""Unknown formatting key used in a formatset string"""
	def __init__(self, string) -> None:
		super().__init__(
			"Unknown formatting key '"
			+ Term.BOLD + Term.color((255, 0, 0)) + string
			+ Term.RESET + "'"
		)

class UnexpectedEndOfStringError(Exception):
	"""Unexpected end of string when parsing a formatting key"""
	def __init__(self, string) -> None:
		super().__init__(
			f"Unexpected end of string ('{string}"
			+ Term.color((150, 0, 0), True)
			+ Term.BOLD + "◄ Expected '>'" + Term.RESET + "')"
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
		"title":	"<text>",
		"inside":	"<percentage>%"
	}

	DESCRIPTIVE: FormatSetEntry = {
		"right":	"E. Time: <etime>s.",
		"title":	"<text>",
		"subtitle":	"<prange1> of <prange2>",
		"inside":	"<percentage>%"
	}

	LEFT_RIGHT: FormatSetEntry = {
		"left":		"<prange1>/<prange2>",
		"right":	"<text>: <percentage>%"
	}

	ONLY_PERCENTAGE: FormatSetEntry = {
		"inside":	"<percentage>%",
	}

	SIMPLE: FormatSetEntry = {
		"title":	"<text>",
		"subtitle":	"<prange1>/<prange2>"
	}

	E_TIME: FormatSetEntry = {
		"title":	"<text>",
		"subtitle":	"Elapsed <etime> seconds"
	}

	TITLE_SUBTITLE: FormatSetEntry = {
		"title":	"<text> (<prange1>/<prange2>)",
		"subtitle":	"<percentage>%, (<etime>s)"
	}

	CLASSIC: FormatSetEntry = {
		"right":	"<text>: <percentage>% (<prange1>/<prange2>) [<etime>s]"
	}

	PLACEHOLDER: FormatSetEntry = {
		"inside":	"inside",
		"right":	"right",
		"left":		"left",
		"title":	"title",
		"subtitle":	"subtitle"
	}


	def __init__(self, newSet: FormatSetEntry) -> None:
		super().__init__(newSet or self.DEFAULT)


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
	def getBarAttrs(cls: "bar.PBar", string: str):
		attrs = {
			"percentage": cls.percentage,
			"prange1": cls._range[0],
			"prange2": cls._range[1],
			"etime": cls.etime,
			"text": FormatSet._rmPoisonChars(cls._text) if cls._text else ""
		}

		if string not in attrs:	raise UnknownFormattingKeyError(string)

		return attrs[string]



	@staticmethod
	def parseString(cls: "bar.PBar", string: str) -> str:
		"""Parse a string that may contain formatting keys"""
		if string is None: return ""

		foundOpen = False		# Did we find a '<'?
		foundBackslash = False	# Did we find a '\'?
		tempStr = ""			# String that contains the current value inside < >
		endStr = ""				# Final string that will be returned
		text = FormatSet._rmPoisonChars(string)

		# Convert the keys to a final string
		for char in text:
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
					if (newValue := FormatSet.getBarAttrs(cls, tempStr)) is None:
						raise UnknownFormattingKeyError(text)
					else: endStr += str(newValue)

					foundOpen = False
					tempStr = ""
				else:
					# No '>' encountered, we can just add another character.
					tempStr += char.lower()
			elif char == "<":
				foundOpen = True
			# elif char == " ":
			# 	endStr += Term.moveHoriz(1)	# ?: Maybe in a future
			else:
				# It is just a normal character that doesn't belong to any formatting key, so just append it to the end string.
				endStr += char

		if foundOpen:	raise UnexpectedEndOfStringError(text)
		return endStr


	def parsedValues(self, cls: "bar.PBar") -> "FormatSet":
		"""Returns a new FormatSet with all values parsed with the properties of the PBar object specified"""
		return FormatSet(self.mapValues(lambda val: self.parseString(cls, val)))


	def emptyValues(self) -> "FormatSet":
		"""Convert all values in the FormatSet to strings with spaces of the same size."""
		return FormatSet(self.mapValues(lambda val: " "*len(val)))