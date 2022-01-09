from shlex import split as strSplit
from typing import Callable

from . import bar, sets, utils, gen


_OPERATORS = {
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
		condition: str,
		colorset: sets.ColorSetEntry = None,
		charset: sets.CharSetEntry = None,
		formatset: sets.FormatSetEntry = None,
		contentg: gen.BContentGen = None,
		callback: Callable[["bar.PBar"], None] = None
	) -> None:
		"""
		Apply different customization options to a bar, or call a callback
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
		vs = self._chk_cond(condition)
		self._attribute, self.operator = vs[:2]
		self._value = float(vs[2]) if utils.is_num(vs[2]) else vs[2].lower()	# convert to float if its a num
		self.new_sets = (colorset, charset, formatset)
		self.conteng = contentg
		self.callback = callback


	@staticmethod
	def _chk_cond(cond: str):
		"""Check types and if the operator supplied is valid"""
		utils.chk_inst_of(cond, str, name="condition")
		splitted = strSplit(cond)	# splits with strings in mind ('test "a b c" hey' > ["test", "a b c", "hey"])
		utils.chk_seq_of_len(splitted, 3, "condition")

		if splitted[1] not in _OPERATORS.values():
			raise RuntimeError(f"Invalid operator {splitted[1]!r}")

		return splitted


	def __repr__(self) -> str:
		"""Returns `Cond('attrib operator value', *newSets)`"""
		return (
			f"{self.__class__.__name__}('{self._attribute} {self.operator} {self._value}', {self.new_sets}, {self.callback}, {self.conteng})"
		)


	def test(self, bar_obj: "bar.PBar") -> bool:
		"""Check if the condition succeeds with the values of the PBar object"""
		op = self.operator
		val = sets.FormatSet.get_bar_attr(bar_obj, self._attribute)
		val = val.lower() if isinstance(val, str) else val

		# we use lambdas because some values may not be compatible with some operators
		operators: dict[str, Callable] = {
			_OPERATORS["EQ"]: lambda: val == self._value,
			_OPERATORS["NE"]: lambda: val != self._value,
			_OPERATORS["GT"]: lambda: val > self._value,
			_OPERATORS["GE"]: lambda: val >= self._value,
			_OPERATORS["LT"]: lambda: val < self._value,
			_OPERATORS["LE"]: lambda: val <= self._value,
			_OPERATORS["IN"]: lambda: self._value in val,
		}

		return operators.get(op, lambda: False)()


	def chk_and_apply(self, bar_obj: "bar.PBar") -> None:
		"""Apply the new sets and run the callback if the condition succeeds"""
		if not self.test(bar_obj):
			return

		if self.new_sets[0]:	bar_obj.colorset = self.new_sets[0]
		if self.new_sets[1]:	bar_obj.charset = self.new_sets[1]
		if self.new_sets[2]:	bar_obj.formatset = self.new_sets[2]

		if self.conteng:	bar_obj.contentg = self.conteng

		if self.callback:	self.callback(bar_obj)
