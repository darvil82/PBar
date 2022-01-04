from io import TextIOWrapper
from time import time as epochTime, sleep
from typing import (
	Generator, Iterable, Literal,
	Optional, SupportsInt, Union, IO
)

from . import utils, gen, sets, cond
from . utils import Term, T


NEVER_DRAW = False
if not Term.isSupported():
	Term.size = lambda: (0, 0)	# we just force it to return a size of 0,0 if it can't get the size
	NEVER_DRAW = True




Position = tuple[Union[Literal["center"], int], Union[Literal["center"], int]]
Conditions = Union[list[cond.Cond], cond.Cond]




class PBar:
	"""Object for managing a progress bar."""
	def __init__(self,
		prange: tuple[int, int] = (0, 1),
		text: str = None,
		size: tuple[int, int] = (20, 1),
		position: Position = ("center", "center"),
		colorset: sets.ColorSetEntry = None,
		charset: sets.CharSetEntry = None,
		formatset: sets.FormatSetEntry = None,
		conditions: Conditions = None,
		contentg: gen.BContentGen = gen.ContentGens.Auto,
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

		@contentg: Content generator for the progress indicator of the bar. Available generators in `pbar.ContentGens`.

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
		self.contentg = contentg
		self.inverted = inverted

		self._oldValues = (*self.computedValues, self._formatset.parsedValues(self))	# This values are used when clearing the old position of the bar (when self._requiresClear is True)


	# -------------------- Properties / Methods the user should use. --------------------


	def draw(self):
		"""Print the progress bar on screen."""

		self._printStr(
			self._genClearedBar(*self._oldValues)	# Clear the bar at the old position and size
			+ self._genBar()	# draw at the new position and size
		)

		self._oldValues = (*self.computedValues, self._formatset.parsedValues(self))	# Reset the old values


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


	def done(self, text: str = None):
		"""Set the progress bar to 100% and draw it."""
		self.percentage = 100
		if text is not None: self.text = text
		self.draw()


	def resetETime(self):
		"""Reset the elapsed time counter."""
		self._time = epochTime()	# Just set _time to the current time.


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
		size = gen.getComputedSize(self.size, sizeOffset=(4, 2), minSize=(1, 1))
		pos = gen.getComputedPosition(self.position, size, sizeOffset=(3, 1))

		return pos, size


	@property
	def etime(self) -> float:
		"""Time elapsed since the bar created."""
		return round(epochTime() - self._time, 2)


	@property
	def conditions(self) -> list[cond.Cond]:
		"""Conditions for the bar."""
		return self._conditions
	@conditions.setter
	def conditions(self, conditions: Optional[Conditions]):
		self._conditions = PBar._getConds(conditions)


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
			return [conditions, ]
		else:
			return []


	def _chkConds(self) -> None:
		for cond in self._conditions:
			cond.chkAndApply(self)


	def checkProps(self) -> tuple[tuple[int, int], tuple[int, int]]:
		"""Check the properties of the bar and return the computed values."""
		if self._conditions:	self._chkConds()

		return self.computedValues


	def _genClearedBar(self,
		position: tuple[int, int],
		size: tuple[int, int], formatset: sets.FormatSet
	) -> str:
		"""Generate a cleared progress bar. The position and size values should be already computed."""
		if not self._isOnScreen:	return ""
		parsedColorSet = sets.ColorSet(sets.ColorSet.EMPTY).parsedValues()

		barShape = gen.bShape(
			position,
			(size[0] + 4, size[1] + 2),
			sets.CharSet.EMPTY,
			parsedColorSet
		)

		barText = gen.bText(
			(position[0] + 2, position[1]),
			(size[0], size[1] + 2),
			parsedColorSet,
			formatset.emptyValues()
		)

		self._isOnScreen = False
		return barText + barShape


	def _genBar(self) -> str:
		"""Generate the progress bar"""
		position, size = self.checkProps()
		parsedColorSet = self._colorset.parsedValues()

		# Build all the parts of the progress bar
		barShape = gen.bShape(
			position,
			(size[0] + 4, size[1] + 2),
			self._charset, parsedColorSet
		)

		barContent = gen.BContentGenMgr(
			self.contentg, self.inverted,
			(position[0] + 2, position[1] + 1),
			size,
			self._charset, parsedColorSet, self._range
		)()

		barText = gen.bText(
			(position[0] + 2, position[1]),
			(size[0], size[1] + 2),
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


def iter(
	iterable: Iterable[T],
	barObj: Optional[PBar] = None,
	length: int = None
) -> Generator[T, None, None]:
	"""
	Yield all the values of the given iterable, while stepping
	the progress bar.
	@iterable: Iterable object to iterate.
	@barObj: PBar object to use.
	@length: Length of the object to iterate.
	(Use this if you don't know the length of the iterable.)
	"""
	if not barObj:
		barObj = PBar()

	barObj.prange = (0, (length or len(iterable)))
	for x in iterable:
		yield x
		barObj.step()


def barHelper(
	position: Position = ("center", "center"),
	size: tuple[int, int] = (20, 1)
) -> tuple[tuple[int, int], tuple[int, int]]:
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
			"empty": "#090",
			"full": "#090"
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