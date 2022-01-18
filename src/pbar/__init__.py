"""
![logo_small](https://user-images.githubusercontent.com/48654552/134991429-1109ad1d-92fa-423f-8ce1-3b777471cb3d.png)

### Library to display customizable progress bars on the terminal easily, for Python3.9+

- [Wiki](https://github.com/DarviL82/PBar/wiki)
- [GitHub Repository](https://github.com/DarviL82/PBar)
- [PyPI](https://pypi.org/manage/project/pbar2)
- [Website](https://darvil82.github.io/PBar)
"""

__version__ = "2.1.1"

from . bar import PBar, iter, animate, bar_helper
from . task_wrapper import task_wrapper
from . sets import CharSet, FormatSet, ColorSet
from . cond import Cond
from . gen import ContentGens
from . utils import Term


# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ░░░░░░░░░░░░░░░░▄▄▄███████▄▄░░░░░░░░░░░░
# ░░░░░░░░░░░░░░▄███████████████▄░░░░░░░░░
# ░░░░░░░░░░░░░█▀▀▀▄░░░░█████▀▀███▄░░░░░░░
# ░░░░░░░░░░░░█░░▄░░█▄▄█░░░░▀▄▄█████░░░░░░
# ░░░░░░░░░▄▀▀▀▄▄▀▀▀▀▀▀▄░░▀░░█▀▀▀░▀██░░░░░
# ░░░░░░░▄▀░░░░░█░░░░░░▀▄▄▄▄█░░░░░░░▀▄░░░░
# ░░░░░░▄▀░░░░░▄█▀▄▄▄▄░░░░░▄░░░░░░░░░█░░░░
# ░░░░░░█░░░░░▄█▀▄▄▄▄▄▄▄▄▄▀▀░░░░░░░░░▀▄░░░
# ░░░░░█░░░░░░▀█▄░░░░░░░░░░░░░░░░░░░░░█░░░
# ░░░░░█░░░░░░░░▀▄░░░░░░░░░░░░░░░░░░░░█░░░
# ░░░░░█░░░░░░░░▄█░░░░░░░░░░░░░░░░░░░░█░░░
# ░░░░░█░░░░░░▄▀░░░░░░░░▀▄░░░░░░░░░░░░█░░░
# ░░░░░█░░░░░░▀▄░░░▄░░░░░█░░░░░░░░░░░░█░░░
# ░░░░░█░░░░░░░░▀▀▀▀▀█▄▄▀░░░░░░░░░░░░░█░░░
# ░░░░░█░░░░░░░░░░░░░░░░░░░░░░░░░░░░░▄██░░
# ░░░░░█▄░░░░░░░░░░░░░░░░░░░░░░░░░░▄▀▀▄▀▄▄
# ░░░░▄█▀▄░░░░░░░░░░░░░░░░░░░░░░▄▄▀░░▄▀░░░
# ░▄░▀░░█░▀▄▄░░░░░░░░░░░░░░░▄▄▄▀░░░▄▀░░░░░
# ▀░░░░░░▀▄░░▀▄░░░░░░░░▄▄▄▀▀░░░░▄▀▀░░░░░░░

# Thanks a lot for taking a look at this project. - DarviL
