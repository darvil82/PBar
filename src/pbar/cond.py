from shlex import split as strSplit

from . utils import chkInstOf, chkSeqOfLen, isNum
from . import bar
from . sets import ColorSetEntry, FormatSetEntry, CharSetEntry, FormatSet

_OP_EQU = "=="
_OP_NEQ = "!="
_OP_GTR = ">"
_OP_LSS = "<"
_OP_GEQ = ">="
_OP_LEQ = "<="
_OP_IN = "<-"


class Cond:
	"""Condition manager used by a PBar object."""
	def __init__(self, condition: str, colorset: ColorSetEntry=None,
				 charset: CharSetEntry=None, formatset: FormatSetEntry=None) -> None:
		"""
		Apply different customization sets to a bar if the condition supplied succeeds.
		Text comparisons are case insensitive.

		The condition string must be composed of three values separated by spaces:

		1. Attribute key (Formatting keys for `pbar.FormatSet`)
		2. Comparison operator (`==`, `!=`, `>`, `<`, `>=`, `<=`, `<-`)
		3. Value

		- Note: The "custom" operator `<-` stands for the attribute key containing the value.

		---

		### Examples:

		>>> Cond("percentage >= 50", ColorSet.DARVIL)

		>>> Cond("text <- 'error'", ColorSet.ERROR, formatset=FormatSet.TITLE_SUBTITLE)
		"""
		vs = self._chkCond(condition)
		self._attribute, self.operator = vs[0:2]
		self._value = float(vs[2]) if isNum(vs[2]) else vs[2].lower()	# convert to float if its a num
		self.newSets = (charset, colorset, formatset)


	@staticmethod
	def _chkCond(cond: str):
		"""Check types and if the operator supplied is valid"""
		chkInstOf(cond, str, name="condition")
		splitted = strSplit(cond)	# splits with strings in mind ('test "a b c" hey' > ["test", "a b c", "hey"])
		chkSeqOfLen(splitted, 3, "condition")

		if splitted[1] not in {_OP_EQU, _OP_NEQ, _OP_GTR, _OP_LSS,	# check if the operator is valid
							   _OP_GEQ, _OP_LEQ, _OP_IN}:
			raise RuntimeError(f"Invalid operator {splitted[1]!r}")

		return splitted


	def __repr__(self) -> str:
		"""Returns `Cond('attrib operator value', *newSets)`"""
		return (f"{self.__class__.__name__}('{self._attribute} {self.operator} {self._value}', {self.newSets})")


	def test(self, cls: "bar.PBar") -> bool:
		"""Check if the condition succeededs with the values of the PBar object"""
		op = self.operator
		val = FormatSet.getBarAttrs(cls, self._attribute)
		val = val.lower() if isinstance(val, str) else val

		if op == _OP_EQU:
			return val == self._value
		elif op == _OP_NEQ:
			return val != self._value
		elif op == _OP_GTR:
			return val > self._value
		elif op == _OP_LSS:
			return val < self._value
		elif op == _OP_GEQ:
			return val >= self._value
		elif op == _OP_LEQ:
			return val <= self._value
		elif op == _OP_IN:
			return self._value in val
		else:
			return False