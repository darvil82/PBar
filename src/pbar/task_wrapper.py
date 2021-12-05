from . bar import PBar
from . import utils

from typing import Callable


def _isinstance_indexsafe(array, index, T) -> bool:
    if index >= len(array):
        return False
    return isinstance(array[index], T)


def taskWrapper(func=None, /, *, overwriteRange=True) -> Callable:
    """
    Use as a decorator. Takes a PBar object, sets its prange depending on the quantity of
    function and method calls inside the functions. Increments to the next step on every
    function and method call.

    The returned function will have barObj in its signiture.

    ```
    import time

    @taskWrapper
    def myTasks(pbar):
            pbar.text = "This is a progress bar"
            time.sleep(1)
            pbar.text = "Loading important assets"
            time.sleep(1)
            pbar.text = "Doing something very useful"
            time.sleep(1)
    ```

    @barObj: PBar object to use.
    @overwriteRange: If True, overwrites the prange of the bar.
    """

    def insertAfterPair(bytecode, opcode, new):
        i = 0
        found = 0
        while i < len(bytecode):
            if bytecode[i] == opcode:
                bytecode = bytecode[:i+2] + new + bytecode[i+2:]
                i += len(new)
                found += 1
            i += 1

        return bytecode, found

    def wrapper(func):
        code = func.__code__
        bytecode = code.co_code

        barConstIndex = len(code.co_consts)

        names = code.co_names + ("step",)
        barMethIndex = len(names)-1

        # Bytecode is
        # LOAD_CONST	barConstIndex
        # LOAD_METHOD	barMethIndex
        # CALL_METHOD	0
        # POP_TOP		null
        insertion = (
            b"\x64" + barConstIndex.to_bytes(1, 'big')
            + b"\xa0" + barMethIndex.to_bytes(1, 'big')
            + b"\xa1\x00"
            + b"\x01\x00"
        )

        # DO NOT FLIP THESE BECAUSE IT WILL MAKE THE PROGRAM FREEZE
        maxRange = 0
        # Insert after all CALL_METHOD
        bytecode, count = insertAfterPair(bytecode, 161, insertion)
        maxRange += count
        # Insert after all CALL_FUNCTION
        bytecode, count = insertAfterPair(bytecode, 131, insertion)
        maxRange += count

        func.__code__ = func.__code__.replace(
            co_code=bytecode, co_names=names
        )

        def inner(*args, **kwargs):
            if _isinstance_indexsafe(args, 0, PBar):
                barObj = args[0]
            elif _isinstance_indexsafe(args, 1, PBar):
                barObj = args[1]
            else:
                raise TypeError(
                    f"{func.__name__} requies a Pbar instance to be the first argument"
                )

            func.__code__ = (
                func.__code__.replace(
                    co_consts=func.__code__.co_consts + (barObj,)
                )
            )

            if overwriteRange:
                barObj.prange = (0, maxRange)

            barObj.draw()
            return func(*args, **kwargs)

        return inner

    if func is None:
        return wrapper

    return wrapper(func)
