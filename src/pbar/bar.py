from io import TextIOWrapper as _TextIOWrapper
from typing import Any, Optional, SupportsInt, Union, IO
from os import get_terminal_size as _get_terminal_size, system as _runsys
from time import time as _time, sleep as _sleep
from inspect import getsourcelines as _srclines

from . sets import CharSet, ColorSet, FormatSet, CharSetEntry, FormatSetEntry, ColorSetEntry
from . utils import *


_runsys("")		# We need to do this, otherwise Windows won't display special VT100 sequences


Position = tuple[Union[str, int], Union[str, int]]


def _genShape(position: tuple[int, int], size: tuple[int, int], charset: CharSet, parsedColorset: dict, filled: Optional[str] = " ") -> str:
	"""Generates a basic rectangular shape that uses a charset and a parsed colorset"""
	width, height = size[0] + 2, size[1]

	charVert = (
		parsedColorset["vert"]["left"] + charset["vert"]["left"],
		parsedColorset["vert"]["right"] + charset["vert"]["right"]
	)
	charHoriz = (
		charset["horiz"]["top"],
		charset["horiz"]["bottom"],
	)
	charCorner = (
		parsedColorset["corner"]["tleft"] + charset["corner"]["tleft"],
		parsedColorset["corner"]["tright"] + charset["corner"]["tright"],
		parsedColorset["corner"]["bleft"] + charset["corner"]["bleft"],
		parsedColorset["corner"]["bright"] + charset["corner"]["bright"]
	)

	endStr: str = (
		VT100.pos(position)
		+ charCorner[0]
		+ parsedColorset["horiz"]["top"] + charHoriz[0]*width
		+ charCorner[1]
	)

	for row in range(1, height):
		endStr += (
			VT100.pos(position, (0, row))
			+ charVert[0]
			+ (VT100.moveHoriz(width) if filled is None else filled[0]*width)
			+ charVert[1]
		)

	endStr += (
		VT100.pos(position, (0, height))
		+ charCorner[2]
		+ parsedColorset["horiz"]["bottom"] + charHoriz[1]*width
		+ charCorner[3]
	)

	return endStr


def _genBarContent(position: tuple[int, int], size: tuple[int, int], charset: CharSet, parsedColorset: ColorSet,
				   rangeValue: tuple[int, int]) -> str:
	"""Generates the progress shape with a parsed colorset and a charset specified"""
	width, height = size
	SEGMENTS_FULL = int((capValue(rangeValue[0], rangeValue[1], 0) / capValue(rangeValue[1], min=1))*width)	# Number of character for the full part of the bar
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
	width, height = size

	def stripText(string: str, maxlen: int):
		"""Return a string stripped if the len of it is larger than the maxlen specified"""
		maxlen = capValue(maxlen, min=3)
		return string[:maxlen-3] + "..." if len(string) > maxlen else string

	txtMaxWidth = width + 2
	txtSubtitle = stripText(formatset["subtitle"], txtMaxWidth)
	txtInside = stripText(formatset["inside"], txtMaxWidth - 4)
	txtTitle = stripText(formatset["title"], txtMaxWidth)

	textTitle = (
		VT100.pos(position, (-1, 0))
		+ parsedColorset["text"]["title"]
		+ txtTitle
	)

	textSubtitle = (
		VT100.pos(position, (width - len(txtSubtitle) + 1, height))
		+ parsedColorset["text"]["subtitle"]
		+ txtSubtitle
	)

	textRight = (
		VT100.pos(position, (width + 3, height/2))
		+ parsedColorset["text"]["right"]
		+ formatset["right"]
		+ VT100.CLEAR_RIGHT
	) if formatset["right"] else ""

	textLeft = (
		VT100.pos(position, (-len(formatset["left"]) - 3, height/2))
		+ VT100.CLEAR_LEFT
		+ parsedColorset["text"]["left"]
		+ formatset["left"]
	) if formatset["left"] else ""

	txtInside = (
		VT100.pos(position, (width/2 - len(txtInside)/2, height/2))
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
	- PBar.prangeFromFile()

	---

	## Properties

	- PBar.percentage
	- PBar.text
	- PBar.prange
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
			prange: tuple[int, int] = (0, 1),
			text: str = None,
			size: tuple[int, int] = (20, 1),
			position: tuple[Union[str, int], Union[str, int]] = ("center", "center"),
			charset: Optional[CharSetEntry] = None,
			colorset: Optional[ColorSetEntry] = None,
			formatset: Optional[FormatSetEntry] = None
		) -> None:
		"""
		### Detailed descriptions:
		@prange: This tuple will specify the range of two values to display in the progress bar.

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

		---

		@colorset: Set of colors to use when drawing the progress bar.

		To use one of the included sets, use any of the constant values in `pbar.ColorSet`.

		Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom colors.

		---

		@formatset: Formatting used when displaying the strings in different places around the bar.

		To use one of the included sets, use any of the constant values in `pbar.FormatSet`.

		Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom formatting.

		---

		### Help

		The [GitHub Repository](https://github.com/DarviL82/PBar) contains more help about all the properties.
		"""
		self._requiresClear = False		# This controls if the bar needs to clear its old position before drawing.
		self._enabled = True			# If disabled, the bar will never draw.
		self._time = _time()			# The elapsed time since the bar created.

		self._range = PBar._getRange(prange)
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
		Add `steps` to the first value in prange, then draw the bar.
		@steps: Value to add to the first value in prange.
		@text: Text to be displayed on the bar.
		"""
		self.prange = (self._range[0] + steps, self._range[1])
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
		"""Return a PBar object with the new configuration given from another PBar or dict."""
		pb = cls()
		pb.config = other.config if isinstance(other, PBar) else other
		return pb


	def prangeFromFile(self, fp: IO[str]):
		"""Modify `prange` with the number of lines of a file."""
		isInstOf(fp, _TextIOWrapper, name="fp")
		self.prange = (0, len(fp.readlines()))
		fp.seek(0)


	@property
	def percentage(self):
		"""Percentage of the progress of the current `prange`."""
		return int((self._range[0]*100) / self._range[1])


	@property
	def text(self):
		"""Text to be displayed on the bar."""
		return self._text
	@text.setter
	def text(self, text: str):
		self._text = FormatSet._rmPoisonChars(text)


	@property
	def prange(self) -> tuple[int, int]:
		"""Range for the bar progress."""
		return (self._range[0], self._range[1])
	@prange.setter
	def prange(self, range: tuple[int, int]):
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
			"prange":		self._range,
			"text":			self._text,
			"size":			self._size,
			"position":		self._pos,
			"charset":		self._charset,
			"colorset":		convertClrs(self._colorset, "HEX"),
			"formatset":	self._formatset,
			"enabled":		self._enabled
		}
	@config.setter
	def config(self, config: dict[str, Any]):
		isInstOf(config, dict, name="config")
		for key in {"prange", "text", "size", "position", "charset", "colorset", "formatset", "enabled"}:
			# Iterate through every key in the dict and populate the config of the class with its values
			if key not in config:
				raise ValueError(f"config dict is missing the {key!r} key")
			setattr(self, key, config[key])


	# --------- ///////////////////////////////////////// ----------


	def _getPos(self, position: Position) -> tuple[int, int]:
		"""Get and process new position requested"""
		chkSeqOfLen(position, 2)

		TERM_SIZE: tuple[int, int] = _get_terminal_size()
		newpos = []

		for index, value in enumerate(position):
			if value == "center":
				value = int(TERM_SIZE[index]/2)+1
			isInstOf(value, int, float, name="pos")

			if value < 0:
				value = TERM_SIZE[index] + value

			if index == 0:
				value = capValue(value, TERM_SIZE[0] - self._size[0]/2 - 1, self._size[0]/2 + 3)
			else:
				value = capValue(value, TERM_SIZE[1] - self._size[1]/2, self._size[1]/2 + 2)

			newpos.append(int(value))
		return tuple(newpos)


	@staticmethod
	def _getSize(size: Optional[tuple[SupportsInt, SupportsInt]]) -> tuple[int, int]:
		"""Get and process new length requested"""
		chkSeqOfLen(size, 2)
		return (int(capValue(size[0], min=5)),
				int(capValue(size[1], min=1)))


	@staticmethod
	def _getRange(range: tuple[SupportsInt, SupportsInt]) -> tuple[int, int]:
		"""Return a capped range"""
		chkSeqOfLen(range, 2)
		return (int(capValue(range[0], range[1], 0)),
				int(capValue(range[1], min=1)))


	def _genClearedBar(self, values: tuple[tuple[int, int], tuple[int, int]]) -> str:
		"""Generate a cleared progress bar. `values[0]` is the position, and `values[1]` is the size"""
		pos, size = values
		parsedColorSet = ColorSet.parsedValues(ColorSet.EMPTY)

		size = size[0], size[1] + 1
		POSITION = (pos[0] + int(size[0]/-2),
					pos[1] + int(size[1]/-2))

		barShape = _genShape(
			(POSITION[0] - 2, POSITION[1]),
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

		return barText + barShape


	def _genBar(self) -> str:
		"""Generate the progress bar"""
		size = self._size[0], self._size[1] + 1
		POSITION = (self._pos[0] + int(size[0]/-2),
					self._pos[1] + int(size[1]/-2))

		parsedColorSet = self._colorset.parsedValues()

		# Build all the parts of the progress bar
		barShape = _genShape(
			(POSITION[0] - 2, POSITION[1]),
			size, self._charset, parsedColorSet
		)

		barContent = _genBarContent(
			POSITION,
			size, self._charset, parsedColorSet, self._range
		)

		barText = _genBarText(
			POSITION,
			size, parsedColorSet, self._formatset.parsedValues(self)
		)

		return barShape + barContent + barText


	def _printStr(self, barString: str):
		"""Prints string to stream"""
		if not self._enabled: return
		print(
			VT100.CURSOR_SAVE + VT100.CURSOR_HIDE
			+ barString
			+ VT100.CURSOR_LOAD + VT100.CURSOR_SHOW,
			flush=True,
			end=""
		)




def taskWrapper(pbarObj: PBar, scope: dict, titleComments = False, overwriteRange = True) -> None:
	"""
	Use as a decorator. Takes a PBar object, sets its prange depending on the quantity of
	statements inside the decorated function, and `steps` the bar over after every function statement.
	Note: Multi-line expressions are not supported.

	@pbarObj: PBar object to use.
	@scope: Dictionary containing the scope local variables.
	@titleComments: If True, comments on a statement starting with "#bTitle:" will be treated as titles for the progress bar.
	@overwriteRange: If True, overwrites the prange of the bar.
	"""
	isInstOf(pbarObj, PBar, name="pbarObj")

	def getTitleComment(string: str) -> Optional[str]:
		"""Returns the text after "#bTitle:" from the string supplied. Returns None if there is no comment."""
		try:
			index = string.rindex("#bTitle:") + 8	# lol
		except ValueError:
			return
		return string[index:].strip()

	def wrapper(func):
		lines = _srclines(func)[0][2:]	# Get the source lines of code

		pbarObj.prange = (0, len(lines)) if overwriteRange else pbarObj.prange

		for inst in lines:	# Iterate through every statement
			instComment = getTitleComment(inst)
			if titleComments and instComment:	pbarObj.text = instComment
			pbarObj.draw()
			try:
				eval(inst, scope)	# yep, this uses evil()
			except SyntaxError:
				raise RuntimeError("Multi-line expressions are not supported inside functions decorated with taskWrapper")
			pbarObj.step()

	return wrapper


def animate(pbarObj: PBar, rng: range, delay: float = 0.1) -> None:
	"""
	Animates the given PBar object by filling it by the range given, with a delay.
	@pbarObj: PBar object to use.
	@rng: range object to set for the bar.
	@delay: Time in seconds between each time the bar draws.
	"""
	steps = rng.step
	pbarObj.prange = rng.start, rng.stop
	for _ in rng:
		pbarObj.step(steps)
		_sleep(delay)


def barHelper(position: Position, size: tuple[int, int]) -> Position:
	"""
	Draw a bar helper on screen indefinitely until the user exits.
	Returns the position of the bar helper.
	@position: Position of the helper on the terminal.
	@size: Size of the helper.
	"""
	b = PBar(	# we create a bar just to make stuff easier
		size=size,
		formatset=FormatSet.EMPTY,
		colorset={
			"vert": "#090",
			"horiz": "#090",
			"corner": "#090",
			"text":	(255, 100, 0),
			"empty": "#090"
		}
	)

	print(VT100.BUFFER_NEW + VT100.CURSOR_HIDE)

	try:
		while True:
			b.position = position
			rPos = b.position
			b.formatset = {"subtitle": f"X:{rPos[0]} Y:{rPos[1]}"}

			xLine = VT100.pos((0, rPos[1])) + "═"*rPos[0]
			yLine = "".join(VT100.pos((rPos[0], x)) + "║" for x in range(rPos[1]))
			center = VT100.pos(rPos) + "╝"

			print(
				VT100.CLEAR_ALL
				+ b._genBar()
				+ VT100.color((255, 100, 0)) + xLine + yLine + center
				+ VT100.CURSOR_HOME + VT100.INVERT + "Press Ctrl-C to exit." + VT100.RESET,
				end=""
			)
			_sleep(0.01)
	except KeyboardInterrupt:
		pass

	print(VT100.BUFFER_OLD + VT100.CURSOR_SHOW, end="")
	del b	# delete the bar we created
	return rPos