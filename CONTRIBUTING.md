# Contributing

First of all, thank you so much for being interested into contributing to this project.

This project does not have very strict contribution guidelines, but there are still some
that must be followed:

## Code

Code should always look consistent to the programmer. That's why we try to encourage everyone to follow
the same style.

- Python code must follow the official [PEP8 style guide](https://www.python.org/dev/peps/pep-0008/),
with the exception of using spaces for indentation. All code indentation must be made with **tabs**.
- No space between parenthesis on function calls, object initialization, etc:
	```py
	# No:
	my_function (arg1, arg2)
	my_function( arg1, arg2 )
	MyClass ( arg1, arg2 )
	
	# Yes:
	my_function(arg1, arg2)
	MyClass(arg1, arg2)
	```
- Keyword arguments should never have spaces between the name, the assign operator and the value, unless type hints
are being used. In that case, it is required to leave spaces. This is just following PEP8.
	```py
	# No:
	def my_function(kwarg1 = 12, kwarg2: str="foo"):
		...
	
	# Yes:
	def my_function(kwarg1=12, kwarg2: str = "foo"):
		...
	```
	This also applies to calls:
	```py
	# No:
	my_function(kwarg1 = 12, kwarg2 = "foo")
		...
	
	# Yes:
	my_function(kwarg1=12, kwarg2="foo")
		...
	```
- Please use type hints to make the code easier to read.
