from io import TextIOWrapper
from os import system as runsys, get_terminal_size, isatty
from time import sleep
import sys, re
if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes
else:
    import termios
from typing import (
	Callable,
	SupportsFloat,
	TypeVar,
	Optional,
	Union,
	Any,
	SupportsInt
)

__all__ = (
	"capValue", "getConstantAttrs", "stripText",
	"convertColor", "chkInstOf", "chkSeqOfLen",
	"isNum", "out", "mapDict", "Term"
)

T = TypeVar("T")
Color = Union[tuple[int, int, int], str]


_HTML_COLOR_NAMES: dict = {  # thanks to https://stackoverflow.com/a/1573141/14546524
	"aliceblue": "#f0f8ff",
	"antiquewhite": "#faebd7",
	"aqua": "#00ffff",
	"aquamarine": "#7fffd4",
	"azure": "#f0ffff",
	"beige": "#f5f5dc",
	"bisque": "#ffe4c4",
	"black": "#000000",
	"blanchedalmond": "#ffebcd",
	"blue": "#0000ff",
	"blueviolet": "#8a2be2",
	"brown": "#a52a2a",
	"burlywood": "#deb887",
	"cadetblue": "#5f9ea0",
	"chartreuse": "#7fff00",
	"chocolate": "#d2691e",
	"coral": "#ff7f50",
	"cornflowerblue": "#6495ed",
	"cornsilk": "#fff8dc",
	"crimson": "#dc143c",
	"cyan": "#00ffff",
	"darkblue": "#00008b",
	"darkcyan": "#008b8b",
	"darkgoldenrod": "#b8860b",
	"darkgray": "#a9a9a9",
	"darkgreen": "#006400",
	"darkkhaki": "#bdb76b",
	"darkmagenta": "#8b008b",
	"darkolivegreen": "#556b2f",
	"darkorange": "#ff8c00",
	"darkorchid": "#9932cc",
	"darkred": "#8b0000",
	"darksalmon": "#e9967a",
	"darkseagreen": "#8fbc8f",
	"darkslateblue": "#483d8b",
	"darkslategray": "#2f4f4f",
	"darkturquoise": "#00ced1",
	"darkviolet": "#9400d3",
	"deeppink": "#ff1493",
	"deepskyblue": "#00bfff",
	"dimgray": "#696969",
	"dodgerblue": "#1e90ff",
	"firebrick": "#b22222",
	"floralwhite": "#fffaf0",
	"forestgreen": "#228b22",
	"fuchsia": "#ff00ff",
	"gainsboro": "#dcdcdc",
	"ghostwhite": "#f8f8ff",
	"gold": "#ffd700",
	"goldenrod": "#daa520",
	"gray": "#808080",
	"green": "#008000",
	"greenyellow": "#adff2f",
	"honeydew": "#f0fff0",
	"hotpink": "#ff69b4",
	"indianred": "#cd5c5c",
	"indigo": "#4b0082",
	"ivory": "#fffff0",
	"khaki": "#f0e68c",
	"lavender": "#e6e6fa",
	"lavenderblush": "#fff0f5",
	"lawngreen": "#7cfc00",
	"lemonchiffon": "#fffacd",
	"lightblue": "#add8e6",
	"lightcoral": "#f08080",
	"lightcyan": "#e0ffff",
	"lightgoldenrodyellow": "#fafad2",
	"lightgrey": "#d3d3d3",
	"lightgreen": "#90ee90",
	"lightpink": "#ffb6c1",
	"lightsalmon": "#ffa07a",
	"lightseagreen": "#20b2aa",
	"lightskyblue": "#87cefa",
	"lightslategray": "#778899",
	"lightsteelblue": "#b0c4de",
	"lightyellow": "#ffffe0",
	"lime": "#00ff00",
	"limegreen": "#32cd32",
	"linen": "#faf0e6",
	"magenta": "#ff00ff",
	"maroon": "#800000",
	"mediumaquamarine": "#66cdaa",
	"mediumblue": "#0000cd",
	"mediumorchid": "#ba55d3",
	"mediumpurple": "#9370d8",
	"mediumseagreen": "#3cb371",
	"mediumslateblue": "#7b68ee",
	"mediumspringgreen": "#00fa9a",
	"mediumturquoise": "#48d1cc",
	"mediumvioletred": "#c71585",
	"midnightblue": "#191970",
	"mintcream": "#f5fffa",
	"mistyrose": "#ffe4e1",
	"moccasin": "#ffe4b5",
	"navajowhite": "#ffdead",
	"navy": "#000080",
	"oldlace": "#fdf5e6",
	"olive": "#808000",
	"olivedrab": "#6b8e23",
	"orange": "#ffa500",
	"orangered": "#ff4500",
	"orchid": "#da70d6",
	"palegoldenrod": "#eee8aa",
	"palegreen": "#98fb98",
	"paleturquoise": "#afeeee",
	"palevioletred": "#d87093",
	"papayawhip": "#ffefd5",
	"peachpuff": "#ffdab9",
	"peru": "#cd853f",
	"pink": "#ffc0cb",
	"plum": "#dda0dd",
	"powderblue": "#b0e0e6",
	"purple": "#800080",
	"rebeccapurple": "#663399",
	"red": "#ff0000",
	"rosybrown": "#bc8f8f",
	"royalblue": "#4169e1",
	"saddlebrown": "#8b4513",
	"salmon": "#fa8072",
	"sandybrown": "#f4a460",
	"seagreen": "#2e8b57",
	"seashell": "#fff5ee",
	"sienna": "#a0522d",
	"silver": "#c0c0c0",
	"skyblue": "#87ceeb",
	"slateblue": "#6a5acd",
	"slategray": "#708090",
	"snow": "#fffafa",
	"springgreen": "#00ff7f",
	"steelblue": "#4682b4",
	"tan": "#d2b48c",
	"teal": "#008080",
	"thistle": "#d8bfd8",
	"tomato": "#ff6347",
	"turquoise": "#40e0d0",
	"violet": "#ee82ee",
	"wheat": "#f5deb3",
	"white": "#ffffff",
	"whitesmoke": "#f5f5f5",
	"yellow": "#ffff00",
	"yellowgreen": "#9acd32",
}


class UnexpectedEndOfStringError(Exception):
	"""Unexpected end of string when parsing a formatting key"""
	def __init__(self, string, expectedChar=">") -> None:
		super().__init__(
			"Unexpected end of string. ('" + string
			+ Term.formatStr(f"<bg=150,0,0>*◄ Expected '{expectedChar}'<reset>')")
		)


Num = TypeVar("Num", int, float)

def capValue(value: Num, max: Num = None, min: Num = None) -> Num:
	"""Clamp a value to a minimum and/or maximum value."""
	if max is not None and value > max:
		return max
	elif min is not None and value < min:
		return min
	else:
		return value


def getConstantAttrs(obj: Any) -> tuple:
	"""Get the constant attributes of an object. (Uppercase attrs)"""
	return tuple(a for a in dir(obj) if a.isupper())


def stripText(string: str, maxlen: int, endStr: str = "…") -> str:
	"""
	Return a cutted string at the end if the len of it is larger than
	the maxlen specified.
	@string: the string to cut
	@maxlen: the maximum length of the string
	@endStr: the string to add at the end of the cutted string
	"""
	if maxlen < (endLen := len(endStr)):
		return ""
	return string[:maxlen-endLen] + endStr if len(string) > maxlen else string


def convertColor(clr: Color, conversion: str) -> Union[str, tuple]:
	"""
	Convert color values to HEX and vice-versa
	@clr:			Color value to convert.
	@conversion:	Type of conversion to do ('RGB' or 'HEX')
	"""
	if not clr:
		raise ValueError("Color value cannot be None")
	elif isinstance(clr, str):
		color = clr.lower()
		if color in _HTML_COLOR_NAMES:	color = _HTML_COLOR_NAMES[color]	# check if its a html color name
	else:
		color = clr

	if conversion == "HEX":
		if isinstance(color, str) and color.startswith("#"):
			return color
		if not isinstance(color, (tuple, list)) or len(color) != 3:
			raise ValueError(f"Invalid color value: {color}")

		capped = tuple(capValue(value, 255, 0) for value in color)
		return f"#{capped[0]:02x}{capped[1]:02x}{capped[2]:02x}"
	elif conversion == "RGB":
		if isinstance(color, (tuple, list)):
			return color
		if not isinstance(color, str) or not color.startswith("#"):
			raise ValueError(f"Invalid color value: {color}")

		clrs = color.lstrip("#")

		if len(clrs) == 3:
			clrs = "".join(c*2 for c in clrs)	# if size of hex color is 3, just duplicate chars to make it 6

		return tuple(int(clrs[i:i+2], 16) for i in (0, 2, 4))
	else:
		return ""


def chkSeqOfLen(obj: Any, length: int, name: str = None) -> bool:
	"""
	Check if an object is a Sequence and has the length specified.
	If fails, raises exception (`Sequence obj | name must have len items`).
	"""
	chkInstOf(obj, tuple, list)
	if len(obj) != length:
		raise ValueError(
			Term.formatStr(
				(name or f"Sequence <orange>{obj!r}<reset>")
				+ f" must have <lime>{length}<reset> items, "
				+ f"not <red>{len(obj)}<reset>"
			)
		)
	return True


def chkInstOf(obj: Any, *typ: Any, name: str = None) -> bool:
	"""
	Check if an object is an instance of any of the other objects specified.
	If fails, raises exception (`Value | name must be *typ, not obj`).
	"""
	if not typ:
		raise ValueError("No type/s were supplied to check against")

	if not isinstance(obj, typ):
		raise TypeError(Term.formatStr(
			(name or f"Value <orange>{obj!r}<reset>")
			+ f" must be {' or '.join(Term.formatStr(f'<lime>{x.__name__}<reset>') for x in typ)}"
			+ f", not <red>{obj.__class__.__name__}<reset>"
		))
	return True


def isNum(obj: SupportsFloat) -> bool:
	"""Return True if `obj` can be casted to float."""
	try:
		float(obj)
	except ValueError:
		return False
	return True


def out(*obj, end: str = "", sep = ""):
	"""Print to stdout."""
	sys.stdout.write(sep.join(str(x) for x in obj) + end)
	sys.stdout.flush()


def mapDict(dictionary: dict, func: Callable) -> dict:
	"""
	Return dict with all values in it used as an arg for a function that will return a new value for it.
	@func: This represents the callable that accepts an argument.

	Example:
	>>> mapDict(lambda val: myFunc("stuff", val), {1: "a", 2: "b", 3: "c"})
	"""
	return {
		key: mapDict(value, func) if isinstance(value, dict) else func(value)
		for key, value in dictionary.items()
	}




class Stdout(TextIOWrapper):
	"""
	A class that may override stdout.
	Keeps track of the number of newlines sent.
	"""
	_cntrs: list["NewLineCounter"] = []
	scroll_offset: int = 0
	always_check: bool = False

	def __init__(self, stdout: TextIOWrapper) -> None:
		self.original = stdout

	def write(self, s: str) -> None:
		"""
		Writes the given string to the terminal.
		@s: String to write.
		"""
		s = str(s)

		"""We check if the string contains newlines, and if it does, check if the
		cursor is positioned at the end of the terminal. If it is, we add 1
		for each newline char to the counters, which will store the number of newlines."""

		if count := sum(s.count(c) for c in "\n\v\f") or Stdout.always_check:
			sys.stdout = self.original	# using original stdout temporarily to prevent recursion... Hacky!
			cPos, tSize, offset = Term.getPos()[1], Term.getSize()[1], Stdout.scroll_offset + 1
			if cPos >= tSize - offset:
				if offset:
					out(
						"\v"*offset
						+ Term.moveVert(-offset)
					)
				for mgr in Stdout._cntrs:
					# we take into account the possible exceeding of the the max size
					mgr._lc += count + (cPos - (tSize - offset) - 1)
			sys.stdout = self

		self.original.write(s)

	def flush(self):
		"""Flushes the stdout buffer."""
		self.original.flush()




class NewLineCounter:
	"""Keeps track of the number of newlines that scrolled the screen."""
	def __init__(self) -> None:
		self._lc = 0
		Stdout._cntrs.append(self)

	@property
	def lines(self):
		l = self._lc
		self._lc = 0
		return l




class Term:
	"""Class for using terminal sequences a bit easier"""
	runsys("")		# We need to do this, otherwise Windows won't display special VT100 sequences

	def _isSupported() -> bool:
		"""Return False if terminal is not supported."""
		try:
			get_terminal_size()
		except OSError:
			return False

		return isatty(0)

	SUPPORTED = _isSupported()


	@staticmethod
	def getSize() -> tuple[int, int]:
		"""Get size of the terminal. Columns and rows."""
		if not Term.SUPPORTED:
			return (0, 0)
		return tuple(get_terminal_size())


	# Thanks to https://stackoverflow.com/a/69582478/14546524
	@staticmethod
	def getPos() -> tuple[int, int]:
		"""
		Get the cursor position on the terminal.
		Returns (-1, -1) if not supported.
		"""
		if not Term.SUPPORTED:
			return (-1, -1)
		if sys.platform == "win32":
			OldStdinMode = ctypes.wintypes.DWORD()
			OldStdoutMode = ctypes.wintypes.DWORD()
			kernel32 = ctypes.windll.kernel32
			kernel32.GetConsoleMode(kernel32.GetStdHandle(-10), ctypes.byref(OldStdinMode))
			kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 0)
			kernel32.GetConsoleMode(kernel32.GetStdHandle(-11), ctypes.byref(OldStdoutMode))
			kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
		else:
			OldStdinMode = termios.tcgetattr(sys.stdin)
			_ = termios.tcgetattr(sys.stdin)
			_[3] = _[3] & ~(termios.ECHO | termios.ICANON)
			termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, _)
		try:
			_ = ""
			sys.stdout.write("\x1b[6n")
			sys.stdout.flush()
			while not (_ := _ + sys.stdin.read(1)).endswith('R'):
				pass
			res = re.match(r".*\[(?P<y>\d*);(?P<x>\d*)R", _)
		finally:
			if sys.platform == "win32":
				kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), OldStdinMode)
				kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), OldStdoutMode)
			else:
				termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, OldStdinMode)
		if res:
			return int(res.group("x")), int(res.group("y"))
		return (-1, -1)


	@staticmethod
	def setPos(
		pos: tuple[SupportsInt, SupportsInt],
		offset: tuple[SupportsInt, SupportsInt] = (0, 0)
	) -> str:
		"""
		Position of the cursor on the terminal.
		@pos: Tuple containing the X and Y position values.
		@offset: Offset applied to `pos`. (Can be negative)
		"""
		chkSeqOfLen(pos, 2)

		position = (int(pos[0]) + int(offset[0]),
					int(pos[1]) + int(offset[1]))

		return f"\x1b[{position[1]};{position[0]}f"


	@staticmethod
	def setPosRel(pos: tuple[SupportsInt, SupportsInt]):
		"""
		Move the cursor to a relative position.
		(Shortcut for `Term.moveHoriz` and `Term.moveVert`)
		Negative values are supported.
		"""
		return Term.moveHoriz(int(pos[0]))+ Term.moveVert(int(pos[1]))


	@staticmethod
	def color(color: Optional[Union[tuple[int, int, int], str]], bg: bool = False) -> str:
		"""
		Color of the cursor.
		@color:	Tuple with RGB values, a HTML color name, or a hex string.
		@bg:	This color will be displayed on the background
		"""
		crgb = convertColor(color, "RGB")
		type = 48 if bg else 38

		return f"\x1b[{type};2;{crgb[0]};{crgb[1]};{crgb[2]}m"


	@staticmethod
	def moveHoriz(dist: SupportsInt) -> str:
		"""Move the cursor horizontally `dist` characters (supports negative numbers)."""
		dist = int(dist)
		return f"\x1b[{abs(dist)}{'D' if dist < 0 else 'C'}"


	@staticmethod
	def moveVert(dist: SupportsInt, cr: bool = False) -> str:
		"""
		Move the cursor vertically `dist` lines (supports negative numbers).
		@cr: Do a carriage return too.
		"""
		dist = int(dist)
		return (
			f"\x1b[{abs(dist)}{'A' if dist < 0 else 'B'}"
			if not cr else
			f"\x1b[{abs(dist)}{'F' if dist < 0 else 'E'}"
		)


	@staticmethod
	def clear() -> str:
		"""
		Shortcut for `Term.CLEAR_ALL`, `Term.CLEAR_SCROLL` and `Term.CURSOR_HOME`.
		(Functionally the same as the `clear` command.)
		"""
		return Term.CURSOR_HOME + Term.CLEAR_ALL + Term.CLEAR_SCROLL


	@staticmethod
	def margin(top: SupportsInt = None, bottom: SupportsInt = None) -> str:
		"""Sets the top and bottom margins of the terminal. Use `None` for default margins."""
		return (
			Term.CURSOR_SAVE	# we save and load the cursor because the margins sequence resets the position to 0, 0
			+ f"\x1b[{(int(top) + 1) if top else ''};{(Term.getSize()[1] - int(bottom)) if bottom else ''}r"
			+ Term.CURSOR_LOAD
		)


	@staticmethod
	def scroll(dist: SupportsInt) -> str:
		"""Scrolls the terminal buffer `dist` lines (supports negative numbers)."""
		dist = int(dist)
		return f"\x1b[{abs(dist)}{'T' if dist < 0 else 'S'}"


	@staticmethod
	def fill(char: str) -> str:
		"""Fill the terminal screen with the character specified."""
		ts = Term.getSize()
		return (
			Term.CURSOR_HOME
			+ "".join(Term.setPos((0, row)) + char[0]*ts[0] for row in range(ts[1] + 1))
		)


	class SeqMgr:
		"""
		Context manager for alternating different terminal sequences.
		By default, it changes to a new buffer, moves to the home position, and
		saves the cursor position.
		"""
		def __init__(self,
			newBuffer: bool = True,
			hideCursor: bool = False,
			homeCursor: bool = True,
			saveCursor: bool = True
		) -> None:
			"""
			@newBuffer: Create a new terminal buffer, then go back to the old one.
			@hideCursor: Hide the cursor, then show it.
			@homeCursor: Move the cursor to the top left corner.
			@saveCursor: Save the cursor position, then load it.
			"""
			self.nbuff = newBuffer
			self.hcur = hideCursor
			self.hocur = homeCursor
			self.scur = saveCursor

		def __enter__(self) -> None:
			out(
				(Term.BUFFER_NEW * self.nbuff)
				+ (Term.CURSOR_HIDE * self.hcur)
				+ (Term.CURSOR_SAVE * self.scur)
				+ (Term.CURSOR_HOME * self.hocur)
			)

		def __exit__(self, *args) -> None:
			out(
				(Term.BUFFER_OLD * self.nbuff)
				+ (Term.CURSOR_SHOW * self.hcur)
				+ (Term.CURSOR_LOAD * self.scur)
			)


	class SetScrollLimit:
		"""
		Context manager for setting the vertical scroll limit of the terminal.
		When the cursor reaches this limit, it will scroll the screen buffer up.
		"""
		def __init__(self, limit: int):
			self.limit = limit

		def __enter__(self):
			self.oldLimit = Stdout.scroll_offset
			Stdout.scroll_offset = self.limit

		def __exit__(self, *args):
			Stdout.scroll_offset = self.oldLimit


	@staticmethod
	def formatStr(string: str, reset: bool = True, ignoreBackslashes: bool = False) -> str:  # sourcery no-metrics
		"""
		Add format to the string supplied by wrapping text with special characters and sequences:

		- Text formatting:
		  - `*`: Bold.
		  - `_`: Italic.
		  - `~`: Strikethrough.
		  - `-`: Underline.
		  - `´`: Blink.
		  - `|`: Invert.
		  - `#`: Dim.
		  - `@`: Invisible.

		- Text coloring:
		  - Specify a color by using the `<[mode=]color>` syntax.
			- `mode` should be `fg` (foreground) or `bg` (background). Use this to decide where to apply the color.
			- `color` can be be specified by typing a HTML color name, comma separated RGB values, or a hex string (including `#`).
			- Use `<reset>` to reset the text formatting.

		Note: Some of this sequences might not work properly on some terminal emulators.

		Note: When disabling `Dim`, bold will also be disabled.

		@reset: Will formatting be resetted at the end?
		@ignoreBackslashes: Ignore backslashes in the string.
		"""
		invert = underline = dim = sthrough = invisible = bold = italic = blink = False
		loopSkipChars = 0
		endStr = ""

		for index, char in enumerate(string):
			if loopSkipChars:
				loopSkipChars -= 1
				continue

			if not ignoreBackslashes and char == "\\":
				# skip a character if backslashes are used
				if index == len(string) - 1:
					break
				endStr += string[index + 1]
				loopSkipChars = 1
				continue


			# simply add escape characters depending on the state of each format
			if char == "*":	# bold
				char = Term.NO_BOLD if bold else Term.BOLD
				bold = not bold
			elif char == "_":	# italic
				char = Term.NO_ITALIC if italic else Term.ITALIC
				italic = not italic
			elif char == "~":	# strikethrough
				char = Term.NO_STHROUGH if sthrough else Term.STHROUGH
				sthrough = not sthrough
			elif char == "-":	# underline
				char = Term.NO_UNDERLINE if underline else Term.UNDERLINE
				underline = not underline
			elif char == "´":	# blink
				char = Term.NO_BLINK if blink else Term.BLINK
				blink = not blink
			elif char == "|":	# invert
				char = Term.NO_INVERT if invert else Term.INVERT
				invert = not invert
			elif char == "#":	# dim
				char = Term.NO_DIM if dim else Term.DIM
				dim = not dim
			elif char == "@":	# invisible
				char = Term.NO_INVISIBLE if invisible else Term.INVISIBLE
				invisible = not invisible


			elif char == "<":	# a color sequence is going to be used
				if ">" not in string[index:]:	# if the sequence is not closed, raise error
					raise UnexpectedEndOfStringError(string)
				endIndex = string.index(">", index)	# we get the index of the end of the sequence
				char = Term._parseStrFormatSeq(string[index + 1:endIndex])	# parse the sequence
				loopSkipChars = endIndex - index	# we now tell the loop to skip the parsed text

			endStr += char

		return endStr + (Term.RESET if reset else "")


	@staticmethod
	def _parseStrFormatSeq(seq: str) -> str:
		"""Convert a string color format (`([bg=]color)|reset`) to a terminal sequence."""

		seq = seq.replace("<", "").replace(">", "")	# remove any possible <> characters

		if seq == "reset":
			return Term.RESET

		mode, color = ("fg", seq) if "=" not in seq else seq.split("=")	# if there is no equal sign, the mode is foreground
		isBg = mode == "bg"

		if "," in color:	# found a comma. We are dealing with RGB values
			return Term.color(
				tuple(map(int, color.split(",")))[:3],
				isBg
			)
		elif "#" in color or color in _HTML_COLOR_NAMES:	# its a hex color or a HTML color name
			return Term.color(color, isBg)
		else:
			return ""	# invalid color format


	@staticmethod
	def flash(times: int = 1, delay: float = 0.1) -> None:
		"""
		Flash the terminal screen.
		@times: How many times to flash the screen.
		@delay: Delay between flashes. In seconds.
		"""
		for t in range(times):
			out(Term.INVERT_ALL)
			sleep(delay)
			out(Term.NO_INVERT_ALL)
			if t != times - 1:	sleep(delay)


	# simple sequences that dont require parsing
	# text formatting
	INVERT: str = "\x1b[7m"
	NO_INVERT: str = "\x1b[27m"
	UNDERLINE: str = "\x1b[4m"
	NO_UNDERLINE: str = "\x1b[24m"
	DIM: str = "\x1b[2m"
	NO_DIM: str = "\x1b[22m"
	STHROUGH: str = "\x1b[9m"
	NO_STHROUGH: str = "\x1b[29m"
	INVISIBLE: str = "\x1b[8m"
	NO_INVISIBLE: str = "\x1b[28m"
	BOLD: str = "\x1b[1m"
	NO_BOLD: str = "\x1b[22m"
	ITALIC: str = "\x1b[3m"
	NO_ITALIC: str = "\x1b[23m"
	BLINK: str = "\x1b[5m"
	NO_BLINK: str = "\x1b[25m"
	RESET: str = "\x1b[0m"

	# special
	CLEAR_LINE: str = "\x1b[2K"
	CLEAR_RIGHT: str = "\x1b[0K"
	CLEAR_LEFT: str = "\x1b[1K"
	CLEAR_DOWN: str = "\x1b[0J"
	CLEAR_ALL: str = "\x1b[2J"
	CLEAR_SCROLL: str = "\x1b[3J"
	CURSOR_SHOW: str = "\x1b[?25h"
	CURSOR_HIDE: str = "\x1b[?25l"
	CURSOR_SAVE: str = "\x1b7"
	CURSOR_LOAD: str = "\x1b8"
	BUFFER_NEW: str = "\x1b[?1049h"
	BUFFER_OLD: str = "\x1b[?1049l"
	CURSOR_HOME: str = "\x1b[H"
	INVERT_ALL: str = "\x1b[?5h"
	NO_INVERT_ALL: str ="\x1b[?5l"