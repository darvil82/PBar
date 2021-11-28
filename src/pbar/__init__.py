"""
![logo_small](https://user-images.githubusercontent.com/48654552/134991429-1109ad1d-92fa-423f-8ce1-3b777471cb3d.png)

### Library to display customizable progress bars on the terminal easily, for Python3.9+

- [GitHub Repository](https://github.com/DarviL82/PBar)
- [Wiki](https://github.com/DarviL82/PBar/wiki)
- [PyPI](https://pypi.org/manage/project/pbar2)
"""

__version__ = "1.13.0"

from . bar import PBar, animate, taskWrapper, barHelper
from . sets import CharSet, FormatSet, ColorSet
from . cond import Cond
from . gen import Gfrom
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