# Version 1.16

The highlight of this version is the new flexibility to implement new custom generators for the progress indicator of the bar. New smaller additions and fixes were made too:

1. Fixed a lot of typing issues.
2. Removed the `config` property of `PBar`.
3. Added `Term.isSupported()` to check if the terminal is valid. This removes the possible return value `False` of `Term.size()`.
4. Fixed color conversion not working correctly with some values.
5. Changed the name of the property `gfrom` to `contentg`. This property now requires a content generator, which are available in the `pbar.ContentGens` class. For example, old: `gfrom=pbar.Gfrom.LEFT`, new: `contentg=pbar.ContentGens.Left`.
6. Refactored the entire content generator system (was called gfrom).
7. Added 5 new content generators:
	- TopLeft
	- TopRight
	- BottomLeft
	- BottomRight
	- Center
8. Rewrited some of the other generators to be faster to draw.
9. The content generator can now be changed with a `Cond` object.
10. Color values can no longer be `None`.

Please make sure to look at the documentation on the wiki for the content generators if you wish to create your own.

---

*Hey, if you are looking for a download page, you can get this from the sites listed [here!](https://github.com/DarviL82/PBar#installation)*