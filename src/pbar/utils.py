from io import TextIOWrapper
from os import system as runsys, get_terminal_size, isatty
from time import sleep
from dataclasses import dataclass
import sys, re
if sys.platform == "win32":
	import ctypes
	from ctypes import wintypes
else:
	import termios
from typing import (
	Callable,
	Sequence,
	SupportsFloat,
	TypeVar,
	Optional,
	Union,
	Any,
	SupportsInt
)

__all__ = (
	"cap_value", "get_constant_attrs", "strip_text",
	"convert_color", "chk_inst_of", "chk_seq_of_len",
	"is_num", "out", "map_dict", "Term"
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
	def __init__(self, string, expected_char=">") -> None:
		super().__init__(
			"Unexpected end of string. ('" + string
			+ Term.style_format(f"<bg=150,0,0>*◄ Expected '{expected_char}'<reset>')")
		)


Num = TypeVar("Num", int, float)

def cap_value(value: Num, max: Num = None, min: Num = None) -> Num:
	"""Clamp a value to a minimum and/or maximum value."""
	if max is not None and value > max:
		return max
	elif min is not None and value < min:
		return min
	else:
		return value


def get_constant_attrs(obj: Any) -> tuple:
	"""Get the constant attributes of an object. (Uppercase attrs)"""
	return tuple(a for a in dir(obj) if a.isupper())


def strip_text(string: str, max_len: int, end_str: str = "…") -> str:
	"""
	Return a cutted string at the end if the len of it is larger than
	the maxlen specified.
	@string: the string to cut
	@maxlen: the maximum length of the string
	@endStr: the string to add at the end of the cutted string
	"""
	if max_len < (end_len := len(end_str)):
		return ""
	return string[:max_len-end_len] + end_str if len(string) > max_len else string


def convert_color(clr: Color, conversion: str) -> Union[str, tuple]:
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

		capped = tuple(cap_value(value, 255, 0) for value in color)
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


def chk_seq_of_len(obj: Any, length: Union[int, range], name: str = None) -> bool:
	"""
	Check if an object is a Sequence and has the length specified.
	If fails, raises exception (`Sequence obj | name must have len items`).
	"""
	chk_inst_of(obj, tuple, list, name=name)
	obj_len, is_range = len(obj), isinstance(length, range)
	is_valid = obj_len in length if is_range else obj_len == length

	if is_valid:
		return True

	name = name or f"Sequence {obj!r}"
	raise ValueError(
		Term.color("orange") + name + Term.RESET
		+ Term.style_format(
			f" must have <lime>{length if not is_range else f'{length.start} to {length.stop - 1}'}<reset> items, "
			+ f"not <red>{obj_len}<reset>"
		)
	)


def chk_inst_of(obj: Any, *typ: Any, name: str = None) -> bool:
	"""
	Check if an object is an instance of any of the other objects specified.
	If fails, raises exception (`Value | name must be *typ, not obj`).
	"""
	if isinstance(obj, typ):
		return True

	name = name or f"Value {obj!r}"
	raise TypeError(Term.style_format(
		Term.color("orange") + name + Term.RESET
		+ f" must be {' or '.join(Term.style_format(f'<lime>{x.__name__}<reset>') for x in typ)}"
		+ f", not <red>{obj.__class__.__name__}<reset>"
	))


def is_num(obj: SupportsFloat) -> bool:
	"""Return True if `obj` can be casted to float."""
	try:
		float(obj)
	except (ValueError, TypeError):
		return False
	return True


def out(*obj, end: str = "", sep: str = "", file=None):
	"""Print to stdout."""
	if file is None:
		file = sys.stdout
	file.write(sep.join(str(x) for x in obj) + end)
	file.flush()


def map_dict(dictionary: dict, func: Callable) -> dict:
	"""
	Return dict with all values in it used as an arg for a function that will return a new value for it.
	@func: This represents the callable that accepts an argument.

	Example:
	>>> map_dict(lambda val: myFunc("stuff", val), {1: "a", 2: "b", 3: "c"})
	"""
	return {
		key: map_dict(value, func) if isinstance(value, dict) else func(value)
		for key, value in dictionary.items()
	}




class Stdout(TextIOWrapper):
	"""
	A class that may override stdout.
	Keeps track of the number of newlines sent.
	"""
	triggers: list[Callable] = []
	scroll_offset: int = 0
	always_check: bool = False
	enabled: bool = True

	def __init__(self, stdout: TextIOWrapper) -> None:
		super().__init__(stdout, encoding=stdout.encoding)
		self.original = stdout

	def write(self, s: str) -> None:
		"""
		Writes the given string to the terminal.
		@s: String to write.
		"""
		s = str(s)

		"""
		We check if the string contains newlines, and if it does, check if the
		cursor is positioned at the end of the terminal. If it is, we call each
		trigger with the number of newlines in the string.
		"""

		if (
			(count := sum(s.count(c) for c in "\n\v\f") or Stdout.always_check)
			and Term.SUPPORTED	# only check if terminal is supported
			and Stdout.triggers	# only if we have triggers
			and Stdout.enabled	# only if enabled
		):
			c_pos, t_size, offset = (
				Term.get_pos(file=self.original)[1],
				Term.get_size()[1],
				max(Stdout.scroll_offset, 0) + 1
			)
			if c_pos >= t_size - offset:
				if offset:
					out("\v"*offset + Term.move_vert(-offset), file=self.original)
				for t in Stdout.triggers:
					# we take into account the possible exceeding of the the max size
					t(count + (c_pos - (t_size - offset)) - 1)

		self.original.write(s)

	def flush(self):
		"""Flushes the stdout buffer."""
		self.original.flush()

	@staticmethod
	def add_trigger(func: Callable[[int], None]) -> Callable[[int], None]:
		"""
		Register a trigger that will be called when the terminal screen is scrolled.
		@func: The function to be called when the buffer is scrolled.

		Returns the index of the trigger in the Stdout triggers property.
		"""
		if not Stdout.enabled:
			return func
		if len(triggers := Stdout.triggers) >= 1000:	# prevent memory overflow
			del triggers[0]
		Stdout.triggers.append(func)
		if Term.SUPPORTED:
			out("\v" + Term.move_vert(-1))	# HACK: doing this to trigger the Stdout detector
		return func




class Term:
	"""Class for using terminal sequences a bit easier"""
	runsys("")		# We need to do this, otherwise Windows won't display special VT100 sequences

	def _is_supported() -> bool:
		"""Return False if terminal is not supported."""
		try:
			get_terminal_size()
		except OSError:
			return False

		return isatty(0)

	SUPPORTED = _is_supported()


	@staticmethod
	def get_size() -> tuple[int, int]:
		"""Get size of the terminal. Columns and rows."""
		return (0, 0) if not Term.SUPPORTED else tuple(get_terminal_size())


	# Thanks to https://stackoverflow.com/a/69582478/14546524
	@staticmethod
	def get_pos(*, file=None) -> tuple[int, int]:
		"""
		Get the cursor position on the terminal.
		Returns (-1, -1) if not supported.
		"""
		if file is None:
			file = sys.stdout
		if not Term.SUPPORTED:
			return (-1, -1)
		if sys.platform == "win32":
			old_stdin_mode = ctypes.wintypes.DWORD()
			old_stdout_mode = ctypes.wintypes.DWORD()
			kernel32 = ctypes.windll.kernel32
			kernel32.GetConsoleMode(kernel32.GetStdHandle(-10), ctypes.byref(old_stdin_mode))
			kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 0)
			kernel32.GetConsoleMode(kernel32.GetStdHandle(-11), ctypes.byref(old_stdout_mode))
			kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
		else:
			old_stdin_mode = termios.tcgetattr(sys.stdin)
			_ = termios.tcgetattr(sys.stdin)
			_[3] = _[3] & ~(termios.ECHO | termios.ICANON)
			termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, _)
		try:
			_ = ""
			file.write("\x1b[6n")
			file.flush()
			while not (_ := _ + sys.stdin.read(1)).endswith('R'):
				pass
			res = re.match(r".*\[(?P<y>\d*);(?P<x>\d*)R", _)
		finally:
			if sys.platform == "win32":
				kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), old_stdin_mode)
				kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), old_stdout_mode)
			else:
				termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, old_stdin_mode)
		if res:
			return int(res.group("x")), int(res.group("y"))
		return (-1, -1)


	@staticmethod
	def set_pos(
		pos: tuple[SupportsInt, SupportsInt],
		offset: tuple[SupportsInt, SupportsInt] = (0, 0)
	) -> str:
		"""
		Position of the cursor on the terminal.
		@pos: Tuple containing the X and Y position values.
		@offset: Offset applied to `pos`. (Can be negative)
		"""
		chk_seq_of_len(pos, 2)

		position = (int(pos[0]) + int(offset[0]),
					int(pos[1]) + int(offset[1]))

		return f"\x1b[{position[1]};{position[0]}f"


	@staticmethod
	def set_pos_rel(pos: tuple[SupportsInt, SupportsInt]):
		"""
		Move the cursor to a relative position.
		(Shortcut for `Term.moveHoriz` and `Term.moveVert`)
		Negative values are supported.
		"""
		return Term.move_horiz(int(pos[0]))+ Term.move_vert(int(pos[1]))


	@staticmethod
	def color(color: Optional[Union[tuple[int, int, int], str]], bg: bool = False) -> str:
		"""
		Color of the cursor.
		@color:	Tuple with RGB values, a HTML color name, or a hex string.
		@bg:	This color will be displayed on the background
		"""
		crgb = convert_color(color, "RGB")
		type = 48 if bg else 38

		return f"\x1b[{type};2;{crgb[0]};{crgb[1]};{crgb[2]}m"


	@staticmethod
	def move_horiz(dist: SupportsInt) -> str:
		"""Move the cursor horizontally `dist` characters (supports negative numbers)."""
		dist = int(dist)
		return f"\x1b[{abs(dist)}{'D' if dist < 0 else 'C'}"


	@staticmethod
	def move_vert(dist: SupportsInt, cr: bool = False) -> str:
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
			+ f"\x1b[{(int(top) + 1) if top else ''};{(Term.get_size()[1] - int(bottom)) if bottom else ''}r"
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
		ts = Term.get_size()
		return (
			Term.CURSOR_HOME
			+ "".join(Term.set_pos((0, row)) + char[0]*ts[0] for row in range(ts[1] + 1))
		)


	@staticmethod
	def set_scroll_limit(limit: int, always_check: bool = False):
		"""
		Set the vertical scroll limit of the terminal.
		When the cursor reaches this limit, it will scroll the screen buffer up.
		@limit: The vertical scroll limit.
		@always_check: If `True`, the cursor position will be checked each time
		text is sent to stdout (slower). Otherwise, only when a newline occurs (faster).
		"""
		Stdout.scroll_offset = limit
		Stdout.always_check = always_check


	@dataclass
	class SeqMgr:
		"""Context manager for alternating different terminal sequences."""
		new_buffer: bool = False
		hide_cursor: bool = False
		home_cursor: bool = False
		save_cursor: bool = False
		margin: tuple[Optional[int], Optional[int]] = None
		scroll_limit: Optional[int] = None

		def __enter__(self) -> None:
			out(
				(Term.BUFFER_NEW * self.new_buffer)
				+ (Term.CURSOR_HIDE * self.hide_cursor)
				+ (Term.CURSOR_SAVE * self.save_cursor)
				+ (Term.CURSOR_HOME * self.home_cursor)
				+ (Term.margin(self.margin[0], self.margin[1]) if self.margin else "")
			)
			if self.scroll_limit:
				self.old_limit = Stdout.scroll_offset
				Term.set_scroll_limit(self.scroll_limit)

		def __exit__(self, *args) -> None:
			out(
				(Term.BUFFER_OLD * self.new_buffer)
				+ (Term.CURSOR_SHOW * self.hide_cursor)
				+ (Term.CURSOR_LOAD * self.save_cursor)
				+ (Term.margin() * bool(self.margin))
			)
			if self.scroll_limit:
				Term.set_scroll_limit(self.old_limit)


	@staticmethod
	def style_format(string: str, reset: bool = True, ignore_backslashes: bool = False) -> str:  # sourcery no-metrics
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

		@string: The string to format.
		@reset: Will formatting be resetted at the end?
		@ignore_backslashes: Ignore backslashes in the string.
		"""
		invert = underline = dim = sthrough = invisible = bold = italic = blink = False
		loop_skip_chars = 0
		end_str = ""

		for index, char in enumerate(string):
			if loop_skip_chars:
				loop_skip_chars -= 1
				continue

			if not ignore_backslashes and char == "\\":
				# skip a character if backslashes are used
				if index == len(string) - 1:
					break
				end_str += string[index + 1]
				loop_skip_chars = 1
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
				end_index = string.index(">", index)	# we get the index of the end of the sequence
				char = Term._parse_str_formatting(string[index + 1:end_index])	# parse the sequence
				loop_skip_chars = end_index - index	# we now tell the loop to skip the parsed text

			end_str += char

		return end_str + (Term.RESET if reset else "")


	@staticmethod
	def _parse_str_formatting(seq: str) -> str:
		"""Convert a string color format (`([bg=]color)|reset`) to a terminal sequence."""

		seq = seq.replace("<", "").replace(">", "")	# remove any possible <> characters

		if seq == "reset":
			return Term.RESET

		mode, color = ("fg", seq) if "=" not in seq else seq.split("=")	# if there is no equal sign, the mode is foreground
		is_bg = mode == "bg"

		if "," in color:	# found a comma. We are dealing with RGB values
			return Term.color(
				tuple(map(int, color.split(",")))[:3],
				is_bg
			)
		elif "#" in color or color in _HTML_COLOR_NAMES:	# its a hex color or a HTML color name
			return Term.color(color, is_bg)
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
