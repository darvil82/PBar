from typing import Optional, Union

from . sets import ColorSetEntry
from . utils import capValue, Term
from . sets import CharSet, ColorSet, FormatSet


class BarContent:
	HORIZONTAL: int = 0
	VERTICAL: int = 1

	def __init__(self, mode: int, gfrom: str) -> None:
		self.mode = mode
		self.gfrom = gfrom

	def getStr(self, position: tuple[int, int], size: tuple[int, int], chars: tuple[str, str],
			   parsedColorset: ColorSetEntry, prange: tuple[int, int]) -> str:
		if self.mode == BarContent.HORIZONTAL:
			return self._genHoriz(
				position,size, chars,
				parsedColorset, prange
			)
		elif self.mode == BarContent.VERTICAL:
			return self._genVert(
				position,size, chars,
				parsedColorset, prange
			)
		else:
			raise RuntimeError(f"unknown mode {self.mode}")


	def _genHoriz(self, pos, size, chars, pColorSet, prange):
		width, height = size
		SEGMENTS_FULL = int((capValue(prange[0], prange[1], 0) / capValue(prange[1], min=1))*width)
		SEGMENTS_EMPTY = width - SEGMENTS_FULL

		charFull, charEmpty = chars

		def iterRows(string: str):
			return "".join((
				Term.pos(pos, (0, row))
				+ string
			) for row in range(1, height))

		if self.gfrom == "left":
			return iterRows(
				pColorSet["full"] + charFull*SEGMENTS_FULL
				+ pColorSet["empty"] + charEmpty*SEGMENTS_EMPTY
			)
		elif self.gfrom == "right":
			return iterRows(
				pColorSet["empty"] + charEmpty*SEGMENTS_EMPTY
				+ pColorSet["full"] + charFull*SEGMENTS_FULL
			)
		elif self.gfrom == "center":
			return iterRows(
				pColorSet["empty"] + charEmpty*width
				+ Term.moveHoriz(-width/2 - SEGMENTS_FULL/2)
				+ pColorSet["full"] + charFull*SEGMENTS_FULL
			)
		else:
			raise RuntimeError(f"invalid gfrom {self.gfrom}")


	def _genVert(self, pos, size, chars, pColorSet, prange):
		width, height = size
		SEGMENTS_FULL = int((capValue(prange[0], prange[1], 0) / capValue(prange[1], min=1))*height)

		return Term.pos(pos, (0, SEGMENTS_FULL)) + "test"




def shape(position: tuple[int, int], size: tuple[int, int], charset: CharSet,
		  parsedColorset: dict, filled: Optional[str] = " ") -> str:
	"""Generates a basic rectangular shape that uses a charset and a parsed colorset"""
	width, height = size[0] + 2, size[1]

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
		Term.pos(position, (0, row))
		+ charVert[0]
		+ (Term.moveHoriz(width) if filled is None else filled[0]*width)
		+ charVert[1]
	) for row in range(1, height))

	bottom: str = (
		Term.pos(position, (0, height))
		+ charCorner[2]
		+ parsedColorset["horiz"]["bottom"] + charHoriz[1]*width
		+ charCorner[3]
	)

	return top + mid + bottom


def content(position: tuple[int, int], size: tuple[int, int], charset: CharSet,
			parsedColorset: ColorSet, rangeValue: tuple[int, int]) -> str:
	"""Generates the progress shape with a parsed colorset and a charset specified"""
	test = BarContent(BarContent.VERTICAL, "bottom")
	return test.getStr(
		position, size, (charset["full"], charset["empty"]), parsedColorset,
		rangeValue
	)


def bText(position: tuple[int, int], size: tuple[int, int],
		  parsedColorset: dict[str, Union[dict, str]], formatset: FormatSet) -> str:
	"""Generates all text for the bar"""
	width, height = size

	def stripText(string: str, maxlen: int):
		"""Return a string stripped if the len of it is larger than the maxlen specified"""
		maxlen = capValue(maxlen, min=3)
		return string[:maxlen-3] + "..." if len(string) > maxlen else string

	# set the max number of characters that a string should have on each part of the bar
	txtMaxWidth = width + 2
	txtSubtitle = stripText(formatset["subtitle"], txtMaxWidth)
	txtInside = stripText(formatset["inside"], txtMaxWidth - 4)
	txtTitle = stripText(formatset["title"], txtMaxWidth)

	# position each text on its correct position relative to the bar
	textTitle = (
		Term.pos(position, (-1, 0))
		+ parsedColorset["text"]["title"]
		+ txtTitle
	)

	textSubtitle = (
		Term.pos(position, (width - len(txtSubtitle) + 1, height))
		+ parsedColorset["text"]["subtitle"]
		+ txtSubtitle
	)

	textRight = (
		Term.pos(position, (width + 3, height/2))
		+ parsedColorset["text"]["right"]
		+ formatset["right"]
		+ Term.CLEAR_RIGHT
	) if formatset["right"] else ""

	textLeft = (
		Term.pos(position, (-len(formatset["left"]) - 3, height/2))
		+ Term.CLEAR_LEFT
		+ parsedColorset["text"]["left"]
		+ formatset["left"]
	) if formatset["left"] else ""

	txtInside = (
		Term.pos(position, (width/2 - len(txtInside)/2, height/2))
		+ parsedColorset["text"]["inside"]
		+ txtInside
	)

	return textTitle + textSubtitle + textRight + textLeft + txtInside