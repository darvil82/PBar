from typing import Callable, Optional

from . import sets, utils, bar
from . utils import Term, capValue


BContentGen = Callable[["BContentGenMgr"], str]


def bShape(
	position: tuple[int, int], size: tuple[int, int], charset,
	parsedColorset: dict, filled: Optional[str] = " "
) -> str:
	"""Generates a basic rectangular shape that uses a charset and a parsed colorset"""
	width, height = size[0] - 2, size[1] - 1

	charVert = (	# Vertical characters, normally "|" at both sides.
		parsedColorset["vert"]["left"] + charset["vert"]["left"],
		parsedColorset["vert"]["right"] + charset["vert"]["right"]
	)
	charHoriz = (	# Horizontal characters, normally "-" at top and bottom. Colors are not specified here to not spam output
		charset["horiz"]["top"],
		charset["horiz"]["bottom"],
	)
	charCorner = (	# Corners of the shape at all four sides
		parsedColorset["corner"]["tleft"] + charset["corner"]["tleft"],
		parsedColorset["corner"]["tright"] + charset["corner"]["tright"],
		parsedColorset["corner"]["bleft"] + charset["corner"]["bleft"],
		parsedColorset["corner"]["bright"] + charset["corner"]["bright"]
	)


	top: str = (
		Term.pos(position)
		+ charCorner[0]
		+ parsedColorset["horiz"]["top"] + charHoriz[0]*width
		+ charCorner[1]
	)

	mid: str = "".join((	# generate all the rows of the bar. If filled is None, we just make the cursor jump to the right
		Term.pos(position, (0, row+1))
		+ charVert[0]
		+ (Term.moveHoriz(width) if filled is None else filled[0]*width)
		+ charVert[1]
	) for row in range(height - 1))

	bottom: str = (
		Term.pos(position, (0, height))
		+ charCorner[2]
		+ parsedColorset["horiz"]["bottom"] + charHoriz[1]*width
		+ charCorner[3]
	)

	return top + mid + bottom


def bText(
	position: tuple[int, int], size: tuple[int, int],
	parsedColorset: dict,
	parsedFormatset: dict
) -> str:
	"""Generates all text for the bar"""
	width, height = size

	# set the max number of characters that a string should have on each part of the bar
	txtMaxWidth = width + 2
	txtSubtitle = utils.stripText(parsedFormatset["subtitle"], txtMaxWidth)
	txtInside = utils.stripText(parsedFormatset["inside"], txtMaxWidth - 4)
	txtTitle = utils.stripText(parsedFormatset["title"], txtMaxWidth)

	# position each text on its correct position relative to the bar
	textTitle = (
		Term.pos(position, (-1, 0))
		+ parsedColorset["text"]["title"]
		+ txtTitle
	) if parsedFormatset["title"] else ""

	textSubtitle = (
		Term.pos(position, (width - len(txtSubtitle) + 1, height - 1))
		+ parsedColorset["text"]["subtitle"]
		+ txtSubtitle
	) if parsedFormatset["subtitle"] else ""

	textRight = (
		Term.pos(position, (width + 3, height/2))
		+ parsedColorset["text"]["right"]
		+ parsedFormatset["right"]
	) if parsedFormatset["right"] else ""

	textLeft = (
		Term.pos(position, (-len(parsedFormatset["left"]) - 3, height/2))
		+ parsedColorset["text"]["left"]
		+ parsedFormatset["left"]
	) if parsedFormatset["left"] else ""

	textInside = (
		Term.pos(position, (width/2 - len(txtInside)/2, height/2))
		+ parsedColorset["text"]["inside"]
		+ txtInside
	) if parsedFormatset["inside"] else ""

	return textTitle + textSubtitle + textRight + textLeft + textInside


def iterRows(string: str, pos: tuple[int, int], height: tuple[int, int]) -> str:
	"""
	Iterate over the rows of the height specified,
	starting from the position given. The string supplied will be repeated
	for each row.
	Automatically positions the cursor at the beginning of each row.
	"""
	return "".join((
		Term.pos(pos, (0, row))
		+ string
	) for row in range(height))


def rect(
	pos: "bar.Position", size: tuple[int, int],
	char: str="█", color: utils.Color="white", centered: bool=False
) -> str:
	"""Generate a rectangle."""
	size = getComputedSize(size, (0, 0))
	pos = getComputedPosition(pos, (size if centered else None))

	if "\x1b" not in color:		# if it is already a terminal sequence, dont need to parse
		color = Term.color(color)

	return color + iterRows(
		char*size[0],
		pos,
		size[1]
	)


def getComputedPosition(
	position: "bar.Position",
	cSize: tuple[int, int],
	sizeOffset: tuple[int, int] = (0, 0)
) -> tuple[int, int]:
	"""
	Return a computed position based on the given position and size,
	and the size of the terminal.
	"""
	termSize = Term.size()
	newpos = list(position)

	for index, value in enumerate(position):
		if isinstance(value, str):
			if value == "center":
				value = termSize[index]//2
			else:
				raise ValueError("Position value must be an integer or 'center'")

		if value < 0:	# if negative value, return Term size - value
			value = termSize[index] + value


		value = utils.capValue(
			value,
			termSize[index] - cSize[index]/2 - sizeOffset[index],
			cSize[index]/2 + 1
		) if cSize else utils.capValue(
			value,
			termSize[index]
		)

		newpos[index] = int(value) - (cSize[index]//2 if cSize else 0)
	return tuple(newpos)


def getComputedSize(
	size: tuple[int, int],
	sizeOffset: tuple[int, int] = (2, 2),
	minSize: tuple[int, int] = (0, 0)
) -> tuple[int, int]:
	"""Return a computed size based on the given size, and the size of the terminal."""
	termSize = Term.size()
	newsize = list(size)

	for index in range(2):	# yields 0 and 1
		newsize[index] = (
			termSize[index] + size[index]
			if size[index] < 0
			else size[index]
		)

	width, height = map(int, newsize)

	return (
		utils.capValue(int(width), termSize[0] - sizeOffset[0], minSize[0]),
		utils.capValue(int(height), termSize[1] - sizeOffset[1], minSize[1])
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
		- `posX`: The X position of the content of the bar.
		- `posY`: The Y position of the content of the bar.
	- `size`: The size of the content of the bar.
		- `width`: The width of the content of the bar.
		- `height`: The height of the content of the bar.
	- `charFull`: The character used to fill the full part of the bar.
	- `charEmpty`: The character used to fill the empty space of the bar.
	- `colorFull`: The parsed color used to fill the full part of the bar.
	- `colorEmpty`: The parsed color used to fill the empty space of the bar.
	- `segmentsFull`: The number of segments used to fill the full part of the bar.
		- `segmentsFull[0]`: Horizontal segments.
		- `segmentsFull[1]`: Vertical segments.
	- `segmentsEmpty`: The number of segments used to fill the empty space of the bar.
		- `segmentsEmpty[0]`: Horizontal segments.
		- `segmentsEmpty[1]`: Vertical segments.

	### Methods

	- `iterRows()`: Iterate throught the rows of the bar height.
	Automatically positions the cursor at the beginning of each row.
	- `fill()`: Fill the bar with the given string.
	"""
	def __init__(self,
		contentg: BContentGen,
		invert: bool,
		position: tuple[int, int],
		size: tuple[int, int],
		charset: sets.CharSet,
		parsedColorset,
		prange: tuple[int, int]
	) -> None:
		"""
		@contentg: Bar content generator.
		@invert: Invert the chars and colors of the bar.
		"""
		self.contentg = contentg
		self.prange = prange

		self.position = position
		self.posX, self.posY = position

		self.size = size
		self.width, self.height = size

		setEntry = ("empty", "full") if invert else ("full", "empty")
		self.charFull, self.charEmpty = (
			charset[setEntry[0]], charset[setEntry[1]])
		self.colorFull, self.colorEmpty = (
			parsedColorset[setEntry[0]], parsedColorset[setEntry[1]])

		self.segmentsFull = (
			int((prange[0] / prange[1])*self.width),
			int(capValue((prange[0] / prange[1])*self.height, max=self.height))
		)
		self.segmentsEmpty = (
			self.width - self.segmentsFull[0],
			capValue(self.height - self.segmentsFull[1], min=0)
		)

	def __call__(self) -> str:
		"""Generate the content of the bar."""
		return Term.pos(self.position) + self.contentg(self)

	def iterRows(self, string: str):
		"""
		Iterate throught the rows of the bar height while adding the supplied
		string on each.
		Automatically positions the cursor at the beginning of each row.
		"""
		return iterRows(string, self.position, self.height)

	def fill(self, string: str):
		"""Fill the bar with the given string multiplied by the width of the bar."""
		return self.iterRows(string*self.width)




class ContentGens:
	"""Generators container."""
	# add all the default generators names
	Auto: BContentGen
	Left: BContentGen
	Right: BContentGen
	CenterX: BContentGen
	Bottom: BContentGen
	Top: BContentGen
	CenterY: BContentGen
	TopLeft: BContentGen
	TopRight: BContentGen
	BottomLeft: BContentGen
	BottomRight: BContentGen
	Center: BContentGen

	@staticmethod
	def register(generator: BContentGen = None, name: str = None) -> BContentGen:
		"""
		Register a new content generator. This basically adds the generator
		supplied to the `ContentGens` class as another attribute.

		@generator: The generator to register.
		@name: The name of the of the generator in the `ContentGens` class.
		By default, the name is the `__name__` of the generator. (the first letter
		will always be uppercase)
		"""
		def inner(generator: BContentGen) -> BContentGen:
			nonlocal name
			gName = generator.__name__ if name is None else name

			# add a attribute so we can tell later it is a generator
			setattr(generator, "isBContentGen", True)

			# add the generator to the class
			setattr(
				ContentGens,
				gName[0].upper() + gName[1:],	# capitalize only the first letter
				generator
			)
			return generator

		if generator is None:
			return inner

		return inner(generator)

	@staticmethod
	def getGens() -> tuple[BContentGen]:
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
	return bar.iterRows(
		bar.colorFull + bar.charFull*bar.segmentsFull[0]
		+ bar.colorEmpty + bar.charEmpty*bar.segmentsEmpty[0]
	)

@ContentGens.register
def right(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the right."""
	return bar.iterRows(
		bar.colorEmpty + bar.charEmpty*bar.segmentsEmpty[0]
		+ bar.colorFull + bar.charFull*bar.segmentsFull[0]
	)

@ContentGens.register
def centerX(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the center on the X axis."""
	return (
		bar.colorEmpty + bar.fill(bar.charEmpty)	# empty
		+ rect(	# full
			(bar.posX + bar.width/2, bar.posY + bar.height/2),
			(bar.segmentsFull[0], bar.height),
			bar.charFull,
			bar.colorFull,
			True
		)
	)

@ContentGens.register
def top(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the top."""
	return (
		bar.colorEmpty + bar.fill(bar.charEmpty)	# empty
		+ rect(	# full
			(bar.posX, bar.posY + bar.segmentsFull[1]),
			(bar.width, bar.segmentsEmpty[1]),
			bar.charFull,
			bar.colorFull,
		)
	)

@ContentGens.register
def bottom(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the bottom."""
	return (
		bar.colorEmpty + bar.fill(bar.charEmpty)
		+ rect(
			(bar.posX, bar.posY + bar.segmentsEmpty[1]),
			(bar.width, bar.segmentsFull[1]),
			bar.charFull,
			bar.colorFull,
		)
	)

@ContentGens.register
def centerY(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the center on the Y axis."""
	return (
		bar.colorEmpty + bar.fill(bar.charEmpty)
		+ rect(
			(bar.posX + bar.width/2, bar.posY + bar.height/2),
			(bar.width, bar.segmentsFull[1]),
			bar.charFull,
			bar.colorFull,
			True
		)
	)

@ContentGens.register
def topLeft(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the top left."""
	return (
		bar.colorEmpty + bar.fill(bar.charEmpty)	# the background
		+ rect(	# the full part
			bar.position,
			bar.segmentsFull,
			bar.charFull,
			bar.colorFull
		)
	)

@ContentGens.register
def topRight(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the top right."""
	return(
		bar.colorEmpty + bar.fill(bar.charEmpty)	# the background
		+ rect(	# the full part
			(
				bar.posX + bar.segmentsEmpty[0],
				bar.posY
			),
			bar.segmentsFull,
			bar.charFull,
			bar.colorFull
		)
	)

@ContentGens.register
def bottomLeft(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the bottom left."""
	return (
		bar.colorEmpty + bar.fill(bar.charEmpty)
		+ rect(	# the full part
			(
				bar.posX,
				bar.posY + bar.segmentsEmpty[1]
			),
			bar.segmentsFull,
			bar.charFull,
			bar.colorFull
		)
	)

@ContentGens.register
def bottomRight(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the bottom right."""
	return (
		bar.colorEmpty + bar.fill(bar.charEmpty)	# the background
		+ rect(	# the full part
			(
				bar.posX + bar.segmentsEmpty[0],
				bar.posY + bar.segmentsEmpty[1]
			),
			bar.segmentsFull,
			bar.charFull,
			bar.colorFull
		)
	)

@ContentGens.register
def center(bar: BContentGenMgr) -> str:
	"""Generate the content of a bar from the center."""
	return (
		bar.colorEmpty + bar.fill(bar.charEmpty)	# the background
		+ rect(	# the full part
			(
				bar.posX + bar.width/2,
				bar.posY + bar.height/2
			),
			bar.segmentsFull,
			bar.charFull,
			bar.colorFull,
			True
		)
	)