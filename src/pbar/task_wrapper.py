from typing import Any, Callable, Sequence, Tuple

from . bar import PBar



def _isinstance_indexsafe(array: Sequence, index: int, T: Any) -> bool:
	if index >= len(array):
		return False
	return isinstance(array[index], T)


def task_wrapper(func: Callable = None, /, *, overwrite_range: bool = True) -> Callable:
	"""
	### EXPERIMENTAL*

	Use as a decorator. Takes a PBar object, sets its prange depending on the quantity of
	function and method calls inside the function. Increments to the next step of the prange
	of the bar on every function and method call.

	The returned function will have `barObj` in its signature.

	```
	import time

	@task_wrapper
	def myTasks(myBar: PBar):
		myBar.text = "This is a progress bar"
		time.sleep(1)
		myBar.text = "Loading important assets"
		time.sleep(1)
		myBar.text = "Doing something very useful"
		time.sleep(1)
	```

	@barObj: PBar object to use.
	@overwrite_range: If False, the decorator will not overwrite the
	prange of the bar, instead, it will just step over the range.

	---

	\*: This function modifies the bytecode of the decorated function. Complex expressions
	may cause unexpected behaviour and errors.
	"""

	def insert_after_pair(bytecode: bytes, opcode: int, new: bytes) -> Tuple[bytes, int]:
		i = 0
		found = 0
		while i < len(bytecode):
			if bytecode[i] == opcode:
				bytecode = bytecode[:i+2] + new + bytecode[i+2:]
				i += len(new)
				found += 1
			i += 1

		return bytecode, found

	def wrapper(func: Callable):
		code = func.__code__
		bytecode = code.co_code

		bar_const_index = len(code.co_consts)

		names = code.co_names + ("step",)
		bar_meth_index = len(names)-1

		# Bytecode is
		# LOAD_CONST	bar_const_index
		# LOAD_METHOD	bar_meth_index
		# CALL_METHOD	0
		# POP_TOP		null
		insertion = (
			b"\x64" + bar_const_index.to_bytes(1, 'big')
			+ b"\xa0" + bar_meth_index.to_bytes(1, 'big')
			+ b"\xa1\x00"
			+ b"\x01\x00"
		)

		# DO NOT FLIP THESE BECAUSE IT WILL MAKE THE PROGRAM FREEZE
		max_range = 0
		# Insert after all CALL_METHOD
		bytecode, count = insert_after_pair(bytecode, 161, insertion)
		max_range += count
		# Insert after all CALL_FUNCTION
		bytecode, count = insert_after_pair(bytecode, 131, insertion)
		max_range += count

		func.__code__ = func.__code__.replace(
			co_code=bytecode, co_names=names
		)

		def inner(*args, **kwargs):
			if _isinstance_indexsafe(args, 0, PBar):
				barObj: PBar = args[0]
			elif _isinstance_indexsafe(args, 1, PBar):
				barObj: PBar = args[1]
			else:
				raise TypeError(
					f"{func.__name__} requires a PBar instance to be the first argument"
				)

			func.__code__ = (
				func.__code__.replace(
					co_consts=func.__code__.co_consts + (barObj,)
				)
			)

			if overwrite_range:
				barObj.prange = (0, max_range)

			barObj.draw()
			return func(*args, **kwargs)

		return inner

	if func is None:
		return wrapper

	return wrapper(func)