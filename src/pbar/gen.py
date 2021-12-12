from abc import ABC, abstractmethod
from typing import Optional

from . import sets, utils, bar
from . utils import Term, capValue




class BarGenerator(ABC):
	@abstractmethod
	def generate(self, bar: "BarContent") -> str:
		pass


class Gfrom:
	"""Generators container."""
	Auto: BarGenerator
	Left: BarGenerator
	Right: BarGenerator
	CenterX: BarGenerator
	Bottom: BarGenerator
	Top: BarGenerator
	CenterY: BarGenerator

	def register(generator: BarGenerator) -> BarGenerator:
		"""Register a new content generator."""
		setattr(Gfrom, generator.__name__, generator)
		return generator


class BarContent:
	"""
	Generate the content of the bar with the BarGenerator selected.
	Call this object to get the content string with the properties supplied.

	This object will contain the following properties, which can be used by
	`BarGenerator` implementations:

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

	- `iterRows()`: Iterate over the rows of the bar height.
	Automatically positions the cursor at the beginning of each row.
	"""
	def __init__(self,
			gfrom: BarGenerator,
			invert: bool,
			position: tuple[int, int],
			size: tuple[int, int],
			charset: sets.CharSet,
			parsedColorset,
			prange: tuple[int, int]
		) -> None:
		"""
		@gfrom: Bar content generator.
		@invert: Invert the chars and colors of the bar.
		"""
		self.gfrom = gfrom
		self.prange = prange

		self.position = position
		self.posX, self.posY = position

		self.size = size
		self.width, self.height = size

		setEntry = ("empty", "full") if invert else ("full", "empty")
		self.charFull, self.charEmpty = charset[setEntry[0]], charset[setEntry[1]]
		self.colorFull, self.colorEmpty = parsedColorset[setEntry[0]], parsedColorset[setEntry[1]]


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
		return Term.pos(self.position) + self.gfrom.generate(self)


	def iterRows(self, string: str):
		"""
		Iterate over the rows of the bar height.
		Automatically positions the cursor at the beginning of each row.
		"""
		return "".join((
			Term.pos(self.position, (0, row))
			+ string
		) for row in range(self.height))




# -------------- Default content generators --------------

@Gfrom.register
class Auto(BarGenerator):
	"""Select between Left or Bottom depending on the size of the bar"""
	def generate(bar: BarContent) -> str:
		return (
			Bottom.generate(bar)
			if bar.height > bar.width else
			Left.generate(bar)
		)

@Gfrom.register
class Left(BarGenerator):
	"""Generate the content of a bar from the left."""
	def generate(bar: BarContent) -> str:
		return bar.iterRows(
			bar.colorFull + bar.charFull*bar.segmentsFull[0]
			+ bar.colorEmpty + bar.charEmpty*bar.segmentsEmpty[0]
		)

@Gfrom.register
class Right(BarGenerator):
	"""Generate the content of a bar from the right."""
	def generate(bar: BarContent) -> str:
		return bar.iterRows(
			bar.colorEmpty + bar.charEmpty*bar.segmentsEmpty[0]
			+ bar.colorFull + bar.charFull*bar.segmentsFull[0]
		)

@Gfrom.register
class CenterX(BarGenerator):
	"""Generate the content of a bar from the center."""
	def generate(bar: BarContent) -> str:
		return bar.iterRows(
			bar.colorEmpty + bar.charEmpty*bar.width
			+ Term.moveHoriz(-bar.width/2 - bar.segmentsFull[0]/2)
			+ bar.colorFull + bar.charFull*bar.segmentsFull[0]
		)

@Gfrom.register
class Top(BarGenerator):
	"""Generate the content of a bar from the top."""
	def generate(bar: BarContent) -> str:
		return (
			bar.colorFull + (
					bar.charFull*bar.width + Term.posRel((-bar.width, 1))
				)*bar.segmentsFull[1]
			+ bar.colorEmpty + (
					bar.charEmpty*bar.width + Term.posRel((-bar.width, 1))
				)*bar.segmentsEmpty[1]
		)

@Gfrom.register
class Bottom(BarGenerator):
	"""Generate the content of a bar from the bottom."""
	def generate(bar: BarContent) -> str:
		return (
			bar.colorEmpty + (
					bar.charEmpty*bar.width + Term.posRel((-bar.width, 1))
				)*bar.segmentsEmpty[1]
			+ bar.colorFull + (
					bar.charFull*bar.width + Term.posRel((-bar.width, 1))
				)*bar.segmentsFull[1]
		)

@Gfrom.register
class CenterY(BarGenerator):
	"""Generate the content of a bar from the center."""
	def generate(bar: BarContent) -> str:
		return (
			bar.colorEmpty + (
					bar.charEmpty*bar.width + Term.posRel((-bar.width, 1))
				)*bar.height
			+ Term.moveVert(-bar.height/2 - bar.segmentsFull[1]/2)
			+ bar.colorFull + (
					bar.charFull*bar.width + Term.posRel((-bar.width, 1))
				)*bar.segmentsFull[1]
		)

# -------------- ////////////////////////////// --------------




def shape(
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


def rect(
		pos: "bar.Position", size: tuple[int, int],
		char: str="█", color: utils.Color="white"
	) -> str:
	"""Generate a rectangle."""
	size = getComputedSize(size)
	pos = getComputedPosition(pos, size)

	return shape(
		pos, size,
		sets.CharSet({"corner": char, "horiz": char, "vert": char}),
		sets.ColorSet({"corner": color, "horiz": color, "vert": color}).parsedValues(),
		char
	) + Term.RESET


def getComputedPosition(position: "bar.Position", cSize: tuple[int, int]) -> tuple[int, int]:
	"""
	Return a computed position based on the given position,
	the size supplied by the user, and the size of the terminal
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

		# set maximun and minimun positions
		value = utils.capValue(
			value,
			termSize[index] - cSize[index]/2 - 1,
			cSize[index]/2 + 1
		)

		newpos[index] = int(value) - cSize[index]//2
	return tuple(newpos)


def getComputedSize(size: tuple[int, int]) -> tuple[int, int]:
	"""Return a computed size based on the given size, and the size of the terminal"""
	termSize = Term.size()
	newsize = list(size)

	for index in range(2):
		newsize[index] = (
			termSize[index] + size[index]
			if size[index] < 0
			else size[index]
		)

	width, height = map(int, newsize)

	return (
		utils.capValue(int(width), termSize[0] - 2, 1),
		utils.capValue(int(height), termSize[1] - 2, 1)
	)