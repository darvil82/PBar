import sys
from typing import Callable, Optional

from . import sets, utils, bar
from . utils import Term, cap_value


BContentGen = Callable[["BContentGenMgr"], str]


def b_shape(
	position: tuple[int, int], size: tuple[int, int], charset: sets.CharSet,
	parsed_colorset: dict, filled: Optional[str] = " "
) -> str:
	"""Generates a basic rectangular shape that uses a charset and a parsed colorset"""
	width, height = size[0] - 2, size[1] - 1

	char_vert = (	# Vertical characters, normally "|" at both sides.
		parsed_colorset["vert"]["left"] + charset["vert"]["left"],
		parsed_colorset["vert"]["right"] + charset["vert"]["right"]
	)
	char_horiz = (	# Horizontal characters, normally "-" at top and bottom. Colors are not specified here to not spam output
		charset["horiz"]["top"],
		charset["horiz"]["bottom"],
	)
	char_corner = (	# Corners of the shape at all four sides
		parsed_colorset["corner"]["tleft"] + charset["corner"]["tleft"],
		parsed_colorset["corner"]["tright"] + charset["corner"]["tright"],
		parsed_colorset["corner"]["bleft"] + charset["corner"]["bleft"],
		parsed_colorset["corner"]["bright"] + charset["corner"]["bright"]
	)


	top: str = (
		Term.set_pos(position)
		+ char_corner[0]
		+ parsed_colorset["horiz"]["top"] + char_horiz[0]*width
		+ char_corner[1]
	)

	mid: str = "".join((	# generate all the rows of the bar. If filled is None, we just make the cursor jump to the right
		Term.set_pos(position, (0, row+1))
		+ char_vert[0]
		+ (Term.move_horiz(width) if filled is None else filled[0]*width)
		+ char_vert[1]
	) for row in range(height - 1))

	bottom: str = (
		Term.set_pos(position, (0, height))
		+ char_corner[2]
		+ parsed_colorset["horiz"]["bottom"] + char_horiz[1]*width
		+ char_corner[3]
	)

	return top + mid + bottom


def b_text(
	position: tuple[int, int],
	size: tuple[int, int],
	parsed_colorset: dict,
	parsed_formatset: dict
) -> str:
	"""Generates all text for the bar"""
	width, height = size

	# set the max number of characters that a string should have on each part of the bar
	txt_max_width = width + 2
	txt_subtitle = utils.strip_text(parsed_formatset["subtitle"], txt_max_width)
	txt_inside = utils.strip_text(parsed_formatset["inside"], txt_max_width - 4)
	txt_title = utils.strip_text(parsed_formatset["title"], txt_max_width)

	# position each text on its correct position relative to the bar
	text_title = (
		Term.set_pos(position, (-1, 0))
		+ parsed_colorset["text"]["title"]
		+ txt_title
	) if parsed_formatset["title"] else ""

	text_subtitle = (
		Term.set_pos(position, (width - len(txt_subtitle) + 1, height - 1))
		+ parsed_colorset["text"]["subtitle"]
		+ txt_subtitle
	) if parsed_formatset["subtitle"] else ""

	text_right = (
		Term.set_pos(position, (width + 3, height/2))
		+ parsed_colorset["text"]["right"]
		+ parsed_formatset["right"]
	) if parsed_formatset["right"] else ""

	text_left = (
		Term.set_pos(position, (-len(parsed_formatset["left"]) - 3, height/2))
		+ parsed_colorset["text"]["left"]
		+ parsed_formatset["left"]
	) if parsed_formatset["left"] else ""

	text_inside = (
		Term.set_pos(position, (width/2 - len(txt_inside)/2, height/2))
		+ parsed_colorset["text"]["inside"]
		+ txt_inside
	) if parsed_formatset["inside"] else ""

	return text_title + text_subtitle + text_right + text_left + text_inside


def iter_rows(string: str, pos: tuple[int, int], height: tuple[int, int]) -> str:
	"""
	Iterate over the rows of the height specified,
	starting from the position given. The string supplied will be repeated
	for each row.
	Automatically positions the cursor at the beginning of each row.
	"""
	return "".join((
		Term.set_pos(pos, (0, row))
		+ string
	) for row in range(height))


def rect(
	pos: "bar.Position",
	size: tuple[int, int],
	char: str = "█",
	color: Optional[utils.Color] = "white",
	centered: bool = False
) -> str:
	"""Generate a rectangle."""
	size = get_computed_size(size, (0, 0))
	pos = get_computed_position(pos, size, (-1, -1), centered)

	if color and "\x1b" not in color:		# if it is already a terminal sequence, dont need to parse
		color = Term.color(color)

	return (color or "") + iter_rows(
		char*size[0],
		pos,
		size[1]
	)


def get_computed_position(
	position: "bar.Position",
	c_size: tuple[int, int],
	size_offset: tuple[int, int] = (0, 0),
	centered: bool = True
) -> tuple[int, int]:
	"""
	Return a computed position based on the given position and size,
	and the size of the terminal.
	"""
	term_size = Term.get_size()
	newpos = list(position)

	for index, value in enumerate(position):
		if isinstance(value, str):
			if value.startswith("c"):
				value = term_size[index]//2 + int(value[1:]) if value[1:] else term_size[index]//2
			elif value.startswith("r"):
				cursor_pos = Term.get_pos(file=sys.stdout.original)
				value = cursor_pos[index] + int(value[1:]) if value[1:] else cursor_pos[index]
			else:
				raise ValueError("Invalid position value")
			value = max(value, 0)

		if value < 0:	# if negative value, return Term size - value
			value = term_size[index] + value

		value = utils.cap_value(
			value,
			term_size[index] - c_size[index]/2 - size_offset[index],
			c_size[index]/2 + 1
		) if centered else utils.cap_value(
			value,
			term_size[index] - c_size[index] - size_offset[index],
			1
		)

		newpos[index] = int(value) - (c_size[index]//2 if centered else 0)
	return newpos[0], newpos[1]

def get_computed_size(
	size: tuple[int, int],
	size_offset: tuple[int, int] = (2, 2),
	min_size: tuple[int, int] = (0, 0)
) -> tuple[int, int]:
	"""Return a computed size based on the given size, and the size of the terminal."""
	term_size = Term.get_size()
	newsize = list(size)

	for index in range(2):	# yields 0 and 1
		newsize[index] = (
			term_size[index] + size[index]
			if size[index] < 0
			else size[index]
		)

	width, height = map(int, newsize)

	return (
		utils.cap_value(int(width), term_size[0] - size_offset[0], min_size[0]),
		utils.cap_value(int(height), term_size[1] - size_offset[1], min_size[1])
	)




class BContentGenMgr:
	"""
	Generate the content of the bar with the bar content generator selected.
	Call this object to get the content string with the properties supplied.

	This object will contain the following properties, which can be used by
	`BContentGen` implementations:

	### Properties

	- `prange`: The current prange of the progress bar.
	- `position`: The position of the content of the bar.
		- `pos_x`: The X position of the content of the bar.
		- `pos_y`: The Y position of the content of the bar.
	- `size`: The size of the content of the bar.
		- `width`: The width of the content of the bar.
		- `height`: The height of the content of the bar.
	- `char_full`: The character used to fill the full part of the bar.
	- `char_empty`: The character used to fill the empty space of the bar.
	- `color_full`: The parsed color used to fill the full part of the bar.
	- `color_empty`: The parsed color used to fill the empty space of the bar.
	- `segments_full`: The number of segments used to fill the full part of the bar.
		- `segments_full[0]`: Horizontal segments.
		- `segments_full[1]`: Vertical segments.
	- `segments_empty`: The number of segments used to fill the empty space of the bar.
		- `segments_empty[0]`: Horizontal segments.
		- `segments_empty[1]`: Vertical segments.

	### Methods

	- `iter_rows()`: Iterate throught the rows of the bar height.
	Automatically positions the cursor at the beginning of each row.
	- `fill()`: Fill the bar with the given string.
	"""
	def __init__(self,
		contentg: BContentGen,
		invert: bool,
		position: tuple[int, int],
		size: tuple[int, int],
		charset: sets.CharSet,
		parsed_colorset,
		prange: tuple[int, int]
	) -> None:
		"""
		@contentg: Bar content generator.
		@invert: Invert the chars and colors of the bar.
		"""
		self.contentg = contentg
		self.prange = prange

		self.position = position
		self.pos_x, self.pos_y = position

		self.size = size
		self.width, self.height = size

		set_entry = ("empty", "full") if invert else ("full", "empty")
		self.char_full, self.char_empty = (
			charset[set_entry[0]], charset[set_entry[1]])
		self.color_full, self.color_empty = (
			parsed_colorset[set_entry[0]], parsed_colorset[set_entry[1]])

		self.segments_full = (
			int((prange[0] / prange[1])*self.width),
			int(cap_value((prange[0] / prange[1])*self.height, max=self.height))
		)
		self.segments_empty = (
			self.width - self.segments_full[0],
			cap_value(self.height - self.segments_full[1], min=0)
		)

	def __call__(self) -> str:
		"""Generate the content of the bar."""
		return Term.set_pos(self.position) + self.contentg(self)

	def iter_rows(self, string: str):
		"""
		Iterate throught the rows of the bar height while adding the supplied
		string on each.
		Automatically positions the cursor at the beginning of each row.
		"""
		return iter_rows(string, self.position, self.height)

	def fill(self, string: str):
		"""Fill the bar with the given string multiplied by the width of the bar."""
		return self.iter_rows(string*self.width)




class ContentGens:
	"""Generators container."""
	# add all the default generators names
	auto: BContentGen
	left: BContentGen
	right: BContentGen
	center_x: BContentGen
	bottom: BContentGen
	top: BContentGen
	center_y: BContentGen
	top_left: BContentGen
	top_right: BContentGen
	bottom_left: BContentGen
	bottom_right: BContentGen
	center: BContentGen

	@staticmethod
	def register(generator: BContentGen = None, name: str = None) -> BContentGen:
		"""
		Register a new content generator. This basically adds the generator
		supplied to the `ContentGens` class as another attribute.

		@generator: The generator to register.
		@name: The name of the of the generator in the `ContentGens` class.
		By default, the name is the `__name__` of the generator.
		"""
		def inner(generator: BContentGen) -> BContentGen:
			nonlocal name
			g_name = generator.__name__ if name is None else name

			# add a attribute so we can tell later it is a generator
			setattr(generator, "isBContentGen", True)

			# add the generator to the class
			setattr(
				ContentGens,
				g_name,
				generator
			)
			return generator

		if generator is None:
			return inner

		return inner(generator)

	@staticmethod
	def get_gens() -> tuple[BContentGen]:
		"""Get the registered generators."""
		return tuple(
			value for attr in dir(ContentGens)
			if hasattr(value := getattr(ContentGens, attr), "isBContentGen")
		)


# ------------------------- Default content generators -------------------------


@ContentGens.register
def auto(bar: BContentGenMgr) -> str:
	"""Select between Left or Bottom depending on the size of the bar"""
	return (
		left(bar)
		if bar.width//2 > bar.height else
		bottom(bar)
	)

@ContentGens.register
def left(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the left."""
	return bar.iter_rows(
		bar.color_full + bar.char_full*bar.segments_full[0]
		+ bar.color_empty + bar.char_empty*bar.segments_empty[0]
	)

@ContentGens.register
def right(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the right."""
	return bar.iter_rows(
		bar.color_empty + bar.char_empty*bar.segments_empty[0]
		+ bar.color_full + bar.char_full*bar.segments_full[0]
	)

@ContentGens.register
def center_x(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the center on the X axis."""
	return (
		bar.color_empty + bar.fill(bar.char_empty)	# empty
		+ rect(	# full
			(bar.pos_x + bar.width/2, bar.pos_y + bar.height/2),
			(bar.segments_full[0], bar.height),
			bar.char_full,
			bar.color_full,
			True
		)
	)

@ContentGens.register
def top(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the top."""
	return (
		bar.color_full + bar.fill(bar.char_full)	# empty
		+ rect(	# full
			(bar.pos_x, bar.pos_y + bar.segments_full[1]),
			(bar.width, bar.segments_empty[1]),
			bar.char_empty,
			bar.color_empty,
		)
	)

@ContentGens.register
def bottom(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the bottom."""
	return (
		bar.color_empty + bar.fill(bar.char_empty)
		+ rect(
			(bar.pos_x, bar.pos_y + bar.segments_empty[1]),
			(bar.width, bar.segments_full[1]),
			bar.char_full,
			bar.color_full,
		)
	)

@ContentGens.register
def center_y(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the center on the Y axis."""
	return (
		bar.color_empty + bar.fill(bar.char_empty)
		+ rect(
			(bar.pos_x + bar.width/2, bar.pos_y + bar.height/2),
			(bar.width, bar.segments_full[1]),
			bar.char_full,
			bar.color_full,
			True
		)
	)

@ContentGens.register
def top_left(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the top left."""
	return (
		bar.color_empty + bar.fill(bar.char_empty)	# the background
		+ rect(	# the full part
			bar.position,
			bar.segments_full,
			bar.char_full,
			bar.color_full
		)
	)

@ContentGens.register
def top_right(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the top right."""
	return(
		bar.color_empty + bar.fill(bar.char_empty)	# the background
		+ rect(	# the full part
			(
				bar.pos_x + bar.segments_empty[0],
				bar.pos_y
			),
			bar.segments_full,
			bar.char_full,
			bar.color_full
		)
	)

@ContentGens.register
def bottom_left(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the bottom left."""
	return (
		bar.color_empty + bar.fill(bar.char_empty)
		+ rect(	# the full part
			(
				bar.pos_x,
				bar.pos_y + bar.segments_empty[1]
			),
			bar.segments_full,
			bar.char_full,
			bar.color_full
		)
	)

@ContentGens.register
def bottom_right(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the bottom right."""
	return (
		bar.color_empty + bar.fill(bar.char_empty)	# the background
		+ rect(	# the full part
			(
				bar.pos_x + bar.segments_empty[0],
				bar.pos_y + bar.segments_empty[1]
			),
			bar.segments_full,
			bar.char_full,
			bar.color_full
		)
	)

@ContentGens.register
def center(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the center."""
	return (
		bar.color_empty + bar.fill(bar.char_empty)	# the background
		+ rect(	# the full part
			(
				bar.pos_x + bar.width/2,
				bar.pos_y + bar.height/2
			),
			bar.segments_full,
			bar.char_full,
			bar.color_full,
			True
		)
	)