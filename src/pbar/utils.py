from typing import Callable, Literal, SupportsFloat, TypeVar, Optional, Union, Any, SupportsInt
from os import get_terminal_size

__all__ = (
	"capValue", "convertClrs", "chkInstOf",
	"chkSeqOfLen", "isNum", "mapDict", "Term"
)



_HTML_COLOR_NAMES: dict = {		# thanks to https://stackoverflow.com/a/1573141/14546524
	"aliceblue":"#f0f8ff", "antiquewhite":"#faebd7", "aqua":"#00ffff", "aquamarine":"#7fffd4", "azure":"#f0ffff",
	"beige":"#f5f5dc", "bisque":"#ffe4c4", "black":"#000000", "blanchedalmond":"#ffebcd", "blue":"#0000ff", "blueviolet":"#8a2be2", "brown":"#a52a2a", "burlywood":"#deb887",
	"cadetblue":"#5f9ea0", "chartreuse":"#7fff00", "chocolate":"#d2691e", "coral":"#ff7f50", "cornflowerblue":"#6495ed", "cornsilk":"#fff8dc", "crimson":"#dc143c", "cyan":"#00ffff",
	"darkblue":"#00008b", "darkcyan":"#008b8b", "darkgoldenrod":"#b8860b", "darkgray":"#a9a9a9", "darkgreen":"#006400", "darkkhaki":"#bdb76b", "darkmagenta":"#8b008b", "darkolivegreen":"#556b2f",
	"darkorange":"#ff8c00", "darkorchid":"#9932cc", "darkred":"#8b0000", "darksalmon":"#e9967a", "darkseagreen":"#8fbc8f", "darkslateblue":"#483d8b", "darkslategray":"#2f4f4f", "darkturquoise":"#00ced1",
	"darkviolet":"#9400d3", "deeppink":"#ff1493", "deepskyblue":"#00bfff", "dimgray":"#696969", "dodgerblue":"#1e90ff",
	"firebrick":"#b22222", "floralwhite":"#fffaf0", "forestgreen":"#228b22", "fuchsia":"#ff00ff",
	"gainsboro":"#dcdcdc", "ghostwhite":"#f8f8ff", "gold":"#ffd700", "goldenrod":"#daa520", "gray":"#808080", "green":"#008000", "greenyellow":"#adff2f",
	"honeydew":"#f0fff0", "hotpink":"#ff69b4",
	"indianred":"#cd5c5c", "indigo":"#4b0082", "ivory":"#fffff0", "khaki":"#f0e68c",
	"lavender":"#e6e6fa", "lavenderblush":"#fff0f5", "lawngreen":"#7cfc00", "lemonchiffon":"#fffacd", "lightblue":"#add8e6", "lightcoral":"#f08080", "lightcyan":"#e0ffff", "lightgoldenrodyellow":"#fafad2",
	"lightgrey":"#d3d3d3", "lightgreen":"#90ee90", "lightpink":"#ffb6c1", "lightsalmon":"#ffa07a", "lightseagreen":"#20b2aa", "lightskyblue":"#87cefa", "lightslategray":"#778899", "lightsteelblue":"#b0c4de",
	"lightyellow":"#ffffe0", "lime":"#00ff00", "limegreen":"#32cd32", "linen":"#faf0e6",
	"magenta":"#ff00ff", "maroon":"#800000", "mediumaquamarine":"#66cdaa", "mediumblue":"#0000cd", "mediumorchid":"#ba55d3", "mediumpurple":"#9370d8", "mediumseagreen":"#3cb371", "mediumslateblue":"#7b68ee",
	"mediumspringgreen":"#00fa9a", "mediumturquoise":"#48d1cc", "mediumvioletred":"#c71585", "midnightblue":"#191970", "mintcream":"#f5fffa", "mistyrose":"#ffe4e1", "moccasin":"#ffe4b5",
	"navajowhite":"#ffdead", "navy":"#000080",
	"oldlace":"#fdf5e6", "olive":"#808000", "olivedrab":"#6b8e23", "orange":"#ffa500", "orangered":"#ff4500", "orchid":"#da70d6",
	"palegoldenrod":"#eee8aa", "palegreen":"#98fb98", "paleturquoise":"#afeeee", "palevioletred":"#d87093", "papayawhip":"#ffefd5", "peachpuff":"#ffdab9", "peru":"#cd853f", "pink":"#ffc0cb", "plum":"#dda0dd", "powderblue":"#b0e0e6", "purple":"#800080",
	"rebeccapurple":"#663399", "red":"#ff0000", "rosybrown":"#bc8f8f", "royalblue":"#4169e1",
	"saddlebrown":"#8b4513", "salmon":"#fa8072", "sandybrown":"#f4a460", "seagreen":"#2e8b57", "seashell":"#fff5ee", "sienna":"#a0522d", "silver":"#c0c0c0", "skyblue":"#87ceeb", "slateblue":"#6a5acd", "slategray":"#708090", "snow":"#fffafa", "springgreen":"#00ff7f", "steelblue":"#4682b4",
	"tan":"#d2b48c", "teal":"#008080", "thistle":"#d8bfd8", "tomato":"#ff6347", "turquoise":"#40e0d0",
	"violet":"#ee82ee",
	"wheat":"#f5deb3", "white":"#ffffff", "whitesmoke":"#f5f5f5",
	"yellow":"#ffff00", "yellowgreen":"#9acd32"
}


Num = TypeVar("Num", int, float)

def capValue(value: Num, max: Num=None, min: Num=None) -> Num:
	"""Clamp a value to a minimum and/or maximum value."""
	if max is not None and value > max:
		return max
	elif min is not None and value < min:
		return min
	else:
		return value


def convertClrs(clr: Union[dict[Any, Union[str, tuple]], str, tuple], type: str) -> Union[str, tuple, dict, None]:
	"""
	Convert color values to HEX and vice-versa
	@clr:	Color value to convert.
	@type:	Type of conversion to do ('RGB' or 'HEX')
	"""
	if isinstance(clr, dict):	# its a dict, call itself with the value
		return {key: convertClrs(value, type) for key, value in clr.items()}
	elif isinstance(clr, str):
		color = clr.lower()
		if color in _HTML_COLOR_NAMES:	color = _HTML_COLOR_NAMES[color]	# check if its a html color name
	else:
		color = clr

	if type == "HEX":
		if not isinstance(color, (tuple, list)) or len(color) != 3: return color

		capped = tuple(capValue(value, 255, 0) for value in color)
		return f"#{capped[0]:02x}{capped[1]:02x}{capped[2]:02x}"
	elif type == "RGB":
		if not isinstance(color, str) or not color.startswith("#"):
			return color

		clrs = color.lstrip("#")

		if len(clrs) == 3:
			clrs = "".join(c*2 for c in clrs)	# if size of hex color is 3, just duplicate chars to make it 6

		try:
			return tuple(int(clrs[i:i+2], 16) for i in (0, 2, 4))
		except ValueError:
			return color
	else:
		return ""


def chkSeqOfLen(obj: Any, length: int, name: str=None) -> bool:
	"""
	Check if an object is a Sequence and has the length specified.
	If fails, raises exception (`Sequence obj | name must have len items`).
	"""
	chkInstOf(obj, tuple, list)
	if len(obj) != length:
		raise ValueError(
			(name or f"Sequence {Term.color((255, 150, 0))}{obj!r}{Term.RESET}")
			+ " must have " + Term.color((0, 255, 0)) + str(length) + Term.RESET + " items, "
			+ "not " + Term.color((255, 0, 0)) + str(len(obj)) + Term.RESET
		)
	return True


def chkInstOf(obj: Any, *typ: Any, name: str=None) -> bool:
	"""
	Check if an object is an instance of any of the other objects specified.
	If fails, raises exception (`Value | name must be *typ, not obj`).
	"""
	if not isinstance(obj, typ):
		raise TypeError(
			(name or f"Value {Term.color((255, 150, 0))}{obj!r}{Term.RESET}")
			+ " must be " + ' or '.join(Term.color((0, 255, 0)) + x.__name__ + Term.RESET for x in typ)
			+ ", not " + Term.color((255, 0, 0)) + obj.__class__.__name__ + Term.RESET
		)
	return True


def isNum(obj: SupportsFloat) -> bool:
	"""Return True if `obj` can be casted to float."""
	try:
		float(obj)
	except ValueError:
		return False
	return True


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




class Term:
	"""Class for using terminal sequences a bit easier"""
	@staticmethod
	def size() -> Union[tuple[int, int], Literal[False]]:
		"""
		Get size of the terminal. Columns and rows.
		`False` will be returned if it is not possible to get the size.
		"""
		try:
			return tuple(get_terminal_size())
		except OSError:
			return False


	@staticmethod
	def pos(pos: tuple[SupportsInt, SupportsInt],
			offset: tuple[SupportsInt, SupportsInt]=(0, 0)) -> str:
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
	def posRel(pos: tuple[SupportsInt, SupportsInt]):
		"""
		Move the cursor to a relative position.
		(Shortcut for `Term.moveHoriz` and `Term.moveVert`)
		Negative values are supported.
		"""
		return Term.moveHoriz(int(pos[0]))+ Term.moveVert(int(pos[1]))


	@staticmethod
	def color(rgb: Optional[tuple[int, int, int]], bg: bool=False) -> str:
		"""
		Color of the cursor.
		@rgb:	Tuple with three values from 0 to 255. (RED GREEN BLUE)
		@bg:	This color will be displayed on the background
		"""
		if not isinstance(rgb, (tuple, list)):
			return Term.RESET
		elif len(rgb) != 3:
			raise ValueError("Sequence must have 3 items")

		crgb = [capValue(value, 255, 0) for value in rgb]

		type = 48 if bg else 38
		return f"\x1b[{type};2;{crgb[0]};{crgb[1]};{crgb[2]}m"


	@staticmethod
	def moveHoriz(dist: SupportsInt) -> str:
		"""Move the cursor horizontally `dist` characters (supports negative numbers)."""
		dist = int(dist)
		return f"\x1b[{abs(dist)}{'D' if dist < 0 else 'C'}"


	@staticmethod
	def moveVert(dist: SupportsInt, cr: bool=False) -> str:
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
	def margin(top: SupportsInt=None, bottom: SupportsInt=None) -> str:
		"""Sets the top and bottom margins of the terminal. Use `None` for default margins."""
		return (
			Term.CURSOR_SAVE	# we save and load the cursor because the margins sequence resets the position to 0, 0
			+ f"\x1b[{(int(top) + 1) if top else ''};{(Term.size()[1] - int(bottom)) if bottom else ''}r"
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
		ts = Term.size()
		return (
			Term.CURSOR_HOME
			+ "".join(Term.pos((0, row)) + char[0]*ts[0] for row in range(ts[1] + 1))
		)


	class NewBuffer:
		"""
		Context manager for changing to an alternate buffer, and returning to the original when finishing.
		(This basically prints `Term.BUFFER_NEW` and `Term.BUFFER_OLD`)
		"""
		def __init__(self, hideCursor: bool=False) -> None:
			self.hcur = hideCursor
		def __enter__(self) -> str:
			print(Term.BUFFER_NEW + (Term.CURSOR_HIDE if self.hcur else ""), end="")
		def __exit__(self, type, value, traceback) -> None:
			print(Term.BUFFER_OLD + (Term.CURSOR_SHOW if self.hcur else ""), end="")


	@staticmethod
	def formatString(string: str, reset: bool=True) -> str:  # sourcery no-metrics
		"""
		Add format to the string supplied by wrapping text with special characters:

		- `*`: Bold.
		- `_`: Italic.
		- `~`: Strikethrough.
		- `-`: Underline.
		- `´`: Blink.
		- `|`: Invert.
		- `#`: Dim.
		- `@`: Invisible.

		Note: Some of this sequences might not work properly on some terminal emulators.

		Note: When disabling `Dim`, bold will also be disabled.

		@reset: Will formatting be resetted at the end?
		"""
		invert = underline = dim = sthrough = invisible = bold = italic = blink = False
		ignoreChar = False
		endStr = ""
		for char in string:
			# skip a character if backslashes are used
			if char == "\\":
				ignoreChar = True
				continue
			if ignoreChar:
				endStr += char
				ignoreChar = False
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
			endStr += char
		return endStr + (Term.RESET if reset else "")


	# simple sequences that dont require parsing
	# text formatting
	INVERT: str =		"\x1b[7m"
	NO_INVERT: str =	"\x1b[27m"
	UNDERLINE: str =	"\x1b[4m"
	NO_UNDERLINE: str =	"\x1b[24m"
	DIM: str =			"\x1b[2m"
	NO_DIM: str =		"\x1b[22m"
	STHROUGH: str = 	"\x1b[9m"
	NO_STHROUGH: str = 	"\x1b[29m"
	INVISIBLE: str =	"\x1b[8m"
	NO_INVISIBLE: str =	"\x1b[28m"
	BOLD: str =			"\x1b[1m"
	NO_BOLD: str =		"\x1b[22m"
	ITALIC: str =		"\x1b[3m"
	NO_ITALIC: str =	"\x1b[23m"
	BLINK: str =		"\x1b[5m"
	NO_BLINK: str =		"\x1b[25m"
	RESET: str =		"\x1b[0m"

	# special
	CLEAR_LINE: str =	"\x1b[2K"
	CLEAR_RIGHT: str =	"\x1b[0K"
	CLEAR_LEFT: str =	"\x1b[1K"
	CLEAR_DOWN: str =	"\x1b[0J"
	CLEAR_ALL: str =	"\x1b[2J"
	CLEAR_SCROLL: str =	"\x1b[3J"
	CURSOR_SHOW: str =	"\x1b[?25h"
	CURSOR_HIDE: str =	"\x1b[?25l"
	CURSOR_SAVE: str =	"\x1b7"
	CURSOR_LOAD: str =	"\x1b8"
	BUFFER_NEW: str =	"\x1b[?1049h"
	BUFFER_OLD: str =	"\x1b[?1049l"
	CURSOR_HOME: str =	"\x1b[H"