from io import TextIOWrapper
from time import time as epochTime, sleep
import sys
from typing import (
	Generator, Iterable,
	Optional, SupportsInt, Union, IO
)

from . import utils, gen, sets, cond
from . utils import Term, T



NEVER_DRAW = not Term.SUPPORTED
DEBUG = False

# we override stdout so we can keep track of the number of newlines
sys.stdout = utils.Stdout(sys.stdout)



Position = tuple[Union[str, int], Union[str, int]]
Conditions = Union[list[cond.Cond], cond.Cond]




class PBar:
	"""Object for managing a progress bar."""
	def __init__(self,
		prange: tuple[int, int] = (0, 1),
		text: str = None,
		size: tuple[int, int] = (20, 1),
		position: Position = ("c", "c"),
		colorset: sets.ColorSetEntry = None,
		charset: sets.CharSetEntry = None,
		formatset: sets.FormatSetEntry = None,
		conditions: Conditions = None,
		contentg: gen.BContentGen = gen.ContentGens.auto,
		inverted: bool = False,
		centered: bool = True,
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

		- The position can be an integer (which will specify an absolute position) or a string, which may specify special positions:
			- Usage: `type[number]`. The number will specify the relative position from the point specified by the type.
			- Types:
				- `c`: Center of the terminal.
				- `r`: Position of the cursor.

		- Using integer negative values will position the bar at the other side of the terminal.

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

		---

		@centered: If `True`, the bar will be centered around the position specified by `position`.
		"""
		self.enabled = True				# If disabled, the bar will never draw.
		self._time = epochTime()		# The elapsed time since the bar created.
		self._is_on_screen = False		# Is the bar on screen?
		self._redraw_on_scroll = True	# If the bar is on screen, should it redraw when the terminal scrolls?

		self._range = PBar._get_range(prange)
		self.text = text if text is not None else ""
		self.size = size
		self.position = position
		self._colorset = sets.ColorSet(colorset)
		self._charset = sets.CharSet(charset)
		self._formatset = sets.FormatSet(formatset)
		self._conditions = PBar._get_conds(conditions)
		self.contentg = contentg
		self.inverted = inverted
		self.centered = centered

		utils.Stdout.add_trigger(lambda c: PBar._redraw_with_offset(self, c))
		self._old_values = (*self.computed_values, self._formatset.parsed_values(self))	# This values are used when clearing the old position of the bar (when self._requiresClear is True)


	# -------------------- Properties / Methods the user should use. --------------------


	def draw(self):
		"""Print the progress bar on screen."""

		self._print_str(
			self._gen_cleared_bar(*self._old_values)	# Clear the bar at the old position and size
			+ self._gen_bar()	# draw at the new position and size
		)

		self._old_values = (*self.computed_values, self._formatset.parsed_values(self))	# Reset the old values


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
		self._print_str(self._gen_cleared_bar(*self._old_values))


	def done(self, text: str = None):
		"""Set the progress bar to 100% and draw it."""
		self.percentage = 100
		if text is not None: self.text = text
		self.draw()


	def reset_etime(self):
		"""Reset the elapsed time counter."""
		self._time = epochTime()	# Just set _time to the current time.


	@property
	def prange(self) -> tuple[int, int]:
		"""Range for the progress of the bar."""
		return (self._range[0], self._range[1])
	@prange.setter
	def prange(self, range: tuple[int, int]):
		self._range = PBar._get_range(range)


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
	def computed_values(self) -> tuple[tuple[int, int], tuple[int, int]]:
		"""Computed position and size of the progress bar."""
		size = gen.get_computed_size(self.size, size_offset=(4, 2), min_size=(1, 1))
		pos = gen.get_computed_position(self.position, size, (3, 1), self.centered)

		return pos, size


	@property
	def etime(self) -> float:
		"""Time elapsed since the bar created."""
		return round(epochTime() - self._time, 2)


	@property
	def rtime(self) -> float:
		"""Time remaining to reach 100% of the progress of the bar."""
		if (perc := self.percentage) in (0, 100): return 0
		return round(self.etime / perc * (100 - perc), 2)


	@property
	def conditions(self) -> list[cond.Cond]:
		"""Conditions for the bar."""
		return self._conditions
	@conditions.setter
	def conditions(self, conditions: Optional[Conditions]):
		self._conditions = PBar._get_conds(conditions)


	# -------------------- ///////////////////////////////////////// --------------------


	@staticmethod
	def _get_range(range: tuple[SupportsInt, SupportsInt]) -> tuple[int, int]:
		"""Return a capped range"""
		utils.chk_seq_of_len(range, 2, "prange")
		start, stop = map(int, range)
		return (utils.cap_value(start, stop, 0),
				utils.cap_value(stop, min=1))


	@staticmethod
	def _get_conds(conditions: Optional[Conditions]) -> list[cond.Cond]:
		if isinstance(conditions, (tuple, list)):
			for item in conditions:	utils.chk_inst_of(item, cond.Cond)
			return conditions
		elif isinstance(conditions, cond.Cond):
			return [conditions, ]
		else:
			return []


	def _chk_conds(self) -> None:
		for cond in self._conditions:
			cond.chk_and_apply(self)


	def check_props(self) -> tuple[tuple[int, int], tuple[int, int]]:
		"""Check the properties of the bar and return the computed values."""
		if self._conditions:
			self._chk_conds()

		return self.computed_values


	def _gen_cleared_bar(
		self,
		position: tuple[int, int],
		size: tuple[int, int],
		formatset: sets.FormatSet
	) -> str:
		"""Generate a cleared progress bar. The position and size values should be already computed."""
		if not self._is_on_screen:
			return ""

		bar_shape = gen.rect(
			position,
			(size[0] + 4, size[1] + 2),
			" ",
			None
		)

		bar_text = gen.b_text(
			(position[0] + 2, position[1]),
			(size[0], size[1] + 2),
			sets.ColorSet(sets.ColorSet.EMPTY).parsed_values(),
			formatset.empty_values()
		)

		self._is_on_screen = False
		return bar_text + bar_shape


	def _gen_bar(self) -> str:
		"""Generate the progress bar"""
		position, size = self.check_props()
		parsed_colorset = self._colorset.parsed_values()

		# Build all the parts of the progress bar
		bar_shape = gen.b_shape(
			position,
			(size[0] + 4, size[1] + 2),
			self._charset,
			parsed_colorset
		)

		bar_content = gen.BContentGenMgr(
			self.contentg,
			self.inverted,
			(position[0] + 2, position[1] + 1),
			size,
			self._charset,
			parsed_colorset,
			self._range
		)()

		bar_text = gen.b_text(
			(position[0] + 2, position[1]),
			(size[0], size[1] + 2),
			parsed_colorset,
			self._formatset.parsed_values(self)
		)

		self._is_on_screen = True
		return bar_shape + bar_content + bar_text


	def _redraw_with_offset(self, count: int):
		if not self._is_on_screen and self._redraw_on_scroll:
			return

		pos, size, formatset = self._old_values
		self._print_str(
			self._gen_cleared_bar(
				(pos[0], pos[1] - count),
				size,
				formatset
			)
		)
		self.draw()


	def _print_str(self, bar_string: str):
		"""Prints string to stream"""
		if not self.enabled or NEVER_DRAW:
			return

		content = (
			Term.CURSOR_SAVE + Term.CURSOR_HIDE
			+ bar_string
			+ Term.CURSOR_LOAD + Term.CURSOR_SHOW + Term.RESET
		)

		if DEBUG:
			content = (
				Term.style_format("<lime>|START BAR =>")
				+ content.replace("\x1b", Term.style_format("<orange>ESC"))
				+ Term.style_format("<lime>|\<= END BAR")
				+ "\n"*4
			)

		utils.out(content, file=sys.stdout.original)







def animate(bar: PBar, rng: range = range(100), delay: float = 0.05) -> None:
	"""
	Animates the given PBar object by filling it by the range given, with a delay.
	@bar: PBar object to use.
	@rng: range object to set for the bar.
	@delay: Time in seconds between each time the bar draws.
	"""
	utils.chk_inst_of(rng, range, name="rng")
	steps = rng.step
	bar.prange = rng.start, rng.stop
	for _ in rng:
		bar.step(steps)
		sleep(delay)


def iter(
	iterable: Iterable[T],
	bar: Optional[PBar] = None,
	length: int = None,
	clear: bool = True,
	set_title: bool = False
) -> Generator[T, None, None]:
	"""
	Yield all the values of the given iterable, while stepping
	the progress bar.
	@iterable: Iterable object to iterate.
	@bar: PBar object to use.
	@length: Length of the object to iterate.
	(Use this if you don't know the length of the iterable.)
	@clear: Clear the progress bar after finishing the iteration.
	@set_title: Set the title of the progress bar to the string representation
	of each yielded value.
	"""
	if not bar:
		bar = PBar()

	bar.prange = (0, (length or len(iterable)))
	bar.draw()
	for x in iterable:
		yield x
		if set_title:
			bar.text = str(x)
		bar.step()

	if clear:
		bar.clear()


def bar_helper(bar: PBar = None) -> tuple[tuple[int, int], tuple[int, int]]:
	"""
	Draw a bar helper on screen indefinitely until the user exits.
	Returns the position of the bar helper.
	@bar: PBar object to use.
	"""
	if not bar:
		bar = PBar(	# we create a bar just to make stuff easier
			size=(20, 1),
			formatset=sets.FormatSet.EMPTY,
			colorset={
				"vert": "#090",
				"horiz": "#090",
				"corner": "#090",
				"text":	"#ff6400",
				"empty": "#090",
				"full": "#090"
			},
			centered=True
		)

	position, size = bar.position, bar.size
	bar.formatset |= {"title": f"uValues: pos{position} size{size}"}
	bar.prange = (0, 100)

	with Term.SeqMgr(hide_cursor=True, new_buffer=True):	# create a new buffer, and hide the cursor
		try:
			while True:
				for perc in range(100):
					bar.percentage = perc
					bar.position = position
					r_pos, r_size = bar.computed_values
					bar.formatset |= {"subtitle": f"cValues: pos{r_pos} size{r_size}"}

					x_line = Term.set_pos((0, r_pos[1])) + "═"*r_pos[0]
					y_line = "".join(Term.set_pos((r_pos[0], x)) + "║" for x in range(r_pos[1]))
					center = Term.set_pos(r_pos) + "╝"

					utils.out(
						Term.CLEAR_ALL
						+ bar._gen_bar()	# the bar itself
						+ Term.color((255, 100, 0)) + x_line + y_line + center	# x and y lines
						+ Term.CURSOR_HOME + Term.INVERT + "Press Ctrl-C to exit." + Term.RESET
					)
					sleep(0.01)
				bar.inverted = not bar.inverted
		except KeyboardInterrupt:
			pass

	del bar	# delete the bar we created
	return r_pos, r_size	# return the latest position and size of the helper