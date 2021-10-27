from . sets import ColorSetEntry
from . utils import capValue, Term

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
			raise RuntimeError("unknown mode")


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
		return ""