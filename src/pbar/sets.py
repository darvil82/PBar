import time
from typing import Callable, Optional, Union
from . import utils, bar
from . utils import Term



ColorSetEntry = dict[str, Union["ColorSetEntry", utils.Color]]	# type: ignore
CharSetEntry = dict[str, Union["CharSetEntry", str]]		# type: ignore
FormatSetEntry = dict[str, Union["FormatSetEntry", str]]	# type: ignore


_IGNORE_CHARS = "\x1b\n\r\b\a\f\v"


class UnknownSetKeyError(Exception):
	"""A key supplied in a dictionary is unknown for the set class that will use it"""
	def __init__(self, key, set_obj) -> None:
		msg = f"Unknown key {key!r} for {set_obj.__class__.__name__!r}"
		set_keys = "', '".join(set_obj.EMPTY)
		super().__init__(f"{msg}. Available valid keys: '{set_keys}'.")


class _BaseSet(dict):
	"""Base class for all the customizable sets for the bar (colorset, charset, formatset)"""
	EMPTY: dict = {}

	def __init__(self, new_set: dict) -> None:
		utils.chk_inst_of(new_set, dict, name="new_set")
		super().__init__(self._populate(self.EMPTY | new_set))


	def __repr__(self) -> str:
		return f"{self.__class__.__name__}({dict(self)})"


	def _populate(self, current_set: dict) -> dict:		# ?: Needs a proper rewrite if we end up needing more subdicts
		"""
		Return a new set with all the necessary keys for drawing the bar,
		making sure that no keys are missing.
		"""
		new_set = {}
		for key, currentValue in current_set.items():
			if key not in self.EMPTY:
				raise UnknownSetKeyError(key, self)

			default_set_value = self.EMPTY[key]

			if not isinstance(currentValue, dict) and isinstance(default_set_value, dict):
				new_set[key] = {subkey: currentValue for subkey in default_set_value}
			elif isinstance(currentValue, dict) and isinstance(default_set_value, dict):
				new_set[key] = default_set_value | currentValue
			else:
				new_set[key] = currentValue

		return new_set


	def map_values(self, func: Callable) -> dict:
		"""Return a dict mapped the values of the set to a function."""
		return utils.map_dict(self, func)




class ColorSet(_BaseSet):
	"""Container for the color sets."""

	EMPTY: ColorSetEntry = {
		"empty": "white",
		"full": "white",
		"vert":	{
			"left": "white",
			"right": "white"
		},
		"horiz": {
			"top": "white",
			"bottom": "white"
		},
		"corner": {
			"tleft": "white",
			"tright": "white",
			"bleft": "white",
			"bright": "white",
		},
		"text":	{
			"inside": "white",
			"right": "white",
			"left": "white",
			"title": "white",
			"subtitle": "white"
		}
	}

	DEFAULT: ColorSetEntry = {
		"full": "#15F28D",
		"empty": "#FF4D4D",
	}

	DARVIL: ColorSetEntry = {
		"empty": "#0067c2",
		"full": "springGreen",
		"vert": "#f76f98",
		"horiz": "#f76f98",
		"corner": "#f76f98",
		"text": {
			"right": "springGreen",
			"title": "#f76f98",
			"subtitle": "#f76f98",
			"left": "springGreen",
			"inside": "springGreen"
		}
	}

	RED: ColorSetEntry = {
		"empty": "darkRed",
		"full": "red",
		"vert": "#ff6464",
		"horiz": "#ff6464",
		"corner": "#ff6464",
		"text": "#ff6464",
	}

	GREEN: ColorSetEntry = {
		"full": "lime",
		"empty": "green",
		"horiz": "paleGreen",
		"corner": "paleGreen",
		"vert": "paleGreen",
		"text": "lime",
	}

	YELLOW: ColorSetEntry = {
		"full": "yellow",
		"empty": "#a77227",
		"horiz": "#dab77b",
		"vert": "#dab77b",
		"corner": "#dab77b",
		"text": "#dab77b",
	}

	FLAG_ES: ColorSetEntry = {
		"corner": "red",
		"horiz": "red",
		"vert": "yellow",
		"full": "yellow",
		"empty": "#9a7600",
		"text": {
			"inside": "yellow",
			"right": "yellow",
			"left": "yellow",
			"title": "red",
			"subtitle": "red",
		},
	}

	FLAG_LESBIAN: ColorSetEntry = {  # Author: ShygalCoco
		"empty": "#777",
		"horiz": {
			"top": "#ff9879",
			"bottom": "#e57bb9"
		},
		"corner": {
			"tleft": "#ff9879",
			"tright": "#ff9879",
			"bleft": "#e57bb9",
			"bright": "#e57bb9",
		},
		"text": {
			"title": "#ff9879",
			"subtitle": "#e57bb9"
		},
	}


	def __init__(self, new_set: Optional[ColorSetEntry]) -> None:
		super().__init__(new_set or self.DEFAULT)


	def parsed_values(self, bg=False) -> dict:
		"""Convert all values in the ColorSet to parsed color sequences for the terminal"""
		return self.map_values(lambda val: Term.color(val, bg))




class CharSet(_BaseSet):
	"""Container for the character sets."""

	EMPTY: CharSetEntry = {
		"empty": " ",
		"full": " ",
		"vert": {
			"right": " ",
			"left": " "
		},
		"horiz": {
			"top": " ",
			"bottom": " "
		},
		"corner": {
			"tleft": " ",
			"tright": " ",
			"bleft": " ",
			"bright": " "
		},
	}

	DEFAULT: CharSetEntry = {
		"empty": "░",
		"full": "█",
		"vert": "│",
		"horiz": "─",
		"corner": {
			"tleft": "┌",
			"tright": "┐",
			"bleft": "└",
			"bright": "┘"
		},
	}

	BASIC: CharSetEntry = {
		"empty": ".",
		"full": "#",
		"vert": {
			"left": "[",
			"right": "]"
		},
	}

	SLIM: CharSetEntry = {
		"empty": "░",
		"full": "█"
	}

	CIRCLES: CharSetEntry = {
		"empty": "○",
		"full": "●"
	}

	BASIC2: CharSetEntry = {
		"empty": ".",
		"full": "#",
		"vert": "|",
		"horiz": "-",
		"corner": "+",
	}

	FULL: CharSetEntry = {
		"empty": "█",
		"full": "█"
	}

	DIFF: CharSetEntry = {
		"full": "+",
		"empty": "-"
	}

	DOTS: CharSetEntry = {
		"full": "⣿",
		"empty": "⢸"
	}

	TRIANGLES: CharSetEntry = {
		"full": "▶",
		"empty": "◁"
	}

	BRICKS: CharSetEntry = {
		"full": "█",
		"empty": "▞",
		"vert": "┋"
	}

	ROUNDED: CharSetEntry = {
		"full": "█",
		"empty": "▁",
		"horiz": "─",
		"vert": "│",
		"corner": {
			"tright": "╮",
			"tleft": "╭",
			"bleft": "╰",
			"bright": "╯"
		},
	}

	TILTED: CharSetEntry = {
		"full": "🙽",
		"empty": "🙽"
	}

	DOUBLE: CharSetEntry = {
		"empty": "░",
		"full": "█",
		"vert": "║",
		"horiz": "═",
		"corner": {
			"tleft": "╔",
			"tright": "╗",
			"bleft": "╚",
			"bright": "╝"
		},
	}


	def __init__(self, new_set: Optional[CharSetEntry]) -> None:
		super().__init__(new_set or self.DEFAULT)
		self |= self._strip()	# we update with the stripped strings


	def _strip(self) -> CharSetEntry:
		def clean(value) -> str:
			if len(value) > 1:
				value = value[0]	# if the string is larger than one, just get the first char
			if value in _IGNORE_CHARS+"\t":
				return "?"	# we just return a "?" if the char is invalid.
			return value

		return self.map_values(lambda val: clean(val))	# map the new dict




class UnknownFormattingKeyError(Exception):
	"""Unknown formatting key used in a formatset string"""
	def __init__(self, string) -> None:
		super().__init__(
			Term.style_format(f"Unknown formatting key '<red>*{string}*<reset>'")
		)


class FormatSet(_BaseSet):
	"""Container for the formatting sets."""

	EMPTY: FormatSetEntry = {
		"inside": "",
		"right": "",
		"left": "",
		"title": "",
		"subtitle": "",
	}

	DEFAULT: FormatSetEntry = {
		"title": "<text>",
		"inside": "<percentage>%"
	}

	DESCRIPTIVE: FormatSetEntry = {
		"right": "Time R.: <rtime>s.",
		"title": "<text>",
		"subtitle": "<prange1> of <prange2>",
		"inside": "<percentage>%",
	}

	LEFT_RIGHT: FormatSetEntry = {
		"left": "<prange1>/<prange2>",
		"right": "<text>: <percentage>%",
	}

	ONLY_PERCENTAGE: FormatSetEntry = {
		"inside": "<percentage>%",
	}

	SIMPLE: FormatSetEntry = {
		"title": "<text>",
		"subtitle": "<prange1>/<prange2>"
	}

	E_TIME: FormatSetEntry = {
		"title": "<text>",
		"subtitle": "Elapsed <etime> seconds"
	}

	R_TIME: FormatSetEntry = {
		"title": "<text>",
		"subtitle": "<rtime> seconds remaining"
	}

	TITLE_SUBTITLE: FormatSetEntry = {
		"title": "<text> (<prange1>/<prange2>)",
		"subtitle": "<percentage>% (<rtimef>)",
	}

	TQDM: FormatSetEntry = {
		"left": "<percentage>%: <text>",
		"right": "<prange1>/<prange2> [<etimef>\<<rtimef>]"
	}

	PLACEHOLDER: FormatSetEntry = {
		"inside": "inside",
		"right": "right",
		"left": "left",
		"title": "title",
		"subtitle": "subtitle",
	}


	def __init__(self, new_set: Optional[FormatSetEntry]) -> None:
		super().__init__(new_set or self.DEFAULT)


	@staticmethod
	def _rm_poison_chars(text: str) -> str:
		"""Remove "dangerous" characters and convert some"""
		end_str = ""
		for char in str(text):
			if char not in _IGNORE_CHARS:	# Ignore this characters entirely
				if char == "\t":
					char = "    "	# Convert tabs to spaces because otherwise we can't tell the length of the string properly
				end_str += char
		return end_str


	@staticmethod
	def get_bar_attr(bar_obj: "bar.PBar", string: str):
		attrs = {
			"percentage": lambda: bar_obj.percentage,
			"prange1": lambda: bar_obj._range[0],
			"prange2": lambda: bar_obj._range[1],
			"etime": lambda: bar_obj.etime,
			"etimef": lambda: time.strftime("%M:%S", time.gmtime(bar_obj.etime)),
			"rtime": lambda: bar_obj.rtime,
			"rtimef": lambda: time.strftime("%M:%S", time.gmtime(bar_obj.rtime)),
			"text": lambda: FormatSet._rm_poison_chars(bar_obj.text) if bar_obj.text else ""
		}

		if string not in attrs:	raise UnknownFormattingKeyError(string)

		return attrs[string]()


	@staticmethod
	def parse_string(bar_obj: "bar.PBar", string: str) -> str:
		"""Parse a string that may contain formatting keys"""
		if string is None:
			return ""

		end_str = ""				# Final string that will be returned
		string = FormatSet._rm_poison_chars(string)
		loop_skip_chars = 0

		# Convert the keys to a final string
		for index, char in enumerate(string):
			if loop_skip_chars:
				loop_skip_chars -= 1
				continue

			# skip a character if backslashes are used
			if char == "\\":
				if index == len(string) - 1:
					break
				end_str += string[index + 1]
				loop_skip_chars = 1
				continue

			if char == "<":
				if ">" not in string[index:]:
					raise utils.UnexpectedEndOfStringError(string)
				end_index = string.index(">", index)
				char = str(FormatSet.get_bar_attr(bar_obj, string[index + 1:end_index]))

				loop_skip_chars = end_index - index

			end_str += char
		return end_str.strip()


	def parsed_values(self, bar_obj: "bar.PBar") -> "FormatSet":
		"""Returns a new FormatSet with all values parsed with the properties of the PBar object specified"""
		return FormatSet(self.map_values(lambda val: self.parse_string(bar_obj, val)))


	def empty_values(self) -> "FormatSet":
		"""Convert all values in the FormatSet to strings with spaces of the same size."""
		return FormatSet(self.map_values(lambda val: " "*len(val)))
