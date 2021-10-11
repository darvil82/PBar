from typing import TypeVar, Optional, Union, Any, SupportsInt


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

def capValue(value: Num, max: Optional[Num] = None, min: Optional[Num] = None) -> Num:
	"""Clamp a value to a minimum and/or maximum value."""
	if max is not None and value > max:
		return max
	elif min is not None and value < min:
		return min
	else:
		return value


def convertClrs(clr: dict[Any, Union[str, tuple]], type: str) -> Union[str, tuple, dict, None]:
	"""Convert color values to HEX and vice-versa
	@clr:	Color value to convert.
	@type:	Type of conversion to do ('RGB' or 'HEX')"""

	if isinstance(clr, dict):
		return {key: convertClrs(value, type) for key, value in clr.items()}
	elif isinstance(clr, str):
		color = clr.lower()
		if color in _HTML_COLOR_NAMES:	color = _HTML_COLOR_NAMES[color]

	if type == "RGB":
		if not isinstance(color, str) or not color.startswith("#"):
			return color

		clrs = color.lstrip("#")

		if len(clrs) == 3:
			clrs = "".join(c*2 for c in clrs)

		try:
			return tuple(int(clrs[i:i+2], 16) for i in (0, 2, 4))
		except ValueError:
			return color
	elif type == "HEX":
		if not isinstance(color, (tuple, list)) or len(color) != 3: return color

		capped = tuple(capValue(value, 255, 0) for value in color)
		return f"#{capped[0]:02x}{capped[1]:02x}{capped[2]:02x}"


def chkSeqOfLen(obj: Any, length: int) -> bool:
	"""Check if an object is a Sequence and has the length specified. If fails, raises exceptions."""
	isInstOf(obj, tuple, list)
	if len(obj) != length:
		raise ValueError(f"Sequence {obj!r} must have {length} items")
	return True


def isInstOf(obj: Any, *typ: Any, name: str = None) -> bool:
	"""Check if an object is an instance of any of the other objects specified. If fails, raises exception."""
	if not isinstance(obj, typ):
		raise TypeError(
			(name or f"Value {VT100.color((255, 150, 0))}{obj!r}{VT100.RESET}")
			+ " must be " + ' or '.join(VT100.color((0, 255, 0)) + x.__name__ + VT100.RESET for x in typ)
			+ ", not " + VT100.color((255, 0, 0)) + obj.__class__.__name__ + VT100.RESET
		)
	return True




class VT100:
	"""Class for using VT100 sequences a bit easier"""

	@staticmethod
	def pos(pos: Optional[tuple[SupportsInt, SupportsInt]], offset: tuple[SupportsInt, SupportsInt] = (0, 0)):
		"""Position of the cursor on the terminal.
		@pos: This tuple can contain either ints, or strings with the value `center` to specify the center of the terminal.
		@offset: Offset applied to `pos`. (Can be negative)
		"""
		chkSeqOfLen(pos, 2)

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

		crgb = [capValue(value, 255, 0) for value in rgb]

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