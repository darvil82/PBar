from typing import TypeVar, Optional, Union, Any, SupportsInt


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

		capped = tuple(capValue(value, 255, 0) for value in clr)
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