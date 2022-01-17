from shlex import split as str_split
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
		callback: Callable[["bar.PBar"], None] = None,
		times: int = 1
	) -> None:
		"""
		Apply different customization options to a bar, or call a callback
		if the condition supplied succeeds.

		@condition: string of the form `attrib operator value`
		@colorset: ColorSetEntry to apply to the bar
		@charset: CharSetEntry to apply to the bar
		@formatset: FormatSetEntry to apply to the bar
		@contentg: BContentGen to apply to the bar
		@callback: The callback function that will be called with the PBar
		object that will use this Cond.
		@times: The maximum number of times the condition will be checked.
		`-1` (or any negative number) will make the condition be checked any number of times.

		---

		#### The condition format
		The condition string must be composed of three values separated by spaces:

		1. Attribute key (Formatting keys for `pbar.FormatSet`)
		2. Comparison operator (`==`, `!=`, `>`, `<`, `>=`, `<=`, `<-`)
		3. Value

		- Note: The "custom" operator `<-` stands for the attribute key containing the value.
		If the property of the bar is a number, a range object can be specified to check for with the
		`{start[..end][..step]}` syntax.

		---

		### Examples:

		>>> Cond("percentage >= 50", ColorSet.DARVIL)

		>>> Cond("text <- 'error'", ColorSet.ERROR, formatset=FormatSet.TITLE_SUBTITLE)

		>>> Cond("etime >= 10", callback=myFunction)

		>>> Cond("percentage <- {25..36}", ColorSet.RED, times=1)	# only check once if the percentage is between 25 and 35
		"""
		vs = self._chk_cond(condition)
		self._attribute, self._operator, self._value = vs
		self.new_sets = (colorset, charset, formatset)
		self.contentg = contentg
		self.callback = callback
		self.times = times


	@staticmethod
	def _chk_cond(cond: str):
		"""Check types and if the operator supplied is valid"""
		utils.chk_inst_of(cond, str, name="condition")
		splitted = str_split(cond)	# splits with strings in mind ('test "a b c" hey' > ["test", "a b c", "hey"])
		utils.chk_seq_of_len(splitted, 3, "condition")

		if splitted[1] not in _OPERATORS.values():
			raise RuntimeError(f"Invalid operator {splitted[1]!r}")

		return splitted


	def __repr__(self) -> str:
		"""Returns `Cond('attrib operator value', newSets)`"""
		return (
			f"{self.__class__.__name__}('{self._attribute} {self._operator} "
			f"{self._value}', {self.new_sets}, {self.callback}, {self.contentg}, {self.times})"
		)


	def test(self, bar_obj: "bar.PBar") -> bool:
		"""Check if the condition succeeds with the values of the PBar object"""
		op = self._operator
		cond_value = float(self._value) if utils.is_num(self._value) else self._value.lower()
		bar_value = sets.FormatSet.get_bar_attr(bar_obj, self._attribute)

		is_checking_range = False	# whether we are checking a number in a range
		if is_checking_range := (
			isinstance(cond_value, str)
			and cond_value.startswith("{") and cond_value.endswith("}")
			and utils.is_num(bar_value)
		):
			range_splitted = cond_value[1:-1].split("..")
			utils.chk_seq_of_len(range_splitted, range(1, 4), "Cond_range")
			cond_value = range(*map(int, range_splitted))

		# we use lambdas because some values may not be compatible with some operators
		operators: dict[str, Callable] = {
			_OPERATORS["EQ"]: lambda: bar_value == cond_value,
			_OPERATORS["NE"]: lambda: bar_value != cond_value,
			_OPERATORS["GT"]: lambda: bar_value > cond_value,
			_OPERATORS["GE"]: lambda: bar_value >= cond_value,
			_OPERATORS["LT"]: lambda: bar_value < cond_value,
			_OPERATORS["LE"]: lambda: bar_value <= cond_value,
			_OPERATORS["IN"]: lambda: (
				cond_value in bar_value
				if not is_checking_range else
				bar_value in cond_value
			),
		}

		return operators.get(op, lambda: False)()


	def chk_and_apply(self, bar_obj: "bar.PBar") -> None:
		"""Apply the new sets and run the callback if the condition succeeds"""
		if not self.test(bar_obj) or self.times == 0:
			return

		if self.new_sets[0]:	bar_obj.colorset = self.new_sets[0]
		if self.new_sets[1]:	bar_obj.charset = self.new_sets[1]
		if self.new_sets[2]:	bar_obj.formatset = self.new_sets[2]

		if self.contentg:	bar_obj.contentg = self.contentg

		if self.callback:	self.callback(bar_obj)

		# subtract 1 from `times` after each successful check
		if self.times > 0:
			self.times -= 1