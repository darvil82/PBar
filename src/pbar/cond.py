from shlex import split as strSplit

from . import bar
from . sets import CharSet, ColorSet, FormatSet

_EQU = "=="
_NEQ = "!="
_GTR = ">"
_LSS = "<"
_GEQ = ">="
_LEQ = "<="


class Cond:
	def __init__(self, condition: str, charset: CharSet = None,
				 colorset: ColorSet = None, formatset: FormatSet = None) -> None:
		vs = strSplit(condition)
		self.attribute = vs[0]
		self.operator = vs[1]
		self.value = float(vs[2]) if vs[2].isnumeric() else vs[2]
		self.newSets = (charset, colorset, formatset)


	def test(self, cls: "bar.PBar") -> bool:
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


	def check(self, cls: "bar.PBar") -> None:
		if not self.test(cls):
			return False

		if self.newSets[0]:
			cls.charset = self.newSets[0]
		if self.newSets[1]:
			cls.colorset = self.newSets[1]
		if self.newSets[2]:
			cls.formatset = self.newSets[2]


	def __bool__(self):
		return self.test()