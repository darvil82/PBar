This version mostly fixes small bugs from the last version. But also adds a few small things to the Cond class.
- Imrpoved the system that checks for screen scrolling generally.
- A cleared bar should be faster to draw now.
- `Cond` condition strings can now use ranges with the `{start[..step][..end]}` syntax. [More information].(https://github.com/DarviL82/PBar/wiki/Cond#the-condition-format)
- `Cond` now has a `times` property, which specifies the maximum number of times the condition will be checked.
- Removed `PBar.prange_from_file()`. Now useless with `pbar.iter()`.