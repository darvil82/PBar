from io import TextIOWrapper
from typing import Any, Callable, Optional, SupportsInt, Union, IO
from os import system as runsys, isatty
from time import time as epochTime, sleep
from inspect import getsourcelines

from . sets import CharSet, ColorSet, FormatSet, CharSetEntry, ColorSetEntry, FormatSetEntry
from . utils import *
from . cond import Cond
from . import gen


NEVER_DRAW = False
if not Term.size() or not isatty(0):
	Term.size = lambda: (0, 0)	# we just force it to return a size of 0,0 if it can't get the size
	NEVER_DRAW = True

runsys("")		# We need to do this, otherwise Windows won't display special VT100 sequences


Position = tuple[Union[str, int], Union[str, int]]




class PBar:
	"""Object for managing a progress bar."""
	def __init__(self,
			prange: tuple[int, int]=(0, 1), text: str=None, size: tuple[int, int]=(20, 1),
			position: tuple[Union[str, int], Union[str, int]]=("center", "center"),
			colorset: ColorSetEntry=None, charset: CharSetEntry=None,
			formatset: FormatSetEntry=None, conditions: Union[list[Cond], Cond]=None,
			gfrom: gen.Gfrom=gen.Gfrom.AUTO
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

		@conditions: One or more conditions to check before each time the bar draws.
		If one succeeds, the specified customization sets will be applied to the bar.

		To create a condition, use `pbar.Cond`.

		---

		@gfrom: Place from where the full part of the bar will grow.
		"""
		self._requiresClear = False		# This controls if the bar needs to clear its old position before drawing.
		self.enabled = True				# If disabled, the bar will never draw.
		self._time = epochTime()		# The elapsed time since the bar created.
		self._isOnScreen = False		# Is the bar on screen?

		self._range = PBar._getRange(prange)
		self._text = FormatSet._rmPoisonChars(text) if text is not None else ""
		self._formatset = FormatSet(formatset)
		self._size = PBar._getSize(size)
		self._charset = CharSet(charset)
		self._colorset = ColorSet(colorset)
		self._pos = self._getPos(position)
		self._conditions = PBar._getConds(conditions)
		self.gfrom = gfrom

		self._oldValues = [self._pos, self._size, self._formatset]	# This values are used when clearing the old position of the bar (when self._requiresClear is True)


	# --------- Properties / Methods the user should use. ----------


	def draw(self):
		"""Print the progress bar on screen."""
		if self._requiresClear:
			# Clear the bar at the old position and length
			clsb = self._genClearedBar(*self._oldValues)
			self._oldValues = [self._pos, self._size, self._formatset]	# Reset the old values
			self._printStr(clsb + self._genBar())	# we print the "cleared" bar and the new bar
		else:
			self._printStr(self._genBar())	# Draw the bar

		self._requiresClear = False


	def step(self, steps: int=1, text=None):
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
		self._printStr(self._genClearedBar(self._pos, self._size, self._formatset))


	def resetETime(self):
		"""Reset the elapsed time counter."""
		self._time = epochTime()	# Just set _time to the current time.


	@classmethod
	def fromConfig(cls, other: Union["PBar", dict]) -> "PBar":
		"""Return a PBar object with the new configuration given from another PBar or dict."""
		pb = cls()
		pb.config = other.config if isinstance(other, PBar) else other
		return pb


	def prangeFromFile(self, fp: IO[str]):
		"""Modify `prange` with the number of lines of a file."""
		chkInstOf(fp, TextIOWrapper, name="fp")
		self.prange = (0, len(fp.readlines()))
		fp.seek(0)


	@property
	def prange(self) -> tuple[int, int]:
		"""Range for the bar progress."""
		return (self._range[0], self._range[1])
	@prange.setter
	def prange(self, range: tuple[int, int]):
		self._range = PBar._getRange(range)


	@property
	def percentage(self) -> int:
		"""Percentage of the progress of the current `prange`."""
		return int((self._range[0]*100) / self._range[1])
	@percentage.setter
	def percentage(self, percentage: int):
		crange = self._range
		perc = crange[1]/100 * percentage
		self.prange = (perc, crange[1])


	@property
	def text(self) -> str:
		"""Text to be displayed on the bar."""
		return self._text
	@text.setter
	def text(self, text: str):
		self._text = FormatSet._rmPoisonChars(text)


	@property
	def colorset(self) -> ColorSet:
		"""Set of colors for the bar."""
		return self._colorset
	@colorset.setter
	def colorset(self, colorset: ColorSetEntry):
		self._colorset = ColorSet(colorset)


	@property
	def charset(self) -> CharSet:
		"""Set of characters for the bar."""
		return self._charset
	@charset.setter
	def charset(self, charset: CharSetEntry):
		self._charset = CharSet(charset)


	@property
	def formatset(self) -> FormatSet:
		"""Formatting used for the bar."""
		return self._formatset
	@formatset.setter
	def formatset(self, formatset: FormatSetEntry):
		newset = FormatSet(formatset)
		if newset != self._formatset:
			self._oldValues[2] = self._formatset
			self._requiresClear = True
			self._formatset = newset


	@property
	def size(self):
		"""Size of the progress bar."""
		return self._size
	@size.setter
	def size(self, size: tuple[int, int]):
		newsize = PBar._getSize(size)
		if newsize != self._size:
			self._oldValues[1] = self._size
			self._requiresClear = True
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
	def etime(self) -> float:
		"""Time elapsed since the bar created."""
		return round(epochTime() - self._time, 2)


	@property
	def conditions(self) -> tuple:
		"""Conditions for the bar."""
		return self._conditions
	@conditions.setter
	def conditions(self, conditions: Optional[Union[list[Cond], Cond]]):
		self._conditions = PBar._getConds(conditions)


	@property
	def config(self) -> dict:
		"""All the values of the progress bar stored in a dict."""
		return {
			"prange":		self._range,
			"text":			self._text,
			"size":			self._size,
			"position":		self._pos,
			"colorset":		self._colorset,
			"charset":		self._charset,
			"formatset":	self._formatset,
			"conditions":	self._conditions,
			"gfrom":		self.gfrom,
			"enabled":		self.enabled
		}
	@config.setter
	def config(self, config: dict[str, Any]):
		chkInstOf(config, dict, name="config")
		for key in {"prange", "text", "size", "position", "colorset", "charset", "formatset", "conditions", "gfrom", "enabled"}:
			# Iterate through every key in the dict and populate the config of the class with its values
			if key not in config:
				raise ValueError(f"config dict is missing the {key!r} key")
			setattr(self, key, config[key])


	# --------- ///////////////////////////////////////// ----------


	def _getPos(self, position: Position) -> tuple[int, int]:
		"""Get and process new position requested"""
		chkSeqOfLen(position, 2)

		TERM_SIZE: tuple[int, int] = Term.size()
		newpos = []

		for index, value in enumerate(position):
			if value == "center":
				value = int(TERM_SIZE[index]/2)
			chkInstOf(value, int, float, name="pos")

			if value < 0:	# if negative value, return Term size - value
				value = TERM_SIZE[index] + value

			# set maximun and minimun positions
			if index == 0:
				value = capValue(value, TERM_SIZE[0] - self._size[0]/2 - 1, self._size[0]/2 + 3)
			else:
				value = capValue(value, TERM_SIZE[1] - self._size[1]/2 - 1, self._size[1]/2 + 2)

			newpos.append(int(value))
		return (newpos[0], newpos[1])


	@staticmethod
	def _getSize(size: tuple[SupportsInt, SupportsInt]) -> tuple[int, int]:
		"""Get and process new length requested"""
		chkSeqOfLen(size, 2)
		width, height = map(int, size)
		return (capValue(int(width), min=1),
				capValue(int(height), min=1))


	@staticmethod
	def _getRange(range: tuple[SupportsInt, SupportsInt]) -> tuple[int, int]:
		"""Return a capped range"""
		chkSeqOfLen(range, 2)
		start, stop = map(int, range)
		return (capValue(start, stop, 0),
				capValue(stop, min=1))


	@staticmethod
	def _getConds(conditions: Union[list[Cond], Cond]) -> list[Cond]:
		if isinstance(conditions, (tuple, list)):
			for item in conditions:	chkInstOf(item, Cond)
			return conditions
		elif isinstance(conditions, Cond):
			return (conditions, )
		else:
			return ()


	def _chkConds(self) -> None:
		for cond in self._conditions:
			if not cond.test(self):	# if a condition succeeds, apply its newsets
				continue
			if cond.newSets[0]:	self.charset = cond.newSets[0]
			if cond.newSets[1]:	self.colorset = cond.newSets[1]
			if cond.newSets[2]:	self.formatset = cond.newSets[2]



	def _genClearedBar(self, pos: tuple[int, int], size: tuple[int, int], formatset: FormatSet) -> str:
		"""Generate a cleared progress bar. `values[0]` is the position, and `values[1]` is the size"""
		if not self._isOnScreen:	return ""
		parsedColorSet = ColorSet(ColorSet.EMPTY).parsedValues()

		size = size[0], size[1] + 1
		POSITION = (pos[0] - int(size[0]/2),
					pos[1] - int(size[1]/2))

		barShape = gen.shape(
			(POSITION[0] - 2, POSITION[1]),
			size,
			CharSet.EMPTY,
			parsedColorSet
		)

		barText = gen.bText(
			POSITION,
			size,
			parsedColorSet,
			formatset.parsedValues(self).emptyValues()
		)

		self._isOnScreen = False
		return barText + barShape


	def _genBar(self) -> str:
		"""Generate the progress bar"""
		if self._conditions:	self._chkConds()
		size = self._size[0], self._size[1] + 1
		POSITION = (self._pos[0] - int(size[0]/2),
					self._pos[1] - int(size[1]/2))

		parsedColorSet = self._colorset.parsedValues()

		# Build all the parts of the progress bar
		barShape = gen.shape(
			(POSITION[0] - 2, POSITION[1]),
			size, self._charset, parsedColorSet
		)

		barContent = gen.BarContent(self.gfrom)(
			POSITION,
			size, self.charset, parsedColorSet, self._range
		)

		barText = gen.bText(
			POSITION,
			size, parsedColorSet, self._formatset.parsedValues(self)
		)

		self._isOnScreen = True
		return barShape + barContent + barText


	def _printStr(self, barString: str):
		"""Prints string to stream"""
		if not self.enabled or NEVER_DRAW: return
		print(
			Term.CURSOR_SAVE + Term.CURSOR_HIDE
			+ barString
			+ Term.CURSOR_LOAD + Term.CURSOR_SHOW,
			flush=True,	# flush file to make sure the bar draws
			end=""
		)




def taskWrapper(barObj: PBar, scope: dict, titleComments=False, overwriteRange=True) -> Callable:
	"""
	Use as a decorator. Takes a PBar object, sets its prange depending on the quantity of
	statements inside the decorated function, and `steps` the bar over after every function statement.

	Note:
	 - Multi-line statements are not supported.
	 - It is only possible to send keyword arguments to the decorated function.

	@barObj: PBar object to use.
	@scope: Dictionary containing the scope local variables.
	@titleComments: If True, comments on a statement starting with "#bTitle:" will be treated as titles for the progress bar.
	@overwriteRange: If True, overwrites the prange of the bar.
	"""
	chkInstOf(barObj, PBar, name="pbarObj")

	def getTitleComment(string: str) -> Optional[str]:
		"""Returns the text after "#bTitle:" from the string supplied. Returns None if there is no comment."""
		try:
			index = string.rindex("#bTitle:") + 8	# we just get the index of this string by adding 8 to get the comment
		except ValueError:
			return None
		return string[index:].strip()

	def wrapper(func):
		lines = getsourcelines(func)[0][2:]	# Get the source lines of code of the decorated function

		def wrapper2(**kwargs):	# this is the function that the decorated func will 'convert' into
			barObj.prange = (0, len(lines)) if overwriteRange else barObj.prange

			for inst in lines:	# Iterate through every line in the source code of the decorated function
				instComment = getTitleComment(inst)
				if titleComments and instComment:	barObj.text = instComment	# set text of the bar as the comment after #bTitle: (if any)

				barObj.draw()

				try:
					eval(inst, scope | kwargs)	# we merge the passed kwargs to the scope dictionary, so that the decorated function can reach them
				except SyntaxError:
					raise RuntimeError("Multi-line expressions are not supported inside functions decorated with taskWrapper")

				barObj.step()

		return wrapper2
	return wrapper


def animate(barObj: PBar, rng: range=range(100), delay: float=0.05) -> None:
	"""
	Animates the given PBar object by filling it by the range given, with a delay.
	@barObj: PBar object to use.
	@rng: range object to set for the bar.
	@delay: Time in seconds between each time the bar draws.
	"""
	chkInstOf(rng, range, name="rng")
	steps = rng.step
	barObj.prange = rng.start, rng.stop
	for _ in rng:
		barObj.step(steps)
		sleep(delay)


def barHelper(position: Position=("center", "center"),
			  size: tuple[int, int]=(20, 1)) -> Position:
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
			"text":	"#ff6400",
			"empty": "#090"
		}
	)

	with Term.NewBuffer(True):	# create a new buffer, and hide the cursor
		try:
			while True:
				b.position = position
				rPos = b.position
				b.formatset = {"subtitle": f"X:{rPos[0]} Y:{rPos[1]}"}

				xLine = Term.pos((0, rPos[1])) + "═"*rPos[0]
				yLine = "".join(Term.pos((rPos[0], x)) + "║" for x in range(rPos[1]))
				center = Term.pos(rPos) + "╝"

				print(
					Term.CLEAR_ALL
					+ b._genBar()	# the bar itself
					+ Term.color((255, 100, 0)) + xLine + yLine + center	# x and y lines
					+ Term.CURSOR_HOME + Term.INVERT + "Press Ctrl-C to exit." + Term.RESET,
					end=""
				)
				sleep(0.01)
		except KeyboardInterrupt:
			pass

	del b	# delete the bar we created
	return rPos	# return the latest position of the helper