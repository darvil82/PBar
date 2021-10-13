from shlex import split as strSplit

from . utils import chkSeqOfLen, isNum
from . import bar
from . sets import ColorSetEntry, FormatSetEntry, CharSetEntry, FormatSet

_EQU = "=="
_NEQ = "!="
_GTR = ">"
_LSS = "<"
_GEQ = ">="
_LEQ = "<="


class Cond:
	"""Condition manager used by a PBar object."""
	def __init__(self, condition: str, charset: CharSetEntry = None,
				 colorset: ColorSetEntry = None, formatset: FormatSetEntry = None) -> None:
		"""
		Apply different customization sets to a bar if the condition supplied succeeds.
		The condition string must be composed of three values separated by spaces:

		1. Attribute key (Formatting keys for `pbar.FormatSet`)
		2. Comparison operator (`==`, `!=`, `>`, `<`, `>=`, `<=`)
		3. Value

		---

		### Examples:

		>>> Cond("percentage >= 50", colorset=ColorSet.DARVIL)

		>>> Cond("text == 'error'", colorset=ColorSet.ERROR, formatset=FormatSet.TITLE_SUBTITLE)
		"""
		vs = strSplit(condition)
		chkSeqOfLen(vs, 3, "condition")
		self.attribute, self.operator = vs[0:2]
		self.value = float(vs[2]) if isNum(vs[2]) else vs[2]
		self.newSets = (charset, colorset, formatset)


	def __repr__(self) -> str:
		return f"{self.__class__.__name__}('{self.attribute} {self.operator} {self.value}', {self.newSets})"


	def test(self, cls: "bar.PBar") -> bool:
		"""Check if the condition succeededs with the values of the PBar object"""
		op = self.operator
		val = FormatSet._getBarAttrs(cls, self.attribute)

		if op == _EQU:
			return val == self.value
		elif op == _NEQ:
			return val != self.value
		elif op == _GTR:
			return val > self.value
		elif op == _LSS:
			return val < self.value
		elif op == _GEQ:
			return val >= self.value
		elif op == _LEQ:
			return val <= self.value
		else:
			raise RuntimeError(f"Invalid operator {op!r}")