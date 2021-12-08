from shlex import split as strSplit
from typing import Callable

from . import bar, sets, utils


_OPs = {
	"EQ": "==",
	"NE": "!=",
	"GT": ">",
	"GE": ">=",
	"LT": "<",
	"LE": "<=",
	"IN": "<-",
}


class Cond:
	"""Condition manager used by a PBar object."""
	def __init__(self,
			condition: str, colorset: sets.ColorSetEntry = None,
			charset: sets.CharSetEntry = None,
			formatset: sets.FormatSetEntry = None,
			callback: Callable[["bar.PBar"], None] = None
		) -> None:
		"""
		Apply different customization sets to a bar, or call a callback
		if the condition supplied succeeds.
		Text comparisons are case insensitive.

		The callback function will be called with the PBar object that will use this Cond.

		---

		The condition string must be composed of three values separated by spaces:

		1. Attribute key (Formatting keys for `pbar.FormatSet`)
		2. Comparison operator (`==`, `!=`, `>`, `<`, `>=`, `<=`, `<-`)
		3. Value

		- Note: The "custom" operator `<-` stands for the attribute key containing the value.

		---

		### Examples:

		>>> Cond("percentage >= 50", ColorSet.DARVIL)

		>>> Cond("text <- 'error'", ColorSet.ERROR, formatset=FormatSet.TITLE_SUBTITLE)

		>>> Cond("etime >= 10", callback=myFunction)
		"""
		vs = self._chkCond(condition)
		self._attribute, self.operator = vs[:2]
		self._value = float(vs[2]) if utils.isNum(vs[2]) else vs[2].lower()	# convert to float if its a num
		self.newSets = (colorset, charset, formatset)
		self.callback = callback


	@staticmethod
	def _chkCond(cond: str):
		"""Check types and if the operator supplied is valid"""
		utils.chkInstOf(cond, str, name="condition")
		splitted = strSplit(cond)	# splits with strings in mind ('test "a b c" hey' > ["test", "a b c", "hey"])
		utils.chkSeqOfLen(splitted, 3, "condition")

		if splitted[1] not in _OPs.values():
			raise RuntimeError(f"Invalid operator {splitted[1]!r}")

		return splitted


	def __repr__(self) -> str:
		"""Returns `Cond('attrib operator value', *newSets)`"""
		return (f"{self.__class__.__name__}('{self._attribute} {self.operator} {self._value}', {self.newSets}, {self.callback})")


	def test(self, barObj: "bar.PBar") -> bool:
		"""Check if the condition succeeds with the values of the PBar object"""
		op = self.operator
		val = sets.FormatSet.getBarAttr(barObj, self._attribute)
		val = val.lower() if isinstance(val, str) else val

		# yeah, I would have used a dict for this, but not all operators are supported for all types
		if op == _OPs["EQ"]:	return val == self._value
		elif op == _OPs["NE"]:	return val != self._value
		elif op == _OPs["GT"]:	return val > self._value
		elif op == _OPs["GE"]:	return val >= self._value
		elif op == _OPs["LT"]:	return val < self._value
		elif op == _OPs["LE"]:	return val <= self._value
		elif op == _OPs["IN"]:	return self._value in val
		else:	return False


	def chkAndApply(self, barObj: "bar.PBar") -> None:
		"""Apply the new sets and run the callback if the condition succeeds"""
		if not self.test(barObj):
			return

		if self.newSets[0]:	barObj.colorset = self.newSets[0]
		if self.newSets[1]:	barObj.charset = self.newSets[1]
		if self.newSets[2]:	barObj.formatset = self.newSets[2]

		if self.callback:	self.callback(barObj)
