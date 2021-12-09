from io import TextIOWrapper
from os import isatty
from time import time as epochTime, sleep
from typing import Any, Optional, SupportsInt, Union, IO

from . import utils, gen, sets, cond
from . utils import Term


NEVER_DRAW = False
if not Term.size() or not isatty(0):
	Term.size = lambda: (0, 0)	# we just force it to return a size of 0,0 if it can't get the size
	NEVER_DRAW = True




Position = Size = tuple[Union[str, int], Union[str, int]]
Conditions = Union[list[cond.Cond], cond.Cond]




class PBar:
	"""Object for managing a progress bar."""
	def __init__(self,
			prange: tuple[int, int] = (0, 1),
			text: str = None,
			size: Size = (20, 1),
			position: Position = ("center", "center"),
			colorset: sets.ColorSetEntry = None,
			charset: sets.CharSetEntry = None,
			formatset: sets.FormatSetEntry = None,
			conditions: Conditions = None,
			gfrom: gen.Gfrom = gen.Gfrom.AUTO,
			inverted: bool = False
		) -> None:
		"""
		### Detailed descriptions:
		@prange: This tuple will specify the range of two values to display in the progress bar.

		---

		@text: String to show in the progress bar.

		---

		@size: Tuple that specifies the width and height of the bar.

		- Negative values will set the size to the space between the bar and the terminal edge (`-1` will stick to the edge).

		---

		@position: Tuple containing the position (X and Y axles of the center) of the progress bar on the terminal.

		- If an axis value is `center`, the bar will be positioned at the center of the terminal on that axis.
		- Negative values will position the bar at the other side of the terminal.

		---

		@colorset: Set of colors to use when drawing the progress bar.

		To use one of the included sets, use any of the constant values in `pbar.ColorSet`.

		Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom colors.

		---

		@charset: Set of characters to use when drawing the progress bar.

		To use one of the included sets, use any of the constant values in `pbar.CharSet`. Keep in mind that some fonts might not have
		the characters used in some charsets.

		Since this value is just a dictionary, it is possible to use custom sets, which should specify the custom characters.

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

		---

		@inverted: If `True`, the bar will be drawn from the end to the beginning.
		"""
		self.enabled = True				# If disabled, the bar will never draw.
		self._time = epochTime()		# The elapsed time since the bar created.
		self._isOnScreen = False		# Is the bar on screen?

		self._range = PBar._getRange(prange)
		self.text = text if text is not None else ""
		self.size = size
		self.position = position
		self._colorset = sets.ColorSet(colorset)
		self._charset = sets.CharSet(charset)
		self._formatset = sets.FormatSet(formatset)
		self._conditions = PBar._getConds(conditions)
		self.gfrom = gfrom
		self.inverted = inverted

		self._oldValues = (*self.computedValues, self._formatset)	# This values are used when clearing the old position of the bar (when self._requiresClear is True)


	# -------------------- Properties / Methods the user should use. --------------------


	def draw(self):
		"""Print the progress bar on screen."""

		self._printStr(
			self._genClearedBar(*self._oldValues)	# Clear the bar at the old position and size
			+ self._genBar()	# draw at the new position and size
		)

		self._oldValues = (*self.computedValues, self._formatset)	# Reset the old values


	def step(self, steps: int = 1, text: str = None):
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
		self._printStr(self._genClearedBar(*self._oldValues))


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
		utils.chkInstOf(fp, TextIOWrapper, name="fp")
		self.prange = (0, len(fp.readlines()))
		fp.seek(0)


	@property
	def prange(self) -> tuple[int, int]:
		"""Range for the progress of the bar."""
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
	def colorset(self) -> sets.ColorSet:
		"""Set of colors for the bar."""
		return self._colorset
	@colorset.setter
	def colorset(self, colorset: sets.ColorSetEntry):
		self._colorset = sets.ColorSet(colorset)


	@property
	def charset(self) -> sets.CharSet:
		"""Set of characters for the bar."""
		return self._charset
	@charset.setter
	def charset(self, charset: sets.CharSetEntry):
		self._charset = sets.CharSet(charset)


	@property
	def formatset(self) -> sets.FormatSet:
		"""Formatting used for the bar."""
		return self._formatset
	@formatset.setter
	def formatset(self, formatset: sets.FormatSetEntry):
		self._formatset = sets.FormatSet(formatset)


	@property
	def computedValues(self) -> tuple[tuple[int, int], tuple[int, int]]:
		"""Computed position and size of the progress bar."""
		size = PBar._getComputedSize(self.size)
		pos = PBar._getComputedPosition(self.position, size)

		return pos, size


	@property
	def etime(self) -> float:
		"""Time elapsed since the bar created."""
		return round(epochTime() - self._time, 2)


	@property
	def conditions(self) -> tuple:
		"""Conditions for the bar."""
		return self._conditions
	@conditions.setter
	def conditions(self, conditions: Optional[Conditions]):
		self._conditions = PBar._getConds(conditions)


	@property
	def config(self) -> dict:
		"""All the values of the progress bar stored in a dict."""
		return {
			"prange": self._range,
			"text": self.text,
			"size": self.size,
			"position": self.position,
			"colorset": self._colorset,
			"charset": self._charset,
			"formatset": self._formatset,
			"conditions": self._conditions,
			"gfrom": self.gfrom,
			"inverted": self.inverted,
			"enabled": self.enabled
		}
	@config.setter
	def config(self, config: dict[str, Any]):
		utils.chkInstOf(config, dict, name="config")
		for key in {"prange", "text", "size", "position", "colorset",
					"charset", "formatset", "conditions", "gfrom", "inverted", "enabled"}:
			# Iterate through every key in the dict and populate the config of the class with its values
			if key not in config:
				raise ValueError(f"config dict is missing the {key!r} key")
			setattr(self, key, config[key])


	# -------------------- ///////////////////////////////////////// --------------------


	@staticmethod
	def _getRange(range: tuple[SupportsInt, SupportsInt]) -> tuple[int, int]:
		"""Return a capped range"""
		utils.chkSeqOfLen(range, 2)
		start, stop = map(int, range)
		return (utils.capValue(start, stop, 0),
				utils.capValue(stop, min=1))


	@staticmethod
	def _getConds(conditions: Optional[Conditions]) -> list[cond.Cond]:
		if isinstance(conditions, (tuple, list)):
			for item in conditions:	utils.chkInstOf(item, cond.Cond)
			return conditions
		elif isinstance(conditions, cond.Cond):
			return (conditions, )
		else:
			return ()


	def _chkConds(self) -> None:
		for cond in self._conditions:
			cond.chkAndApply(self)


	@staticmethod
	def _getComputedPosition(position: Position, cSize: tuple[int, int]) -> tuple[int, int]:
		"""Get and process new position requested"""
		termSize = Term.size()
		newpos = []

		for index, value in enumerate(position):
			if value == "center":
				value = termSize[index]//2

			if value < 0:	# if negative value, return Term size - value
				value = termSize[index] + value

			# set maximun and minimun positions
			value = utils.capValue(value,
				termSize[index] - cSize[index]/2 - 1,
				cSize[index]/2 + 1
			)

			newpos.append(int(value) - cSize[index]//2)
		return tuple(newpos)


	@staticmethod
	def _getComputedSize(size: Size):
		"""Get and process new length requested"""
		termSize = Term.size()
		newsize = list(size)

		for index in range(2):
			newsize[index] = termSize[index] + newsize[index] if newsize[index] < 0 else newsize[index]

		width, height = map(int, newsize)

		return (
			utils.capValue(int(width), termSize[0] - 2, 1),
			utils.capValue(int(height), termSize[1] - 2, 1)
		)


	def checkProps(self) -> tuple[tuple[int, int], tuple[int, int]]:
		"""Check the properties of the bar and return the computed values."""
		if self._conditions:	self._chkConds()

		return self.computedValues


	def _genClearedBar(
			self, position: tuple[int, int],
			size: tuple[int, int], formatset: sets.FormatSet
		) -> str:
		"""Generate a cleared progress bar. The position and size values should be already computed."""
		if not self._isOnScreen:	return ""
		parsedColorSet = sets.ColorSet(sets.ColorSet.EMPTY).parsedValues()

		barShape = gen.shape(
			position,
			(size[0] + 2, size[1] + 2),
			sets.CharSet.EMPTY,
			parsedColorSet
		)

		barText = gen.bText(
			(position[0] + 2, position[1]),
			(size[0] - 2, size[1] + 2),
			parsedColorSet,
			formatset.parsedValues(self).emptyValues()
		)

		self._isOnScreen = False
		return barText + barShape


	def _genBar(self) -> str:
		"""Generate the progress bar"""
		position, size = self.checkProps()
		parsedColorSet = self._colorset.parsedValues()

		# Build all the parts of the progress bar
		barShape = gen.shape(
			position,
			(size[0] + 2, size[1] + 2),
			self._charset, parsedColorSet
		)

		barContent = gen.BarContent(self.gfrom, self.inverted)(
			(position[0] + 2, position[1] + 1),
			(size[0] - 2, size[1]),
			self._charset, parsedColorSet, self._range
		)

		barText = gen.bText(
			(position[0] + 2, position[1]),
			(size[0] - 2, size[1] + 2),
			parsedColorSet, self._formatset.parsedValues(self)
		)

		self._isOnScreen = True
		return barShape + barContent + barText


	def _printStr(self, barString: str):
		"""Prints string to stream"""
		if not self.enabled or NEVER_DRAW: return
		utils.out(
			Term.CURSOR_SAVE + Term.CURSOR_HIDE
			+ barString
			+ Term.CURSOR_LOAD + Term.CURSOR_SHOW + Term.RESET
		)




def animate(barObj: PBar, rng: range = range(100), delay: float = 0.05) -> None:
	"""
	Animates the given PBar object by filling it by the range given, with a delay.
	@barObj: PBar object to use.
	@rng: range object to set for the bar.
	@delay: Time in seconds between each time the bar draws.
	"""
	utils.chkInstOf(rng, range, name="rng")
	steps = rng.step
	barObj.prange = rng.start, rng.stop
	for _ in rng:
		barObj.step(steps)
		sleep(delay)


def barHelper(
		position: Position = ("center", "center"),
		size: tuple[int, int] = (20, 1)
	) -> Position:
	"""
	Draw a bar helper on screen indefinitely until the user exits.
	Returns the position of the bar helper.
	@position: Position of the helper on the terminal.
	@size: Size of the helper.
	"""
	b = PBar(	# we create a bar just to make stuff easier
		size=size,
		formatset=sets.FormatSet.EMPTY,
		colorset={
			"vert": "#090",
			"horiz": "#090",
			"corner": "#090",
			"text":	"#ff6400",
			"empty": "#090"
		},
		prange=(34, 100)
	)

	b.formatset |= {"title": f"uValues: pos{position} size{size}"}

	with Term.SeqMgr(hideCursor=True):	# create a new buffer, and hide the cursor
		try:
			while True:
				b.position = position
				rPos, rSize = b.computedValues
				b.formatset |= {"subtitle": f"cValues: pos{rPos} size{rSize}"}

				xLine = Term.pos((0, rPos[1])) + "═"*rPos[0]
				yLine = "".join(Term.pos((rPos[0], x)) + "║" for x in range(rPos[1]))
				center = Term.pos(rPos) + "╝"

				utils.out(
					Term.CLEAR_ALL
					+ b._genBar()	# the bar itself
					+ Term.color((255, 100, 0)) + xLine + yLine + center	# x and y lines
					+ Term.CURSOR_HOME + Term.INVERT + "Press Ctrl-C to exit." + Term.RESET
				)
				sleep(0.01)
		except KeyboardInterrupt:
			pass

	del b	# delete the bar we created
	return rPos, rSize	# return the latest position and size of the helper